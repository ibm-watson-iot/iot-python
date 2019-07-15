# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import pytest
import testUtils
import wiotp.sdk


class TestGatewayMgd(testUtils.AbstractTest):
    registeredDevice = None
    registeredGateway = None

    def testManagedgatewayQSException(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            options = {"identity": {"orgId": "quickstart", "typeId": "xxx", "deviceId": "xxx"}}
            wiotp.sdk.gateway.ManagedGatewayClient(options)
        assert "QuickStart does not support device management" == e.value.reason

    def testManagedGatewayConnectException(self, gateway):
        badOptions = {
            "identity": {"orgId": self.ORG_ID, "typeId": gateway.typeId, "deviceId": gateway.deviceId},
            "auth": {"token": gateway.authToken},
        }
        gatewayInfoObj = wiotp.sdk.gateway.DeviceInfo()
        managedGateway = wiotp.sdk.gateway.ManagedGatewayClient(badOptions, deviceInfo=gatewayInfoObj)
        assert isinstance(managedGateway, wiotp.sdk.gateway.ManagedGatewayClient)
        managedGateway.connect()
        assert managedGateway.isConnected() == True
        managedGateway.disconnect()
        assert managedGateway.isConnected() == False
