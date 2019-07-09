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


@testUtils.oneJobOnlyTest
class TestPhysicalInterfaces(testUtils.AbstractTest):

    testSchemaName = "python-api-test-pi_schema"

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

    testEventTypeName = "python-api-test-pi_eventType"
    testPhysicalInterfaceName = "python-api-test-physicalInterface"
    updatedPhysicalInterfaceName = "python-api-test-physicalInterface-updated"

    testEventIdRoot = "python-api-test-pi_eventId"
    testEventIdCount = 5

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for pi in self.appClient.state.draft.physicalInterfaces:
            if pi.name in (
                TestPhysicalInterfaces.testPhysicalInterfaceName,
                TestPhysicalInterfaces.updatedPhysicalInterfaceName,
            ):
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.state.draft.physicalInterfaces[pi.id]

        for et in self.appClient.state.draft.eventTypes:
            if et.name == TestPhysicalInterfaces.testEventTypeName:
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name == TestPhysicalInterfaces.testSchemaName:
                del self.appClient.state.draft.schemas[s.id]

    def checkPI(self, physicalInterface, name, description):
        assert physicalInterface.name == name
        assert physicalInterface.description == description

        assert isinstance(physicalInterface.created, datetime)
        assert isinstance(physicalInterface.createdBy, str)
        assert isinstance(physicalInterface.updated, datetime)
        assert isinstance(physicalInterface.updatedBy, str)

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

    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        return createdSchema

    def createEventType(self, name, description, schemaId):
        createdEventType = self.appClient.state.draft.eventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        return createdEventType

    def createAndCheckPI(self, name, description):
        createdPI = self.appClient.state.draft.physicalInterfaces.create({"name": name, "description": description})
        self.checkPI(createdPI, name, description)

        # now actively refetch the PI to check it is stored
        fetchedPI = self.appClient.state.draft.physicalInterfaces.__getitem__(createdPI.id)
        assert createdPI == fetchedPI

        # Check that there are no associated event mappings when it's just created
        for a in fetchedPI.events.find({"name": name}):
            assert False

        return createdPI

    def testPhysicalInterfaceCRUD(self):
        testPIName = TestPhysicalInterfaces.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a Physical Interface
        createdPI = self.createAndCheckPI(testPIName, "Test Physical Interface description")

        # Can we search for it
        assert self.doesPINameExist(testPIName) == True

        # Update the PI
        updated_pi_name = TestPhysicalInterfaces.updatedPhysicalInterfaceName
        updatedPI = self.appClient.state.draft.physicalInterfaces.update(
            createdPI.id, {"id": createdPI.id, "name": updated_pi_name, "description": "Test PI updated description"}
        )
        self.checkPI(updatedPI, updated_pi_name, "Test PI updated description")

        # Delete the PI
        del self.appClient.state.draft.physicalInterfaces[createdPI.id]
        # It should be gone
        assert self.doesPINameExist(testPIName) == False

    def testPhysicalInterfaceEventCRUD(self):
        test_schema_name = TestPhysicalInterfaces.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestPhysicalInterfaces.testEventTypeName
        assert self.doesEventTypeNameExist(test_eventType_name) == False
        testPIName = TestPhysicalInterfaces.testPhysicalInterfaceName
        assert self.doesPINameExist(testPIName) == False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestPhysicalInterfaces.testEventSchema, "Test schema description"
        )

        # Create an eventType
        createdEventType = self.createEventType(test_eventType_name, "Test event type description", createdSchema.id)

        # Create a Physical Interface
        createdPI = self.createAndCheckPI(testPIName, "Test Physical Interface description")

        # Can we search for it
        assert self.doesPINameExist(testPIName) == True

        # Check that there are no associated event mappings when it's just created
        for em in createdPI.events.find():
            print("Unexpected event mapping %s" % em)
            assert False

        # Associate Event Types with PI
        for typeNo in range(self.testEventIdCount):
            createdPI.events.create({"eventId": self.testEventIdRoot + str(typeNo), "eventTypeId": createdEventType.id})

        # Refetch the event mappings, check we have the number created
        eventMappingCount = 0
        for em in createdPI.events.find():
            # TBD DEBUG print ("Counting event mapping %s" % em)
            eventMappingCount = eventMappingCount + 1
        assert eventMappingCount == self.testEventIdCount

        # Delete the event mappings
        for em in createdPI.events.find():
            # TBD DEBUG print ("Deleting event mapping %s" % em)
            del createdPI.events[em.eventId]

        # Check that there are no associated event mappings after deletion
        for em in createdPI.events.find():
            print("Unexpected event mapping %s" % em)
            assert False

        # Delete the PI
        del self.appClient.state.draft.physicalInterfaces[createdPI.id]
        # It should be gone
        assert self.doesPINameExist(testPIName) == False

        # Delete the event type
        del self.appClient.state.draft.eventTypes[createdEventType.id]
        # It should be gone
        assert self.doesEventTypeNameExist(test_eventType_name) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name) == False
