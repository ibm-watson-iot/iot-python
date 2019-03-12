# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import datetime, timedelta
import pytest
import testUtils

@pytest.mark.skip(reason="API currently unavailable (503)")
class TestClientConnectivityStatus(testUtils.AbstractTest):
    
    # =========================================================================
    # Client Connectivity Staus Tests
    #
    # These all need to be rewritten -- hard to do while the API is broken tho :/
    # =========================================================================
  
    def testGetClientConnectionStates(self):
        response = self.appClient.registry.connectionStatus.getClientStates()
        assert response != None
        assert "results" in response

    def testGetConnectedClientConnectionStates(self):
        response = self.appClient.registry.connectionStatus.getConnectedClientStates()
        assert response != None
        assert "results" in response
    
    def testGetClientConnectionState(self):
        # gets the connection state of a particular client id, returns 404 if client id is not found
        response = self.appClient.registry.connectionStatus.getState("fakeId")
        assert response != None
        assert response['exception']['properties'] == ['fakeId']
        
    def testGetRecentClientConnectionStates(self):
        #checks for clients that have connected in the last two days
        iso8601Date = datetime.now() - timedelta(days=2)
        response = self.appClient.registry.connectionStatus.getRecentConnectionClientStates(iso8601Date.isoformat())
        assert response != None
        assert "results" in response
    