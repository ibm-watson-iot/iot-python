import uuid
from nose.tools import *
from nose import SkipTest

import testUtils
from ibmiotf.api.registry import Registry
from ibmiotf.api.registry.devices import DeviceUid

class TestDevice(testUtils.AbstractTest):
    
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
    # Device Type tests
    # =========================================================================
    def testDeviceTypeExistsCheck(self):
        if "vm" in self.registry.devicetypes:
            pass
        else:
            raise Exception()
        
        if "doesntexist" not in self.registry.devicetypes:
            pass
        else:
            raise Exception()
        
    def testGetDeviceType(self):
        # Get a device, and cache the response in a local object
        myDeviceType = self.registry.devicetypes["vm"]
        print(myDeviceType.id)
        print(myDeviceType.classId)
        print(myDeviceType)
    
    @raises(Exception)
    def testGetDeviceTypeThatDoesntExist(self):
        self.registry.devicetypes["doesntexist"]

    @raises(Exception)
    def testUnsupportedCreateUpdate(self):
        self.registry.devicetypes["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}
        
    def testListDeviceTypes(self):
        count = 0
        print("First 10 types:")
        for type in self.registry.devicetypes:
            print("%s %s" % (type.id, type.classId))
            count += 1
            if count > 10:
                break    
            
    # =========================================================================
    # Device under DeviceType tests
    # =========================================================================
    def testDeviceExistsCheck(self):
        myDeviceType = self.registry.devicetypes["vm"]
        if "iot-test-02" in myDeviceType.devices:
            pass
        else:
            raise Exception()
        
        if "iot-test-06" not in myDeviceType.devices:
            pass
        else:
            raise Exception()

    def testGetDeviceFromDeviceType(self):
        # Get a device, and cache the response in a local object
        myDevice = self.registry.devicetypes["vm"].devices["iot-test-02"]
        print(myDevice.clientId)
        print(myDevice.typeId)
        print(myDevice.deviceId)
        print(myDevice)
    
    def testListDevicesFromDeviceType(self):
        # Get a device, and cache the response in a local object
        myDeviceType = self.registry.devicetypes["vm"]
        count = 0
        for device in myDeviceType.devices:
            print(device.clientId)
            count += 1
            if count > 10:
                break
    
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