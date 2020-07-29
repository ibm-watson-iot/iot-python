# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import datetime, timedelta
import uuid
import pytest
import testUtils
from wiotp.sdk.exceptions import ApiException


class TestClientConnectivityStatus(testUtils.AbstractTest):

    # =========================================================================
    # Client Connectivity Staus Tests
    #
    # These all need to be rewritten -- hard to do while the API is broken tho :/
    # =========================================================================

    # def testGetClientConnectionStates(self):
    #    response = self.appClient.registry.connectionStatus.getClientStates()
    #   assert response != None
    #  assert "results" in response

    # def testGetConnectedClientConnectionStates(self):
    #   response = self.appClient.registry.connectionStatus.getConnectedClientStates()
    #  assert response != None
    # assert "results" in response

    # def testGetClientConnectionState(self):
    # gets the connection state of a particular client id, returns 404 if client id is not found
    #   response = self.appClient.registry.connectionStatus.getState("fakeId")
    #    assert response != None
    #  assert response["exception"]["properties"] == ["fakeId"]

    # def testGetRecentClientConnectionStates(self):
    # checks for clients that have connected in the last two days
    #   iso8601Date = datetime.now() - timedelta(days=2)
    #  response = self.appClient.registry.connectionStatus.getRecentConnectionClientStates(iso8601Date.isoformat())
    # assert response != None
    # assert "results" in response

    def testConnectionStatusContainsTrueValue(self):
        try:
            key = 15
            connectionStatusContains = self.appClient.registry.connectionStatus.__contains__(key)
            assert True
        except:
            assert False == True

    def testConnectionStatusContainsAPIException(self):
        with pytest.raises(ApiException) as e:
            key = "fff/kdk/f?"
            connectionStatusContains = self.appClient.registry.connectionStatus.__contains__(key)
            assert e

    def testConnectionStatusGetItemValue(self):
        try:
            key = 15
            connectionStatusGetItem = self.appClient.registry.connectionStatus.__getitem__(key)
            assert False == True
        except:
            assert True

    def testConnectionStatusIter(self):
        try:
            deviceIter = self.appClient.registry.connectionStatus.__iter__()
            assert True
        except:
            assert False == True

    def testConnectionStatusGetItemError(self):
        with pytest.raises(KeyError) as e:
            key = 1
            test = self.appClient.registry.connectionStatus.__getitem__(key)
            assert ("No status avaliable for client %s" % (key)) in str(e.value)

    def testConnectionStatusMissingDeviceError(self):
        with pytest.raises(KeyError) as e:
            key = "k"
            test = self.appClient.registry.connectionStatus.__missing__(key)
            assert ("No status avaliable for client %s" % (key)) in str(e.value)

    def testConnectionStatusSetItemError(self):
        with pytest.raises(Exception) as e:
            test = self.appClient.registry.connectionStatus.__setitem__("s", 1)
            assert "Unsupported operation" in str(e.value)

    def testConnectionStatusDelItemError(self):
        with pytest.raises(Exception) as e:
            message = self.appClient.registry.connectionStatus.__delitem__(1)
            assert "Unsupported operation" in str(e.value)

    def testConnectionStatusFindTypeIdValue(self):
        deviceTypeId = str(uuid.uuid4())
        try:
            deviceTypeTest = self.appClient.registry.connectionStatus.find(typeId=deviceTypeId)
            assert True  # It has successfully inputed the values into IterableClientStatusList
        except:
            assert False == True  # It has failed to input the values into IterableClientStatusList

    def testConnectionStatusFindDeviceIdValue(self):
        deviceTypeId = str(uuid.uuid4())
        try:
            deviceTypeTest = self.appClient.registry.connectionStatus.find(deviceId="Test")
            assert True  # It has successfully inputed the values into IterableClientStatusList
        except:
            assert False == True  # It has failed to input the values into IterableClientStatusList

    def testConnectionStatusFindConnectionStatusValues(self):
        deviceTypeId = str(uuid.uuid4())
        try:
            deviceTypeTest = self.appClient.registry.connectionStatus.find(connectionStatus="connected")
            assert True  # It has successfully inputed the values into IterableClientStatusList
        except:
            assert False == True  # It has failed to input the values into IterableClientStatusList

    def testConnectionStatusFindConnectedAfterValues(self):
        deviceTypeId = str(uuid.uuid4())
        try:
            deviceTypeTest = self.appClient.registry.connectionStatus.find(connectedAfter=100)
            assert True  # It has successfully inputed the values into IterableClientStatusList
        except:
            assert False == True  # It has failed to input the values into IterableClientStatusList

    def testConnectionStatusFindParametersValues(self):
        deviceTypeId = str(uuid.uuid4())
        try:
            deviceTypeTest = self.appClient.registry.connectionStatus.find(
                typeId=deviceTypeId, deviceId="Test", connectionStatus="connected", connectedAfter=100
            )
            assert True  # It has successfully inputed the values into IterableClientStatusList
        except:
            assert False == True  # It has failed to input the values into IterableClientStatusList
