#!/usr/bin/env python

# *****************************************************************************
# Copyright (c) 2014, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import argparse
import time
import sys
import psutil
import platform
import json
import signal
from uuid import getnode as get_mac


try:
    import wiotp.sdk.device
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import wiotp.sdk"
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../../src"))
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import wiotp.sdk.device


def interruptHandler(signal, frame):
    client.disconnect()
    sys.exit(0)


def commandProcessor(cmd):
    global interval
    print("Command received: %s" % cmd.data)
    if cmd.commandId == "setInterval":
        if "interval" not in cmd.data:
            print("Error - command is missing required information: 'interval'")
        else:
            try:
                interval = int(cmd.data["interval"])
            except ValueError:
                print("Error - interval not an integer: ", cmd.data["interval"])
    elif cmd.commandId == "print":
        if "message" not in cmd.data:
            print("Error - command is missing required information: 'message'")
        else:
            print(cmd.data["message"])


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interruptHandler)

    # Seconds to sleep between readings
    interval = 5

    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform PSUtil device client.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/psutil",
        epilog="If neither the quickstart or cfg parameter is provided the device will attempt to parse the configuration from environment variables.",
    )
    parser.add_argument(
        "-n", "--name", required=False, default=platform.node(), help="Defaults to platform.node() if not set"
    )
    parser.add_argument("-q", "--quickstart", required=False, action="store_true", help="Connect device to quickstart?")
    parser.add_argument(
        "-c",
        "--cfg",
        required=False,
        default=None,
        help="Location of device configuration file (ignored if quickstart mode is enabled)",
    )
    parser.add_argument("-v", "--verbose", required=False, action="store_true", help="Enable verbose log messages?")
    args, unknown = parser.parse_known_args()

    client = None
    try:
        if args.quickstart:
            options = {
                "identity": {
                    "orgId": "quickstart",
                    "typeId": "sample-iotpsutil",
                    "deviceId": str(hex(int(get_mac())))[2:],
                }
            }
        elif args.cfg is not None:
            options = wiotp.sdk.device.parseConfigFile(args.cfg)
        else:
            options = wiotp.sdk.device.parseEnvVars()

        client = wiotp.sdk.device.DeviceClient(options)
        client.commandCallback = commandProcessor
        client.connect()
    except Exception as e:
        print(str(e))
        sys.exit(1)

    if args.quickstart:
        print(
            "Welcome to IBM Watson IoT Platform Quickstart, view a vizualization of live data from this device at the URL below:"
        )
        print(
            "https://quickstart.internetofthings.ibmcloud.com/#/device/%s/sensor/" % (options["identity"]["deviceId"])
        )

    print("(Press Ctrl+C to disconnect)")

    # Take initial reading
    psutil.cpu_percent(percpu=False)
    before_ts = time.time()
    ioBefore = psutil.net_io_counters()
    diskBefore = psutil.disk_io_counters()
    psutil.disk_io_counters(perdisk=False, nowrap=True)
    while True:
        time.sleep(interval)
        after_ts = time.time()
        ioAfter = psutil.net_io_counters()
        diskAfter = psutil.disk_io_counters()
        # Calculate the time taken between IO checks
        duration = after_ts - before_ts

        data = {
            "name": args.name,
            "cpu": psutil.cpu_percent(percpu=False),
            "mem": psutil.virtual_memory().percent,
            "network": {
                "up": round((ioAfter.bytes_sent - ioBefore.bytes_sent) / (duration * 1024), 2),
                "down": round((ioAfter.bytes_recv - ioBefore.bytes_recv) / (duration * 1024), 2),
            },
            "disk": {
                "read": round((diskAfter.read_bytes - diskBefore.read_bytes) / (duration * 1024), 2),
                "write": round((diskAfter.write_bytes - diskBefore.write_bytes) / (duration * 1024), 2),
            },
        }
        if args.verbose:
            print("Datapoint = " + json.dumps(data))

        client.publishEvent("psutil", "json", data)
        # Update timestamp and data ready for next loop
        before_ts = after_ts
        ioBefore = ioAfter
        diskBefore = diskAfter
