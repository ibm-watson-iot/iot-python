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
from wiotp.sdk.api.actionmanager import Actions
from wiotp.sdk.exceptions import ApiException

class TestActions(testUtils.AbstractTest):
    
    # =========================================================================
    # Set up services
    # =========================================================================
    def testCleanup(self):
        for a in self.appClient.actionManager.actions:
            if a.name == "test-action":
                print("Deleting old test action instance: %s" % (a))
                del self.appClient.actions[a.id]



    def testCreateDeleteService1(self):
        action = {
            "name": "test-action", 
            "description": "Test action"
        }

        createdAction = self.appClient.actionManager.actions.create(action)

        assert createdAction.name == "test-action"
        assert createdAction.description == "Test action"
        assert isinstance(createdAction.created, datetime)
        assert isinstance(createdAction.updated, datetime)

        # Can we search for it
        count = 0
        for a in self.appClient.Actions.find(nameFilter="test-action"):
            assert a.name == "test-action"
            assert createdAction.id == a.id
            count += 1
        assert count == 1

        del self.appClient.actionManager.actions[createdAction.id]
