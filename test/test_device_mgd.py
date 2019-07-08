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
