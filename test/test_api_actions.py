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

class TestActions(testUtils.AbstractTest):
    
    testActionName = "test-action"
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for a in self.appClient.actionManager.actions:
            if a.name == TestActions.testActionName:
                print("Deleting old test action instance: %s" % (a))
                del self.appClient.actionManager.actions[a.id]


    def checkAction (self, action, name, type, description, configuration, enabled):
        assert action.name == name
        assert action.actionType == type
        assert action.description == description
        # the config could also include additional elements when created, so just check the given configuration elements
        for configElement in configuration:
            assert action.configuration[configElement] is not None
        assert action.enabled == enabled
        assert isinstance(action.created, datetime)
        assert isinstance(action.createdBy, str)
        assert isinstance(action.updated, datetime)        
        assert isinstance(action.updatedBy, str)            
        
    def doesActionNameExist (self, name):
        for a in self.appClient.actionManager.actions.find(nameFilter=name):
            return True
        return False


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

    def testCreateDeleteActionAndTrigger1(self):
        test_action_name = TestActions.testActionName
        assert self.doesActionNameExist(test_action_name)==False

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
              "logicalInterfaceId" : "4718d1b435d9ea9990be9fb3",
              "type": "*",
              "typeId": "*",
              "instanceId": "*",
            }, {}, True)

        del self.appClient.actionManager.actions[createdAction.id]
        
        # Action and Trigger should be gone
        assert self.doesActionNameExist(test_action_name)==False
