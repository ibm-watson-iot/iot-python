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
        try: 
            deviceType = self.setupAppClient.api.getDeviceType(self.DEVICE_TYPE)
        except APIException as e:
            if e.httpCode == 404:
                deviceType = self.setupAppClient.api.addDeviceType(self.DEVICE_TYPE)
            else: 
                raise e
        self.registeredDevice = self.setupAppClient.api.registerDevice(self.DEVICE_TYPE, self.DEVICE_ID)
        
        # Register a Gateway
        try: 
            gatewayType = self.setupAppClient.api.getDeviceType(self.GATEWAY_TYPE)
        except APIException as e:
            if e.httpCode == 404:
                deviceType = self.setupAppClient.api.addDeviceType(self.GATEWAY_TYPE, classId = "Gateway")
            else: 
                raise e
        self.registeredGateway = self.setupAppClient.api.registerDevice(self.GATEWAY_TYPE, self.GATEWAY_ID)
        
        self.options={
            "org": self.ORG_ID,
            "type": self.registeredGateway["typeId"],
            "id": self.registeredGateway["deviceId"],
            "auth-method": "token",
            "auth-token": self.registeredGateway["authToken"]
        }
        
        

    @classmethod
    def teardown_class(self):
        self.setupAppClient.api.deleteDevice(self.DEVICE_TYPE, self.DEVICE_ID)
        self.setupAppClient.api.deleteDevice(self.GATEWAY_TYPE, self.GATEWAY_ID)


    @raises(Exception)
    def testMissingOptions(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({})
        assert_equal(e.exception.msg, 'Missing required property: org')

    @raises(Exception)
    def testMissingOrg(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": None, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": "token", "auth-token": self.registeredGateway["authToken"] })
        assert_equal(e.exception.msg, 'Missing required property: org')

    @raises(Exception)
    def testMissingType(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.ORG_ID, "type": None, "id": self.registeredGateway["deviceId"], "auth-method": "token", "auth-token": self.registeredGateway["authToken"] })
        assert_equal(e.exception.msg, 'Missing required property: type')

    @raises(Exception)
    def testMissingId(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": None, "auth-method": "token", "auth-token": self.registeredGateway["authToken"]})
        assert_equal(e.exception.msg, 'Missing required property: id')

    @raises(Exception)
    def testMissingAuthMethod(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": None, "auth-token": self.registeredGateway["authToken"]})
        assert_equal(e.exception.msg, 'Missing required property: auth-method')

    @raises(Exception)
    def testMissingAuthToken(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": "token", "auth-token": None })
        assert_equal(e.exception.msg, 'Missing required property: auth-token')

    @raises(Exception)
    def testUnSupportedAuthMethod(self):
        with assert_raises(UnsupportedAuthenticationMethod) as e:
            ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": "unsupported-method", "auth-token": self.registeredGateway["authToken"]})
        assert_equal(e.exception_type,UnsupportedAuthenticationMethod)


    def testGatewayClientInstance(self):
        gatewayCli = ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": "token", "auth-token": self.registeredGateway["authToken"]})
        assert_is_instance(gatewayCli , ibmiotf.gateway.Client)

    @raises(Exception)
    def testMissingConfigFile(self):
        deviceFile="InvalidFile.out"
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.ParseConfigFile(deviceFile)
        assert_equal(e.exception.msg, 'Error reading device configuration file')

    @raises(Exception)
    def testInvalidConfigFile(self):
        deviceFile="nullValues.conf"
        with assert_raises(AttributeError) as e:
            ibmiotf.gateway.ParseConfigFile(deviceFile)
        assert_equal(e.exception, AttributeError)

    def testNotAuthorizedConnect(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)

        client = ibmiotf.gateway.Client({"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method": "token", "auth-token": "MGxxx3g7Yjt-6keG(l", "auth-key":"a-xxxxxx-s1tsofmoxo"})
        with assert_raises(ConnectionException) as e:
            client.connect()

    def testMissingMessageEncoder(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.Client(self.options)
        gatewayClient.connect()

        with assert_raises(MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishDeviceEvent(self.registeredGateway["typeId"],self.registeredGateway["deviceId"],"missingMsgEncode", "jason", myData)

    def testMissingMessageEncoderWithPublishGatewayEvent(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.Client(self.options)
        gatewayClient.connect()

        with assert_raises(MissingMessageEncoderException) as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            gatewayClient.publishGatewayEvent("missingMsgEncode", "jason", myData)

    def testGatewayPubSubMethods(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.Client(self.options)
        gatewayClient.connect()

        def publishCallback():
            print("Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_true(gatewayClient.publishDeviceEvent(self.DEVICE_TYPE, self.DEVICE_ID, "testDevicePublishEventJson", "json", myData, on_publish=publishCallback))
        assert_true(gatewayClient.publishGatewayEvent("testGatewayPublishEventJson", "json", myData, on_publish=publishCallback))

        assert_true(gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID))
        assert_true(gatewayClient.subscribeToGatewayCommands())
        assert_true(gatewayClient.subscribeToGatewayNotifications())

        gatewayClient.disconnect()

    def testGatewayPubSubMethodsInQSMode(self):
        # Delay 5 seconds so that the gateway is active before we try to connect
        time.sleep(5)
        
        gatewayClient = ibmiotf.gateway.Client({"org": "quickstart", "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method":"None", "auth-token":"None" })
        gatewayClient.connect()

        def publishCallback():
            print("Publish Event done!!!")

        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        
        assert_true(gatewayClient.publishDeviceEvent(self.DEVICE_TYPE, self.DEVICE_ID, "testDevicePublishEvent", "json", myData, on_publish=publishCallback))
        assert_true(gatewayClient.publishGatewayEvent("testGatewayPublishEvent", "json", myData, on_publish=publishCallback))

        assert_false(gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID))
        assert_false(gatewayClient.subscribeToGatewayCommands())
        assert_false(gatewayClient.subscribeToGatewayNotifications())

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

        gatewayClient = ibmiotf.gateway.Client(self.options)
        
        gatewayClient.commandCallback = gatewayCmdCallback
        gatewayClient.deviceCommandCallback = deviceCmdCallback
        gatewayClient.notificationCallback = notificationCallback
        gatewayClient.connect()
        gatewayClient.subscribeToDeviceCommands(self.DEVICE_TYPE, self.DEVICE_ID)
        gatewayClient.subscribeToGatewayCommands()
        gatewayClient.subscribeToGatewayNotifications()

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
        gatewayClient = ibmiotf.gateway.Client(self.options)
        assert_is_instance(gatewayClient.api, ibmiotf.api.ApiClient)

        #Add new device
        newDeviceId = str(uuid.uuid4())
        addResult = gatewayClient.api.registerDevice(self.DEVICE_TYPE, newDeviceId)
        
        assert_equal(addResult['typeId'], self.DEVICE_TYPE)
        assert_equal(addResult['deviceId'], newDeviceId)
        
        time.sleep(5)
        
        #Remove the added device
        gatewayClient.api.deleteDevice(self.DEVICE_TYPE, newDeviceId)
