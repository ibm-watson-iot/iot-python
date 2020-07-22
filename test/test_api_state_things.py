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
from test_state_utils import TestStateUtils


@testUtils.oneJobOnlyTest
class TestThing(testUtils.AbstractTest):

    # Physical Interface Stuff
    testEventSchemaName = "python-api-test-dt-pi_schema"
    testEventSchema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Sensor Event Schema",
        "properties": {
            "temperature": {
                "description": "temperature in degrees Celsius",
                "type": "number",
                "minimum": -237.15,
                "default": 0.0,
            },
            "humidity": {"description": "relative humidty (%)", "type": "number", "minimum": 0.0, "default": 0.0},
            "publishTimestamp": {"description": "publishTimestamp", "type": "number", "minimum": 0.0, "default": 0.0},
        },
        "required": ["temperature", "humidity", "publishTimestamp"],
    }
    testEventTypeName = "python-api-test-dt-pi_eventType"
    testEventId = "python-api-test-dt-pi_eventId"
    testPhysicalInterfaceName = "python-api-test-dt-pi"

    # Logical Interface Stuff
    testLiSchemaName = "python-api-test-dt-li-schema"
    testLISchema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Environment Sensor Schema",
        "properties": {
            "temperature": {
                "description": "temperature in degrees Celsius",
                "type": "number",
                "minimum": -237.15,
                "default": 0.0,
            },
            "humidity": {"description": "relative humidity (%)", "type": "number", "minimum": 0.0, "default": 0.0},
            "publishTimestamp": {"description": "publishTimestamp", "type": "number", "minimum": 0.0, "default": 0.0},
        },
        "required": ["temperature", "humidity", "publishTimestamp"],
    }
    testLogicalInterfaceName = "python-api-test-dt-li"

    testDeviceTypeName = "python-api-test-DeviceType"
    updatedDeviceTypeName = "python-api-test-DeviceType-updated"
    thingSchemaName = "thingSchema"
    thingTypeId = "thingTypeId"

    def createAndCheckTT(self, id, name, description, schemaId, metadata=None):

        createdTT = TestStateUtils.createTT(self.appClient, id, name, description, schemaId, metadata)
        TestStateUtils.checkTT(createdTT, id, name, description, schemaId, metadata)

        # now actively refetch the TT to check it is stored
        fetchedTT = self.appClient.state.draft.thingTypes.__getitem__(createdTT.id)
        assert createdTT == fetchedTT

        return createdTT

    def createAndCheckThing(self, thingTypeId, thingId, name, description, aggregatedObjects, metadata=None):
        createdThing = TestStateUtils.createThing(
            self.appClient, thingTypeId, thingId, name, description, aggregatedObjects, metadata
        )
        TestStateUtils.checkThing(createdThing, thingTypeId, thingId, name, description, aggregatedObjects, metadata)
        return createdThing

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):

        # delete any left over device types
        for tt in self.appClient.state.active.thingTypes:
            # print("Device type instance: %s" % (dt))
            if tt.id in (TestThing.thingTypeName):
                for thing in tt.things:
                    print("Deleting things %s for thing type instance: %s" % (thing.thingId, tt.id))
                    del tt.things[thing.thingId]
                print("Deleting old test thing type instance: %s" % (tt.id))
                self.appClient.state.active.thingTypes[tt.id].deactivate()

        for tt in self.appClient.state.draft.thingTypes:
            if tt.id in TestThing.thingTypeName:
                del self.appClient.state.draft.thingTypes[tt.id]

                # delete any left over device types
        for dt in self.appClient.state.active.deviceTypes:
            # print("Device type instance: %s" % (dt))
            if dt.id in (TestThing.testDeviceTypeName, TestThing.updatedDeviceTypeName):
                for dev in dt.devices:
                    print("Deleting devices %s for device type instance: %s" % (dev.deviceId, dt.id))
                    del dt.devices[dev.deviceId]
                print("Deleting old test device type instance: %s" % (dt.id))
                del self.appClient.state.active.deviceTypes[dt.id]

        # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestThing.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestThing.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestThing.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name in (TestThing.testEventSchemaName, TestThing.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
                del self.appClient.state.draft.schemas[s.id]

    def checkDT(
        self, DeviceType, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):
        assert DeviceType.id == name
        assert DeviceType.description == description

        # TBD more needed here

    def doesSchemaNameExist(self, name):
        for a in self.appClient.state.draft.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesEventTypeNameExist(self, name):
        for et in self.appClient.state.draft.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def doesPINameExist(self, name):
        for pi in self.appClient.state.draft.physicalInterfaces.find({"name": name}):
            if pi.name == name:
                return True
        return False

    def doesLINameExist(self, name):
        for li in self.appClient.state.draft.logicalInterfaces.find({"name": name}):
            if li.name == name:
                return True
        return False

    def doesDTNameExist(self, name):
        for dt in self.appClient.state.active.deviceTypes.find({"id": name}):
            if dt.id == name:
                return True
        return False

    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        return createdSchema

    def createEventType(self, name, description, schemaId):
        createdEventType = self.appClient.state.draft.eventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdEventType

    def createPI(self, name, description):
        createdPI = self.appClient.state.draft.physicalInterfaces.create({"name": name, "description": description})
        return createdPI

    def comparePIs(self, PI1, PI2):
        assert PI1.id == PI2.id
        assert PI1.name == PI2.name
        assert PI1.description == PI2.description
        assert PI1.version == PI2.version
        assert PI1.events == PI2.events

    def createLI(self, name, description, schemaId):
        createdLI = self.appClient.state.draft.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdLI

    def createAndCheckDT(
        self, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):
        payload = {
            "id": name,
            "description": description,
            "deviceInfo": deviceInfo,
            "metadata": metadata,
            "classId": classId,
            "edgeConfiguration": edgeConfiguration,
        }

        # createdDT = self.appClient.registry.devicetypes.create(payload)

        createdDT = self.appClient.state.active.deviceTypes.create(payload)

        self.checkDT(createdDT, name, description, deviceInfo, metadata, edgeConfiguration, classId)
        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.state.active.deviceTypes.__getitem__(createdDT.id)
        assert createdDT == fetchedDT

        return createdDT

    def testCreatePreReqs(self):
        # LI
        test_schema_name = TestThing.testLiSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestThing.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        TestThing.createdLISchema = self.createSchema(
            test_schema_name, "liSchema.json", TestThing.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestThing.createdLI = self.createLI(
            testLIName, "Test Logical Interface description", TestThing.createdLISchema.id
        )

        # PI
        test_schema_name = TestThing.testEventSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestThing.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name) == False
        testPIName = TestThing.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a schema
        TestThing.createdEventSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestThing.testEventSchema, "Test schema description"
        )

        # Create an eventType
        TestThing.createdEventType = self.createEventType(
            test_eventType_name, "Test event type description", TestThing.createdEventSchema.id
        )

        # Create a Physical Interface
        TestThing.createdPI = self.createPI(testPIName, "Test Physical Interface description")

        # Associate event with PI
        TestThing.createdPI.events.create(
            {"eventId": TestThing.testEventId, "eventTypeId": TestThing.createdEventType.id}
        )

        test_dt_name = TestThing.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name) == False

        # Create a Device Type
        TestThing.createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        # Associate PI
        TestThing.createdDT.physicalInterface = TestThing.createdPI

        # Associate the LI
        TestThing.createdDT.logicalInterfaces.create(TestThing.createdLI)

        TestThing.createdDT.mappings.create(
            {
                "logicalInterfaceId": TestThing.createdLI.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {
                    TestThing.testEventId: {
                        "temperature": "$event.temperature",
                        "humidity": "$event.humidity",
                        "publishTimestamp": "$event.publishTimestamp",
                    }
                },
            }
        )
        # Validate and activate deviceType
        TestThing.createdDT.validate()
        TestThing.createdDT.activate()

        # Create Device
        createdDeviceId = str(uuid.uuid4())
        deviceInfo = {"serialNumber": "123", "descriptiveLocation": "Floor 3, Room 2"}
        metadata = {"customField1": "customValue1", "customField2": "customValue2"}

        TestThing.createdDT = self.appClient.state.draft.deviceTypes[TestThing.createdDT.id]
        TestThing.createdDevice = TestThing.createdDT.devices.create(
            {
                "deviceId": createdDeviceId,
                "authToken": "NotVerySecretPassw0rd",
                "deviceInfo": deviceInfo,
                "metadata": metadata,
            }
        )

        # read it back to check it's there
        for retrievedDevice in TestThing.createdDT.devices:
            assert retrievedDevice.typeId == TestThing.createdDT.id
            assert retrievedDevice.deviceId == createdDeviceId
            assert retrievedDevice.metadata == metadata
            assert retrievedDevice.registration != None
            assert retrievedDevice.status != None
            assert retrievedDevice.deviceInfo == deviceInfo

        # Create thingType
        # Make sure thingType does not already exist
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThing.thingTypeId) == False

        testThingTypeSchema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "title": "TestThingSchema",
            "description": "defines the properties of a schema type",
            "properties": {
                "Temperature": {"type": "object", "description": "info", "$logicalInterfaceRef": TestThing.createdLI.id}
            },
            "required": ["Temperature"],
        }

        # create thing type schema
        thingSchema = TestStateUtils.createSchema(
            self.appClient,
            TestThing.thingSchemaName,
            "liThingSchema.json",
            testThingTypeSchema,
            "Test schema description",
        )

        # create and check thing type
        TestThing.createdTT = self.createAndCheckTT(
            TestThing.thingTypeId, "temperature type", "Test Device Type description", thingSchema.id
        )

        # create logical interface for thingType
        LItest = TestThing.createdTT.logicalInterfaces.create({"id": TestThing.createdLI.id})

        # create mapping for thing type
        TestThing.createdTT.mappings.create(
            {
                "logicalInterfaceId": LItest.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {"Temperature": {"temperature": "$event.temperature"}},
            }
        )

        # validate thingType
        self.appClient.state.draft.thingTypes[TestThing.createdTT.id].validate()

        # Check that draft thing type exists and active does not
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThing.thingTypeId) == True
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThing.thingTypeId) == False

        # Activate thingType
        self.appClient.state.draft.thingTypes[TestThing.createdTT.id].activate()
        configDifferences2 = TestThing.createdTT.differences()
        assert configDifferences2["contentState"] == "SAME"

        # Check that both active and draft thingType exist
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThing.thingTypeId) == True
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThing.thingTypeId) == True

    def testRegisterThing(self):
        thingId = "thingId"
        thingName = "TemperatureThingName"
        thingDescription = "Temp thing description"
        # Aggregated devices for thing
        aggregated = {
            "Temperature": {"type": "device", "typeId": TestThing.createdDT.id, "id": TestThing.createdDevice.deviceId}
        }

        # Create the thing
        createdThing = self.createAndCheckThing(
            TestThing.createdTT.id, thingId, thingName, thingDescription, aggregated, metadata=None
        )

        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId)

        for retrievedThing in TestThing.createdTT.things:
            assert retrievedThing.thingTypeId == TestThing.createdTT.id
            assert retrievedThing.thingId == thingId
            assert retrievedThing.name == thingName
            assert retrievedThing.metadata == None
            assert retrievedThing.description == thingDescription
            assert retrievedThing.aggregatedObjects == aggregated

        del self.appClient.state.active.thingTypes[TestThing.createdTT.id].things[createdThing.thingId]
        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId) == False

    def testRegisterThingMetadata(self):
        thingId = "thingId"
        thingName = "TemperatureThingName"
        thingDescription = "Temp thing description"
        # Aggregated devices for thing
        aggregated = {
            "Temperature": {"type": "device", "typeId": TestThing.createdDT.id, "id": TestThing.createdDevice.deviceId}
        }

        # Create the thing
        createdThing = self.createAndCheckThing(
            TestThing.createdTT.id, thingId, thingName, thingDescription, aggregated, metadata={"test": "test"}
        )

        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId)

        for retrievedThing in TestThing.createdTT.things:
            assert retrievedThing.thingTypeId == TestThing.createdTT.id
            assert retrievedThing.thingId == thingId
            assert retrievedThing.name == thingName
            assert retrievedThing.metadata == {"test": "test"}
            assert retrievedThing.description == thingDescription
            assert retrievedThing.aggregatedObjects == aggregated

        del self.appClient.state.active.thingTypes[TestThing.createdTT.id].things[createdThing.thingId]
        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId) == False

    def testRegisterThingDescriptionNone(self):
        thingId = "thingId"
        thingName = "TemperatureThingName"
        thingDescription = None
        # Aggregated devices for thing
        aggregated = {
            "Temperature": {"type": "device", "typeId": TestThing.createdDT.id, "id": TestThing.createdDevice.deviceId}
        }

        # Create the thing
        createdThing = self.createAndCheckThing(
            TestThing.createdTT.id, thingId, thingName, thingDescription, aggregated, metadata={"test": "test"}
        )

        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId)

        for retrievedThing in TestThing.createdTT.things:
            assert retrievedThing.thingTypeId == TestThing.createdTT.id
            assert retrievedThing.thingId == thingId
            assert retrievedThing.name == thingName
            assert retrievedThing.metadata == {"test": "test"}
            assert retrievedThing.description == None
            assert retrievedThing.aggregatedObjects == aggregated

        del self.appClient.state.active.thingTypes[TestThing.createdTT.id].things[createdThing.thingId]
        assert TestStateUtils.doesThingIdExist(self.appClient, TestThing.thingTypeId, createdThing.thingId) == False

    def testDeletePreReqs(self):
        # delete any left over thing types
        for tt in self.appClient.state.active.thingTypes:
            if tt.id in (TestThing.thingTypeId):
                for thing in tt.things:
                    print("Deleting things %s for thing type instance: %s" % (thing.thingId, tt.id))
                    del tt.things[thing.thingId]
                print("Deleting old test thing type instance: %s" % (tt.id))
                self.appClient.state.active.thingTypes[tt.id].deactivate()

        for tt in self.appClient.state.draft.thingTypes:
            if tt.id in TestThing.thingTypeId:
                del self.appClient.state.draft.thingTypes[tt.id]

        del self.appClient.state.active.deviceTypes[TestThing.createdDT.id].devices[TestThing.createdDevice.deviceId]

        del self.appClient.state.active.deviceTypes[TestThing.createdDT.id]
        assert self.doesDTNameExist(TestThing.testDeviceTypeName) == False

        del self.appClient.state.draft.physicalInterfaces[TestThing.createdPI.id]
        assert self.doesPINameExist(TestThing.testPhysicalInterfaceName) == False

        del self.appClient.state.draft.eventTypes[TestThing.createdEventType.id]
        assert self.doesEventTypeNameExist(TestThing.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestThing.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestThing.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestThing.createdLI.id]
        assert self.doesLINameExist(TestThing.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestThing.createdLISchema.id]
        assert self.doesSchemaNameExist(TestThing.testLiSchemaName) == False


#
