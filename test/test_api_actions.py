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
import sys
import json


@testUtils.oneJobOnlyTest
class TestActions(testUtils.AbstractTest):

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

    testActionName = "test-action-new"
    updated_action_name = testActionName + "-updated"

    def isstring(self, s):
        # if we use Python 3
        if sys.version_info[0] >= 3:
            basestring = str
        return isinstance(s, basestring)

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for a in self.appClient.actions:
            print("Action instance %s, name: %s" % (a.id, a.name))
            if a.name in [TestActions.testActionName, TestActions.updated_action_name]:
                print("Deleting old test action instance: %s" % (a))
                del self.appClient.actions[a.id]
            else:
                print("Found a non matching test action instance: %s" % (a))

        # delete any left over device types
        for dt in self.appClient.state.active.deviceTypes:
            # print("Device type instance: %s" % (dt))
            if dt.id in (TestActions.testDeviceTypeName, TestActions.updatedDeviceTypeName):
                print("Deleting old test device type instance: %s" % (dt))
                del self.appClient.state.active.deviceTypes[dt.id]

        # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestActions.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestActions.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestActions.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name in (TestActions.testEventSchemaName, TestActions.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
                del self.appClient.state.draft.schemas[s.id]

    def checkAction(self, action, name, type, description, configuration, enabled):
        assert action.name == name
        assert action.actionType == type
        assert action.description == description
        # the config could also include additional elements when created, so just check the given configuration elements
        for configElement in configuration:
            assert action.configuration[configElement] is not None
        assert action.enabled == enabled
        assert isinstance(action.created, datetime)
        assert self.isstring(action.createdBy)
        assert isinstance(action.updated, datetime)
        assert self.isstring(action.updatedBy)

    def doesActionNameExist(self, name):
        for a in self.appClient.actions.find({"name": name}):
            if a.name == name:
                return True
        return False

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

    def createLI(self, name, description, schemaId):
        createdLI = self.appClient.state.draft.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdLI

    def createDT(self, name, description, deviceInfo=None, metadata=None, edgeConfiguration=None, classId="Device"):
        payload = {
            "id": name,
            "description": description,
            "deviceInfo": deviceInfo,
            "metadata": metadata,
            "classId": classId,
            "edgeConfiguration": edgeConfiguration,
        }
        createdDT = self.appClient.state.active.deviceTypes.create(payload)
        return createdDT

    def createAndCheckAction(self, name, type, description, configuration, enabled):

        createdAction = self.appClient.actions.create(
            {"name": name, "type": type, "description": description, "configuration": configuration, "enabled": enabled}
        )
        self.checkAction(createdAction, name, type, description, configuration, enabled)

        # now actively refetch the action to check it is stored
        fetchedAction = self.appClient.actions.__getitem__(createdAction.id)
        assert createdAction == fetchedAction

        return createdAction

    def checkTrigger(self, trigger, expectedTrigger):
        id = trigger.id  # just make sure it exists
        assert trigger.name == expectedTrigger["name"]
        assert trigger.triggerType == expectedTrigger["type"]
        assert trigger.enabled == expectedTrigger["enabled"]
        assert trigger.variableMappings == expectedTrigger["variableMappings"]
        assert trigger.configuration == expectedTrigger["configuration"]

    def createAndCheckTrigger(self, action, trigger):
        createdTrigger = action.triggers.create(trigger)
        self.checkTrigger(createdTrigger, trigger)

        # now actively refetch the trigger to check it is stored
        for fetchedTrigger in action.triggers:
            assert createdTrigger == fetchedTrigger

        return createdTrigger

    def activateDeviceType(self):
        # LI
        test_schema_name = TestActions.testLiSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestActions.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        TestActions.createdLISchema = self.createSchema(
            test_schema_name, "liSchema.json", TestActions.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestActions.createdLI = self.createLI(
            testLIName, "Test Logical Interface description", TestActions.createdLISchema.id
        )

        # PI
        test_schema_name = TestActions.testEventSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestActions.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name) == False
        testPIName = TestActions.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a schema
        TestActions.createdEventSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestActions.testEventSchema, "Test schema description"
        )

        # Create an eventType
        TestActions.createdEventType = self.createEventType(
            test_eventType_name, "Test event type description", TestActions.createdEventSchema.id
        )

        # Create a Physical Interface
        TestActions.createdPI = self.createPI(testPIName, "Test Physical Interface description")

        # Associate event with PI
        TestActions.createdPI.events.create(
            {"eventId": TestActions.testEventId, "eventTypeId": TestActions.createdEventType.id}
        )

        test_dt_name = TestActions.testDeviceTypeName
        assert self.doesDTNameExist(test_dt_name) == False

        # Create a Device Type
        self.createdDT = self.createDT(test_dt_name, "Test Device Type description")

        # Associate PI
        self.createdDT.physicalInterface = TestActions.createdPI

        # Associate the LI
        self.createdDT.logicalInterfaces.create(TestActions.createdLI)

        # Mappings
        self.createdDT.mappings.create(
            {
                "logicalInterfaceId": TestActions.createdLI.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {
                    TestActions.testEventId: {
                        "temperature": "$event.temperature",
                        "humidity": "$event.humidity",
                        "publishTimestamp": "$event.publishTimestamp",
                    }
                },
            }
        )

        # Validate and Activate the LI
        self.createdDT.validate()

        self.createdDT.activate()

        # Check all the active resources, we mayhave to wait for this to complete
        for attempt in range(6):
            if (
                self.doesActiveSchemaNameExist(TestActions.testEventSchemaName)
                and self.doesActiveSchemaNameExist(TestActions.testLiSchemaName)
                and self.doesActiveEventTypeNameExist(TestActions.testEventTypeName)
                and self.doesActivePINameExist(TestActions.testPhysicalInterfaceName)
                and self.doesActiveLINameExist(TestActions.testLogicalInterfaceName)
                and self.doesActiveDTNameExist(TestActions.testDeviceTypeName)
            ):
                break
            print("Device Type resources not yet activated, attempt %s" % attempt)
            print(
                "Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s, Devive Type: %s"
                % (
                    self.doesActiveSchemaNameExist(TestActions.testEventSchemaName),
                    self.doesActiveSchemaNameExist(TestActions.testLiSchemaName),
                    self.doesActiveEventTypeNameExist(TestActions.testEventTypeName),
                    self.doesActivePINameExist(TestActions.testPhysicalInterfaceName),
                    self.doesActiveLINameExist(TestActions.testLogicalInterfaceName),
                    self.doesActiveDTNameExist(TestActions.testDeviceTypeName),
                )
            )
            time.sleep(10)

    def deactivateDeviceType(self):
        self.createdDT.deactivate()

        # Check all the active resources are removed, we may have to wait for this to complete
        for attempt in range(6):
            if not (
                self.doesActiveSchemaNameExist(TestActions.testEventSchemaName)
                or self.doesActiveSchemaNameExist(TestActions.testLiSchemaName)
                or self.doesActiveEventTypeNameExist(TestActions.testEventTypeName)
                or self.doesActivePINameExist(TestActions.testPhysicalInterfaceName)
                or self.doesActiveLINameExist(TestActions.testLogicalInterfaceName)
            ):
                break
            print("Device Type resources not yet de-activated, attempt %s" % attempt)
            print(
                "Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Physical Interface: %s, Logical Interface: %s"
                % (
                    self.doesActiveSchemaNameExist(TestActions.testEventSchemaName),
                    self.doesActiveSchemaNameExist(TestActions.testLiSchemaName),
                    self.doesActiveEventTypeNameExist(TestActions.testEventTypeName),
                    self.doesActivePINameExist(TestActions.testPhysicalInterfaceName),
                    self.doesActiveLINameExist(TestActions.testLogicalInterfaceName),
                )
            )
            time.sleep(10)

        del self.appClient.state.active.deviceTypes[self.createdDT.id]
        assert self.doesDTNameExist(TestActions.testDeviceTypeName) == False

        del self.appClient.state.draft.physicalInterfaces[TestActions.createdPI.id]
        assert self.doesPINameExist(TestActions.testPhysicalInterfaceName) == False

        del self.appClient.state.draft.eventTypes[TestActions.createdEventType.id]
        assert self.doesEventTypeNameExist(TestActions.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestActions.createdEventSchema.id]
        assert self.doesSchemaNameExist(TestActions.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestActions.createdLI.id]
        assert self.doesLINameExist(TestActions.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestActions.createdLISchema.id]
        assert self.doesSchemaNameExist(TestActions.testLiSchemaName) == False

    def testCreateDeleteAction1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name) == False

        # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name,
            "webhook",
            "Test action description",
            {"targetUrl": "https://my.lovely.com/api/something"},
            True,
        )
        # Can we search for it
        assert self.doesActionNameExist(test_action_name) == True

        # Delete the action
        del self.appClient.actions[createdAction.id]
        # It should be gone
        assert self.doesActionNameExist(test_action_name) == False

    def testCreateUpdateDeleteAction1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name) == False

        # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name,
            "webhook",
            "Test action description",
            {"targetUrl": "https://my.lovely.com/api/something"},
            True,
        )
        # Can we search for it
        assert self.doesActionNameExist(test_action_name) == True

        # Update the action
        updated_action_name = TestActions.updated_action_name
        updatedAction = self.appClient.actions.update(
            createdAction.id,
            {
                "id": createdAction.id,
                "name": updated_action_name,
                "type": "webhook",
                "description": "Test action updated description",
                "configuration": {"targetUrl": "https://my.lovely.com/api/somethingelse"},
                "enabled": False,
            },
        )
        self.checkAction(
            updatedAction,
            updated_action_name,
            "webhook",
            "Test action updated description",
            {"targetUrl": "https://my.lovely.com/api/somethingelse"},
            False,
        )

        # Can we search for it
        assert self.doesActionNameExist(updated_action_name) == True

        # Delete the action
        del self.appClient.actions[createdAction.id]
        # It should be gone
        assert self.doesActionNameExist(test_action_name) == False

    def testCreateDeleteActionAndTrigger1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name) == False

        self.activateDeviceType()

        # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name,
            "webhook",
            "Test action description",
            {"targetUrl": "https://my.lovely.com/api/something"},
            True,
        )
        assert self.doesActionNameExist(test_action_name) == True

        trigger1 = self.createAndCheckTrigger(
            createdAction,
            {
                "name": "Test Rule Trigger",
                "type": "rule",
                "description": "Rule Trigger Description",
                "configuration": {
                    "ruleId": "*",
                    "logicalInterfaceId": self.createdLI.id,
                    "type": "*",
                    "typeId": "*",
                    "instanceId": "*",
                },
                "variableMappings": {},
                "enabled": True,
            },
        )

        del self.appClient.actions[createdAction.id]

        # Action and Trigger should be gone
        assert self.doesActionNameExist(test_action_name) == False

        self.deactivateDeviceType()
