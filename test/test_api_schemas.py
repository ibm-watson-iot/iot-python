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

class TestSchemas(testUtils.AbstractTest):
    
    testSchemaName = "test-schemas"
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for a in self.appClient.statemanagement.schemas:
            if a.name == TestSchemas.testSchemaName:
                print("Deleting old test schema instance: %s" % (a))
                del self.appClient.statemanagement.schemas[a.id]


    def checkSchema (self, schema, name, type, description, configuration, enabled):
        assert schema.name == name
        assert schema.schemaType == type
        assert schema.description == description
        # the config could also include additional elements when created, so just check the given configuration elements
        for configElement in configuration:
            assert schema.configuration[configElement] is not None
        assert schema.enabled == enabled
        assert isinstance(schema.created, datetime)
        assert isinstance(schema.createdBy, str)
        assert isinstance(schema.updated, datetime)        
        assert isinstance(schema.updatedBy, str)            
        
    def doesSchemaNameExist (self, name):
        for a in self.appClient.statemanagement.schemas.find({"nameFilter","name"}):
            return True
        return False


    def createAndCheckSchema(self, name, type, description, configuration, enabled):

        createdSchema = self.appClient.statemanagement.schemas.create(
            name, type, description, configuration, enabled)
        self.checkSchema(createdSchema, name, type, description, configuration, enabled)

        # now actively refetch the schema to check it is stored
        fetchedSchema = self.appClient.statemanagement.schemas.__getitem__(createdSchema.id)
        assert createdSchema == fetchedSchema
        
        return createdSchema

    def testCreateDeleteSchema1(self):
        test_schema_name = TestSchemas.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False

        # Create an schema
        createdSchema = self.createAndCheckSchema(
            test_schema_name, 
            "webhook", 
            "Test schema description", 
            {"targetUrl": "https://my.lovely.com/api/something"}, 
            True)
       # Can we search for it
        assert self.doesSchemaNameExist(test_schema_name)==True

        # Delete the schema
        del self.appClient.statemanagement.schemas[createdSchema.id]
        # It should be gone
        assert self.doesSchemaNameExist(test_schema_name)==False

    def testCreateDeleteSchemaAndTrigger1(self):
        test_schema_name = TestSchemas.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False

        # Create an schema
        createdSchema = self.createAndCheckSchema(
            test_schema_name, 
            "webhook", 
            "Test schema description", 
            {"targetUrl": "https://my.lovely.com/api/something"}, 
            True)
        assert self.doesSchemaNameExist(test_schema_name)==True

        trigger1 = createdSchema.triggers.create(
            "Test Rule Trigger", 
            "rule", 
            "Rule Trigger Description", 
            { "ruleId": "*",
              "logicalInterfaceId" : "4718d1b435d9ea9990be9fb3",
              "type": "*",
              "typeId": "*",
              "instanceId": "*",
            }, {}, True)

        del self.appClient.statemanagement.schemas[createdSchema.id]
        
        # Schema and Trigger should be gone
        assert self.doesSchemaNameExist(test_schema_name)==False
