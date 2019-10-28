# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
#
import uuid
from datetime import datetime
import testUtils
import time
import pytest
from wiotp.sdk.exceptions import ApiException
import string
import json
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation
import sys


class TestStateUtils:
    def deleteThingTypes(appClient, TTNameList):
        # delete any left over device types
        for tt in appClient.state.active.thingTypes:
            # print("Device type instance: %s" % (dt))
            if tt.id in TTNameList:
                for thing in tt.things:
                    print("Deleting things %s for active thing type instance: %s" % (thing.thingId, tt.id))
                    del tt.devices[thing.thingId]
                print("Deactivating old test thing type instance: %s" % (tt.id))
                appClient.state.active.thingTypes[tt.id].deactivate()
        for tt in appClient.state.draft.thingTypes:
            # print("Device type instance: %s" % (dt))
            if tt.id in TTNameList:
                for thing in tt.things:
                    print("Deleting things %s for draft thing type instance: %s" % (thing.thingId, tt.id))
                    del tt.devices[thing.thingId]
                print("Deleting old test thing type instance: %s" % (tt.id))
                del appClient.state.draft.thingTypes[tt.id]


class TestStateUtils:
    def deleteDeviceTypes(appClient, DTNameList):
        # delete any left over device types
        for dt in appClient.state.active.deviceTypes:
            # print("Device type instance: %s" % (dt))
            if dt.id in DTNameList:
                for dev in dt.devices:
                    print("Deleting devices %s for device type instance: %s" % (dev.deviceId, dt.id))
                    del dt.devices[dev.deviceId]
                print("Deleting old test device type instance: %s" % (dt.id))
                del appClient.state.active.deviceTypes[dt.id]

    def deleteDraftLIs(appClient, LINameList):
        # delete any left over logical interfaces
        for li in appClient.state.draft.logicalInterfaces:
            if li.name in LINameList:
                print("Deleting old test LI: %s" % (li))
                del appClient.state.draft.logicalInterfaces[li.id]

    def deleteDraftPIs(appClient, NameList):
        # delete any left over physical interfaces, event type and schema
        for pi in appClient.state.draft.physicalInterfaces:
            if pi.name in NameList:
                print("Deleting old test PI: %s" % (pi))
                del appClient.state.draft.physicalInterfaces[pi.id]

    def deleteDraftEventTypes(appClient, NameList):
        for et in appClient.state.draft.eventTypes:
            if et.name in NameList:
                print("Deleting old test event type: %s" % (et))
                try:
                    del appClient.state.draft.eventTypes[et.id]
                except:
                    print(
                        "Deleting old test event types could not be completed as the object is referenced by another resource"
                    )

    def deleteDraftSchemas(appClient, NameList):
        for s in appClient.state.draft.schemas:
            if s.name in NameList:
                print("Deleting old test schema instance: %s" % (s))
                try:
                    del appClient.state.draft.schemas[s.id]
                except:
                    print(
                        "Deleting old test schema instances could not be completed as the object is referenced by another resource"
                    )

    def isstring(s):
        # if we use Python 3
        if sys.version_info[0] >= 3:
            basestring = str
        return isinstance(s, basestring)

    def checkDT(
        deviceType, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):
        # print("Checking Device Type: %s" % (deviceType))
        assert deviceType.id == name
        assert deviceType.description == description
        assert deviceType.deviceInfo == deviceInfo
        assert deviceType.metadata == metadata
        assert deviceType.edgeConfiguration == edgeConfiguration
        assert deviceType.classId == classId

    def checkTT(thingType, id, name, description, schemaId, metadata=None):
        assert thingType.id == id
        assert thingType.name == name
        assert thingType.description == description
        assert thingType.schemaId == schemaId
        assert thingType.metadata == metadata

    def checkThing(thing, thingTypeId, thingId, name, description, aggregatedObjects, metadata=None):
        assert thing.thingTypeId == thingTypeId
        assert thing.thingId == thingId
        assert thing.description == description
        assert thing.name == name
        assert thing.metadata == metadata
        assert thing.aggregatedObjects == aggregatedObjects

    def checkMapping(mapping, logicalInterfaceId, notificationStrategy, propertyMappings, version="draft"):
        # print("Checking Device Type: %s" % (deviceType))
        assert mapping.logicalInterfaceId == logicalInterfaceId
        assert mapping.notificationStrategy == notificationStrategy
        assert mapping.propertyMappings == propertyMappings
        assert mapping.logicalInterfaceId == logicalInterfaceId
        assert mapping.version == version
        assert isinstance(mapping.created, datetime)
        assert TestStateUtils.isstring(mapping.createdBy)
        assert isinstance(mapping.updated, datetime)
        assert TestStateUtils.isstring(mapping.updatedBy)
        # TBD more needed here

    def doesSchemaNameExist(appClient, name):
        for a in appClient.state.draft.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesEventTypeNameExist(appClient, name):
        for et in appClient.state.draft.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def doesPINameExist(appClient, name):
        for pi in appClient.state.draft.physicalInterfaces.find({"name": name}):
            if pi.name == name:
                return True
        return False

    def doesLINameExist(appClient, name):
        for li in appClient.state.draft.logicalInterfaces.find({"name": name}):
            if li.name == name:
                return True
        return False

    def doesDTNameExist(appClient, name):
        for dt in appClient.state.active.deviceTypes.find({"id": name}):
            if dt.id == name:
                return True
        return False

    def doesTTNameExist(appClient, name):
        for tt in appClient.state.draft.thingTypes.find({"id": name}):
            if tt.id == name:
                return True
        return False

    def doesThingIdExist(appClient, thingTypeId, name):
        for thing in appClient.state.active.thingTypes[thingTypeId].things:
            if thing.thingId == name:
                return True
        return False

    def doesActiveSchemaNameExist(appClient, name):
        for a in appClient.state.active.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesActiveEventTypeNameExist(appClient, name):
        for et in appClient.state.active.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def doesActivePINameExist(appClient, name):
        for pi in appClient.state.active.physicalInterfaces.find({"name": name}):
            if pi.name == name:
                return True
        return False

    def doesActiveLINameExist(appClient, name):
        for li in appClient.state.active.logicalInterfaces.find({"name": name}):
            if li.name == name:
                return True
        return False

    def doesActiveDTNameExist(appClient, name):
        for dt in appClient.state.active.deviceTypes.find({"id": name}):
            if dt.id == name:
                return True
        return False

    def doesActiveTTNameExist(appClient, name):
        for tt in appClient.state.active.thingTypes.find({"id": name}):
            if tt.id == name:
                return True
        return False

    def createSchema(appClient, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        return createdSchema

    def createEventType(appClient, name, description, schemaId):
        createdEventType = appClient.state.draft.eventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdEventType

    def createPI(appClient, name, description):
        createdPI = appClient.state.draft.physicalInterfaces.create({"name": name, "description": description})
        return createdPI

    def comparePIs(PI1, PI2):
        assert PI1.id == PI2.id
        assert PI1.name == PI2.name
        assert PI1.description == PI2.description
        assert PI1.version == PI2.version
        assert PI1.events == PI2.events

    def createLI(appClient, name, description, schemaId):
        createdLI = appClient.state.draft.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdLI

    def createDT(
        appClient, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):
        payload = {
            "id": name,
            "description": description,
            "deviceInfo": deviceInfo,
            "metadata": metadata,
            "classId": classId,
            "edgeConfiguration": edgeConfiguration,
        }
        createdDT = appClient.state.active.deviceTypes.create(payload)
        return createdDT

    def createTT(appClient, id, name, description, schemaId, metadata=None):
        payload = {"id": id, "name": name, "description": description, "schemaId": schemaId, "metadata": metadata}
        createdDT = appClient.state.draft.thingTypes.create(payload)
        return createdDT

    def createThing(appClient, thingTypeId, thingId, name, description, aggregatedObjects, metadata=None):
        payload = {
            "thingTypeId": thingTypeId,
            "thingId": thingId,
            "name": name,
            "description": description,
            "aggregatedObjects": aggregatedObjects,
            "metadata": metadata,
        }
        createdThing = appClient.state.active.thingTypes[thingTypeId].things.create(payload)
        return createdThing

    def createMapping(appClient, deviceType, logicalInterfaceId, notificationStrategy, propertyMappings):
        payload = {
            "logicalInterfaceId": logicalInterfaceId,
            "notificationStrategy": notificationStrategy,
            "propertyMappings": propertyMappings,
        }
        createdMapping = deviceType.mappings.create(payload)
        return createdMapping
