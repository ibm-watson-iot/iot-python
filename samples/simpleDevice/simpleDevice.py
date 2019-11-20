# *****************************************************************************
# Copyright (c) 2017, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import time
import sys
import uuid
import argparse

try:
    import wiotp.sdk
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import wiotp.sdk"
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../src"))
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import wiotp.sdk


def commandProcessor(cmd):
    print("Command received: %s" % cmd.data)


authMethod = None

# Initialize the properties we need
parser = argparse.ArgumentParser()

# Primary Options
parser.add_argument("-o", "--organization", required=False, default="quickstart")
parser.add_argument("-T", "--typeId", required=False, default="simpleDev")
parser.add_argument("-I", "--deviceId", required=False, default=str(uuid.uuid4()))
parser.add_argument("-t", "--token", required=False, default=None, help="authentication token")
parser.add_argument("-c", "--cfg", required=False, default=None, help="configuration file")
parser.add_argument("-E", "--event", required=False, default="event", help="type of event to send")
parser.add_argument(
    "-N", "--nummsgs", required=False, type=int, default=1, help="send this many messages before disconnecting"
)
parser.add_argument("-D", "--delay", required=False, type=float, default=1, help="number of seconds between msgs")
args, unknown = parser.parse_known_args()

if args.token:
    authMethod = "token"

# Initialize the device client.

try:
    if args.cfg is not None:
        deviceOptions = wiotp.sdk.device.parseConfigFile(args.cfg)
    elif args.organization == "quickstart":
        deviceOptions = {"identity": {"orgId": args.organization, "typeId": args.typeId, "deviceId": args.deviceId}}
    else:
        deviceOptions = {
            "identity": {"orgId": args.organization, "typeId": args.typeId, "deviceId": args.deviceId},
            "auth": {"token": args.token},
        }
    deviceCli = wiotp.sdk.device.DeviceClient(deviceOptions)
    deviceCli.commandCallback = commandProcessor
except Exception as e:
    print("Caught exception connecting device: %s" % str(e))
    sys.exit()

# Connect and send datapoint(s) into the cloud
deviceCli.connect()
for x in range(0, args.nummsgs):
    data = {"simpledev": "ok", "x": x}

    def myOnPublishCallback():
        print("Confirmed event %s received by WIoTP\n" % x)

    success = deviceCli.publishEvent(args.event, "json", data, qos=0, onPublish=myOnPublishCallback)
    if not success:
        print("Not connected to WIoTP")

    time.sleep(args.delay)


# Disconnect the device and application from the cloud
deviceCli.disconnect()
