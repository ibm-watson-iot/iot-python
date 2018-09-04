import uuid
import time
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
import ibmiotf.device
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from ibmiotf.api.registry.diag import DeviceLog, DeviceErrorCode
from ibmiotf.api.common import ApiException, DateTimeEncoder

class TestRegistryDevicesDiagEc(testUtils.AbstractTest):


    def testDeviceDiagEc(self):
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

        # Check it's empty
        assert_equals(0, len(deviceAfterCreate.diagErrorCodes))
        
        # Create a log 
        deviceAfterCreate.diagErrorCodes.append(errorCode=0, timestamp=datetime.now())
        time.sleep(10)
        
        assert_equals(1, len(deviceAfterCreate.diagErrorCodes))
        assert_equals(0, deviceAfterCreate.diagErrorCodes[0].errorCode)
        
        deviceAfterCreate.diagErrorCodes.append(DeviceErrorCode(errorCode=99, timestamp=datetime.now()))
        time.sleep(10)
        
        assert_equals(2, len(deviceAfterCreate.diagErrorCodes))
        assert_equals(99, deviceAfterCreate.diagErrorCodes[0].errorCode)
        assert_equals(0, deviceAfterCreate.diagErrorCodes[1].errorCode)

        deviceAfterCreate.diagErrorCodes.clear()
        time.sleep(10)
        assert_equals(0, len(deviceAfterCreate.diagErrorCodes))
                
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
    