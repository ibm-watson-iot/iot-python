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


@testUtils.oneJobOnlyTest
class TestDevice(testUtils.AbstractTest):

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

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        # delete any left over device types
        for dt in self.appClient.state.active.deviceTypes:
            # print("Device type instance: %s" % (dt))
            if dt.id in (TestDevice.testDeviceTypeName, TestDevice.updatedDeviceTypeName):
                for dev in dt.devices:
                    print("Deleting devices %s for device type instance: %s" % (dev.deviceId, dt.id))
                    del dt.devices[dev.deviceId]
                print("Deleting old test device type instance: %s" % (dt.id))
                del self.appClient.state.active.deviceTypes[dt.id]

        # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestDevice.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestDevice.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestDevice.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name in (TestDevice.testEventSchemaName, TestDevice.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
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
        test_schema_name = TestDevice.testLiSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestDevice.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        TestDevice.createdLISchema = self.createSchema(
            test_schema_name, "liSchema.json", TestDevice.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestDevice.createdLI = self.createLI(
            testLIName, "Test Logical Interface description", TestDevice.createdLISchema.id
        )

        # PI
        test_schema_name = TestDevice.testEventSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestDevice.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name) == False
        testPIName = TestDevice.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a schema
        TestDevice.createdEventSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestDevice.testEventSchema, "Test schema description"
        )

        # Create an eventType
        TestDevice.createdEventType = self.createEventType(
            test_eventType_name, "Test event type description", TestDevice.createdEventSchema.id
        )

        # Create a Physical Interface
        TestDevice.createdPI = self.createPI(testPIName, "Test Physical Interface description")

        # Associate event with PI
        TestDevice.createdPI.events.create(
            {"eventId": TestDevice.testEventId, "eventTypeId": TestDevice.createdEventType.id}
        )

        test_dt_name = TestDevice.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name) == False

        # Create a Device Type
        TestDevice.createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

    def testRegisterDevice(self):
        createdDeviceId = str(uuid.uuid4())
        deviceInfo = {"serialNumber": "123", "descriptiveLocation": "Floor 3, Room 2"}
        metadata = {"customField1": "customValue1", "customField2": "customValue2"}
        TestDevice.createdDevice = TestDevice.createdDT.devices.create(
            {
                "deviceId": createdDeviceId,
                "authToken": "NotVerySecretPassw0rd",
                "deviceInfo": deviceInfo,
                "metadata": metadata,
            }
        )

        # read it back to check it's there
        for retrievedDevice in TestDevice.createdDT.devices:
            assert retrievedDevice.typeId == TestDevice.createdDT.id
            assert retrievedDevice.deviceId == createdDeviceId
            assert retrievedDevice.metadata == metadata
            assert retrievedDevice.registration != None
            assert retrievedDevice.status != None
            assert retrievedDevice.deviceInfo == deviceInfo

    def testDeletePreReqs(self):

        del self.appClient.state.active.deviceTypes[TestDevice.createdDT.id].devices[TestDevice.createdDevice.deviceId]

        del self.appClient.state.active.deviceTypes[TestDevice.createdDT.id]
        assert self.doesDTNameExist(TestDevice.testDeviceTypeName) == False

        del self.appClient.state.draft.physicalInterfaces[TestDevice.createdPI.id]
        assert self.doesPINameExist(TestDevice.testPhysicalInterfaceName) == False

        del self.appClient.state.draft.eventTypes[TestDevice.createdEventType.id]
        assert self.doesEventTypeNameExist(TestDevice.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestDevice.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestDevice.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestDevice.createdLI.id]
        assert self.doesLINameExist(TestDevice.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestDevice.createdLISchema.id]
        assert self.doesSchemaNameExist(TestDevice.testLiSchemaName) == False
