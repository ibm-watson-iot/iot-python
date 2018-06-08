import uuid
from nose.tools import *
from nose import SkipTest

import testUtils
from ibmiotf.api.registry import Registry
from ibmiotf.api.registry.devices import DeviceUid

class TestRegistryDevicetypes(testUtils.AbstractTest):
    
    @classmethod
    def setup_class(self):
        self.registry = Registry(self.WIOTP_API_KEY, self.WIOTP_API_TOKEN)


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
    