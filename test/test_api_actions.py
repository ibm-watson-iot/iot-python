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

class TestActions(testUtils.AbstractTest):
    
    testSchemaName = "python-api-test-li-schema"
    
    testLISchema =  {
        "$schema" : "http://json-schema.org/draft-04/schema#",
        "type" : "object",
        "title" : "Environment Sensor Schema",
        "properties" : {
            "temperature" : {
                "description" : "temperature in degrees Celsius",
                "type" : "number",
                "minimum" : -237.15,
                "default" : 0.0
            },
            "humidity" : {
                "description" : "relative humidity (%)",
                "type" : "number",
                "minimum" : 0.0,
                "default" : 0.0
            },
            "publishTimestamp" : {
                "description" : "publishTimestamp",
                "type" : "number",
                "minimum" : 0.0,
                "default" : 0.0
            }
        },
        "required" : ["temperature", "humidity", "publishTimestamp"]
    } 
    
    testLogicalInterfaceName = "python-api-test-logicalInterface"
    updatedLogicalInterfaceName = "python-api-test-logicalInterface-updated"

    testActionName = "test-action-new"
    updated_action_name = testActionName +"-updated"
    
    def isstring(self, s):
        # if we use Python 3
        if (sys.version_info[0] >= 3):
            return isinstance(s, str)
        # we use Python 2
        return isinstance(s, basestring)


    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        print("Cleaning up  old test action instances")
        for a in self.appClient.actionManager.actions:
            print("Action instance %s, name: %s" % (a.id, a.name))
            if a.name in [TestActions.testActionName, TestActions.updated_action_name]:
                print("Deleting old test action instance: %s" % (a))
                del self.appClient.actionManager.actions[a.id]
            else:
                print("Found a non matching test action instance: %s" % (a))
 
        for li in self.appClient.statemanagement.logicalInterfaces:
            if li.name in (TestActions.testLogicalInterfaceName, TestActions.updatedLogicalInterfaceName):
                # print("Deleting old test schema instance: %s" % (a))
                del self.appClient.statemanagement.logicalInterfaces[li.id]
            
        for s in self.appClient.statemanagement.schemas:
            if s.name == TestActions.testSchemaName:
                del self.appClient.statemanagement.schemas[s.id]      


    def checkAction (self, action, name, type, description, configuration, enabled):
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
        
    def doesActionNameExist (self, name):
        for a in self.appClient.actionManager.actions.find(nameFilter=name):
            if (a.name == name):
                return True
        return False
    
    def doesSchemaNameExist (self, name):
        for a in self.appClient.statemanagement.schemas.find({"name": name}):
            if (a.name == name):
                return True
        return False
    
    def doesLINameExist (self, name):
        for li in self.appClient.statemanagement.logicalInterfaces.find({"name": name}):
            if (li.name == name):
                return True
        return False
    
    def createSchema(self, name, schemaFileName, schemaContents, description):
        jsonSchemaContents = json.dumps(schemaContents)
        createdSchema = self.appClient.statemanagement.schemas.create(
            name, schemaFileName, jsonSchemaContents, description)        
        return createdSchema
    
    def createLI(self, name, description, schemaId):
        createdLI = self.appClient.statemanagement.logicalInterfaces.create(
            {"name": name, "description": description, "schemaId": schemaId})
        return createdLI

    def createAndCheckAction(self, name, type, description, configuration, enabled):

        createdAction = self.appClient.actionManager.actions.create(
            name, type, description, configuration, enabled)
        self.checkAction(createdAction, name, type, description, configuration, enabled)

        # now actively refetch the action to check it is stored
        fetchedAction = self.appClient.actionManager.actions.__getitem__(createdAction.id)
        assert createdAction == fetchedAction
        
        return createdAction

    def testCreateDeleteAction1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name)==False

        # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name, 
            "webhook", 
            "Test action description", 
            {"targetUrl": "https://my.lovely.com/api/something"}, 
            True)
       # Can we search for it
        assert self.doesActionNameExist(test_action_name)==True

        # Delete the action
        del self.appClient.actionManager.actions[createdAction.id]
        # It should be gone
        assert self.doesActionNameExist(test_action_name)==False

    def testCreateUpdateDeleteAction1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name)==False

        # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name, 
            "webhook", 
            "Test action description", 
            {"targetUrl": "https://my.lovely.com/api/something"}, 
            True)
       # Can we search for it
        assert self.doesActionNameExist(test_action_name)==True

        # Update the action
        updated_action_name = TestActions.updated_action_name
        updatedAction = self.appClient.actionManager.actions.update(
            createdAction.id, updated_action_name, "webhook", "Test action updated description",  {"targetUrl": "https://my.lovely.com/api/somethingelse"}, False)
        self.checkAction(updatedAction, updated_action_name, "webhook", "Test action updated description",  {"targetUrl": "https://my.lovely.com/api/somethingelse"}, False)
 
        # Can we search for it
        assert self.doesActionNameExist(updated_action_name)==True
        
        # Delete the action
        del self.appClient.actionManager.actions[createdAction.id]
        # It should be gone
        assert self.doesActionNameExist(test_action_name)==False
    
        
    def testCreateDeleteActionAndTrigger1(self):
        test_schema_name = TestActions.testSchemaName
        assert self.doesSchemaNameExist(test_schema_name)==False
        testLIName = TestActions.testLogicalInterfaceName
        assert self.doesLINameExist(testLIName)==False
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name)==False

        # Create a schema
        createdSchema = self.createSchema(
            test_schema_name, 
            "liSchema.json", 
            TestActions.testLISchema, 
            "Test schema description",
            )

        # Create a Logical Interface
        createdLI = self.createLI(
            testLIName, 
            "Test Logical Interface description",
            createdSchema.id)
        
        createdLI.activate()
 
         # Create an action
        createdAction = self.createAndCheckAction(
            test_action_name, 
            "webhook", 
            "Test action description", 
            {"targetUrl": "https://my.lovely.com/api/something"}, 
            True)
        assert self.doesActionNameExist(test_action_name)==True

        trigger1 = createdAction.triggers.create(
             "Test Rule Trigger", 
             "rule", 
             "Rule Trigger Description", 
             { "ruleId": "*",
               "logicalInterfaceId" : createdLI.id,
               "type": "*",
               "typeId": "*",
               "instanceId": "*",
             }, {}, True)


        del self.appClient.actionManager.actions[createdAction.id]
        
        # Action and Trigger should be gone
        assert self.doesActionNameExist(test_action_name)==False
        
        # Delete the LI
        del self.appClient.statemanagement.logicalInterfaces[createdLI.id]
        assert self.doesLINameExist(testLIName)==False

        # Delete the schema
        del self.appClient.statemanagement.schemas[createdSchema.id]
        assert self.doesSchemaNameExist(test_schema_name)==False
