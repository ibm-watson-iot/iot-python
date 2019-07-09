# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import time
import pytest
import testUtils
import wiotp.sdk.gateway
import wiotp.sdk.application


class TestGateway(testUtils.AbstractTest):
    registeredDevice = None
    registeredGateway = None

    def testNotAuthorizedConnect(self, gateway):
        client = wiotp.sdk.gateway.GatewayClient(
            {
                "identity": {"orgId": self.ORG_ID, "typeId": gateway.typeId, "deviceId": gateway.deviceId},
                "auth": {"token": "MGxxxxxxxxxxxxx"},
            }
        )
        assert isinstance(client, wiotp.sdk.gateway.GatewayClient)
        with pytest.raises(wiotp.sdk.ConnectionException) as e:
            client.connect()

    def testMissingMessageEncoder(self, gateway):
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": gateway.typeId, "deviceId": gateway.deviceId},
            "auth": {"token": gateway.authToken},
        }
        gatewayClient = wiotp.sdk.gateway.GatewayClient(options)
        gatewayClient.connect()

        with pytest.raises(wiotp.sdk.MissingMessageEncoderException) as e:
            myData = {"name": "foo", "cpu": 60, "mem": 50}
            gatewayClient.publishEvent("missingMsgEncode", "jason", myData)

        gatewayClient.disconnect()

    def testMissingMessageEncoderWithPublishEvent(self, gateway):
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": gateway.typeId, "deviceId": gateway.deviceId},
            "auth": {"token": gateway.authToken},
        }
        gatewayClient = wiotp.sdk.gateway.GatewayClient(options)
        gatewayClient.connect()

        with pytest.raises(wiotp.sdk.MissingMessageEncoderException) as e:
            myData = {"name": "foo", "cpu": 60, "mem": 50}
            gatewayClient.publishEvent("missingMsgEncode", "jason", myData)
        gatewayClient.disconnect()

    def testGatewayPubSubMethods(self, gateway):
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": gateway.typeId, "deviceId": gateway.deviceId},
            "auth": {"token": gateway.authToken},
        }
        gatewayClient = wiotp.sdk.gateway.GatewayClient(options)
        gatewayClient.connect()

        def publishCallback():
            print("Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        assert (
            gatewayClient.publishDeviceEvent(
                gateway.typeId,
                gateway.deviceId,
                "testDevicePublishEventJson",
                "json",
                myData,
                onPublish=publishCallback,
            )
            == True
        )
        assert (
            gatewayClient.publishEvent("testGatewayPublishEventJson", "json", myData, onPublish=publishCallback) == True
        )

        # mid = 0 means there was a problem with the subscription
        assert gatewayClient.subscribeToDeviceCommands(gateway.typeId, gateway.deviceId) != 0
        assert gatewayClient.subscribeToCommands() != 0
        assert gatewayClient.subscribeToNotifications() != 0

        gatewayClient.disconnect()

    def testDeviceInfoInstance(self):
        deviceInfoObj = wiotp.sdk.gateway.DeviceInfo()
        assert isinstance(deviceInfoObj, wiotp.sdk.gateway.DeviceInfo)
        print(deviceInfoObj)
