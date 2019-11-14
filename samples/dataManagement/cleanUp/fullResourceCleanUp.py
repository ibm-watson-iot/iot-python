#!/usr/bin/env python

# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Initial Contribution:
#   Martin Smithson
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
    # Scripts for deleting ALL of each resource:
    # ##########################################################################

    # Delete all of the devices and device types in the Org.  Deleting the
    # device type will automatically deactivate any IM configuration
    # associated with, avoiding the need to explicitly deactivate.
    for dt in appClient.state.active.deviceTypes:
        for dev in dt.devices:
            print("Deleting devices %s for device type instance: %s" % (dev.deviceId, dt.id))
            del dt.devices[dev.deviceId]
        print("Deleting device type: %s" % (dt.id))
        del appClient.state.active.deviceTypes[dt.id]

    # Delete any physical interfaces, event type and schema
    for pi in appClient.state.draft.physicalInterfaces:
        print("Deleting physical interface: %s" % (pi.name))
        del appClient.state.draft.physicalInterfaces[pi.id]

    # Delete any event types
    for et in appClient.state.draft.eventTypes:
        print("Deleting event type: %s" % (et.name))
        del appClient.state.draft.eventTypes[et.id]

    # Delete logical interfaces
    for li in appClient.state.draft.logicalInterfaces:
        print("Deleting logical interface: %s" % (li.name))
        del appClient.state.draft.logicalInterfaces[li.id]

    # Delete schemas
    for s in appClient.state.draft.schemas:
        print("Deleting schema: %s" % (s.name))
        del appClient.state.draft.schemas[s.id]
