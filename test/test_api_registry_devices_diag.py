import uuid
import time
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
import wiotp.sdk.device
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from wiotp.sdk.api.registry.diag import DeviceLog
from wiotp.sdk.exceptions import ApiException

class TestRegistryDevicesDiag(testUtils.AbstractTest):


    def testDeviceDiagLogs(self, deviceType, device):       
        assert_true(device.deviceId in deviceType.devices)

        # Check it's empty
        assert_equals(0, len(device.diagLogs))
        
        # Create a log 
        device.diagLogs.append(message="hi dave0", data="0", timestamp=datetime.now(), severity=0)
        time.sleep(5)
        assert_equals(1, len(device.diagLogs))
        
        assert_equals("hi dave0", device.diagLogs[0].message)
        assert_equals("0", device.diagLogs[0].data)
        assert_equals(0, device.diagLogs[0].severity)
        
        # Get the id
        logEntry1id = device.diagLogs[0].id
        
        assert_equals("hi dave0", device.diagLogs[logEntry1id].message)
        assert_equals("0", device.diagLogs[logEntry1id].data)
        assert_equals(0, device.diagLogs[logEntry1id].severity)
        
        device.diagLogs.append(DeviceLog(message="hi dave1", data="1", timestamp=datetime.now(), severity=1))
        time.sleep(5)

        assert_equals(2, len(device.diagLogs))
        
        # Logs are in decending order
        assert_equals("hi dave1", device.diagLogs[0].message)
        assert_equals("1", device.diagLogs[0].data)
        assert_equals(1, device.diagLogs[0].severity)

        del device.diagLogs[0]
        time.sleep(5)
        assert_equals(1, len(device.diagLogs))

        device.diagLogs.clear()
        time.sleep(5)
        assert_equals(0, len(device.diagLogs))    
    
    def testDeviceBadDiagLogs(self, deviceType, device):
        assert_true(device.deviceId in deviceType.devices)
                
        # Check it's empty
        assert_equals(0, len(device.diagLogs))
        
        # Create a log with invalid severity
        try:
            device.diagLogs.append(DeviceLog(message="hi dave0", data="0", timestamp=datetime.now(), severity=3))
            # Fail if doesn't raise an exception
            assert_true(False)
        except ApiException as e:
            assert_equals("CUDRS0007E", e.id)
            assert_equals(1, len(e.violations))

