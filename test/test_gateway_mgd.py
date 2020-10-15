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
from wiotp.sdk.gateway import ManagedGatewayClient
from wiotp.sdk import Utf8Codec
import unittest


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

    def testPublishDeviceEvent(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).publishDeviceEvent(
                typeId="test", deviceId="test2", eventId="test3", msgFormat="test4", data="test5"
            )
            test
            assert True
        except:
            assert False == True

    def testPublishEvent(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).publishEvent(eventId="test", msgFormat="test2", data="test3")
            test
            assert True
        except:
            assert False == True

    def testSubscribeToDeviceCommands(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).subscribeToDeviceCommands(typeId="test", deviceId="test2")
            test
            assert True
        except:
            assert False == True

    def testSubscribeToCommands(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).subscribeToCommands()
            test
            assert True
        except:
            assert False == True

    def testSubscribeToNotifications(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).subscribeToNotifications()
            test
            assert True
        except:
            assert False == True

    def testSetPropertyNameError(self, gateway):
        with pytest.raises(Exception) as e:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).setProperty(name="test", value="test2")
            assert "Unsupported property name: " in str(e.value)

    def testSetPropertyName(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            test = ManagedGatewayClient(option).setProperty(name="model", value="test2")
            assert True
        except:
            assert False == True

    def testOnDeviceCommand0Lifetime(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3599
            test = ManagedGatewayClient(option)
            test2 = test.manage(lifetime=testVariable)
            assert True
        except:
            assert False == True

    def testOnDeviceCommandLifetime(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3600
            test = ManagedGatewayClient(option)
            test2 = test.manage(lifetime=testVariable)
            assert True
        except:
            assert False == True

    def testUnmanage(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3600
            test = ManagedGatewayClient(option)
            test2 = test.unmanage()
            assert True
        except:
            assert False == True

    def testSetErrorCodesNone(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3600
            test = ManagedGatewayClient(option).setErrorCode(errorCode=None)
            assert True
        except:
            assert False == True

    def testSetErrorCodesValue(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3600
            test = ManagedGatewayClient(option).setErrorCode(errorCode=0)
            assert True
        except:
            assert False == True

    def testSetErrorCodesValue(self, gateway):
        try:
            option = {
                "identity": {"orgId": "test", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            testVariable = 3600
            test = ManagedGatewayClient(option).clearErrorCodes()
            assert True
        except:
            assert False == True

    def testManagedDeviceMgmtResponseError(self, gateway):
        with pytest.raises(Exception) as e:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": gateway.authToken},
            }
            managedDevice = ManagedGatewayClient(config)
            testValue = "Test"
            encodedPayload = Utf8Codec.encode(testValue)
            managedDevice._ManagedGatewayClient__onDeviceMgmtResponse(client=1, userdata=2, pahoMessage=encodedPayload)
            assert "Unable to parse JSON. payload=" " error" in str(e.value)
