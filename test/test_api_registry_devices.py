import uuid
from nose.tools import *
from nose import SkipTest

import testUtils
from ibmiotf.api.registry import Registry
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo

class TestRegistryDevices(testUtils.AbstractTest):
    
    @classmethod
    def setup_class(self):
        self.registry = Registry(self.WIOTP_API_KEY, self.WIOTP_API_TOKEN)


    # =========================================================================
    # Bulk operations tests
    # =========================================================================
    def testBulkAddAndDelete(self):
        device1Id = DeviceUid("test", str(uuid.uuid4()))
        device2Id = DeviceUid("test", str(uuid.uuid4()))
        
        devicesToRegister = [device1Id, device2Id]
        self.registry.devices.create(devicesToRegister)
        
        myDeviceType = self.registry.devicetypes["test"]        
        assert_true(device1Id.deviceId in myDeviceType.devices)
        assert_true(device2Id.deviceId in myDeviceType.devices)        
    
        self.registry.devices.delete(devicesToRegister)
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
        print(myDevice.clientId)
        print(myDevice.typeId)
        print(myDevice.deviceId)
        print(myDevice)
    
    def testCreateAndUpdate1Device(self):
        deviceUid = DeviceCreateRequest(
            typeId="test", 
            deviceId=str(uuid.uuid4()), 
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123")
        )
        
        self.registry.devices.create(deviceUid)
        
        myDeviceType = self.registry.devicetypes[deviceUid.typeId]        
        assert_true(deviceUid.deviceId in myDeviceType.devices)
        
        assert_equals("123", myDeviceType.devices[deviceUid.deviceId].deviceInfo.serialNumber)
        
        myDeviceType.devices[deviceUid.deviceId].update(metadata={"foo": "bar"})
        
        assert_true("foo" in myDeviceType.devices[deviceUid.deviceId].metadata)
        assert_equals("bar", myDeviceType.devices[deviceUid.deviceId].metadata["foo"])
        
        assert_equals(None, myDeviceType.devices[deviceUid.deviceId].deviceInfo.description)
        assert_equals(None, myDeviceType.devices[deviceUid.deviceId].deviceInfo.model)
        
        # Update description only
        myDeviceType.devices[deviceUid.deviceId].update(deviceInfo={"description": "hello"})
        assert_equals("hello", myDeviceType.devices[deviceUid.deviceId].deviceInfo.description)
        
        # Update model, verify that description wasn't wiped
        myDeviceType.devices[deviceUid.deviceId].update(deviceInfo=DeviceInfo(model="foobar"))
        assert_equals("hello", myDeviceType.devices[deviceUid.deviceId].deviceInfo.description)
        assert_equals("foobar", myDeviceType.devices[deviceUid.deviceId].deviceInfo.model)
        
        # Cleanup
        assert_true("foo" in myDeviceType.devices[deviceUid.deviceId].metadata)
        assert_equals("bar", myDeviceType.devices[deviceUid.deviceId].metadata["foo"])

        self.registry.devices.delete(devicesToRegister)
        assert_false(deviceUid.deviceId in myDeviceType.devices)
        
    @raises(Exception)
    def testGetDeviceThatDoesntExist(self):
        self.registry.devices["d:hldtxx:vm:iot-test-06"]

    @raises(Exception)
    def testUnsupportedCreateUpdate(self):
        self.registry.devices["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}
        
    def testListDevices(self):
        count = 0
        print("First 10 devices:")
        for device in self.registry.devices:
            print(device.clientId)
            count += 1
            if count > 10:
                break