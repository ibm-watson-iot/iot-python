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
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            options={
                "identity": {
                    "orgId": "quickstart", 
                    "typeId": self.registeredDevice["typeId"], 
                    "deviceId": self.registeredDevice["deviceId"]
                }
            }
            wiotp.sdk.device.ManagedDeviceClient(options)
            assert "QuickStart does not support device management" == e.value.reason

    def testManagedClientInstance(self):
        managedClient = wiotp.sdk.device.ManagedDeviceClient(self.options)
        assert isinstance(managedClient, wiotp.sdk.device.ManagedDeviceClient)
