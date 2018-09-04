import uuid
import time
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
import ibmiotf.device
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from ibmiotf.api.registry.diag import DeviceLog
from ibmiotf.api.common import ApiException, DateTimeEncoder

class TestRegistryDevicesDiag(testUtils.AbstractTest):


    def testDeviceDiagLogs(self):
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
        assert_equals(0, len(deviceAfterCreate.diagLogs))
        
        # Create a log 
        deviceAfterCreate.diagLogs.append(message="hi dave0", data="0", timestamp=datetime.now(), severity=0)
        time.sleep(5)
        assert_equals(1, len(deviceAfterCreate.diagLogs))
        
        assert_equals("hi dave0", deviceAfterCreate.diagLogs[0].message)
        assert_equals("0", deviceAfterCreate.diagLogs[0].data)
        assert_equals(0, deviceAfterCreate.diagLogs[0].severity)
        
        # Get the id
        logEntry1id = deviceAfterCreate.diagLogs[0].id
        
        assert_equals("hi dave0", deviceAfterCreate.diagLogs[logEntry1id].message)
        assert_equals("0", deviceAfterCreate.diagLogs[logEntry1id].data)
        assert_equals(0, deviceAfterCreate.diagLogs[logEntry1id].severity)
        
        deviceAfterCreate.diagLogs.append(DeviceLog(message="hi dave1", data="1", timestamp=datetime.now(), severity=1))
        time.sleep(5)

        assert_equals(2, len(deviceAfterCreate.diagLogs))
        
        # Logs are in decending order
        assert_equals("hi dave1", deviceAfterCreate.diagLogs[0].message)
        assert_equals("1", deviceAfterCreate.diagLogs[0].data)
        assert_equals(1, deviceAfterCreate.diagLogs[0].severity)

        del deviceAfterCreate.diagLogs[0]
        time.sleep(5)
        assert_equals(1, len(deviceAfterCreate.diagLogs))

        deviceAfterCreate.diagLogs.clear()
        time.sleep(5)
        assert_equals(0, len(deviceAfterCreate.diagLogs))
                
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
    
    
    def testDeviceBadDiagLogs(self):
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
        assert_equals(0, len(deviceAfterCreate.diagLogs))
        
        # Create a log with invalid severity
        try:
            deviceAfterCreate.diagLogs.append(DeviceLog(message="hi dave0", data="0", timestamp=datetime.now(), severity=3))
            # Fail if doesn't raise an exception
            assert_true(False)
        except ApiException as e:
            assert_equals("CUDRS0007E", e.id)
            assert_equals(1, len(e.violations))
                            
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
