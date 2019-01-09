import uuid
import time
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
import wiotp.sdk.device
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from wiotp.sdk.exceptions import ApiException

class TestRegistryDevices(testUtils.AbstractTest):


    def testDeviceLocationGetAndUpdate(self, deviceType, device):   
        assert_true(device.deviceId in deviceType.devices)

        locationBefore = device.getLocation()
        assert_equals(None, locationBefore)
           
        device.setLocation({"latitude": 50, "longitude": 60})
        locationAfter = device.getLocation()        
        
        assert_not_equal(None, locationAfter.updatedDateTime)
        assert_not_equal(None, locationAfter.measuredDateTime)
        
        assert_true(isinstance(locationAfter.updatedDateTime, datetime))
        assert_true(isinstance(locationAfter.measuredDateTime, datetime))
        
        assert_equals(50, locationAfter.latitude)
        assert_equals(60, locationAfter.longitude)

        device.setLocation(DeviceLocation(latitude=80, longitude=75))
        locationAfter = device.getLocation()        
        assert_equals(80, locationAfter.latitude)
        assert_equals(75, locationAfter.longitude)

    def testDeviceLocationInvalid(self, deviceType, device):
        assert_true(device.deviceId in deviceType.devices)

        locationBefore = device.getLocation()
        assert_equals(None, locationBefore)
           
        try:
            device.setLocation(DeviceLocation(latitude=100, longitude=120))
        except ApiException as e:
            assert_equals("CUDRS0007E", e.id)
            assert_true(len(e.violations) == 1)

    
    def testDeviceMgmt(self, deviceType, device):
        assert_true(device.deviceId in deviceType.devices)
        mgmtInfo = device.getMgmt()
        assert_equals(None, mgmtInfo)

    def testDeviceConnectionLogs(self, deviceType, device, authToken):
        assert_true(device.deviceId in deviceType.devices)
                
        options={
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": device.typeId,
                "deviceId": device.deviceId
            },
            "auth": {
                "token": authToken
            }
        }
        
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        time.sleep(10)
        deviceClient.disconnect()
        # Allow 30 seconds for the logs to make it through
        time.sleep(30)

        connLogs= device.getConnectionLogs()
        
        # There may be more than 2 entries due to previous connection attempts if we re-used a device ID.  But there should be at least two!
        assert_true(len(connLogs) >= 2)
        for entry in connLogs:
            assert_true(isinstance(entry, LogEntry))
            assert_true(isinstance(entry.timestamp, datetime))
        
