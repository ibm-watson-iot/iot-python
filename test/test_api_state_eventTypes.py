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
class TestEventTypes(testUtils.AbstractTest):

    testSchemaName = "python-api-test-ev-schema"

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

    testEventTypeName = "python-api-test-eventType"
    updatedEventTypeName = "python-api-test-eventType-updated"

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for et in self.appClient.state.draft.eventTypes:
            if et.name in (TestEventTypes.testEventTypeName, TestEventTypes.updatedEventTypeName):
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.state.draft.eventTypes[et.id]

        for s in self.appClient.state.draft.schemas:
            if s.name == TestEventTypes.testSchemaName:
                del self.appClient.state.draft.schemas[s.id]

    def checkEventType(self, eventType, name, description, schemaId):
        assert eventType.name == name
        assert eventType.description == description
        assert eventType.schemaId == schemaId
        assert eventType.version == "draft"

        assert isinstance(eventType.created, datetime)
        assert isinstance(eventType.createdBy, str)
        assert isinstance(eventType.updated, datetime)
        assert isinstance(eventType.updatedBy, str)

    def doesSchemaNameExist(self, name):
        for a in self.appClient.state.draft.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesActiveEventTypeNameExist(self, name):
        for et in self.appClient.state.active.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def doesDraftEventTypeNameExist(self, name):
        for et in self.appClient.state.draft.eventTypes.find({"name": name}):
            if et.name == name:
                return True
        return False

    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        return createdSchema

    def createAndCheckEventType(self, name, description, schemaId):
        createdEventType = self.appClient.state.draft.eventTypes.create(
            {"name": name, "description": description, "schemaId": schemaId}
        )
        self.checkEventType(createdEventType, name, description, schemaId)

        # now actively refetch the schema to check it is stored
        fetchedEventType = self.appClient.state.draft.eventTypes.__getitem__(createdEventType.id)
        assert createdEventType == fetchedEventType

        return createdEventType

    def testCreateDeleteEventType(self):
        test_schema_name = TestEventTypes.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestEventTypes.testEventTypeName
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestEventTypes.testEventSchema, "Test schema description"
        )

        # Create an eventType
        createdEventType = self.createAndCheckEventType(
            test_eventType_name, "Test event type description", createdSchema.id
        )

        # Can we search for it
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == True
        # Creating the draft shouldn't create the active
        assert self.doesActiveEventTypeNameExist(test_eventType_name) == False

        # Delete the event type
        del self.appClient.state.draft.eventTypes[createdEventType.id]
        # It should be gone
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name) == False

    def testCreateUpdateDeleteEventType(self):
        test_schema_name = TestEventTypes.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        test_eventType_name = TestEventTypes.testEventTypeName
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, "eventSchema.json", TestEventTypes.testEventSchema, "Test schema description"
        )

        # Create an eventType
        createdEventType = self.createAndCheckEventType(
            test_eventType_name, "Test event type description", createdSchema.id
        )

        # Can we search for it
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == True
        # Creating the draft shouldn't create the active
        assert self.doesActiveEventTypeNameExist(test_eventType_name) == False

        # Update the event type
        updated_eventType_name = TestEventTypes.updatedEventTypeName
        updatedEventType = self.appClient.state.draft.eventTypes.update(
            createdEventType.id,
            {
                "id": createdEventType.id,
                "name": updated_eventType_name,
                "description": "Test event type updated description",
                "schemaId": createdSchema.id,
            },
        )
        self.checkEventType(
            updatedEventType, updated_eventType_name, "Test event type updated description", createdSchema.id
        )

        # Delete the event type
        del self.appClient.state.draft.eventTypes[createdEventType.id]
        # It should be gone
        assert self.doesDraftEventTypeNameExist(test_eventType_name) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name) == False
