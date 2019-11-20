# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
from datetime import datetime
import pytest
import testUtils
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation
from wiotp.sdk.exceptions import ApiException


class TestRegistryDevices(testUtils.AbstractTest):

    # =========================================================================
    # Bulk operations tests
    # =========================================================================
    def testBulkAddAndDelete(self, deviceType):
        device1Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))

        devicesToRegister = [device1Id, device2Id]
        self.appClient.registry.devices.create(devicesToRegister)

        assert str(device1Id) == device1Id.typeId + ":" + device1Id.deviceId

        assert device1Id.deviceId in deviceType.devices
        assert device2Id.deviceId in deviceType.devices

        self.appClient.registry.devices.delete(devicesToRegister)
        assert device1Id.deviceId not in deviceType.devices
        assert device2Id.deviceId not in deviceType.devices

    def testBulkDeleteThatDoesntExist(self, deviceType):
        device1Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))

        assert device1Id.deviceId not in deviceType.devices
        assert device2Id.deviceId not in deviceType.devices

        devicesToDelete = [device1Id, device2Id]
        self.appClient.registry.devices.delete(devicesToDelete)

        assert device1Id.deviceId not in deviceType.devices
        assert device2Id.deviceId not in deviceType.devices

    # =========================================================================
    # Device tests
    # =========================================================================
    def testDeviceExistsCheck(self, device):
        if device.clientId in self.appClient.registry.devices:
            pass
        else:
            raise Exception()

    def testGetDevice(self, device):
        # Get a device, and cache the response in a local object
        retrievedDevice = self.appClient.registry.devices[device.clientId]
        assert retrievedDevice.clientId == device.clientId
        assert retrievedDevice.typeId == device.typeId
        assert retrievedDevice.deviceId == device.deviceId

    def testCreateAndUpdate1Device(self, deviceType):
        deviceUid = DeviceCreateRequest(
            typeId=deviceType.id,
            deviceId=str(uuid.uuid4()),
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2"),
        )

        assert deviceUid.authToken == "NotVerySecretPassw0rd"
        assert deviceUid.location is None
        assert deviceUid.metadata is None

        deviceCreateResponse = self.appClient.registry.devices.create(deviceUid)

        assert deviceCreateResponse.typeId == deviceUid.typeId
        assert deviceCreateResponse.deviceId == deviceUid.deviceId
        assert deviceCreateResponse.success == True
        assert deviceCreateResponse.authToken == deviceUid.authToken

        assert deviceUid.deviceId in deviceType.devices

        deviceAfterCreate = deviceType.devices[deviceUid.deviceId]
        assert deviceAfterCreate.deviceInfo.serialNumber == "123"
        assert deviceAfterCreate.deviceInfo.descriptiveLocation == "Floor 3, Room 2"

        self.appClient.registry.devices.update(deviceUid, metadata={"foo": "bar"})

        deviceAfterUpdate = deviceType.devices[deviceUid.deviceId]
        assert "foo" in deviceAfterUpdate.metadata
        assert deviceAfterUpdate.metadata["foo"] == "bar"

        assert deviceAfterUpdate.deviceInfo.description is None
        assert deviceAfterUpdate.deviceInfo.model is None

        # Update description only
        self.appClient.registry.devices.update(deviceUid, deviceInfo={"description": "hello"})
        assert deviceType.devices[deviceUid.deviceId].deviceInfo.description == "hello"

        # Update model, verify that description wasn't wiped
        self.appClient.registry.devices.update(deviceUid, deviceInfo=DeviceInfo(model="foobar"))

        deviceAfter3rdUpdate = deviceType.devices[deviceUid.deviceId]
        assert "foo" in deviceAfter3rdUpdate.metadata
        assert deviceAfter3rdUpdate.metadata["foo"] == "bar"
        assert deviceAfter3rdUpdate.deviceInfo.description == "hello"
        assert deviceAfter3rdUpdate.deviceInfo.model == "foobar"
        assert deviceAfter3rdUpdate.deviceInfo.descriptiveLocation == "Floor 3, Room 2"
        assert deviceAfter3rdUpdate.deviceInfo.deviceClass == None
        assert deviceAfter3rdUpdate.deviceInfo.fwVersion == None
        assert deviceAfter3rdUpdate.deviceInfo.hwVersion == None
        assert deviceAfter3rdUpdate.deviceInfo.manufacturer == None

        assert str(deviceAfter3rdUpdate) == "[%s] hello" % (deviceAfter3rdUpdate.clientId)

        # Cleanup
        self.appClient.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert deviceUid.deviceId not in deviceType.devices

    def testGetDeviceThatDoesntExist(self):
        with pytest.raises(KeyError):
            self.appClient.registry.devices["d:hldtxx:vm:iot-test-06"]

    def testDeleteDevice(self, deviceType):
        deviceUid = DeviceCreateRequest(
            typeId=deviceType.id,
            deviceId=str(uuid.uuid4()),
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2"),
        )

        assert deviceUid.authToken == "NotVerySecretPassw0rd"
        assert deviceUid.location is None
        assert deviceUid.metadata is None

        deviceCreateResponse = self.appClient.registry.devices.create(deviceUid)

        assert deviceCreateResponse.typeId == deviceUid.typeId
        assert deviceCreateResponse.deviceId == deviceUid.deviceId
        assert deviceCreateResponse.success == True
        assert deviceCreateResponse.authToken == deviceUid.authToken

        assert deviceUid.deviceId in deviceType.devices

        del self.appClient.registry.devicetypes[deviceUid.typeId].devices[deviceUid.deviceId]
        assert deviceUid.deviceId not in deviceType.devices

    def testDeleteDeviceThatDoesntExist(self):
        with pytest.raises(KeyError):
            del self.appClient.registry.devices["d:hldtxx:vm:iot-test-06"]

    def testUnsupportedCreateUpdate(self):
        with pytest.raises(Exception):
            self.appClient.registry.devices["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}

    def testUpdateDeviceThatDoesntExistUsingDictInsteadOfDeviceUidObject(self):
        id = str(uuid.uuid4())
        try:
            self.appClient.registry.devices.update({"typeId": "test", "deviceId": id}, metadata={"foo": "bar"})
        except ApiException as e:
            assert e.response.status_code == 404

    def testListDevices(self):
        count = 0
        # print("First 10 devices:")
        for device in self.appClient.registry.devices:
            # print(device.clientId)
            count += 1
            if count > 10:
                break
