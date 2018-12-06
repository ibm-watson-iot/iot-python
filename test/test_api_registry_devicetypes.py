import uuid
from nose.tools import *
from nose import SkipTest

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
        assert_equals(retrievedDeviceType.id, deviceType.id)
        assert_equals(retrievedDeviceType.classId, "Device")
    
    @raises(Exception)
    def testGetDeviceTypeThatDoesntExist(self):
        self.appClient.registry.devicetypes["doesntexist"]

    @raises(Exception)
    def testUnsupportedCreateUpdate(self):
        self.appClient.registry.devicetypes["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}
        
    def testListDeviceTypes(self, deviceType):
        count = 0
        for type in self.appClient.registry.devicetypes:
            count += 1
            if count > 10:
                break
    
    def testCreateDeviceType(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.appClient.registry.devicetypes.create( {"id": typeId, "description": "This is a test"} )
        
        myDeviceTypeRetrieved = self.appClient.registry.devicetypes[typeId]
        
        assert_equals(myDeviceTypeRetrieved.id, typeId)
        assert_equals(myDeviceTypeRetrieved.description, "This is a test")
        
        del self.appClient.registry.devicetypes[typeId]
        
    def testUpdateDeviceType(self, deviceType):
        self.appClient.registry.devicetypes.update(deviceType.id, description="This is still a test")
        updatedDeviceType = self.appClient.registry.devicetypes[deviceType.id]
        assert_equals(updatedDeviceType.description, "This is still a test")
            
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
    