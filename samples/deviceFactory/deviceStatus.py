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
        description="IBM Watson IoT Platform Device Status.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/deviceFactory"
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
        "-n",
        "--numberOfDevices",
        required=True,
        type=int,
        help="How many device configuration files should be produced by the factory. Max value is 1000",
    )

    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # Terminal colour mods
    red = "%c[31m" % chr(27)
    green = "%c[32m" % chr(27)
    off = "%c[0m" % chr(27)

    statuses = client.registry.connectionStatus.find(typeId=args.typeId)
    output = {}
    for status in statuses:
        # print(status)
        clientId = status["id"]
        deviceId = clientId.split(":")[3]
        if not deviceId.startswith(args.batchId):
            continue

        (batchId, batchNum) = clientId.split("-")
        if status["connectionStatus"] == "disconnected":
            output[batchNum] = "%s%s%s" % (red, batchNum, off)
        elif status["connectionStatus"] == "connected":
            output[batchNum] = "%s%s%s" % (green, batchNum, off)
        else:
            output[batchNum] = "%s" % (batchNum)

    print("=================================================")
    print("Device Connection State Report")
    print("")
    print("%s:%s-x" % (args.typeId, args.batchId))
    print("")
    print("%sconnected%s / %sdisconnected%s / unknown" % (green, off, red, off))
    print("=================================================")
    outStr = ""
    for i in range(1, args.numberOfDevices + 1):
        batchNum = "%04d" % (i)
        if batchNum in output:
            outStr += output[batchNum] + " "
        else:
            outStr += batchNum + " "

        if batchNum[3] == "0":
            outStr += "\n"

    print(outStr)
