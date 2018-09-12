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


    def testDeviceDiagEc(self, deviceType, device):
        assert_true(device.deviceId in deviceType.devices)

        # Check it's empty
        assert_equals(0, len(device.diagErrorCodes))
        
        # Create a log 
        device.diagErrorCodes.append(errorCode=0, timestamp=datetime.now())
        time.sleep(10)
        
        assert_equals(1, len(device.diagErrorCodes))
        assert_equals(0, device.diagErrorCodes[0].errorCode)
        
        device.diagErrorCodes.append(DeviceErrorCode(errorCode=99, timestamp=datetime.now()))
        time.sleep(10)
        
        assert_equals(2, len(device.diagErrorCodes))
        assert_equals(99, device.diagErrorCodes[0].errorCode)
        assert_equals(0, device.diagErrorCodes[1].errorCode)

        device.diagErrorCodes.clear()
        time.sleep(10)
        assert_equals(0, len(device.diagErrorCodes))
  
    