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
import string
import json
import sys
from test_state_utils import TestStateUtils


@testUtils.oneJobOnlyTest
class TestThingTypes(testUtils.AbstractTest):

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
            }
        },
        "required": ["temperature"],
    }
    testEventTypeName = "python-api-test-dt-pi_eventType"
    testEventId = "python-api-test-dt-pi_eventId"

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
            }
        },
        "required": ["temperature"],
    }

    testLogicalInterfaceName = "python-api-test-dt-li"

    thingTypeId = "thingTypeId"
    testPhysicalInterfaceName = "python-api-test-dt-pi"

    thingSchemaName = "thingSchema"

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        # delete any left over device types
        for tt in self.appClient.state.active.thingTypes:
            # print("Device type instance: %s" % (dt))
            if tt.id in (TestThingTypes.thingTypeName):
                for thing in tt.things:
                    print("Deleting things %s for thing type instance: %s" % (thing.thingId, tt.id))
                    del tt.things[thing.thingId]
                print("Deleting old test thing type instance: %s" % (tt.id))
                self.appClient.state.active.thingTypes[tt.id].deactivate()

        for tt in self.appClient.state.draft.thingTypes:
            if tt.id in TestThingTypes.thingTypeName:
                del self.appClient.state.draft.thingTypes[tt.id]

        # delete any left over logical interfaces
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name == TestThingTypes.testLogicalInterfaceName:
                print("Deleting old test LI: %s" % (li))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        # delete any left over physical interfaces, event type and schema
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name == TestThingTypes.testPhysicalInterfaceName:
                print("Deleting old test PI: %s" % (pi))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestThingTypes.testEventTypeName:
                print("Deleting old test event type: %s" % (et))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name in (TestThingTypes.testEventSchemaName, TestThingTypes.testLiSchemaName):
                print("Deleting old test schema instance: %s" % (s))
                del self.appClient.state.draft.schemas[s.id]

    def isstring(self, s):
        # if we use Python 3
        if sys.version_info[0] >= 3:
            basestring = str
        return isinstance(s, basestring)

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

        fetchedThing = self.appClient.state.active.thing.__getitem__(createdThing.id)
        assert createdThing == fetchedThing

        return createdThing

    def testCreatePreReqs(self):
        # LI
        test_schema_name = TestThingTypes.testLiSchemaName
        assert TestStateUtils.doesSchemaNameExist(self.appClient, test_schema_name) == False
        testLIName = TestThingTypes.testLogicalInterfaceName
        assert TestStateUtils.doesLINameExist(self.appClient, testLIName) == False

        # Create a schema
        TestThingTypes.createdLISchema = TestStateUtils.createSchema(
            self.appClient, test_schema_name, "liSchema.json", TestThingTypes.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        TestThingTypes.createdLI = TestStateUtils.createLI(
            self.appClient, testLIName, "Test Logical Interface description", TestThingTypes.createdLISchema.id
        )

        # PI
        test_schema_name = TestThingTypes.testEventSchemaName
        assert TestStateUtils.doesSchemaNameExist(self.appClient, test_schema_name) == False
        test_eventType_name = TestThingTypes.testEventTypeName
        assert TestStateUtils.doesEventTypeNameExist(self.appClient, test_eventType_name) == False
        # Create a schema
        TestThingTypes.createdEventSchema = TestStateUtils.createSchema(
            self.appClient,
            test_schema_name,
            "eventSchema.json",
            TestThingTypes.testEventSchema,
            "Test schema description",
        )

        # Create an eventType
        TestThingTypes.createdEventType = TestStateUtils.createEventType(
            self.appClient, test_eventType_name, "Test event type description", TestThingTypes.createdEventSchema.id
        )

    def testThingTypeActivation(self):
        # Check all the resources, we may have to wait for this to complete
        for attempt in range(6):
            if (
                TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testEventSchemaName)
                and TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testLiSchemaName)
                and TestStateUtils.doesEventTypeNameExist(self.appClient, TestThingTypes.testEventTypeName)
                and TestStateUtils.doesLINameExist(self.appClient, TestThingTypes.testLogicalInterfaceName)
            ):
                break
            print("Thing Type resources not yet activated, attempt %s" % attempt)
            print(
                "Active? Event Schema: %s, LI Schema: %s, Event Type: %s, Logical Interface: %s"
                % (
                    TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testEventSchemaName),
                    TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testLiSchemaName),
                    TestStateUtils.doesEventTypeNameExist(self.appClient, TestThingTypes.testEventTypeName),
                    TestStateUtils.doesLINameExist(self.appClient, TestThingTypes.testLogicalInterfaceName),
                )
            )
            time.sleep(10)

        # make sure that thingType does not already exist
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThingTypes.thingTypeId) == False

        testThingTypeSchema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "title": "TestThingSchema",
            "description": "defines the properties of a schema type",
            "properties": {
                "Temperature": {
                    "type": "object",
                    "description": "info",
                    "$logicalInterfaceRef": TestThingTypes.createdLI.id,
                }
            },
            "required": ["Temperature"],
        }
        # create thing type schema
        thingSchema = TestStateUtils.createSchema(
            self.appClient,
            TestThingTypes.thingSchemaName,
            "liThingSchema.json",
            testThingTypeSchema,
            "Test schema description",
        )
        # create and check thing type
        TestThingTypes.createdTT = self.createAndCheckTT(
            TestThingTypes.thingTypeId, "temperature type", "Test Device Type description", thingSchema.id
        )
        # create logical interface for thingType
        LItest = TestThingTypes.createdTT.logicalInterfaces.create({"id": TestThingTypes.createdLI.id})

        # create mapping for thing type
        TestThingTypes.createdTT.mappings.create(
            {
                "logicalInterfaceId": LItest.id,
                "notificationStrategy": "on-state-change",
                "propertyMappings": {"Temperature": {"temperature": "$event.temperature"}},
            }
        )
        # validate thingType
        self.appClient.state.draft.thingTypes[TestThingTypes.createdTT.id].validate()

        # Check that draft thing type exists and active does not
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThingTypes.thingTypeId) == True
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThingTypes.thingTypeId) == False

        # Activate thingType
        self.appClient.state.draft.thingTypes[TestThingTypes.createdTT.id].activate()

        configDifferences2 = TestThingTypes.createdTT.differences()
        assert configDifferences2["contentState"] == "SAME"

        # Check that both active and draft thingType exist
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThingTypes.thingTypeId) == True
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThingTypes.thingTypeId) == True

    def testThingTypeDeactivation(self):

        self.appClient.state.active.thingTypes[TestThingTypes.createdTT.id].deactivate()
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThingTypes.thingTypeId) == True
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThingTypes.thingTypeId) == False

        # delete thingType and check both are gone
        del self.appClient.state.draft.thingTypes[TestThingTypes.createdTT.id]
        assert TestStateUtils.doesTTNameExist(self.appClient, TestThingTypes.thingTypeId) == False
        assert TestStateUtils.doesActiveTTNameExist(self.appClient, TestThingTypes.thingTypeId) == False

    def testDeletePreReqs(self):

        del self.appClient.state.draft.eventTypes[TestThingTypes.createdEventType.id]
        assert TestStateUtils.doesEventTypeNameExist(self.appClient, TestThingTypes.testEventTypeName) == False

        del self.appClient.state.draft.schemas[TestThingTypes.createdEventSchema.id]
        assert TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testEventSchemaName) == False

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[TestThingTypes.createdLI.id]
        assert TestStateUtils.doesLINameExist(self.appClient, TestThingTypes.testLogicalInterfaceName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[TestThingTypes.createdLISchema.id]
        assert TestStateUtils.doesSchemaNameExist(self.appClient, TestThingTypes.testLiSchemaName) == False
