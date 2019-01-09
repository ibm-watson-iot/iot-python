# *****************************************************************************
# Copyright (c) 2016,2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import wiotp.sdk
import uuid
import os
from nose.tools import *
from nose import SkipTest
import logging
import testUtils

class TestDevice(testUtils.AbstractTest):
    registeredDevice = None
    managedClient = None

    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())

    @classmethod
    def setup_class(self):
        if self.DEVICE_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.registry.devicetypes.create({"id": self.DEVICE_TYPE})

        self.registeredDevice = self.appClient.registry.devices.create({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})

        self.options={
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": self.registeredDevice["typeId"],
                "deviceId": self.registeredDevice["deviceId"]
            },
            "auth" : {
                "token": self.registeredDevice["authToken"]
            }
        }

        #Create default DeviceInfo Instance and associate with ManagedClient Instance
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        deviceInfoObj.fwVersion = 0.0
        self.managedClient = wiotp.sdk.device.ManagedDeviceClient(self.options, deviceInfo=deviceInfoObj)

    @classmethod
    def teardown_class(self):
        del self.managedClient
        del self.appClient.registry.devicetypes[self.DEVICE_TYPE].devices[self.DEVICE_ID]


    def testManagedClientQSException(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            options={
                "identity": {
                    "orgId": "quickstart", 
                    "typeId": self.registeredDevice["typeId"], 
                    "deviceId": self.registeredDevice["deviceId"]
                }
            }
            wiotp.sdk.device.ManagedDeviceClient(options)
        assert_equals("QuickStart does not support device management", e.exception.reason)

    def testManagedClientInstance(self):
        managedClient = wiotp.sdk.device.ManagedDeviceClient(self.options)
        assert_is_instance(managedClient, wiotp.sdk.device.ManagedDeviceClient)

    @SkipTest
    def testManagedClientSetMethods(self):
        self.managedClient.connect()
        #Define device properties to be notified whenever reset
        self.managedClient._deviceMgmtObservations = ["deviceInfo.manufacturer", "deviceInfo.descriptiveLocation",
                                                "deviceInfo.fwVersion", "deviceInfo.model", "deviceInfo.description",
                                                "deviceInfo.deviceClass", "deviceInfo.hwVersion", "deviceInfo.serialNumber"]

        #Reset managedClient properties  and validate the returned is instance of threading.Event
        if sys.version_info[0] < 3:
            assert_is_instance(self.managedClient.setErrorCode(1),threading._Event)
            assert_is_instance(self.managedClient.setLocation(longitude=200, latitude=278),threading._Event)
            assert_is_instance(self.managedClient.setSerialNumber('iot-device-12345'),threading._Event)
            assert_is_instance(self.managedClient.setManufacturer("IBM India Pvt Ltd"),threading._Event)
            assert_is_instance(self.managedClient.setModel("2016"),threading._Event)
            assert_is_instance(self.managedClient.setdeviceClass("Smart Device"),threading._Event)
            assert_is_instance(self.managedClient.setDescription("Sample Smart IoT Device"),threading._Event)
            assert_is_instance(self.managedClient.setFwVersion("1.0"),threading._Event)
            assert_is_instance(self.managedClient.setHwVersion("2.0"),threading._Event)
            assert_is_instance(self.managedClient.setDescriptiveLocation("ISL Lab Bangalore"),threading._Event)
            assert_is_instance(self.managedClient.clearErrorCodes(),threading._Event)
            assert_is_instance(self.managedClient.addLog(),threading._Event)
            assert_is_instance(self.managedClient.clearLog(),threading._Event)
            assert_is_instance(self.managedClient.unmanage(),threading._Event)
        else:
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

    @SkipTest
    def testDeviceRebootAction(self):
        def rebootActionCB(reqId,action):
            print("Device rebootActionCB called")

        mgmtRequest = {"action": "device/reboot", "parameters": [{"name": "action","value": "reboot" }],
                       "devices": [{ "typeId": self.registeredDevice["typeId"], "deviceId": self.registeredDevice["deviceId"] }]}

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

    @SkipTest
    def testDeviceFactoryResetAction(self):
        def factoryResetActionCB(reqId,action):
            print("Device factoryResetActionCB called")

        mgmtRequest = {"action": "device/factoryReset", "parameters": [{"name": "action","value": "reset" }],
                       "devices": [{ "typeId": self.registeredDevice["typeId"], "deviceId": self.registeredDevice["deviceId"] }]}

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

    @SkipTest
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
                       "devices": [{"typeId": self.registeredDevice["typeId"],"deviceId": self.registeredDevice["deviceId"]}]};

        self.managedClient.__firmwareUpdate = wiotp.sdk.device.DeviceFirmware('0.0','0.0','uri','verifier',wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE,
                                                      wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE,'updatedDateTime')

        #Setup user defined firmware download call back
        self.managedClient.firmwereActionCallback = firmwareDownloadActionCB
        self.managedClient.connect()
        self.managedClient.setState(wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE)
        self.managedClient.setUpdateStatus(wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE)

        #Initialize device management request for firmware download
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        time.sleep(1)

        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))

        self.managedClient.disconnect()

    @SkipTest
    def testFirmwareUpdateAction(self):
        def updateHandler(client,info):
            try:
                print("Setting ManagedClient.UPDATESTATE_IN_PROGRESS")
                client.setUpdateStatus(wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IN_PROGRESS)
                print("Setting ManagedClient.UPDATESTATE_SUCCESS")
                threading.Timer(5,client.setUpdateStatus,[wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_SUCCESS]).start()

            except Exception :
                print("Exception from updateHandler")

        def firmwareUpdateActionCB(action,devInfo):
            print("Device firmwareUpdateActionCB called")
            self.managedClient.setUpdateStatus(wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE)
            print("Calling updateHandler Thread")

            uThread = threading.Thread(target=updateHandler,args=(self.managedClient,devInfo))
            uThread.start()
            uThread.join()
            print("updateHandler Thread is done")


        mgmtRequest = {"action": "firmware/update", "parameters": [{"name": "version", "value": "0.1.11" },
                       {"name": "name", "value": "RasPi01 firmware"}, {"name": "verifier", "value": "123df"},
                       {"name": "uri","value": "https://github.com/ibm-messaging/iot-raspberrypi/releases/download/1.0.2.1/iot_1.0-2_armhf.deb"}],
                       "devices": [{"typeId": self.registeredDevice["typeId"],"deviceId": self.registeredDevice["deviceId"]}]};

        self.managedClient.__firmwareUpdate = wiotp.sdk.device.ManagedDeviceClient('0.0','0.0','uri','verifier',wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE,
                                                      wiotp.sdk.device.ManagedDeviceClient.UPDATESTATE_IDLE,'updatedDateTime')

        #Setup user defined firmware download call back
        self.managedClient.firmwereActionCallback = firmwareUpdateActionCB
        self.managedClient.connect()
        self.managedClient.setUpdateStatus(device.ManagedDeviceClient.UPDATESTATE_IDLE)

        #Initialize device management request for firmware download
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']
        time.sleep(1)

        #Delete initiated device management request
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))

        self.managedClient.disconnect()

    @SkipTest
    def testDMEAction(self):
        def doDMEAction(topic,data,reqId):
            print("In DME Action Callabck")
            print("Received topic = "+topic)
            print("Received reqId = "+reqId)
            print("Received data = %s" %data)
            return True

        self.managedClient.connect()

        dmeData1 = {"bundleId": "example-dme-actions-v1",
                   "displayName": {"en_US": "example-dme Actions v1"},
                   "version": "1.0","actions": {"installPlugin": {
                   "actionDisplayName": { "en_US": "Install Plug-in"},
                   "parameters": [ { "name": "pluginURI",
                                     "value": "http://example.dme.com",
                                    "required": "true" } ] } } }
        dmeData2 = {"bundleId": "example-dme-actions-v2",
                   "displayName": {"en_US": "example-dme Actions v2"},
                   "version": "1.0","actions": {"installPlugin": {
                   "actionDisplayName": { "en_US": "Install Plug-in"},
                   "parameters": [ { "name": "pluginURI",
                                     "value": "http://example.dme.com",
                                    "required": "true" } ] } } }
        dmeData3 = {"bundleId": "example-dme-actions-v3",
                   "displayName": {"en_US": "example-dme Actions v3"},
                   "version": "1.0","actions": {"installPlugin": {
                   "actionDisplayName": { "en_US": "Install Plug-in"},
                   "parameters": [ { "name": "pluginURI",
                                     "value": "http://example.dme.com",
                                    "required": "true" } ] } } }

        self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1')
        self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v2')
        self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v3')

        addResult = self.apiClient.createDeviceManagementExtensionPkg(dmeData1)
        assert_equal(addResult['bundleId'],'example-dme-actions-v1')
        addResult = self.apiClient.createDeviceManagementExtensionPkg(dmeData2)
        assert_equal(addResult['bundleId'],'example-dme-actions-v2')
        addResult = self.apiClient.createDeviceManagementExtensionPkg(dmeData3)
        assert_equal(addResult['bundleId'],'example-dme-actions-v3')

        self.managedClient.dmeActionCallback = doDMEAction;
        self.managedClient.manage(lifetime=0,supportDeviceMgmtExtActions=True,
                                        bundleIds=['example-dme-actions-v1',
                                                   'example-dme-actions-v2',
                                                   'example-dme-actions-v3'])
        mgmtRequest = {"action": "example-dme-actions-v1/installPlugin",
                       "parameters": [{ "name": "pluginURI",
                                         "value": "http://example.dme.com",}],
                       "devices": [{ "typeId": self.registeredDevice["typeId"], "deviceId": self.registeredDevice["deviceId"] }]}
        initResult = self.apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']

        assert_true(self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1'))
        assert_true(self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v2'))
        assert_true(self.apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v3'))
        assert_true(self.apiClient.deleteDeviceManagementRequest(reqId))

        self.managedClient.unmanage()
        self.managedClient.disconnect()
