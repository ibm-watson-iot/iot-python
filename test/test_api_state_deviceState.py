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
from pip._vendor.chardet import codingstatemachine


@testUtils.oneJobOnlyTest
class TestDeviceState(testUtils.AbstractTest):

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

    defaultDeviceState = {"temperature": 0.0, "humidity": 0.0, "publishTimestamp": 0.0}
    testLogicalInterfaceName = "python-api-test-dt-li"

    testDeviceTypeName = "python-api-test-DeviceType"
    updatedDeviceTypeName = "python-api-test-DeviceType-updated"

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        # delete any left over device types
        for dt in self.appClient.state.active.deviceTypes:
            # print("Device type instance: %s" % (dt))
            if dt.id in (TestDeviceState.testDeviceTypeName, TestDeviceState.updatedDeviceTypeName):
                for dev in dt.devices:
                    # print("Deleting devices %s for device type instance: %s" % (dev.deviceId, dt.id))
                    del dt.devices[dev.deviceId]
                # print("Deleting old test device type instance: %s" % (dt.id))
                del self.appClient.state.active.deviceTypes[dt.id]

        # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestDeviceState.testLogicalInterfaceName:
                # print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestDeviceState.testPhysicalInterfaceName:
                # print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestDeviceState.testEventTypeName:
                # print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name in (TestDeviceState.testEventSchemaName, TestDeviceState.testLiSchemaName):
                # print("Deleting old test schema instance: %s" % (s))
                del self.appClient.state.draft.schemas[s.id]

        # TBD this was all debugv stuff
        # for DT in self.appClient.state.active.deviceTypes:
        #    print ("Active Device Type: %s" % DT)

        # for li in self.appClient.state.draft.logicalInterfaces:
        #    #print ("Logical Interface: %s" % li.id)
        #    for DT in self.appClient.state.draft.deviceTypes.find({"logicalInterfaceId":li.id}):
        #        print ("LI: %s, Draft Device Type: %s" % (li.id, DT))
        #        newPI = DT.physicalInterface
        #        print ("DT physicalInterface: %s" % DT.physicalInterface)
        #        for subLi in DT.logicalInterfaces:
        #            print ("LI: %s" % (subLi.id))
        #        for map in DT.mappings:
        #            print ("Mapping: %s" % (map))
        # return

    def checkDT(
        self, DeviceType, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):
        assert DeviceType.id == name
        assert DeviceType.description == description

    def checkState(self, state, expectedState):
        assert state.state == expectedState

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

    def doesActiveSchemaNameExist(self, name):
        for a in self.appClient.state.active.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesActiveEventTypeNameExist(self, name):
        for et in self.appClient.state.active.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def doesActivePINameExist(self, name):
        for pi in self.appClient.state.active.physicalInterfaces.find({"name": name}):
            if pi.name == name:
                return True
        return False

    def doesActiveLINameExist(self, name):
        for li in self.appClient.state.active.logicalInterfaces.find({"name": name}):
            if li.name == name:
                return True
        return False

    def doesActiveDTNameExist(self, name):
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

        createdDT = self.appClient.state.active.deviceTypes.create(payload)
        self.checkDT(createdDT, name, description, deviceInfo, metadata, edgeConfiguration, classId)

        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.state.active.deviceTypes.__getitem__(createdDT.id)
        assert createdDT == fetchedDT

        return createdDT

    def testCreatePreReqs(self):
        # LI
        test_schema_name = TestDeviceState.testLiSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestDeviceState.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        TestDeviceState.createdLISchema = self.createSchema(
            test_schema_name, "liSchema.json", TestDeviceState.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestDeviceState.createdLI = self.createLI(
            testLIName, "Test Logical Interface description", TestDeviceState.createdLISchema.id
        )

        # PI
        test_schema_name = TestDeviceState.testEventSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestDeviceState.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name) == False
        testPIName = TestDeviceState.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a schema
        TestDeviceState.createdEventSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestDeviceState.testEventSchema, "Test schema description"
        )

        # Create an eventType
        TestDeviceState.createdEventType = self.createEventType(
            test_eventType_name, "Test event type description", TestDeviceState.createdEventSchema.id
        )

        # Create a Physical Interface
        TestDeviceState.createdPI = self.createPI(testPIName, "Test Physical Interface description")

        # Associate event with PI
        TestDeviceState.createdPI.events.create(
            {"eventId": TestDeviceState.testEventId, "eventTypeId": TestDeviceState.createdEventType.id}
        )

        test_dt_name = TestDeviceState.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name) == False

        # Create a Device Type
        TestDeviceState.createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        # Associate PI
        TestDeviceState.createdDT.physicalInterface = TestDeviceState.createdPI

        # Associate the LI
        TestDeviceState.createdDT.logicalInterfaces.create(TestDeviceState.createdLI)

        # Mappings
        TestDeviceState.createdDT.mappings.create(
            {
                "logicalInterfaceId": TestDeviceState.createdLI.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {
                    TestDeviceState.testEventId: {
                        "temperature": "$event.temperature",
                        "humidity": "$event.humidity",
                        "publishTimestamp": "$event.publishTimestamp",
                    }
                },
            }
        )

        # Validate and Activate the LI
        TestDeviceState.createdDT.validate()

        TestDeviceState.createdDT.activate()

        # register a device
        TestDeviceState.createdDevice = TestDeviceState.createdDT.devices.create(
            {
                "deviceId": str(uuid.uuid4()),
                "authToken": "NotVerySecretPassw0rd",
                "deviceInfo": DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2"),
            }
        )

    def testDefaultDeviceState(self):
        # print("test Device state")
        for li in TestDeviceState.createdDT.logicalInterfaces:
            # print("LI: %s" % (li.id))
            if li.name == TestDeviceState.testLogicalInterfaceName:
                deviceState = TestDeviceState.createdDevice.states[li.id]
                # print("Device state: %s" % (deviceState))
                self.checkState(deviceState, TestDeviceState.defaultDeviceState)

    def testResetDeviceState(self):
        # print("test Device state")
        for li in TestDeviceState.createdDT.logicalInterfaces:
            # print("LI: %s" % (li.id))
            if li.name == TestDeviceState.testLogicalInterfaceName:
                TestDeviceState.createdDevice.states[li.id].reset()
                deviceState = TestDeviceState.createdDevice.states[li.id]
                # print("Device state: %s" % (deviceState))
                self.checkState(deviceState, TestDeviceState.defaultDeviceState)

    def testDeviceStateErrors(self):
        # Check state for a non existent LI
        try:
            dummyLiId = "DummyLI"
            deviceState = TestDeviceState.createdDevice.states[dummyLiId]
            print("There should be no device state for LI %s. We have: %s" % (dummyLiId, deviceState))
            assert False == True  # fail
        except KeyError as e:
            assert True  # This is what we expect

        # Try to iterate over state for all LIs
        try:
            for deviceState in TestDeviceState.createdDevice.states:
                print("We shouldn't be able to iterate over device state for LIs. We have: %s" % deviceState)
                assert False == True  # fail
        except:
            assert True  # This is what we expect

        # Try to 'find' state
        try:
            for deviceState in TestDeviceState.createdDevice.states.find({"name": ""}):
                print("We shouldn't be able to iterate over device state for LIs. We have: %s" % deviceState)
                assert False == True  # fail
        except:
            assert True  # This is what we expect

    def testDeletePreReqs(self):

        del self.appClient.state.active.deviceTypes[TestDeviceState.createdDT.id].devices[
            TestDeviceState.createdDevice.deviceId
        ]

        del self.appClient.state.active.deviceTypes[TestDeviceState.createdDT.id]
        assert self.doesDTNameExist(TestDeviceState.testDeviceTypeName) == False

        del self.appClient.state.draft.physicalInterfaces[TestDeviceState.createdPI.id]
        assert self.doesPINameExist(TestDeviceState.testPhysicalInterfaceName) == False

        del self.appClient.state.draft.eventTypes[TestDeviceState.createdEventType.id]
        assert self.doesEventTypeNameExist(TestDeviceState.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestDeviceState.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestDeviceState.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestDeviceState.createdLI.id]
        assert self.doesLINameExist(TestDeviceState.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestDeviceState.createdLISchema.id]
        assert self.doesSchemaNameExist(TestDeviceState.testLiSchemaName) == False
