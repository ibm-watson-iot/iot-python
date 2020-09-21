# *****************************************************************************
# Copyright (c) 2016,2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import pytest
import testUtils
import uuid
import os
import wiotp.sdk
import time
from wiotp.sdk.device import ManagedDeviceClient
from wiotp.sdk import Utf8Codec


class TestDeviceMgd(testUtils.AbstractTest):
    def testManagedDeviceQSException(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            options = {"identity": {"orgId": "quickstart", "typeId": "xxx", "deviceId": "xxx"}}
            wiotp.sdk.device.ManagedDeviceClient(options)
        assert "QuickStart does not support device management" == e.value.reason

    def testManagedDeviceConnectException(self, device):
        badOptions = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
        }
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        managedDevice = wiotp.sdk.device.ManagedDeviceClient(badOptions, deviceInfo=deviceInfoObj)
        assert isinstance(managedDevice, wiotp.sdk.device.ManagedDeviceClient)
        with pytest.raises(wiotp.sdk.ConnectionException) as e:
            managedDevice.connect()
        assert managedDevice.isConnected() == False

    def testManagedDeviceConnect(self, device):
        badOptions = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
        }
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        managedDevice = wiotp.sdk.device.ManagedDeviceClient(badOptions, deviceInfo=deviceInfoObj)
        assert isinstance(managedDevice, wiotp.sdk.device.ManagedDeviceClient)
        managedDevice.connect()
        assert managedDevice.isConnected() == True
        managedDevice.disconnect()
        assert managedDevice.isConnected() == False

    def testManagedDeviceSetPropertyNameNone(self):
        with pytest.raises(Exception) as e:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            managedDeviceClientValue.setProperty(value=1)
            assert "Unsupported property name: " in str(e.value)

    def testManagedDeviceSetPropertyValue(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            testName = "model"
            testValue = 2
            test = managedDeviceClientValue.setProperty(name=testName, value=testValue)
            assert managedDeviceClientValue._deviceInfo[testName] == testValue
        except:
            assert False == True

    # TO DO Rest of SetProperty and Notifyfieldchange (onSubscribe put variables)
    # Code in comments hangs when running but improves percentage
    # Look into later
    #    def testManagedDeviceManageOnSubscribe(self):
    #        try:
    #            config = {
    #                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
    #                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
    #            }
    #            managedDeviceClientValue = ManagedDeviceClient(config)
    #            test = managedDeviceClientValue._onSubscribe(mqttc=1, userdata=2, mid=3, granted_qos=4)
    #            assert True
    #        except:
    #            assert False == True

    def testManagedDeviceManageLifetimeValueZero(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.manage(lifetime=3000)
            assert True
        except:
            assert False == True

    def testManagedDeviceUnManage(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.unmanage()
            assert True
        except:
            assert False == True

    def testManagedDeviceSetLocationLongitude(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setLocation(longitude=1, latitude=2)
            assert managedDeviceClientValue._location["longitude"] == 1
        except:
            assert False == True

    def testManagedDeviceSetLocationLatitude(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setLocation(longitude=1, latitude=2)
            assert managedDeviceClientValue._location["latitude"] == 2
        except:
            assert False == True

    def testManagedDeviceSetLocationElevation(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setLocation(longitude=1, latitude=2, elevation=3)
            assert managedDeviceClientValue._location["elevation"] == 3
        except:
            assert False == True

    def testManagedDeviceSetLocationAccuracy(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setLocation(longitude=1, latitude=2, elevation=3, accuracy=4)
            assert managedDeviceClientValue._location["accuracy"] == 4
        except:
            assert False == True

    def testManagedDeviceSetErrorCodeNone(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setErrorCode(errorCode=None)
            assert managedDeviceClientValue._errorCode == 0
        except:
            assert False == True

    def testManagedDeviceSetErrorCode(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setErrorCode(errorCode=15)
            assert True
        except:
            assert False == True

    def testManagedDeviceClearErrorCodes(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.clearErrorCodes()
            assert managedDeviceClientValue._errorCode == None
        except:
            assert False == True

    def testManagedDeviceAddLog(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.addLog(msg="h", data="e")
            assert True
        except:
            assert False == True

    def testManagedDeviceClearLog(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.clearLog()
            assert True
        except:
            assert False == True

    def testManagedDeviceRespondDeviceAction(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.respondDeviceAction(reqId=1)
            assert True
        except:
            assert False == True

    # Do line 337 - 571
    def testManagedDeviceSetState(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setState(status=1)
            assert True
        except:
            assert False == True

    def testManagedDeviceSetUpdateStatus(self):
        try:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDeviceClientValue = ManagedDeviceClient(config)
            test = managedDeviceClientValue.setUpdateStatus(status=1)
        except:
            assert False == True

    # Use template for rest __functions

    def testManagedDeviceMgmtResponseError(self):
        with pytest.raises(Exception) as e:
            config = {
                "identity": {"orgId": "1", "typeId": "xxx", "deviceId": "xxx"},
                "auth": {"token": "xxxxxxxxxxxxxxxxxx"},
            }
            managedDevice = ManagedDeviceClient(config)
            testValue = "Test"
            encodedPayload = Utf8Codec.encode(testValue)
            managedDevice._ManagedDeviceClient__onDeviceMgmtResponse(client=1, userdata=2, pahoMessage=encodedPayload)
            assert "Unable to parse JSON. payload=" " error" in str(e.value)
