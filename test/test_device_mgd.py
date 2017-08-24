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
import uuid
import os
from ibmiotf import *
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
        try:
            deviceType = self.setupAppClient.api.getDeviceType(self.DEVICE_TYPE)
        except APIException as e:
            if e.httpCode == 404:
                deviceType = self.setupAppClient.api.addDeviceType(self.DEVICE_TYPE)
            else:
                raise e

        self.registeredDevice = self.setupAppClient.api.registerDevice(self.DEVICE_TYPE, self.DEVICE_ID)

        self.options={
            "org": self.ORG_ID,
            "type": self.registeredDevice["typeId"],
            "id": self.registeredDevice["deviceId"],
            "auth-method": "token",
            "auth-token": self.registeredDevice["authToken"]
        }

        #Create default DeviceInfo Instance and associate with ManagedClient Instance
        deviceInfoObj = ibmiotf.device.DeviceInfo()
        deviceInfoObj.fwVersion = 0.0
        self.managedClient = ibmiotf.device.ManagedClient(self.options, deviceInfo=deviceInfoObj)

    @classmethod
    def teardown_class(self):
        del self.managedClient
        self.setupAppClient.api.deleteDevice(self.DEVICE_TYPE, self.DEVICE_ID)


    @raises(Exception)
    def testManagedClientQSException(self):
        with assert_raises(Exception)as e:
            options={"org": "quickstart", "type": self.registeredDevice["typeId"], "id": self.registeredDevice["deviceId"],
                                        "auth-method":"None", "auth-token":"None" }
            ibmiotf.device.ManagedClient(options)
        assert_equals(e.exception, Exception)

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

    @SkipTest
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
                       "devices": [{"typeId": self.registeredDevice["typeId"],"deviceId": self.registeredDevice["deviceId"]}]};

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
