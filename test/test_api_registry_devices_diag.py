# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import time
from datetime import datetime
import pytest
import testUtils
import wiotp.sdk.device
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest, DeviceLocation, LogEntry
from wiotp.sdk.api.registry.diag import DeviceLog
from wiotp.sdk.exceptions import ApiException


class TestRegistryDevicesDiag(testUtils.AbstractTest):
    def testDeviceDiagLogs(self, deviceType, device):
        assert device.deviceId in deviceType.devices

        # Check it's empty
        assert len(device.diagLogs) == 0

        # Create a log
        device.diagLogs.append(message="hi dave0", data="0", timestamp=datetime.now(), severity=0)
        time.sleep(5)
        assert len(device.diagLogs) == 1

        assert device.diagLogs[0].message == "hi dave0"
        assert device.diagLogs[0].data == "0"
        assert device.diagLogs[0].severity == 0

        # Get the id
        logEntry1id = device.diagLogs[0].id

        assert device.diagLogs[logEntry1id].message == "hi dave0"
        assert device.diagLogs[logEntry1id].data == "0"
        assert device.diagLogs[logEntry1id].severity == 0

        device.diagLogs.append(DeviceLog(message="hi dave1", data="1", timestamp=datetime.now(), severity=1))
        time.sleep(5)

        assert len(device.diagLogs) == 2

        # Logs are in decending order
        assert device.diagLogs[0].message == "hi dave1"
        assert device.diagLogs[0].data == "1"
        assert device.diagLogs[0].severity == 1

        del device.diagLogs[0]
        time.sleep(5)
        assert len(device.diagLogs) == 1

        device.diagLogs.clear()
        time.sleep(5)
        assert len(device.diagLogs) == 0

    def testDeviceBadDiagLogs(self, deviceType, device):
        assert device.deviceId in deviceType.devices

        # Check it's empty
        assert len(device.diagLogs) == 0

        # Create a log with invalid severity
        with pytest.raises(ApiException) as e:
            device.diagLogs.append(DeviceLog(message="hi dave0", data="0", timestamp=datetime.now(), severity=3))

            assert e.value.id == "CUDRS0007E"
            assert len(e.value.violations) == 1
