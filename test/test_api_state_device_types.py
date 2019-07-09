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
import sys
from test_state_utils import TestStateUtils


@testUtils.oneJobOnlyTest
class TestDeviceTypes(testUtils.AbstractTest):

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

    testDeviceTypeName = "python-api-test-DeviceType2"
    updatedDeviceTypeName = "python-api-test-DeviceType-updated"
    oldtestDeviceTypeName = "python-api-test-DeviceType"

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        TestStateUtils.deleteDeviceTypes(
            self.appClient,
            (
                TestDeviceTypes.testDeviceTypeName,
                TestDeviceTypes.updatedDeviceTypeName,
                TestDeviceTypes.oldtestDeviceTypeName,
            ),
        )
        TestStateUtils.deleteDraftLIs(self.appClient, (TestDeviceTypes.testLogicalInterfaceName))
        TestStateUtils.deleteDraftPIs(self.appClient, (TestDeviceTypes.testPhysicalInterfaceName))
        TestStateUtils.deleteDraftEventTypes(self.appClient, (TestDeviceTypes.testEventTypeName))
        TestStateUtils.deleteDraftSchemas(
            self.appClient, (TestDeviceTypes.testEventSchemaName, TestDeviceTypes.testLiSchemaName)
        )

    def isstring(self, s):
        # if we use Python 3
        if sys.version_info[0] >= 3:
            basestring = str
        return isinstance(s, basestring)

    def createAndCheckDT(
        self, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"
    ):

        createdDT = TestStateUtils.createDT(
            self.appClient, name, description, deviceInfo, metadata, edgeConfiguration, classId
        )
        TestStateUtils.checkDT(createdDT, name, description, deviceInfo, metadata, edgeConfiguration, classId)

        # now actively refetch the DT to check it is stored
        fetchedDT = self.appClient.state.active.deviceTypes.__getitem__(createdDT.id)
        assert createdDT == fetchedDT

        return createdDT

    def createAndCheckMapping(self, deviceType, logicalInterfaceId, notificationStrategy, propertyMappings):
        createdMapping = TestStateUtils.createMapping(
            self.appClient, deviceType, logicalInterfaceId, notificationStrategy, propertyMappings
        )
        TestStateUtils.checkMapping(createdMapping, logicalInterfaceId, notificationStrategy, propertyMappings)

        # now actively refetch the mapping to check it is stored
        for fetchedMapping in deviceType.mappings:
            assert createdMapping == fetchedMapping

        return createdMapping

    def testCreatePreReqs(self):
        # LI
        test_schema_name = TestDeviceTypes.testLiSchemaName
        assert TestStateUtils.doesSchemaNameExist(self.appClient, test_schema_name) == False
        testLIName = TestDeviceTypes.testLogicalInterfaceName
        assert TestStateUtils.doesLINameExist(self.appClient, testLIName) == False

        # Create a schema
        TestDeviceTypes.createdLISchema = TestStateUtils.createSchema(
            self.appClient, test_schema_name, "liSchema.json", TestDeviceTypes.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestDeviceTypes.createdLI = TestStateUtils.createLI(
            self.appClient, testLIName, "Test Logical Interface description", TestDeviceTypes.createdLISchema.id
        )

        # PI
        test_schema_name = TestDeviceTypes.testEventSchemaName
        assert TestStateUtils.doesSchemaNameExist(self.appClient, test_schema_name) == False
        test_eventType_name = TestDeviceTypes.testEventTypeName
        assert TestStateUtils.doesEventTypeNameExist(self.appClient, test_eventType_name) == False
        testPIName = TestDeviceTypes.testPhysicalInterfaceName
        assert TestStateUtils.doesPINameExist(self.appClient, testPIName) == False

        # Create a schema
        TestDeviceTypes.createdEventSchema = TestStateUtils.createSchema(
            self.appClient,
            test_schema_name,
            "eventSchema.json",
            TestDeviceTypes.testEventSchema,
            "Test schema description",
        )

        # Create an eventType
        TestDeviceTypes.createdEventType = TestStateUtils.createEventType(
            self.appClient, test_eventType_name, "Test event type description", TestDeviceTypes.createdEventSchema.id
        )

        # Create a Physical Interface
        TestDeviceTypes.createdPI = TestStateUtils.createPI(
            self.appClient, testPIName, "Test Physical Interface description"
        )

        # Associate event with PI
        TestDeviceTypes.createdPI.events.create(
            {"eventId": TestDeviceTypes.testEventId, "eventTypeId": TestDeviceTypes.createdEventType.id}
        )

    def testDeviceTypeCRUD(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        # Can we search for it
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == True

        # Update the DT
        updatedDT = self.appClient.state.active.deviceTypes.update(
            createdDT.id, {"description": "Test Device Type updated description"}
        )
        TestStateUtils.checkDT(updatedDT, test_dt_name, "Test Device Type updated description")

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeviceTypeFullCRUD(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        deviceInfo = {
            "serialNumber": "100087",
            "manufacturer": "ACME Co.",
            "model": "7865",
            "deviceClass": "A",
            "description": "My shiny device",
            "fwVersion": "1.0.0",
            "hwVersion": "1.0",
            "descriptiveLocation": "Office 5, D Block",
        }

        metadata = {"customField1": "customValue1", "customField2": "customValue2"}

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description", deviceInfo, metadata)

        # Can we search for it
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == True

        # Update the DT
        updatedDT = self.appClient.state.active.deviceTypes.update(
            createdDT.id, {"description": "Test Device Type updated description"}
        )
        TestStateUtils.checkDT(updatedDT, test_dt_name, "Test Device Type updated description", deviceInfo, metadata)

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeviceTypePICRUD(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        # Check the PI
        try:
            PI = createdDT.physicalInterface
            print("A newly created Device Type shouldn't have an associated Physical Interface. We have: %s" % PI)
            assert False == True  # fail
        except:
            assert True  # TBD check the exception

        createdDT.physicalInterface = TestDeviceTypes.createdPI

        TestStateUtils.comparePIs(createdDT.physicalInterface, TestDeviceTypes.createdPI)

        # Update the PI
        createdDT.physicalInterface = TestDeviceTypes.createdPI

        # Delete the PI
        del createdDT.physicalInterface

        try:
            PI = createdDT.physicalInterface
            print("We deleted the PI, so there shouldn't be an associated Physical Interface. We have: %s" % PI)
            assert False == True  # fail
        except:
            assert True  # TBD check the exception

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeviceTypeLICRUD(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == True

        # Check the LI
        for li in createdDT.logicalInterfaces:
            print("A newly created Device Type shouldn't have an associated Logical Interface, we have %s" % li)
            assert False == True

        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI)

        associatedLICount = 0
        for li in createdDT.logicalInterfaces:
            associatedLICount = associatedLICount + 1
            assert li == TestDeviceTypes.createdLI
        assert associatedLICount == 1

        # delete the associated LI
        for li in createdDT.logicalInterfaces:
            del createdDT.logicalInterfaces[li.id]

        # Check the LI
        for li in createdDT.logicalInterfaces:
            print("This Device Type shouldn't have an associated Logical Interface, we have %s" % li)
            assert False == True

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeviceTypeEventMappingCRUD(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI)

        # Check there are no Mappings
        for m in createdDT.mappings:
            print("A newly created Device Type shouldn't have an associated Mappings, we have %s" % m)
            assert False == True

        self.createAndCheckMapping(
            createdDT,
            TestDeviceTypes.createdLI.id,
            "on-state-change",
            propertyMappings={
                TestDeviceTypes.testEventId: {
                    "temperature": "$event.temperature",
                    "humidity": "$event.humidity",
                    "publishTimestamp": "$event.publishTimestamp",
                }
            },
        )

        associatedMapCount = 0
        for m in createdDT.mappings:
            associatedMapCount = associatedMapCount + 1
            # TBD assert li == TestDeviceTypes.createdLI
        assert associatedMapCount == 1

        # delete the associated Mappings
        for m in createdDT.mappings:
            del createdDT.mappings[m.logicalInterfaceId]

        # Check the Mappings have gone
        for m in createdDT.mappings:
            print("The Device Type shouldn't have any associated Mappings, we have %s" % m)
            assert False == True

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeviceTypeActivation(self):

        test_dt_name = TestDeviceTypes.testDeviceTypeName
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

        # Create a Device Type
        createdDT = self.createAndCheckDT(test_dt_name, "Test Device Type description")

        # Associate PI
        createdDT.physicalInterface = TestDeviceTypes.createdPI

        # Associate the LI
        createdDT.logicalInterfaces.create(TestDeviceTypes.createdLI)

        # Mappings
        createdDT.mappings.create(
            {
                "logicalInterfaceId": TestDeviceTypes.createdLI.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {
                    TestDeviceTypes.testEventId: {
                        "temperature": "$event.temperature",
                        "humidity": "$event.humidity",
                        "publishTimestamp": "$event.publishTimestamp",
                    }
                },
            }
        )

        # Validate and Activate the LI
        createdDT.validate()

        createdDT.activate()

        # Wait for active resources

        # Check all the active resources, we mayhave to wait for this to complete
        for attempt in range(6):
            if (
                TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testEventSchemaName)
                and TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testLiSchemaName)
                and TestStateUtils.doesActiveEventTypeNameExist(self.appClient, TestDeviceTypes.testEventTypeName)
                and TestStateUtils.doesActivePINameExist(self.appClient, TestDeviceTypes.testPhysicalInterfaceName)
                and TestStateUtils.doesActiveLINameExist(self.appClient, TestDeviceTypes.testLogicalInterfaceName)
                and TestStateUtils.doesActiveDTNameExist(self.appClient, TestDeviceTypes.testDeviceTypeName)
            ):
                break
            print("Device Type resources not yet activated, attempt %s" % attempt)
            print(
                "Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s, Devive Type: %s"
                % (
                    TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testEventSchemaName),
                    TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testLiSchemaName),
                    TestStateUtils.doesActiveEventTypeNameExist(self.appClient, TestDeviceTypes.testEventTypeName),
                    TestStateUtils.doesActivePINameExist(self.appClient, TestDeviceTypes.testPhysicalInterfaceName),
                    TestStateUtils.doesActiveLINameExist(self.appClient, TestDeviceTypes.testLogicalInterfaceName),
                    TestStateUtils.doesActiveDTNameExist(self.appClient, TestDeviceTypes.testDeviceTypeName),
                )
            )
            time.sleep(10)

        # Now we should be able to activate the LI:
        TestDeviceTypes.createdLI.validate()
        TestDeviceTypes.createdLI.activate()

        # print ("Device Type differences: %s" % )
        configDifferences = createdDT.differences()
        assert configDifferences["contentState"] == "SAME"

        # print ("deactivating Device Type %s" % createdDT)
        createdDT.deactivate()

        # Check all the active resources are removed, we may have to wait for this to complete
        for attempt in range(6):
            if not (
                TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testEventSchemaName)
                or TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testLiSchemaName)
                or TestStateUtils.doesActiveEventTypeNameExist(self.appClient, TestDeviceTypes.testEventTypeName)
                or TestStateUtils.doesActivePINameExist(self.appClient, TestDeviceTypes.testPhysicalInterfaceName)
                or TestStateUtils.doesActiveLINameExist(self.appClient, TestDeviceTypes.testLogicalInterfaceName)
            ):
                break
            print("Device Type resources not yet de-activated, attempt %s" % attempt)
            print(
                "Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s"
                % (
                    TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testEventSchemaName),
                    TestStateUtils.doesActiveSchemaNameExist(self.appClient, TestDeviceTypes.testLiSchemaName),
                    TestStateUtils.doesActiveEventTypeNameExist(self.appClient, TestDeviceTypes.testEventTypeName),
                    TestStateUtils.doesActivePINameExist(self.appClient, TestDeviceTypes.testPhysicalInterfaceName),
                    TestStateUtils.doesActiveLINameExist(self.appClient, TestDeviceTypes.testLogicalInterfaceName),
                )
            )
            time.sleep(10)

        # Delete the DT
        del self.appClient.state.active.deviceTypes[createdDT.id]
        # It should be gone
        assert TestStateUtils.doesDTNameExist(self.appClient, test_dt_name) == False

    def testDeletePreReqs(self):
        del self.appClient.state.draft.physicalInterfaces[TestDeviceTypes.createdPI.id]
        assert TestStateUtils.doesPINameExist(self.appClient, TestDeviceTypes.testPhysicalInterfaceName) == False

        del self.appClient.state.draft.eventTypes[TestDeviceTypes.createdEventType.id]
        assert TestStateUtils.doesEventTypeNameExist(self.appClient, TestDeviceTypes.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestDeviceTypes.createdEventSchema.id]
        assert TestStateUtils.doesSchemaNameExist(self.appClient, TestDeviceTypes.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestDeviceTypes.createdLI.id]
        assert TestStateUtils.doesLINameExist(self.appClient, TestDeviceTypes.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestDeviceTypes.createdLISchema.id]
        assert TestStateUtils.doesSchemaNameExist(self.appClient, TestDeviceTypes.testLiSchemaName) == False
