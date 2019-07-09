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
import json
import wiotp.sdk.application


if __name__ == "__main__":
    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform Data Management Configuration for Reference Device Clients.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/dataManagement"
    )
    parser.add_argument("-d", "--diff", required=False, action="store_true", default=False, help="Run difference")
    parser.add_argument("-v", "--validate", required=False, action="store_true", default=False, help="Run validation")
    parser.add_argument("-a", "--activate", required=False, action="store_true", default=False, help="Run activation")
    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # =========================================================================
    # Validate and activate the configuration
    # =========================================================================
    if args.diff:
        print(client.state.draft.deviceTypes["iotpsutil"].differences())
        print(client.state.draft.deviceTypes["iotoshi"].differences())

    if args.validate:
        print(client.state.draft.deviceTypes["iotpsutil"].validate())
        print(client.state.draft.deviceTypes["iotoshi"].validate())

    if args.activate:
        print(client.state.draft.deviceTypes["iotpsutil"].activate())
        print(client.state.draft.deviceTypes["iotoshi"].activate())

    # =========================================================================
    # Retrieve the state of the device for the first ten devices of each type
    # =========================================================================
    for typeId in ["iotpsutil", "iotoshi"]:
        count = 0
        limit = 10
        for device in client.state.active.deviceTypes[typeId].devices:
            if count > limit:
                break
            print("%s:%s - %s" % (typeId, device.deviceId, device.states["sysutil"].state))
            count += 1

    # =========================================================================
    # Retrieve the state of the device for the first ten devices of each type
    # =========================================================================
    for typeId in ["iotpsutil"]:
        count = 0
        limit = 10
        for device in client.state.active.deviceTypes[typeId].devices:
            if count > limit:
                break
            print("%s:%s - %s" % (typeId, device.deviceId, device.states["networkio"].state))
            count += 1
