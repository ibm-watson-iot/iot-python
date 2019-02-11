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
    
    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())
    
    GATEWAY_TYPE = "test_gateway"
    GATEWAY_ID = str(uuid.uuid4())

    
    @classmethod
    def setup_class(self):
        # Register a Device
        if self.DEVICE_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.registry.devicetypes.create({"id": self.DEVICE_TYPE})

        self.registeredDevice = self.appClient.registry.devices.create({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})
        
        # Register a Gateway
        if self.GATEWAY_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.registry.devicetypes.create({"id": self.GATEWAY_TYPE, "classId": "Gateway"})

        self.registeredGateway = self.appClient.registry.devices.create({"typeId": self.GATEWAY_TYPE, "deviceId": self.GATEWAY_ID})
        
        self.options={
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": self.registeredGateway["typeId"],
                "deviceId": self.registeredGateway["deviceId"]
            },
            "auth": {
                "token": self.registeredGateway["authToken"]
            }
        }
        
        

    @classmethod
    def teardown_class(self):
        del self.appClient.registry.devicetypes[self.DEVICE_TYPE].devices[self.DEVICE_ID]
        del self.appClient.registry.devicetypes[self.GATEWAY_TYPE].devices[self.GATEWAY_ID]


    def testGatewayClientInstance(self):
        gatewayCli = wiotp.sdk.gateway.GatewayClient({
            "identity": { "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] }, 
            "auth": { "token": self.registeredGateway["authToken"] }
        })
        assert isinstance(gatewayCli , wiotp.sdk.gateway.GatewayClient)


    def testNotAuthorizedConnect(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)

        client = wiotp.sdk.gateway.GatewayClient({
            "identity": { "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] }, 
            "auth": { "token": "MGxxxxxxxxxxxxx" }
        })
        with pytest.raises(wiotp.sdk.ConnectionException) as e:
            client.connect()

    def testMissingMessageEncoder(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = wiotp.sdk.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        with pytest.raises(wiotp.sdk.MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishDeviceEvent(self.registeredGateway["typeId"],self.registeredGateway["deviceId"],"missingMsgEncode", "jason", myData)

    def testMissingMessageEncoderWithPublishEvent(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = wiotp.sdk.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        with pytest.raises(wiotp.sdk.MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishEvent("missingMsgEncode", "jason", myData)

    def testGatewayPubSubMethods(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = wiotp.sdk.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        def publishCallback():
            print("Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert gatewayClient.publishDeviceEvent(self.DEVICE_TYPE, self.DEVICE_ID, "testDevicePublishEventJson", "json", myData, on_publish=publishCallback) == True
        assert gatewayClient.publishEvent("testGatewayPublishEventJson", "json", myData, on_publish=publishCallback) == True

        # mid = 0 means there was a problem with the subscription
        assert gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID) != 0
        assert gatewayClient.subscribeToCommands() != 0
        assert gatewayClient.subscribeToNotifications() != 0

        gatewayClient.disconnect()

    def testDeviceInfoInstance(self):
        deviceInfoObj = wiotp.sdk.gateway.DeviceInfo()
        assert isinstance(deviceInfoObj, wiotp.sdk.gateway.DeviceInfo)
        print(deviceInfoObj)
