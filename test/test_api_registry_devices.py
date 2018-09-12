import uuid
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation
from ibmiotf.api.common import ApiException

class TestRegistryDevices(testUtils.AbstractTest):

    # =========================================================================
    # Bulk operations tests
    # =========================================================================
    def testBulkAddAndDelete(self, deviceType):
        device1Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        
        devicesToRegister = [device1Id, device2Id]
        self.registry.devices.create(devicesToRegister)
        
        assert_true(device1Id.deviceId in deviceType.devices)
        assert_true(device2Id.deviceId in deviceType.devices)
    
        self.registry.devices.delete(devicesToRegister)
        assert_false(device1Id.deviceId in deviceType.devices)
        assert_false(device2Id.deviceId in deviceType.devices)

    def testBulkDeleteThatDoesntExist(self, deviceType):
        device1Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId=deviceType.id, deviceId=str(uuid.uuid4()))
        
        assert_false(device1Id.deviceId in deviceType.devices)
        assert_false(device2Id.deviceId in deviceType.devices)
        
        devicesToDelete = [device1Id, device2Id]
        self.registry.devices.delete(devicesToDelete)
        
        assert_false(device1Id.deviceId in deviceType.devices)
        assert_false(device2Id.deviceId in deviceType.devices)
            
    # =========================================================================
    # Device tests
    # =========================================================================
    def testDeviceExistsCheck(self, device):
        if device.clientId in self.registry.devices:
            pass
        else:
            raise Exception()

    def testGetDevice(self, device):
        # Get a device, and cache the response in a local object
        retrievedDevice = self.registry.devices[device.clientId]
        assert_equals(retrievedDevice.clientId, device.clientId)
        assert_equals(retrievedDevice.typeId, device.typeId)
        assert_equals(retrievedDevice.deviceId, device.deviceId)
        
    
    def testCreateAndUpdate1Device(self, deviceType):
        deviceUid = DeviceCreateRequest(
            typeId=deviceType.id, 
            deviceId=str(uuid.uuid4()), 
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2")
        )
        
        self.registry.devices.create(deviceUid)
             
        assert_true(deviceUid.deviceId in deviceType.devices)
        
        deviceAfterCreate = deviceType.devices[deviceUid.deviceId]
        assert_equals("123", deviceAfterCreate.deviceInfo.serialNumber)
        assert_equals("Floor 3, Room 2", deviceAfterCreate.deviceInfo.descriptiveLocation)
        
        self.registry.devices.update(deviceUid, metadata={"foo": "bar"})
        
        deviceAfterUpdate = deviceType.devices[deviceUid.deviceId]
        assert_true("foo" in deviceAfterUpdate.metadata)
        assert_equals("bar", deviceAfterUpdate.metadata["foo"])
        
        assert_equals(None, deviceAfterUpdate.deviceInfo.description)
        assert_equals(None, deviceAfterUpdate.deviceInfo.model)
        
        # Update description only
        self.registry.devices.update(deviceUid, deviceInfo={"description": "hello"})
        assert_equals("hello", deviceType.devices[deviceUid.deviceId].deviceInfo.description)
        
        # Update model, verify that description wasn't wiped
        self.registry.devices.update(deviceUid, deviceInfo=DeviceInfo(model="foobar"))

        deviceAfter3rdUpdate = deviceType.devices[deviceUid.deviceId]
        assert_true("foo" in deviceAfter3rdUpdate.metadata)
        assert_equals("bar", deviceAfter3rdUpdate.metadata["foo"])
        assert_equals("hello", deviceAfter3rdUpdate.deviceInfo.description)
        assert_equals("foobar", deviceAfter3rdUpdate.deviceInfo.model)
        assert_equals("Floor 3, Room 2", deviceAfter3rdUpdate.deviceInfo.descriptiveLocation)

        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in deviceType.devices)
    
    @raises(KeyError)
    def testGetDeviceThatDoesntExist(self):
        self.registry.devices["d:hldtxx:vm:iot-test-06"]

    @raises(KeyError)
    def testDeleteDeviceThatDoesntExist(self):
        del self.registry.devices["d:hldtxx:vm:iot-test-06"]
        
    @raises(Exception)
    def testUnsupportedCreateUpdate(self):
        self.registry.devices["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}

    def testUpdateDeviceThatDoesntExistUsingDictInsteadOfDeviceUidObject(self):
        id = str(uuid.uuid4())
        try:
            self.registry.devices.update({"typeId": "test", "deviceId": id}, metadata={"foo": "bar"})
        except ApiException as e:
            assert_equals(404, e.response.status_code) 
            
    def testListDevices(self):
        count = 0
        #print("First 10 devices:")
        for device in self.registry.devices:
            #print(device.clientId)
            count += 1
            if count > 10:
                break