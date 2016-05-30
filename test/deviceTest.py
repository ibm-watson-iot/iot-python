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

import ibmiotf.device
import ibmiotf.application
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
import logging

class TestDevice:
    deviceClient=None
    managedClient=None
    options=None
    
    @classmethod
    def setup_class(self):
        deviceFile="device.conf"
        self.options = ibmiotf.device.ParseConfigFile(deviceFile)
        self.org = self.options['org']
        self.deviceType = self.options['type']
        self.deviceId = self.options['id']
        self.authToken = self.options['auth-token']
        
        self.deviceClient = ibmiotf.device.Client(self.options)    
                
        #Create default DeviceInfo Instance and associate with ManagedClient Instance
        deviceInfoObj = ibmiotf.device.DeviceInfo()
        deviceInfoObj.fwVersion = 0.0
        self.managedClient = ibmiotf.device.ManagedClient(self.options,deviceInfo=deviceInfoObj)
        
        #Get application options
        appConfFile="application.conf"
        self.appOptions = ibmiotf.application.ParseConfigFile(appConfFile)
        
        #Setup logger instance
        self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    
        self.apiClient = ibmiotf.api.ApiClient(self.appOptions,self.logger)
        
    @classmethod    
    def teardown_class(self):
        self.deviceClient=None
        self.managedClient=None
        self.options=None

    @raises(Exception)
    def testMissingOptions(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({})
        assert_equal(e.exception.msg, 'Missing required property: org')
        
    @raises(Exception)
    def testMissingOrg(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({"org": None, "type": self.deviceType, "id": self.deviceId, 
                                   "auth-method": "token", "auth-token": self.authToken })
        assert_equal(e.exception.msg, 'Missing required property: org')

    @raises(Exception)
    def testMissingType(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({"org": self.org, "type": None, "id": self.deviceId, 
                                   "auth-method": "token", "auth-token": self.authToken })
        assert_equal(e.exception.msg, 'Missing required property: type')

    @raises(Exception)
    def testMissingId(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": None, 
                                   "auth-method": "token", "auth-token": self.authToken})
        assert_equal(e.exception.msg, 'Missing required property: id')

    @raises(Exception)
    def testMissingAuthMethod(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId, 
                                   "auth-method": None, "auth-token": self.authToken})
        assert_equal(e.exception.msg, 'Missing required property: auth-method')

    @raises(Exception)
    def testMissingAuthToken(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId, 
                                   "auth-method": "token", "auth-token": None })
        assert_equal(e.exception.msg, 'Missing required property: auth-token')
        
    @raises(Exception)
    def testUnSupportedAuthMethod(self):
        with assert_raises(UnsupportedAuthenticationMethod) as e:
            ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId, 
                                   "auth-method": "unsupported-method", "auth-token": self.authToken})
        assert_equal(e.exception_type,UnsupportedAuthenticationMethod)
        
    def testDeviceClientInstance(self):
        deviceCli = ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId, 
                                           "auth-method": "token", "auth-token": self.authToken})
        assert_is_instance(deviceCli , ibmiotf.device.Client)

    @raises(Exception)
    def testMissingConfigFile(self):
        deviceFile="InvalidFile.out"
        with assert_raises(ConfigurationException) as e:
            ibmiotf.device.ParseConfigFile(deviceFile)
        assert_equal(e.exception.msg, 'Error reading device configuration file')
        
    @raises(Exception)
    def testInvalidConfigFile(self):    
        deviceFile="nullValues.conf"
        with assert_raises(AttributeError) as e:
            ibmiotf.device.ParseConfigFile(deviceFile)
        assert_equal(e.exception, AttributeError)
        
    @SkipTest    
    def testNotAuthorizedConnect(self):
        client = ibmiotf.device.Client({"org": self.org, "type": self.deviceType, "id": self.deviceId, 
                                              "auth-method": "token", "auth-token": "MGhUixxxxxxxxxxxx", "auth-key":"a-xxxxxx-s1tsofmoxo"})
        with assert_raises(ConnectionException) as e:
            client.connect()
        assert_equals(e.exception, ConnectionException)
        assert_equals(e.exception.msg,'Not authorized')
        
    @SkipTest
    def testMissingMessageEncoder(self):
        with assert_raises(MissingMessageEncoderException)as e:
            myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
            self.deviceClient.connect()
            self.deviceClient.publishEvent("missingMsgEncode", "jason", myData)
        assert_equals(e.exception, MissingMessageEncoderException)    
       
    def testPublishEvent(self):
        def devPublishCallback():
            print("Device Publish Event done!!!")
            
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        self.deviceClient.connect()
        assert_true(self.deviceClient.publishEvent("testPublishEvent", "json", myData,on_publish=devPublishCallback,qos=2))
        self.deviceClient.disconnect()   
                
    def testPublishEventOverHTTPs(self):
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        self.deviceClient.connect()
        assert_equals(self.deviceClient.publishEventOverHTTP("testPublishEventHTTPs", myData),200)
        self.deviceClient.disconnect()   
                                        
    def testPublishEventOverHTTP(self):
        client = ibmiotf.device.Client({"org": "quickstart", "type": self.deviceType, "id": self.deviceId,
                                        "auth-method":"None", "auth-token":"None" })
        client.connect()
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(client.publishEventOverHTTP("testPublishEventHTTP", myData),200)
        client.disconnect()
        
    def testDeviceInfoInstance(self):
        deviceInfoObj = ibmiotf.device.DeviceInfo()
        assert_is_instance(deviceInfoObj, ibmiotf.device.DeviceInfo)
        print(deviceInfoObj)     
    
    def testDeviceFirmwareInstance(self):
        deviceFWObj = ibmiotf.device.DeviceFirmware()
        assert_is_instance(deviceFWObj, ibmiotf.device.DeviceFirmware)
        print(deviceFWObj)
        
    def testManagedClientInstance(self):
        managedClient = ibmiotf.device.ManagedClient(self.options)
        assert_is_instance(managedClient, ibmiotf.device.ManagedClient)    
        
    @raises(Exception)
    def testManagedClientQSException(self):
        with assert_raises(Exception)as e:
            options={"org": "quickstart", "type": self.deviceType, "id": self.deviceId,
                                        "auth-method":"None", "auth-token":"None" }
            ibmiotf.device.ManagedClient(options)
        assert_equals(e.exception, Exception)    
    
    def testManagedClientSetMethods(self):
        self.managedClient.connect()
        #Define device properties to be notified whenever reset
        self.managedClient._deviceMgmtObservations = ["deviceInfo.manufacturer", "deviceInfo.descriptiveLocation", 
                                                "deviceInfo.fwVersion", "deviceInfo.model", "deviceInfo.description", 
                                                "deviceInfo.deviceClass", "deviceInfo.hwVersion", "deviceInfo.serialNumber"]
        
        #Reset managedClient properties  and validate the returned is instance of threading.Event
        assert_is_instance(self.managedClient.setErrorCode(1),threading.Event)
        assert_is_instance(self.managedClient.setLocation(longitude=200, latitude=278),threading.Event)   
        assert_is_instance(self.managedClient.setSerialNumber('iot-device-12345'),threading.Event)
        assert_is_instance(self.managedClient.setManufacturer("IBM India Pvt Ltd"),threading.Event)
        assert_is_instance(self.managedClient.setModel("2016"),threading.Event)
        assert_is_instance(self.managedClient.setdeviceClass("Smart Device"),threading.Event)
        assert_is_instance(self.managedClient.setDescription("Sample Smart IoT Device"),threading.Event)
        assert_is_instance(self.managedClient.setFwVersion("1.0"),threading.Event)
        assert_is_instance(self.managedClient.setHwVersion("2.0"),threading.Event)
        assert_is_instance(self.managedClient.setDescriptiveLocation("ISL Lab Bangalore"),threading.Event)
        assert_is_instance(self.managedClient.clearErrorCodes(),threading.Event)       
        assert_is_instance(self.managedClient.addLog(),threading.Event)
        assert_is_instance(self.managedClient.clearLog(),threading.Event)
        assert_is_instance(self.managedClient.unmanage(),threading.Event)
        
        self.managedClient.disconnect()
        
    def testPublishCommandByApplication(self):
        def devCmdCallback(cmd):
            assert_true(cmd.data['rebootDelay'] == 50)
  
        def appCmdPublishCallback():
            print("Application Publish Command done!!!")
  
        self.deviceClient.commandCallback = devCmdCallback;
        self.deviceClient.connect()
        
        appClient = ibmiotf.application.Client(self.appOptions)        
        appClient.connect()
        commandData={'rebootDelay' : 50}
        assert_true(appClient.publishCommand(self.deviceType, self.deviceId, "reboot", "json", commandData, on_publish=appCmdPublishCallback))
        time.sleep(1)   
        
        appClient.disconnect()
        self.deviceClient.disconnect()

    def testDeviceRebootAction(self):
        def rebootActionCB(reqId,action):
            print("Device rebootActionCB called")
                        
        mgmtRequest = {"action": "device/reboot", "parameters": [{"name": "action","value": "reboot" }], 
                       "devices": [{ "typeId": self.deviceType, "deviceId": self.deviceId }]}
        
        #Setup user defined reboot call back
        self.managedClient.deviceActionCallback = rebootActionCB
        self.managedClient.connect()
        
        
        #Initialize device management request to reboot
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        
        time.sleep(1)
        
        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))
        
        self.managedClient.disconnect()
    
    def testDeviceFactoryResetAction(self):
        def factoryResetActionCB(reqId,action):
            print("Device factoryResetActionCB called")
         
        mgmtRequest = {"action": "device/factoryReset", "parameters": [{"name": "action","value": "reset" }], 
                       "devices": [{ "typeId": self.deviceType, "deviceId": self.deviceId }]}
        
        #Setup user defined factory reset call back
        self.managedClient.deviceActionCallback = factoryResetActionCB
        self.managedClient.connect()
                
        #Initialize device management request for factory reset
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        
        time.sleep(1)
        
        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))
        
        self.managedClient.disconnect()
    
    def testFirmwareDownloadAction(self):
        def downloadHandler(client,info):
            try:
                print("Setting ManagedClient.UPDATESTATE_DOWNLOADING") 
                client.setState(device.ManagedClient.UPDATESTATE_DOWNLOADING)
                print("Setting ManagedClient.UPDATESTATE_DOWNLOADED")
                client.setState(device.ManagedClient.UPDATESTATE_DOWNLOADED)
            except Exception :
                print("Exception from downloadHandler")
                    
        def firmwareDownloadActionCB(action,devInfo):
            print("Device firmwareDownloadActionCB called")
            self.managedClient.setState(device.ManagedClient.UPDATESTATE_IDLE)
            print("Calling downloadHandler Thread")
            
            dThread = threading.Thread(target=downloadHandler,args=(self.managedClient,devInfo))
            dThread.start()
            dThread.join()
            print("downloadHandler Thread is done")
                        
            
        mgmtRequest = {"action": "firmware/download", "parameters": [{"name": "version", "value": "0.1.11" },
                       {"name": "name", "value": "RasPi01 firmware"}, {"name": "verifier", "value": "123df"},
                       {"name": "uri","value": "https://github.com/ibm-messaging/iot-raspberrypi/releases/download/1.0.2.1/iot_1.0-2_armhf.deb"}],
                       "devices": [{"typeId": self.deviceType,"deviceId": self.deviceId}]};
                       
        self.managedClient.__firmwareUpdate = device.DeviceFirmware('0.0','0.0','uri','verifier',device.ManagedClient.UPDATESTATE_IDLE,
                                                      device.ManagedClient.UPDATESTATE_IDLE,'updatedDateTime')
                
        #Setup user defined firmware download call back
        self.managedClient.firmwereActionCallback = firmwareDownloadActionCB
        self.managedClient.connect()
        self.managedClient.setState(device.ManagedClient.UPDATESTATE_IDLE)
        self.managedClient.setUpdateStatus(device.ManagedClient.UPDATESTATE_IDLE)
                        
        #Initialize device management request for firmware download
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        time.sleep(1)
        
        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))
      
        self.managedClient.disconnect()
        
    def testFirmwareUpdateAction(self):
        def updateHandler(client,info):
            try:
                print("Setting ManagedClient.UPDATESTATE_IN_PROGRESS") 
                client.setUpdateStatus(device.ManagedClient.UPDATESTATE_IN_PROGRESS)
                print("Setting ManagedClient.UPDATESTATE_SUCCESS")
                threading.Timer(5,client.setUpdateStatus,[device.ManagedClient.UPDATESTATE_SUCCESS]).start()
                
            except Exception :
                print("Exception from updateHandler")
                    
        def firmwareUpdateActionCB(action,devInfo):
            print("Device firmwareUpdateActionCB called")
            self.managedClient.setUpdateStatus(device.ManagedClient.UPDATESTATE_IDLE)
            print("Calling updateHandler Thread")
            
            uThread = threading.Thread(target=updateHandler,args=(self.managedClient,devInfo))
            uThread.start()
            uThread.join()
            print("updateHandler Thread is done")
                        
            
        mgmtRequest = {"action": "firmware/update", "parameters": [{"name": "version", "value": "0.1.11" },
                       {"name": "name", "value": "RasPi01 firmware"}, {"name": "verifier", "value": "123df"},
                       {"name": "uri","value": "https://github.com/ibm-messaging/iot-raspberrypi/releases/download/1.0.2.1/iot_1.0-2_armhf.deb"}],
                       "devices": [{"typeId": self.deviceType,"deviceId": self.deviceId}]};
                       
        self.managedClient.__firmwareUpdate = device.DeviceFirmware('0.0','0.0','uri','verifier',device.ManagedClient.UPDATESTATE_IDLE,
                                                      device.ManagedClient.UPDATESTATE_IDLE,'updatedDateTime')
                
        #Setup user defined firmware download call back
        self.managedClient.firmwereActionCallback = firmwareUpdateActionCB
        self.managedClient.connect()
        self.managedClient.setUpdateStatus(device.ManagedClient.UPDATESTATE_IDLE)
                        
        #Initialize device management request for firmware download
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        time.sleep(1)
        
        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))
      
        self.managedClient.disconnect()        
        