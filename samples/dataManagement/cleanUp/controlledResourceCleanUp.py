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
    # Scripts for deleting specific resources:
    # ##########################################################################

    # Delete a physical interfaces, event type and schema - use resourceFetch.py to view ID
    physicalInterfaceToDelete = "INSERT PHYSICAL INTERFACE ID HERE"
    print("Deleting physical interface with ID: %s" % (physicalInterfaceToDelete))
    del appClient.state.draft.physicalInterfaces[physicalInterfaceToDelete]

    # Delete an event type - use resourceFetch.py to view IDs
    eventTypeToDelete = "INSERT EVENT TYPE ID HERE"
    print("Deleting event type with ID: %s" % (eventTypeToDelete))
    del appClient.state.draft.eventTypes[eventTypeToDelete]

    # Delete a logical interfaces - use resourceFetch.py to view ID
    logicalInterfaceToDelete = "INSERT LOGICAL INTERFACE ID HERE"
    print("Deleting logical interface with ID: %s" % (logicalInterfaceToDelete))
    del appClient.state.draft.logicalInterfaces[logicalInterfaceToDelete]

    # Delete a schema - use resourceFetch.py to view ID
    schemaToDelete = "INSERT LOGICAL INTERFACE ID HERE"
    print("Deleting schema with ID: %s" % (schemaToDelete))
    del appClient.state.draft.schemas[schemaToDelete]
