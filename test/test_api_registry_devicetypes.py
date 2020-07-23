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
from wiotp.sdk.api.registry.devices import DeviceInfo
from wiotp.sdk.exceptions import ApiException


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

    # DeviceTypeDescription test
    def testCreateDeviceType(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create({"id": typeId, "description": "This is a test"})

        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]

        assert myDeviceTypeRetrieved.id == typeId
        assert myDeviceTypeRetrieved.description == "This is a test"

        del self.appClient.registry.devicetypes[typeId]

    def testCreateDeviceTypeNone(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create({"id": typeId, "description": None})

        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]

        assert myDeviceTypeRetrieved.id == typeId
        assert myDeviceTypeRetrieved.description == None

        del self.appClient.registry.devicetypes[typeId]

    # Metadata test
    def testCreateDeviceMetadata(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create(
            {"id": typeId, "description": "This is still a test", "metadata": {"test": "test"}}
        )

        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]

        assert myDeviceTypeRetrieved.id == typeId
        assert myDeviceTypeRetrieved.description == "This is still a test"
        assert myDeviceTypeRetrieved.metadata == {"test": "test"}

        del self.appClient.registry.devicetypes[typeId]

    def testCreateDeviceMetadataNone(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create(
            {"id": typeId, "description": "This is still a test", "metadata": None}
        )

        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]

        assert myDeviceTypeRetrieved.id == typeId
        assert myDeviceTypeRetrieved.description == "This is still a test"
        assert myDeviceTypeRetrieved.metadata == None

        del self.appClient.registry.devicetypes[typeId]

    def testUpdateDeviceType(self, deviceType):
        self.appClient.registry.devicetypes.update(deviceType.id, description="This is still a test")
        updatedDeviceType = self.appClient.registry.devicetypes[deviceType.id]

        assert updatedDeviceType.description == "This is still a test"

    def testUpdateDeviceInfo(self, deviceType):
        self.appClient.registry.devicetypes.update(deviceType.id, deviceInfo=DeviceInfo(serialNumber="111"))
        updatedDeviceType = self.appClient.registry.devicetypes[deviceType.id]

        assert updatedDeviceType.deviceInfo.serialNumber == "111"

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

    def testCreateDeviceType(self):
        with pytest.raises(ApiException):
            typeId = 1
            r = self.appClient.registry.devicetypes.create(typeId)

    def testUpdateDeviceType(self):
        with pytest.raises(ApiException):
            data = None
            r = self.appClient.registry.devicetypes.update(data)

    def testDeleteTypeId(self, device, deviceType):
        typeId = str(uuid.uuid4())
        self.appClient.registry.devicetypes.create(
            {"id": typeId, "description": "This is still a test", "metadata": {"test": "test"}}
        )
        self.appClient.registry.devicetypes.delete(typeId)
        assert typeId not in deviceType.devices