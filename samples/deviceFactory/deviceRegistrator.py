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


def saveConfigFile(destination, content):
    with open(destination, "w") as out_file:
        out_file.write(yaml.dump(content, default_flow_style=False))


if __name__ == "__main__":
    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform Device Registrator.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/deviceFactory",
        epilog="Use multiple bacthes to register more than 1000 devices",
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
    parser.add_argument(
        "-t",
        "--typeId",
        required=False,
        default="iotpsutil",
        help="Set the typeId for the device batch.  Defaults to iotpsutil",
    )
    parser.add_argument(
        "-c",
        "--classId",
        required=False,
        default="Device",
        help="Set the classId of the devices (Device, or Gateway). Defaults to Device",
    )
    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # Check whether the deviceType already exists

    if args.typeId not in client.registry.devicetypes:
        client.registry.devicetypes.create(
            {"id": args.typeId, "classId": args.classId, "description": "Created by deviceFactory"}
        )

    # Generate deviceId using args
    bulkCreateRequest = []
    for i in range(1, args.numberOfDevices + 1):
        deviceId = "%s-%04d" % (args.batchId, i)
        bulkCreateRequest.append({"typeId": args.typeId, "deviceId": deviceId})

    createResponse = client.registry.devices.create(bulkCreateRequest)

    configDirectory = "./localDeviceRegistry/%s/%s/%s" % (args.classId.lower(), args.typeId, args.batchId)

    if not os.path.exists(configDirectory):
        print("Creating local store: %s" % (configDirectory))
        os.makedirs(configDirectory)

    for device in createResponse:
        # print(device)
        if device.success:
            cfgFile = {
                "identity": {"orgId": options.orgId, "typeId": device.typeId, "deviceId": device.deviceId},
                "auth": {"token": device.authToken},
            }
            print("Device registration success: %s:%s" % (device.typeId, device.deviceId))
            configFileDestination = os.path.join(configDirectory, device.deviceId + ".yaml")
            saveConfigFile(configFileDestination, cfgFile)
        else:
            print("Device registration failed:  %s:%s" % (device.typeId, device.deviceId))
