#!/usr/bin/env python

# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
from __future__ import print_function
import uuid
import wiotp.sdk.application

###############################################################################
# Main
###############################################################################
if __name__ == "__main__":

    options = wiotp.sdk.application.parseEnvVars()
    appClient = wiotp.sdk.application.ApplicationClient(options)

    # ##########################################################################
    # Scripts for fetching resources:
    # ##########################################################################

    # Fetch all of the devices and device types in the Org
    for dt in appClient.state.active.deviceTypes:
        print("Device type name: %s" % (dt.name))
        print("            - ID: %s" % (dt.id))
        print("                      Devices of type %s:" % (dt.name))
        for dev in dt.devices:
            print("                          - DeviceID: %s" % (dev.deviceId))

    # Fetch All physical interfaces, event type and schema
    for pi in appClient.state.draft.physicalInterfaces:
        print("Physical interface name: %s" % (pi.name))
        print("                   - ID: %s" % (pi.id))

    # Fetch all event types
    for et in appClient.state.draft.eventTypes:
        print("Event type name: %s" % (et.name))
        print("          - ID : %s" % (et.id))

    # Fetach all logical interfaces
    for li in appClient.state.draft.logicalInterfaces:
        print("Logical interface name: %s" % (li.name))
        print("                  - ID: %s" % (li.id))

    # Fetch all schemas
    for s in appClient.state.draft.schemas:
        print("Schema name: %s" % (s.name))
        print("       - ID: %s" % (s.id))
