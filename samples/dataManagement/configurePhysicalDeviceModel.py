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


def manageSchema(schemaName, schemaFileName, description):
    schemaContent = {}
    with open(os.path.join("schemas", "events", schemaFileName), "r") as schemaFile:
        schemaContent = json.load(schemaFile)

    existingSchema = None
    # Does the schema already exist?  find() is a fuzzy search and we want to check for the EXACT name!
    for a in client.state.draft.schemas.find({"name": schemaName}):
        if a.name == schemaName:
            existingSchema = a

    # TODO: Be Pythonic - We shouldn't serializse this to string, accept a python dict representing the schema
    schemaContentAsString = json.dumps(schemaContent)

    if existingSchema is None:
        print("Event schema %s needs to be created" % (schemaName))
        createdSchema = client.state.draft.schemas.create(
            schemaName, schemaFileName, schemaContentAsString, description
        )
        print(createdSchema)
        print("")
        return createdSchema
    else:
        print("Event Schema %s already exists - updating it" % (schemaName))
        client.state.draft.schemas.updateContent(existingSchema.id, schemaFileName, schemaContentAsString)
        updatedSchema = client.state.draft.schemas.update(
            existingSchema.id, {"id": createdSchema.id, "name": schemaName, "description": description}
        )
        print(updatedSchema)
        print("")
        return updatedSchema


def manageEventType(typeName, schemaId, description):
    existingType = None
    # Does the type already exist?  find() is a fuzzy search and we want to check for the EXACT name!
    for et in client.state.draft.eventTypes.find({"name": typeName}):
        if et.name == typeName:
            existingType = et

    if existingType is None:
        print("Event type %s needs to be created" % (typeName))

        createdType = client.state.draft.eventTypes.create(
            {"name": typeName, "description": description, "schemaId": schemaId}
        )
        print(createdType)
        print("")
        return createdType
    else:
        print("Event type %s already exists" % (typeName))
        print(existingType)
        print("")
        return existingType


def managePI(piName, description, eventId, eventTypeId):
    pi = None
    existingPi = None
    for pi in client.state.draft.physicalInterfaces.find({"name": piName}):
        if pi.name == piName:
            existingPi = pi

    if existingPi is None:
        print("PI %s needs to be created" % (piName))
        createdPI = client.state.draft.physicalInterfaces.create({"name": piName, "description": description})
        print(createdPI)
        print("")
        pi = createdPI
    else:
        print("PI %s already exists" % (piName))
        print(existingPi)
        print("")
        pi = existingPi

    # Check that there are no associated event mappings after deletion
    foundEventInPI = False
    for em in pi.events.find():
        if em.eventId == eventId:
            foundEventInPI = True

    if foundEventInPI:
        print("Event %s already configured on physical interface %s" % (eventId, pi.name))
        # TODO: Can I update the event?
    else:
        print("Event %s need to be added to physical interface %s" % (eventId, pi.name))
        pi.events.create({"eventId": eventId, "eventTypeId": eventTypeId})

    # The API has not implemented indivual GET endpoint for physicalinterface/{physicalInterfaceId}/events/{eventId} so the generic __contains__ does not work this this endpoint
    # there is no way to query whether a specific eventId is registered or not without iterating through the whole list :/
    #
    # Throws an error:
    #    Traceback (most recent call last):
    #  File "configureInterfaces.py", line 132, in <module>
    #    psutilPi = managePI(piName="psutil-pi", description="PSUTIL Physical Interface", eventId="psutil", eventTypeId=psutilEventType.id)
    #  File "configureInterfaces.py", line 89, in managePI
    #    if eventId in pi.events:
    #  File "c:\python37\lib\site-packages\wiotp\sdk\api\common.py", line 312, in __contains__
    #    raise ApiException(r)
    # wiotp.sdk.exceptions.ApiException: Unexpected return code from API: 403 (Forbidden) - https://hldtxx.internetofthings.ibmcloud.com/api/v0002/draft/physicalinterfaces/5d026bc010654c00208c823b/events/psutil
    #
    # if eventId in pi.events:
    #    print("Event %s already configured on physical interface %s" % (eventId, pi.name))
    #    # TODO: Can I update the event?
    # else:
    #    print("Event %s need to be added to physical interface %s" % (eventId, pi.name))
    #    pi.events.create({"eventId": eventId, "eventTypeId": eventTypeId})

    # This also does not work due to the lack of any direct accessor API for an event under the PI
    # print(pi.events[eventId])

    # This doesn't work .. only outputs:
    #     DraftEventMappings(None, {})
    #
    # print(pi.events)

    for em in pi.events.find():
        print("%s -> %s" % (em.eventId, em.eventTypeId))

    print("")
    return pi


def manageDeviceType(typeId, pi):
    deviceType = client.state.draft.deviceTypes[typeId]
    deviceType.physicalInterface = pi

    print("Set up PI for device type %s" & (deviceType.id))

    return deviceType


if __name__ == "__main__":
    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform Data Management Configuration for Reference Device Clients.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/dataManagement"
    )
    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # =========================================================================
    # Create Event Schemas
    # =========================================================================
    psutilSchema = manageSchema(
        schemaName="psutil-eschema", schemaFileName="psutil-schema.json", description="Schema for PSUTIL event data"
    )
    oshiSchema = manageSchema(
        schemaName="oshi-eschema", schemaFileName="oshi-schema.json", description="Schema for OSHI event data"
    )

    # =========================================================================
    # Create Event Type
    # =========================================================================
    psutilEventType = manageEventType(
        typeName="psutil-etype", description="PSUTIL Event Type", schemaId=psutilSchema.id
    )
    oshiEventType = manageEventType(typeName="oshi-etype", description="OSHI Event Type", schemaId=oshiSchema.id)

    # =========================================================================
    # Set up Physical Interfaces
    # =========================================================================
    psutilPi = managePI(
        piName="psutil-pi", description="PSUTIL Physical Interface", eventId="psutil", eventTypeId=psutilEventType.id
    )
    oshiPi = managePI(
        piName="oshi-pi", description="OSHI Physical Interface", eventId="oshi", eventTypeId=oshiEventType.id
    )

    # =========================================================================
    # Update the Device Type to add the PI
    # =========================================================================
    psutilType = manageDeviceType("iotpsutil", psutilPi)
    oshiType = manageDeviceType("iotoshi", oshiPi)

    print("")
    print("")
    print(
        "Congratulations.  You have now configured the physical device model for the IoT PSUTIL and IoT OSHI reference device samples"
    )
