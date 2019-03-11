# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import iso8601
from datetime import datetime, date, timedelta
import json
from collections import defaultdict

import uuid
import pytest
import testUtils
from idlelib.rpc import response_queue

class TestClientConnectivityStatus(testUtils.AbstractTest):
    
    # =========================================================================
    # Client Connectivity Staus Tests
    # =========================================================================
  
        
    def testGetClientConnectionStates(self):
        response = self.appClient.registry.clientConnectivityStatus.getClientConnectionStates()
        assert response != None
        assert "results" in response

    def testGetConnectedClientConnectionStates(self):
        response = self.appClient.registry.clientConnectivityStatus.getConnectedClientConnectionStates()
        assert response != None
        assert "results" in response
    
    def testGetClientConnectionState(self):
        # gets the connection state of a particular client id, returns 404 if client id is not found
        response = self.appClient.registry.clientConnectivityStatus.getClientConnectionState("fakeId")
        assert response != None
        assert response['exception']['properties'] == ['fakeId']
        
    def testGetRecentClientConnectionStates(self):
        #checks for clients that have connected in the last two days
        iso8601Date = datetime.now() - timedelta(days=2)
        response = self.appClient.registry.clientConnectivityStatus.getRecentClientConnectionStates(iso8601Date.isoformat())
        assert response != None
        assert "results" in response
    