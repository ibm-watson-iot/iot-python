import uuid
import time
from datetime import datetime
from nose.tools import *
from nose import SkipTest
from pprint import pprint

import testUtils
import ibmiotf.device
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from ibmiotf.api.common import ApiException

class TestRegistryDevices(testUtils.AbstractTest):


    def testDeviceLocationGetAndUpdate(self):
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

        locationBefore = deviceAfterCreate.getLocation()
        assert_equals(None, locationBefore)
           
        deviceAfterCreate.setLocation({"latitude": 50, "longitude": 60})
        locationAfter = deviceAfterCreate.getLocation()        
        
        assert_not_equal(None, locationAfter.updatedDateTime)
        assert_not_equal(None, locationAfter.measuredDateTime)
        
        assert_true(isinstance(locationAfter.updatedDateTime, datetime))
        assert_true(isinstance(locationAfter.measuredDateTime, datetime))
        
        assert_equals(50, locationAfter.latitude)
        assert_equals(60, locationAfter.longitude)

        deviceAfterCreate.setLocation(DeviceLocation(latitude=80, longitude=75))
        locationAfter = deviceAfterCreate.getLocation()        
        assert_equals(80, locationAfter.latitude)
        assert_equals(75, locationAfter.longitude)
        
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)

    def testDeviceLocationInvalid(self):
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

        locationBefore = deviceAfterCreate.getLocation()
        assert_equals(None, locationBefore)
           
        try:
            deviceAfterCreate.setLocation(DeviceLocation(latitude=100, longitude=120))
        except ApiException as e:
            assert_equals("CUDRS0007E", e.id)
            assert_true(len(e.violations) == 1)
        
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
    
    def testDeviceMgmt(self):
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

        mgmtInfo = deviceAfterCreate.getMgmt()
        assert_equals(None, mgmtInfo)
                
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)

    def testDeviceConnectionLogs(self):
        deviceUid = DeviceCreateRequest(
            typeId="test", 
            deviceId=str(uuid.uuid4()), 
            authToken="NotVerySecretPassw0rd",
            deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2")
        )
        
        createdDevice = self.registry.devices.create(deviceUid)
        
        myDeviceType = self.registry.devicetypes[deviceUid.typeId]        
        assert_true(deviceUid.deviceId in myDeviceType.devices)
                
        options={
            "org": self.ORG_ID,
            "type": createdDevice.typeId,
            "id": createdDevice.deviceId,
            "auth-method": "token",
            "auth-token": createdDevice.authToken
        }
        
        deviceClient = ibmiotf.device.Client(options)
        deviceClient.connect()
        time.sleep(10)
        deviceClient.disconnect()
        # Allow 30 seconds for the logs to make it through
        time.sleep(30)
        
        deviceAfterCreate = self.registry.devicetypes[deviceUid.typeId].devices[deviceUid.deviceId]
        
        connLogs= deviceAfterCreate.getConnectionLogs()
        
        assert_equals(2, len(connLogs))
        for entry in connLogs:
            assert_true(isinstance(entry, LogEntry))
            assert_true(isinstance(entry.timestamp, datetime))
                
        # Cleanup
        self.registry.devices.delete({"typeId": deviceUid.typeId, "deviceId": deviceUid.deviceId})
        assert_false(deviceUid.deviceId in myDeviceType.devices)
