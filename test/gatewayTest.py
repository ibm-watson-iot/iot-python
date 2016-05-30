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
from ibmiotf import *
from nose.tools import *
from nose import SkipTest

class TestGateway:
    #gatewayClient=None
    #managedGateway=None
    #options=None
    
    @classmethod
    def setup_class(self):
        gwayConfFile="gateway.conf"
        gwayOptions = ibmiotf.gateway.ParseConfigFile(gwayConfFile)
        
        self.org = gwayOptions['org']
        self.gatewayType = gwayOptions['type']
        self.gatewayId = gwayOptions['id']
        self.authToken = gwayOptions['auth-token']
                        
    @classmethod    
    def teardown_class(self):
        pass;
        
    @raises(Exception)
    def testMissingOptions(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({})
        assert_equal(e.exception.msg, 'Missing required property: org')
        
    @raises(Exception)
    def testMissingOrg(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": None, "type": self.gatewayType, "id": self.gatewayId, 
                                   "auth-method": "token", "auth-token": self.authToken })
        assert_equal(e.exception.msg, 'Missing required property: org')

    @raises(Exception)
    def testMissingType(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.org, "type": None, "id": self.gatewayId, 
                                   "auth-method": "token", "auth-token": self.authToken })
        assert_equal(e.exception.msg, 'Missing required property: type')

    @raises(Exception)
    def testMissingId(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": None, 
                                   "auth-method": "token", "auth-token": self.authToken})
        assert_equal(e.exception.msg, 'Missing required property: id')

    @raises(Exception)
    def testMissingAuthMethod(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": self.gatewayId, 
                                   "auth-method": None, "auth-token": self.authToken})
        assert_equal(e.exception.msg, 'Missing required property: auth-method')

    @raises(Exception)
    def testMissingAuthToken(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": self.gatewayId, 
                                   "auth-method": "token", "auth-token": None })
        assert_equal(e.exception.msg, 'Missing required property: auth-token')
        
    @raises(Exception)
    def testUnSupportedAuthMethod(self):
        with assert_raises(UnsupportedAuthenticationMethod) as e:
            ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": self.gatewayId, 
                                   "auth-method": "unsupported-method", "auth-token": self.authToken})
        assert_equal(e.exception_type,UnsupportedAuthenticationMethod)

    
    def testGatewayClientInstance(self):
        gatewayCli = ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": self.gatewayId, "auth-method": "token", "auth-token": self.authToken})
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
        
    @SkipTest    
    def testNotAuthorizedConnect(self):
        client = ibmiotf.gateway.Client({"org": self.org, "type": self.gatewayType, "id": self.gatewayId, 
                                              "auth-method": "token", "auth-token": "MGxxx3g7Yjt-6keG(l", "auth-key":"a-xxxxxx-s1tsofmoxo"})
        with assert_raises(ConnectionException) as e:
            client.connect()
        assert_equals(e.exception, ConnectionException)
        assert_equals(e.exception.msg,'Not authorized')
       
    @SkipTest
    def testMissingMessageEncoder(self):
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        gatewayClient = ibmiotf.gateway.Client(options)    
        gatewayClient.connect()
        
        with assert_raises(MissingMessageEncoderException)as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            self.gatewayClient.publishDeviceEvent(self.gatewayType,self.gatewayId,"missingMsgEncode", "jason", myData)
        assert_equals(e.exception, MissingMessageEncoderException)
    
    @SkipTest
    def testMissingMessageEncoderWithPublishGatewayEvent(self):
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        gatewayClient = ibmiotf.gateway.Client(options)    
        gatewayClient.connect()
        
        with assert_raises(MissingMessageEncoderException)as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            self.gatewayClient.publishGatewayEvent("missingMsgEncode", "jason", myData)
        assert_equals(e.exception, MissingMessageEncoderException)
            
    def testGatewayPubSubMethods(self):
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        deviceFile="device.conf"
        devOptions = ibmiotf.gateway.ParseConfigFile(deviceFile)
        
        gatewayClient = ibmiotf.gateway.Client(options)    
        gatewayClient.connect()
        
        def publishCallback():
            print("Publish Event done!!!")
           
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_true(gatewayClient.publishDeviceEvent(devOptions['type'],devOptions['id'],"testDevicePublishEvent", "json", myData,on_publish=publishCallback))    
        assert_true(gatewayClient.publishGatewayEvent("testGatewayPublishEvent", "json", myData,on_publish=publishCallback))   
        assert_equals(gatewayClient.publishEventOverHTTP("testPublishEventHTTPs", myData),403)
        
        assert_true(gatewayClient.subscribeToDeviceCommands(devOptions['type'],devOptions['id']))
        assert_true(gatewayClient.subscribeToGatewayCommands())     
        assert_true(gatewayClient.subscribeToGatewayNotifications())
        
        gatewayClient.disconnect()   
                                        
    def testGatewayPubSubMethodsInQSMode(self):
        deviceFile="device.conf"
        devOptions = ibmiotf.gateway.ParseConfigFile(deviceFile)
        
        gatewayClient = ibmiotf.gateway.Client({"org": "quickstart", "type": self.gatewayType, "id": self.gatewayId,
                                        "auth-method":"None", "auth-token":"None" })
        gatewayClient.connect()
        
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(gatewayClient.publishEventOverHTTP("testPublishEventHTTP", myData),200)
        
        assert_false(gatewayClient.subscribeToDeviceCommands(devOptions['type'], devOptions['id']))
        assert_false(gatewayClient.subscribeToGatewayCommands())     
        assert_false(gatewayClient.subscribeToGatewayNotifications())
        
        gatewayClient.disconnect()
        
    def testDeviceInfoInstance(self):
        deviceInfoObj = ibmiotf.gateway.DeviceInfo()
        assert_is_instance(deviceInfoObj, ibmiotf.gateway.DeviceInfo)
        print(deviceInfoObj)
        
    def testManagedGatewayInstance(self):
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        managedGateway = ibmiotf.gateway.ManagedGateway(options)
        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedGateway)        
        
    @raises(Exception)
    def testManagedgatewayQSException(self):
        with assert_raises(Exception)as e:
            options={"org": "quickstart", "type": self.gatewayType, "id": self.gatewayId,
                                        "auth-method":"None", "auth-token":"None" }
            ibmiotf.gateway.ManagedGateway(options)
        assert_equals(e.exception, Exception)    
        
    @SkipTest
    def testManagedGatewayConnectException(self):
        options={"org": self.org, "type": self.gatewayType, "id": self.gatewayId,
                                        "auth-method":"token", "auth-token":self.authToken }
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedGateway(options,deviceInfo=gatewayInfoObj)
        with assert_raises(ConnectionException)as e:
            managedGateway.connect()
        assert_equals(e.exception, ConnectionException)        
    
    def testManagedGatewayInstanceWithDeviceInfo(self):
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedGateway(options,deviceInfo=gatewayInfoObj)
            
        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedGateway)
        
        #Connect managedGateway
        managedGateway.connect()
                
        #Define device properties to be notified whenever reset
        managedGateway._deviceMgmtObservations = ["deviceInfo.manufacturer", "deviceInfo.descriptiveLocation", 
                                                  "deviceInfo.fwVersion", "deviceInfo.model", "deviceInfo.description", 
                                                  "deviceInfo.deviceClass", "deviceInfo.hwVersion", "deviceInfo.serialNumber"]
        
        #Reset managedgateway properties  and validate the returned is instance of threading.Event
        assert_is_instance(managedGateway.setErrorCode(1),threading.Event)
        assert_is_instance(managedGateway.setLocation(longitude=100, latitude=78, accuracy=100,elevation=45),threading.Event)   
        
        managedGateway.setSerialNumber('iot-pgateway-12345')
        managedGateway.setManufacturer("IBM India Pvt Ltd")
        managedGateway.setModel("2016")
        managedGateway.setdeviceClass("Smart Gateway")
        managedGateway.setDescription("Sample Smart IoT Gateway")
        managedGateway.setFwVersion("1.0")
        managedGateway.setHwVersion("2.0")
        managedGateway.setDescriptiveLocation("ISL Lab Bangalore")
        
        managedGateway.clearErrorCodes()    
        
        #Disconnect ManagedGateway
        managedGateway.unmanage()
        managedGateway.disconnect()
        
    def testPublishCommandByApplication(self):
        def deviceCmdCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)
            
        def gatewayCmdCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)
            
        def notificationCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)    
  
        def appCmdPublishCallback():
            print("Application Publish Command done!!!")
  
        gatewayFile="gateway.conf"
        options = ibmiotf.gateway.ParseConfigFile(gatewayFile)
        gatewayClient = ibmiotf.gateway.Client(options)
        
        deviceFile="device.conf"
        devOptions = ibmiotf.gateway.ParseConfigFile(deviceFile)
        deviceType = devOptions['type']
        deviceId = devOptions['id']
        
        gatewayClient.commandCallback = gatewayCmdCallback
        gatewayClient.deviceCommandCallback = deviceCmdCallback
        gatewayClient.notificationCallback = notificationCallback
        gatewayClient.connect()
        gatewayClient.subscribeToDeviceCommands(deviceType,deviceId)
        gatewayClient.subscribeToGatewayCommands()
        gatewayClient.subscribeToGatewayNotifications()
               
        appConfFile="application.conf"
        appOptions = ibmiotf.application.ParseConfigFile(appConfFile)
        appClient = ibmiotf.application.Client(appOptions)
        appClient.connect()
                        
        commandData={'rebootDelay' : 50}
        assert_true(appClient.publishCommand(self.gatewayType, self.gatewayId, "reboot", "json", commandData, on_publish=appCmdPublishCallback))
        time.sleep(2)
        assert_true(appClient.publishCommand(deviceType, deviceId, "reboot", "json", commandData, on_publish=appCmdPublishCallback))
        time.sleep(2)        
        
        appClient.disconnect()
        gatewayClient.disconnect()
    