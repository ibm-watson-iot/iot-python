import uuid
from nose.tools import *
from nose import SkipTest

import testUtils

class TestRegistryDevicetypes(testUtils.AbstractTest):
    
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
        # {"classId": "Device", "createdDateTime": "2015-09-17T09:10:27+00:00", "description": "Virtual Machine", "deviceInfo": {}, "id": "vm", "refs": {"logicalInterfaces": "api/v0002/device/types/vm/logicalinterfaces", "mappings": "api/v0002/device/types/vm/mappings", "physicalInterface": "api/v0002/device/types/vm/physicalinterface"}, "updatedDateTime": "2017-02-27T10:27:11.959Z"}
        assert_true(True)
        assert_equals(myDeviceType.id, "vm")
        assert_equals(myDeviceType.classId, "Device")
    
    @raises(Exception)
    def testGetDeviceTypeThatDoesntExist(self):
        self.registry.devicetypes["doesntexist"]

    @raises(Exception)
    def testUnsupportedCreateUpdate(self):
        self.registry.devicetypes["d:hldtxx:vm:iot-test-06"] = {"foo", "bar"}
        
    def testListDeviceTypes(self):
        count = 0
        for type in self.registry.devicetypes:
            count += 1
            if count > 10:
                break
    
    def testCreateDeviceType(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.registry.devicetypes.create( {"id": typeId, "description": "This is a test"} )
        
        myDeviceTypeRetrieved = self.registry.devicetypes[typeId]
        
        assert_equals(myDeviceTypeRetrieved.id, typeId)
        assert_equals(myDeviceTypeRetrieved.description, "This is a test")
        
        del self.registry.devicetypes[typeId]
        
    def testUpdateDeviceType(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.registry.devicetypes.create( {"id": typeId} )
        myDeviceTypeRetrieved = self.registry.devicetypes[typeId]
        
        assert_equals(myDeviceTypeRetrieved.id, typeId)
        assert_equals(myDeviceTypeRetrieved.description, None)

        myUpdatedDeviceType = self.registry.devicetypes.update(typeId, description="This is still a test")
        myUpdatedDeviceTypeRetrieved = self.registry.devicetypes[typeId]
        assert_equals(myUpdatedDeviceTypeRetrieved.description, "This is still a test")
        
        del self.registry.devicetypes[typeId]
    
    def testPartialDeviceTypeUpdate(self):
        typeId = str(uuid.uuid4())
        myDeviceType = self.registry.devicetypes.create( {"id": typeId} )
        myDeviceTypeRetrieved = self.registry.devicetypes[typeId]
        
        assert_equals(myDeviceTypeRetrieved.id, typeId)
        assert_equals(myDeviceTypeRetrieved.description, None)
        
        del self.registry.devicetypes[typeId]
            
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
    
    def testListDevicesFromDeviceType(self):
        # Get a device, and cache the response in a local object
        myDeviceType = self.registry.devicetypes["vm"]
        count = 0
        for device in myDeviceType.devices:
            count += 1
            if count > 10:
                break
    