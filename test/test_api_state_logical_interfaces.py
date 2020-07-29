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
class TestLogicalInterfaces(testUtils.AbstractTest):

    testSchemaName = "python-api-test-li-schema"

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

    testLogicalInterfaceName = "python-api-test-logicalInterface"
    updatedLogicalInterfaceName = "python-api-test-logicalInterface-updated"

    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for li in self.appClient.state.draft.logicalInterfaces:
            if li.name in (
                TestLogicalInterfaces.testLogicalInterfaceName,
                TestLogicalInterfaces.updatedLogicalInterfaceName,
            ):
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.state.draft.logicalInterfaces[li.id]

        for s in self.appClient.state.draft.schemas:
            if s.name == TestLogicalInterfaces.testSchemaName:
                del self.appClient.state.draft.schemas[s.id]

    def checkLI(self, logicalInterface, name, description, schemaId, version, alias):
        assert logicalInterface.name == name
        assert logicalInterface.description == description
        assert logicalInterface.schemaId == schemaId
        assert logicalInterface.version == version
        assert logicalInterface.alias == alias

        assert isinstance(logicalInterface.created, datetime)
        assert isinstance(logicalInterface.createdBy, str)
        assert isinstance(logicalInterface.updated, datetime)
        assert isinstance(logicalInterface.updatedBy, str)

    def doesSchemaNameExist(self, name):
        for a in self.appClient.state.draft.schemas.find({"name": name}):
            if a.name == name:
                return True
        return False

    def doesLINameExist(self, name):
        for li in self.appClient.state.draft.logicalInterfaces.find({"name": name}):
            if li.name == name:
                return True
        return False

    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.state.draft.schemas.create(name, schemaFileName, jsonSchemaContents, description)
        return createdSchema

    def createAndCheckLI(self, name, description, schemaId, version, alias):
        createdLI = self.appClient.state.draft.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId, "version": version, "alias": alias}
        )
        self.checkLI(createdLI, name, description, schemaId, version, alias)

        # now actively refetch the LI to check it is stored
        fetchedLI = self.appClient.state.draft.logicalInterfaces.__getitem__(createdLI.id)
        assert createdLI == fetchedLI

        return createdLI

    def testLogicalInterfaceCRUD(self):
        test_schema_name = TestLogicalInterfaces.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestLogicalInterfaces.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, "liSchema.json", TestLogicalInterfaces.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        createdLI = self.createAndCheckLI(
            testLIName, "Test Logical Interface description", createdSchema.id, "draft", "alias"
        )

        # Can we search for it
        assert self.doesLINameExist(testLIName) == True

        # Update the LI
        updated_li_name = TestLogicalInterfaces.updatedLogicalInterfaceName
        updatedLI = self.appClient.state.draft.logicalInterfaces.update(
            createdLI.id,
            {
                "id": createdLI.id,
                "name": updated_li_name,
                "description": "Test LI updated description",
                "schemaId": createdSchema.id,
                "version": "draft",
                "alias": "test",
            },
        )
        self.checkLI(updatedLI, updated_li_name, "Test LI updated description", createdSchema.id, "draft", "test")

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[createdLI.id]
        # It should be gone
        assert self.doesLINameExist(testLIName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name) == False

    def testLogicalInterfaceActivation(self):
        test_schema_name = TestLogicalInterfaces.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name) == False
        testLIName = TestLogicalInterfaces.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName) == False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, "liSchema.json", TestLogicalInterfaces.testLISchema, "Test schema description"
        )

        # Create a Logical Interface
        createdLI = self.createAndCheckLI(
            testLIName, "Test Logical Interface description", createdSchema.id, "draft", "alias"
        )

        # Can we search for it
        assert self.doesLINameExist(testLIName) == True

        # Validate and Activate the LI
        createdLI.validate()
        print("LI Differences: %s " % createdLI.validate())

        # Activating the Li should fail as it is not yet associated with a Device or Thing Type.
        try:
            createdLI.activate()
            # Hmm, the activate should raise an exception
            assert False
        except:
            assert True
            # The expected exception was raised

        # This should fail as there are currently no differences with the LI
        try:
            createdLI.differences()
            # Should raise an exception
            assert False
        except:
            assert True
            # The expected exception was raised

        # Delete the LI
        del self.appClient.state.draft.logicalInterfaces[createdLI.id]
        # It should be gone
        assert self.doesLINameExist(testLIName) == False

        # Delete the schema
        del self.appClient.state.draft.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name) == False
