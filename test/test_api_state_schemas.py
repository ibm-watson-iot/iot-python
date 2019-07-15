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
class TestSchemas(testUtils.AbstractTest):

    testSchemaName = "python-api-test-schema"
    updatedTestSchemaName = testSchemaName + "-updated"

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

    testEventSchemaUpdated = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "title": "Sensor Event Schema with temperature removed",
        "properties": {
            "humidity": {"description": "relative humidty (%)", "type": "number", "minimum": 0.0, "default": 0.0},
            "publishTimestamp": {"description": "publishTimestamp", "type": "number", "minimum": 0.0, "default": 0.0},
        },
        "required": ["humidity", "publishTimestamp"],
    }

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        # print("Cleaning up  old test schema instances")
        for a in self.appClient.state.draft.schemas:
            if a.name == TestSchemas.testSchemaName:
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.state.draft.schemas[a.id]
            # TBD debug else:
            #  print("Found a non matching test schema instance: %s" % (a))

    def checkSchema(self, schema, name, schemaFileName, schemaContents, description, version="draft"):
        assert schema.name == name
        assert schema.description == description
        assert schema.schemaType == "json-schema"
        assert schema.schemaFileName == schemaFileName
        assert schema.contentType == "application/json"
        assert schema.content == schemaContents
        assert schema.version == version

        assert isinstance(schema.created, datetime)
        assert isinstance(schema.createdBy, str)
        assert isinstance(schema.updated, datetime)
        assert isinstance(schema.updatedBy, str)

    def doesDraftSchemaNameExist(self, name):
        for a in self.appClient.state.draft.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesActiveSchemaNameExist(self, name):
        for a in self.appClient.state.active.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def createAndCheckSchema(self, name, schemaFileName, schemaContents, description):

        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        self.checkSchema(createdSchema, name, schemaFileName, schemaContents, description)

        # now actively refetch the schema to check it is stored
        fetchedSchema = self.appClient.state.draft.schemas.__getitem__(createdSchema.id)
        assert createdSchema == fetchedSchema

        return createdSchema

    def testCreateDeleteSchema1(self):
        test_schema_name = TestSchemas.testSchemaName
        assert self.doesDraftSchemaNameExist(test_schema_name) == False
        assert self.doesActiveSchemaNameExist(test_schema_name) == False

        # Create a schema
        createdSchema = self.createAndCheckSchema(
            test_schema_name, "eventSchema.json", TestSchemas.testEventSchema, "Test schema description"
        )

        # Can we search for it
        assert self.doesDraftSchemaNameExist(test_schema_name) == True
        # Creating the draft shouldn't create the active
        assert self.doesActiveSchemaNameExist(test_schema_name) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesDraftSchemaNameExist(test_schema_name) == False

    def testCreateUpdateDeleteSchema1(self):
        test_schema_name = TestSchemas.testSchemaName
        assert self.doesDraftSchemaNameExist(test_schema_name) == False

        # Create a schema
        createdSchema = self.createAndCheckSchema(
            test_schema_name, "eventSchema.json", TestSchemas.testEventSchema, "Test schema description"
        )

        # Can we search for it
        assert self.doesDraftSchemaNameExist(test_schema_name) == True
        # Creating the draft shouldn't create the active
        assert self.doesActiveSchemaNameExist(test_schema_name) == False

        # Update the schema
        updated_schema_name = TestSchemas.updatedTestSchemaName
        updatedSchema = self.appClient.state.draft.schemas.update(
            createdSchema.id,
            {"id": createdSchema.id, "name": updated_schema_name, "description": "Test schema updated description"},
        )
        self.checkSchema(
            updatedSchema,
            updated_schema_name,
            "eventSchema.json",
            TestSchemas.testEventSchema,
            "Test schema updated description",
        )

        # Update the schema content
        updated_schema_name = TestSchemas.updatedTestSchemaName
        result = self.appClient.state.draft.schemas.updateContent(
            createdSchema.id, "newEventSchema.json", TestSchemas.testEventSchemaUpdated
        )
        assert result == True
        updatedSchema = self.appClient.state.draft.schemas[createdSchema.id]
        self.checkSchema(
            updatedSchema,
            updated_schema_name,
            "newEventSchema.json",
            TestSchemas.testEventSchemaUpdated,
            "Test schema updated description",
        )

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesDraftSchemaNameExist(test_schema_name) == False

    # ==================================================================================
    # We'll test the presence of active schemas as part of device type activation tests.
    # ==================================================================================
