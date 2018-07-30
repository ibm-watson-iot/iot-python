import uuid
from nose.tools import *
from nose import SkipTest

import testUtils
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest
from ibmiotf.api.common import ApiException

class TestRegistryDevices(testUtils.AbstractTest):

    # =========================================================================
    # Bulk operations tests
    # =========================================================================
    def testBulkAddAndDelete(self):
        device1Id = DeviceUid(typeId="test", deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId="test", deviceId=str(uuid.uuid4()))
        
        devicesToRegister = [device1Id, device2Id]
        self.registry.devices.create(devicesToRegister)
        
        myDeviceType = self.registry.devicetypes["test"]
        assert_true(device1Id.deviceId in myDeviceType.devices)
        assert_true(device2Id.deviceId in myDeviceType.devices)
    
        self.registry.devices.delete(devicesToRegister)
        assert_false(device1Id.deviceId in myDeviceType.devices)
        assert_false(device2Id.deviceId in myDeviceType.devices)

    def testBulkDeleteThatDoesntExist(self):
        device1Id = DeviceUid(typeId="test", deviceId=str(uuid.uuid4()))
        device2Id = DeviceUid(typeId="test", deviceId=str(uuid.uuid4()))
        
        myDeviceType = self.registry.devicetypes["test"]
        assert_false(device1Id.deviceId in myDeviceType.devices)
        assert_false(device2Id.deviceId in myDeviceType.devices)
        
        devicesToDelete = [device1Id, device2Id]
        self.registry.devices.delete(devicesToDelete)
        
        assert_false(device1Id.deviceId in myDeviceType.devices)
        assert_false(device2Id.deviceId in myDeviceType.devices)
    
            
    # =========================================================================
    # Device tests
    # =========================================================================
    def testDeviceExistsCheck(self):
        if "d:hldtxx:vm:iot-test-02" in self.registry.devices:
            pass
        else:
            raise Exception()
        
        if "d:hldtxx:vm:iot-test-06" not in self.registry.devices:
            pass
        else:
            raise Exception()

    def testGetDevice(self):
        # Get a device, and cache the response in a local object
        myDevice = self.registry.devices["d:hldtxx:vm:iot-test-02"]
        assert_equals("d:hldtxx:vm:iot-test-02", myDevice.clientId)
        assert_equals("vm", myDevice.typeId)
        assert_equals("iot-test-02", myDevice.deviceId)
        
    
    def testCreateAndUpdate1Device(self):
        deviceUid = DeviceCreateRequest(
            typeId="test", 
            deviceId=str(uuid.uuid4()), 
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2")
        )
        
        self.registry.devices.create(deviceUid)
        
        myDeviceType = self.registry.devicetypes[deviceUid.typeId]        
        assert_true(deviceUid.deviceId in myDeviceType.devices)
        
        deviceAfterCreate = myDeviceType.devices[deviceUid.deviceId]
        assert_equals("123", deviceAfterCreate.deviceInfo.serialNumber)
        assert_equals("Floor 3, Room 2", deviceAfterCreate.deviceInfo.descriptiveLocation)
        
        self.registry.devices.update(deviceUid, metadata={"foo": "bar"})
        
        deviceAfterUpdate = myDeviceType.devices[deviceUid.deviceId]
        assert_true("foo" in deviceAfterUpdate.metadata)
        assert_equals("bar", deviceAfterUpdate.metadata["foo"])
        
        assert_equals(None, deviceAfterUpdate.deviceInfo.description)
        assert_equals(None, deviceAfterUpdate.deviceInfo.model)
        
        # Update description only
        self.registry.devices.update(deviceUid, deviceInfo={"description": "hello"})
        assert_equals("hello", myDeviceType.devices[deviceUid.deviceId].deviceInfo.description)
        
        # Update model, verify that description wasn't wiped
        self.registry.devices.update(deviceUid, deviceInfo=DeviceInfo(model="foobar"))

        deviceAfter3rdUpdate = myDeviceType.devices[deviceUid.deviceId]
        assert_true("foo" in deviceAfter3rdUpdate.metadata)
        assert_equals("bar", deviceAfter3rdUpdate.metadata["foo"])
        assert_equals("hello", deviceAfter3rdUpdate.deviceInfo.description)
        assert_equals("foobar", deviceAfter3rdUpdate.deviceInfo.model)
        assert_equals("Floor 3, Room 2", deviceAfter3rdUpdate.deviceInfo.descriptiveLocation)

        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
    
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