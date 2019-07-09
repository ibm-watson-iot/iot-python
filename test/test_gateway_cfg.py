# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import pytest
import testUtils
import wiotp.sdk.gateway


class TestGatewayCfg(testUtils.AbstractTest):
    def testMissingOptions(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({})
        assert e.value.reason == "Missing identity from configuration"

    def testMissingOrg(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient(
                {"identity": {"orgId": None, "typeId": "myType", "deviceId": "myId"}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason == "Missing identity.orgId from configuration"

    def testMissingType(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient(
                {"identity": {"orgId": "myOrg", "typeId": None, "deviceId": "myId"}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason == "Missing identity.typeId from configuration"

    def testMissingId(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient(
                {"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": None}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason, "Missing identity.deviceId from configuration"

    def testMissingAuthToken(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient(
                {"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": "myId"}, "auth": {"token": None}}
            )
            wiotp.sdk.gateway.GatewayClient(
                {
                    "org": self.ORG_ID,
                    "type": self.registeredDevice.typeId,
                    "id": self.registeredDevice.deviceId,
                    "auth-method": None,
                    "auth-token": self.registeredDevice.authToken,
                }
            )
        assert e.value.reason == "Missing auth.token from configuration"

    def testMissingConfigFile(self):
        deviceFile = "InvalidFile.out"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.parseConfigFile(deviceFile)
        assert (
            e.value.reason
            == "Error reading device configuration file 'InvalidFile.out' ([Errno 2] No such file or directory: 'InvalidFile.out')"
        )

    def testAuthProperties(self):
        config = wiotp.sdk.gateway.GatewayClientConfig(
            **{"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": "myId"}, "auth": {"token": "myToken"}}
        )

        assert config.apiKey == "g/myOrg/myType/myId"
        assert config.apiToken == "myToken"
