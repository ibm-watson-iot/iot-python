# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta  - Initial Contribution
# *****************************************************************************

import ibmiotf.gateway
import ibmiotf.application
import uuid
import time
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
import testUtils

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
        gatewayCli = ibmiotf.gateway.GatewayClient({
            "identity": { "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] }, 
            "auth": { "token": self.registeredGateway["authToken"] }
        })
        assert_is_instance(gatewayCli , ibmiotf.gateway.GatewayClient)


    def testNotAuthorizedConnect(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)

        client = ibmiotf.gateway.GatewayClient({
            "identity": { "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] }, 
            "auth": { "token": "MGxxxxxxxxxxxxx" }
        })
        with assert_raises(ConnectionException) as e:
            client.connect()

    def testMissingMessageEncoder(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        with assert_raises(MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishDeviceEvent(self.registeredGateway["typeId"],self.registeredGateway["deviceId"],"missingMsgEncode", "jason", myData)

    def testMissingMessageEncoderWithPublishEvent(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        with assert_raises(MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishEvent("missingMsgEncode", "jason", myData)

    def testGatewayPubSubMethods(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.GatewayClient(self.options)
        gatewayClient.connect()

        def publishCallback():
            print("Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_true(gatewayClient.publishDeviceEvent(self.DEVICE_TYPE, self.DEVICE_ID, "testDevicePublishEventJson", "json", myData, on_publish=publishCallback))
        assert_true(gatewayClient.publishEvent("testGatewayPublishEventJson", "json", myData, on_publish=publishCallback))

        assert_true(gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID))
        assert_true(gatewayClient.subscribeToCommands())
        assert_true(gatewayClient.subscribeToNotifications())

        gatewayClient.disconnect()

    def testDeviceInfoInstance(self):
        deviceInfoObj = ibmiotf.gateway.DeviceInfo()
        assert_is_instance(deviceInfoObj, ibmiotf.gateway.DeviceInfo)
        print(deviceInfoObj)
    
    @SkipTest
    def testPublishCommandByApplication(self):
        def deviceCmdCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)

        def gatewayCmdCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)

        def notificationCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)

        def appCmdPublishCallback():
            print("Application Publish Command done!!!")

        gatewayClient = ibmiotf.gateway.GatewayClient(self.options)
        
        gatewayClient.commandCallback = gatewayCmdCallback
        gatewayClient.deviceCommandCallback = deviceCmdCallback
        gatewayClient.notificationCallback = notificationCallback
        gatewayClient.connect()
        gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID)
        gatewayClient.subscribeToCommands()
        gatewayClient.subscribeToNotifications()

        appClient = ibmiotf.application.Client(self.appOptions)
        appClient.connect()

        commandData={'rebootDelay' : 50}
        
        assert_true(appClient.publishCommand(self.registeredGateway["typeId"], self.registeredGateway["deviceId"], "reboot", "json", commandData, on_publish=appCmdPublishCallback))
        time.sleep(2)
        
        assert_true(appClient.publishCommand(self.DEVICE_TYPE, self.DEVICE_ID, "reboot", "json", commandData, on_publish=appCmdPublishCallback))
        time.sleep(2)

        appClient.disconnect()
        gatewayClient.disconnect()

    @SkipTest
    # This can be enabled once platform update 102 is released and fixes a bug in the gateway device registration
    def testGatewayApiClientSupport(self):
        gatewayClient = ibmiotf.gateway.GatewayClient(self.options)
        assert_is_instance(gatewayClient.api, ibmiotf.api.ApiClient)

        #Add new device
        newDeviceId = str(uuid.uuid4())
        addResult = gatewayClient.api.registerDevice(self.DEVICE_TYPE, newDeviceId)
        
        assert_equal(addResult['typeId'], self.DEVICE_TYPE)
        assert_equal(addResult['deviceId'], newDeviceId)
        
        time.sleep(5)
        
        #Remove the added device
        gatewayClient.api.deleteDevice(self.DEVICE_TYPE, newDeviceId)
