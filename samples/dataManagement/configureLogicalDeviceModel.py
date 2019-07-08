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


def manageLiSchema(schemaName, schemaFileName, description):
    schemaContent = {}
    with open(os.path.join("schemas", "interfaces", schemaFileName), "r") as schemaFile:
        schemaContent = json.load(schemaFile)

    existingSchema = None
    for schema in client.state.draft.schemas.find({"name": schemaName}):
        if schema.name == schemaName:
            existingSchema = schema

    jsonSchemaContent = json.dumps(schemaContent)
    if existingSchema is None:
        print("LI Schema %s needs to be created" % (schemaName))
        createdSchema = client.state.draft.schemas.create(schemaName, schemaFileName, jsonSchemaContent, description)
        print(createdSchema)
        print("")
        return createdSchema
    else:
        print("LI Schema %s already exists - updating it" % (schemaName))
        client.state.draft.schemas.updateContent(existingSchema.id, schemaFileName, jsonSchemaContent)
        updatedSchema = client.state.draft.schemas.update(
            existingSchema.id, {"id": createdSchema.id, "name": schemaName, "description": description}
        )
        print(updatedSchema)
        print("")
        return updatedSchema


def manageLi(liName, liAlias, description, schemaId):
    li = None
    existingLi = None
    for li in client.state.draft.logicalInterfaces.find({"name": liName}):
        if li.name == liName:
            existingLi = li

    if existingLi is None:
        print("LI %s needs to be created" % (liName))
        createdLI = client.state.draft.logicalInterfaces.create(
            {"name": liName, "alias": liAlias, "description": description, "schemaId": schemaId}
        )
        print(createdLI)
        print("")
        li = createdLI
    else:
        print("LI %s already exists" % (liName))
        existingLi = client.state.draft.logicalInterfaces.update(
            existingLi.id,
            {"id": existingLi.id, "name": liName, "alias": liAlias, "description": description, "schemaId": schemaId},
        )
        print(existingLi)
        print("")
        li = existingLi

    return li


def manageDeviceType(typeId, liList):
    deviceType = client.state.draft.deviceTypes[typeId]

    for li in liList:
        liAlreadyAdded = False
        for l in deviceType.logicalInterfaces:
            if li.name == l.name:
                liAlreadyAdded = True

        if not liAlreadyAdded:
            print("LI %s needs to be added to device type %s" % (li.name, typeId))
            deviceType.logicalInterfaces.create(li)
        else:
            print("LI %s already exists in device type %s" % (li.name, typeId))

    return deviceType


def addMappings(deviceType, mappings):
    for mapping in mappings:
        if mapping["logicalInterfaceId"] in deviceType.mappings:
            print("Mapping for LI %s already exists in device type %s" % (mapping["logicalInterfaceId"], deviceType.id))
        else:
            print(
                "Mapping for LI %s needs to be created in device type %s"
                % (mapping["logicalInterfaceId"], deviceType.id)
            )
            deviceType.mappings.create(mapping)


if __name__ == "__main__":
    # Initialize the properties we need
    parser = argparse.ArgumentParser(
        description="IBM Watson IoT Platform Data Management Configuration for Reference Device Clients.  For more information see https://github.com/ibm-watson-iot/iot-python/samples/dataManagement"
    )
    args, unknown = parser.parse_known_args()

    options = wiotp.sdk.application.parseEnvVars()
    client = wiotp.sdk.application.ApplicationClient(options)

    # =========================================================================
    # Create a logical interface schema
    # =========================================================================
    sysutilSchema = manageLiSchema(
        schemaName="sysutil-lischema",
        schemaFileName="sysutil-schema.json",
        description="Schema that defines the canonical interface for anything capable of reading System Utilization data",
    )
    networkioSchema = manageLiSchema(
        schemaName="networkio-lischema",
        schemaFileName="networkio-schema.json",
        description="Schema that defines the canonical interface for anything capable of reading Network I/O data",
    )

    # =========================================================================
    # Create the logical interface
    # =========================================================================
    sysutilLI = manageLi(
        liName="sysutil-li",
        liAlias="sysutil",
        description="System Utilization Logical Interface",
        schemaId=sysutilSchema.id,
    )
    networkioLI = manageLi(
        liName="networkio-li",
        liAlias="networkio",
        description="Network I/O Logical Interface",
        schemaId=networkioSchema.id,
    )

    # =========================================================================
    # Add the logical interface to a device type
    # =========================================================================
    psutilType = manageDeviceType("iotpsutil", [sysutilLI, networkioLI])
    oshiType = manageDeviceType("iotoshi", [sysutilLI])

    # =========================================================================
    # Define mappings for the logical interface
    # =========================================================================
    psutilMappings = [
        {
            "logicalInterfaceId": sysutilLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {"psutil": {"cpu": "$event.cpu", "memory": "$event.mem"}},
        },
        {
            "logicalInterfaceId": networkioLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {
                "psutil": {"network.inbound": "$event.network.down", "network.outbound": "$event.network.up"}
            },
        },
    ]

    oshiMappings = [
        {
            "logicalInterfaceId": sysutilLI.id,
            "notificationStrategy": "on-state-change",
            "propertyMappings": {"oshi": {"cpu": "$event.cpu", "memory": "$event.memory"}},
        }
    ]

    addMappings(deviceType=psutilType, mappings=psutilMappings)
    addMappings(deviceType=oshiType, mappings=oshiMappings)
