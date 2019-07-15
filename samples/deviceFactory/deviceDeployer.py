#!/usr/bin/env python

# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import argparse
import sys
import os
import yaml

import wiotp.sdk.application


def loadConfigFile(source):
    data = {}
    with open(source, "r") as sourceFile:
        data = yaml.full_load(sourceFile)
    return data


if __name__ == "__main__":
    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform Device Deployer.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/deviceFactory"
    )
    parser.add_argument(
        "-c",
        "--classId",
        required=False,
        default="Device",
        help="Set the classId of the devices (Device, or Gateway). Defaults to Device",
    )
    parser.add_argument(
        "-t",
        "--typeId",
        required=False,
        default="iotpsutil",
        help="Set the typeId for the device batch.  Defaults to iotpsutil",
    )
    parser.add_argument(
        "-b",
        "--batchId",
        required=True,
        help="DeviceIDs will be prefixed by the batch number, e.g. batchID-0001, batchID-0002",
    )
    parser.add_argument(
        "--numberOfDevices",
        required=True,
        type=int,
        help="How many devices in the batch should be deployed. Max value is 1000",
    )

    parser.add_argument(
        "--helmCmd",
        required=False,
        default="helm",
        help="If helm command is not on the path, use this to set the helm command explicitly",
    )
    parser.add_argument("--helmChart", required=True, help="Set the helm chart to use")
    args, unknown = parser.parse_known_args()

    # Search through the directory
    configDirectory = "./localDeviceRegistry/%s/%s/%s" % (args.classId.lower(), args.typeId, args.batchId)
    scriptDirectory = "./bin/"
    if not os.path.exists(scriptDirectory):
        print("Creating bin directory: %s" % (scriptDirectory))
        os.makedirs(scriptDirectory)

    count = 0
    commands = []
    stopCommands = []
    # For each device create the helm upgrade --install command
    for cfgFile in os.listdir(configDirectory):
        if count >= args.numberOfDevices:
            break
        if cfgFile.endswith(".yaml"):
            valuesFile = os.path.join(configDirectory, cfgFile)
            # get the devicecfg
            cfg = loadConfigFile(valuesFile)
            releaseName = "%s-%s" % (cfg["identity"]["typeId"], cfg["identity"]["deviceId"])
            # Add "--timeout 300 --wait" if want to make the deploy wait to verify each release (will slow things down a lot)!
            command = "%s upgrade %s %s -i --values %s" % (args.helmCmd, releaseName, args.helmChart, valuesFile)
            commands.append(command)

            stopCommand = "%s delete --purge %s" % (args.helmCmd, releaseName)
            stopCommands.append(stopCommand)
        count += 1

    # Write the script file
    scriptFilePath = os.path.join(
        scriptDirectory, "deploy-%s-%s-%s.bat" % (args.classId.lower(), args.typeId, args.batchId)
    )
    with open(scriptFilePath, "w") as scriptFile:
        for command in commands:
            scriptFile.write(command + "\n")

    scriptFilePath2 = os.path.join(
        scriptDirectory, "recall-%s-%s-%s.bat" % (args.classId.lower(), args.typeId, args.batchId)
    )
    with open(scriptFilePath2, "w") as scriptFile2:
        for command in stopCommands:
            scriptFile2.write(command + "\n")
