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
        description="IBM Watson IoT Platform Device Deployer.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/deviceFactory",
    )
    parser.add_argument(
        "-c", "--classId", required=False, default="Device", help="Set the classId of the devices (Device, or Gateway). Defaults to Device"
    )
    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # =========================================================================
    # Validate and activate the configuration
    # =========================================================================
    #print(client.state.draft.deviceTypes["iotpsutil"].validate())
    #print(client.state.draft.deviceTypes["iotoshi"].validate())

    #print(client.state.draft.deviceTypes["iotpsutil"].activate())
    #print(client.state.draft.deviceTypes["iotoshi"].activate())

    # =========================================================================
    # Retrieve the state of the device
    # =========================================================================

    count = 0
    limit = 10
    for device in client.state.active.deviceTypes["iotpsutil"].devices:
        if count > limit:
            break
        
        print("%s - %s" % (device.deviceId, device.states["sysutil"]))
        print("%s - %s" % (device.deviceId, device.states["networkio"]))
    
