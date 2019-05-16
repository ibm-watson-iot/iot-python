# *****************************************************************************
# Copyright (c) 2015, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import argparse
import json
import sys
import os
import logging

try:
    import wiotp.sdk.application
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../src"))
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import wiotp.sdk.application


def exportTypes(destination):
    global client, cliArgs
    print("Exporting Device Types ...")

    with open(destination, "a") as out_file:
        for deviceType in client.registry.devicetypes:
            export = {
                "id": deviceType.id,
                "classId": deviceType.classId,
                "description": deviceType.description,
                "deviceInfo": deviceType.deviceInfo,
                "metadata": deviceType.metadata,
            }
            out_file.write(json.dumps(export) + "\n")


def exportDevices(destination):
    global client, cliArgs
    print("Exporting Devices ...")

    with open(destination, "a") as out_file:
        for device in client.registry.devices:
            export = {
                "typeId": device.typeId,
                "deviceId": device.deviceId,
                "deviceInfo": device.deviceInfo,
                "metadata": device.metadata,
            }
            out_file.write(json.dumps(export) + "\n")


def importTypes(source):
    # There is no bulk type registration in the API (yet)
    with open(source, "r") as in_file:
        for line in in_file:
            data = json.loads(line)
            client.api.registry.devicetypes.create(data)


def importDevices(source):
    deviceArray = []
    with open(source, "r") as in_file:
        for line in in_file:
            data = json.loads(line)
            deviceArray.append(data)
    result = client.api.registry.devices.create(deviceArray)


if __name__ == "__main__":

    # Initialize the properties we need
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", required=True)
    parser.add_argument("-d", "--directory", required=True)

    args, unknown = parser.parse_known_args()

    client = None
    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)
    client.logger.setLevel(logging.DEBUG)
    # Note that we do not need to call connect to make API calls

    devicesFilePath = args.directory + "/devices.txt"
    typesFilePath = args.directory + "/types.txt"

    if args.mode == "import":
        importTypes(typesFilePath)
        importDevices(devicesFilePath)

    elif args.mode == "export":
        if os.path.isfile(typesFilePath):
            os.remove(typesFilePath)
        exportTypes(typesFilePath)

        if os.path.isfile(devicesFilePath):
            os.remove(devicesFilePath)
        exportDevices(devicesFilePath)
