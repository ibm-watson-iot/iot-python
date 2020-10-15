# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import time
from datetime import datetime
import testUtils

import wiotp.sdk.device
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from wiotp.sdk.exceptions import ApiException


class TestRegistryDevices(testUtils.AbstractTest):
    def testDeviceLocationGetAndUpdate(self, deviceType, device):
        assert device.deviceId in deviceType.devices

        locationBefore = device.getLocation()
        assert locationBefore is None

        device.setLocation({"latitude": 50, "longitude": 60})
        locationAfter = device.getLocation()

        assert locationAfter.updatedDateTime is not None
        assert locationAfter.measuredDateTime is not None

        assert isinstance(locationAfter.updatedDateTime, datetime)
        assert isinstance(locationAfter.measuredDateTime, datetime)

        assert locationAfter.latitude == 50
        assert locationAfter.longitude == 60

        device.setLocation(DeviceLocation(latitude=80, longitude=75))
        locationAfter = device.getLocation()
        assert locationAfter.latitude == 80
        assert locationAfter.longitude == 75

    def testDeviceLocationInvalid(self, deviceType, device):
        assert device.deviceId in deviceType.devices

        locationBefore = device.getLocation()
        assert locationBefore is None

        try:
            device.setLocation(DeviceLocation(latitude=100, longitude=120))
        except ApiException as e:
            assert e.id == "CUDHT0300I"
            assert len(e.violations) == 1

    def testDeviceMgmt(self, deviceType, device):
        assert device.deviceId in deviceType.devices
        mgmtInfo = device.getMgmt()
        assert mgmtInfo is None

    def testDeviceConnectionLogs(self, deviceType, device, authToken):
        assert device.deviceId in deviceType.devices

        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": authToken},
        }

        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        time.sleep(10)
        deviceClient.disconnect()
        deviceClient.connect()
        time.sleep(10)
        deviceClient.disconnect()
        # Allow 30 seconds for the logs to make it through
        time.sleep(30)

        connLogs = device.getConnectionLogs()

        # There may be more than 2 entries due to previous connection attempts if we re-used a device ID.  But there should be at least two!
        assert len(connLogs) >= 2
        for entry in connLogs:
            assert isinstance(entry, LogEntry)
            assert isinstance(entry.timestamp, datetime)
