# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import pytest
import testUtils


class TestRegistryDevicetypes(testUtils.AbstractTest):

    # =========================================================================
    # Device Type tests
    # =========================================================================
    def testDeviceTypeExistsCheck(self, deviceType):
        if deviceType.id in self.appClient.registry.devicetypes:
            pass
        else:
            raise Exception()

        if "doesntexist" not in self.appClient.registry.devicetypes:
            pass
        else:
            raise Exception()

    def testGetDeviceType(self, deviceType):
        retrievedDeviceType = self.appClient.registry.devicetypes[deviceType.id]
        assert retrievedDeviceType.id == deviceType.id
        assert retrievedDeviceType.classId == "Device"

    def testGetDeviceTypeThatDoesntExist(self):
        with pytest.raises(Exception):
            self.appClient.registry.devicetypes["doesntexist"]

    def testUnsupportedCreateUpdate(self):
        with pytest.raises(Exception):
            self.appClient.registry.devicetypes["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}

    def testListDeviceTypes(self, deviceType):
        count = 0
        for type in self.appClient.registry.devicetypes:
            count += 1
            if count > 10:
                break

    def testCreateDeviceType(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create({"id": typeId, "description": "This is a test"})

        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]

        assert myDeviceTypeRetrieved.id == typeId
        assert myDeviceTypeRetrieved.description == "This is a test"

        del self.appClient.registry.devicetypes[typeId]

    def testUpdateDeviceType(self, deviceType):
        self.appClient.registry.devicetypes.update(deviceType.id, description="This is still a test")
        updatedDeviceType = self.appClient.registry.devicetypes[deviceType.id]
        assert updatedDeviceType.description == "This is still a test"

    # =========================================================================
    # Device under DeviceType tests
    # =========================================================================
    def testDeviceExistsCheck(self, deviceType, device):
        if device.deviceId in deviceType.devices:
            pass
        else:
            raise Exception()

        if "wheredidyago" not in deviceType.devices:
            pass
        else:
            raise Exception()

    def testGetDeviceFromDeviceType(self, deviceType, device):
        myDevice = self.appClient.registry.devicetypes[deviceType.id].devices[device.deviceId]

    def testListDevicesFromDeviceType(self, deviceType, device):
        # Get a device, and cache the response in a local object
        count = 0
        for device in deviceType.devices:
            count += 1
            if count > 10:
                break
