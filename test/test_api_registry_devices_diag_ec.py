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
from wiotp.sdk.api.registry.diag import DeviceLog, DeviceErrorCode, DeviceErrorCodes, DeviceLogs
from wiotp.sdk.exceptions import ApiException
import pytest


class TestRegistryDevicesDiagEc(testUtils.AbstractTest):
    def testDeviceDiagEc(self, deviceType, device):
        assert device.deviceId in deviceType.devices

        # Check it's empty
        assert len(device.diagErrorCodes) == 0

        # Create a log
        device.diagErrorCodes.append(errorCode=0, timestamp=datetime.now())
        time.sleep(10)

        assert len(device.diagErrorCodes) == 1
        assert device.diagErrorCodes[0].errorCode == 0

        device.diagErrorCodes.append(DeviceErrorCode(errorCode=99, timestamp=datetime.now()))
        time.sleep(10)

        assert len(device.diagErrorCodes) == 2
        assert device.diagErrorCodes[0].errorCode == 99
        assert device.diagErrorCodes[1].errorCode == 0

        device.diagErrorCodes.clear()
        time.sleep(10)
        assert len(device.diagErrorCodes) == 0

    def testErrorCodesInsert(self):
        with pytest.raises(Exception) as e:
            DeviceErrorCodes(apiClient="1", typeId="2", deviceId="3").insert(index="1", value="2")
            assert "only append() is supported for new error codes" in str(e.value)

    def testErrorCodesDelItem(self):
        with pytest.raises(Exception) as e:
            test = DeviceErrorCodes(apiClient="1", typeId="2", deviceId="3").__delitem__(index="1")
            assert "Individual error codes can not be deleted use clear() method instead" in str(e.value)

    def testErrorCodesSetItem(self):
        with pytest.raises(Exception) as e:
            test = DeviceErrorCodes(apiClient="1", typeId="2", deviceId="3").__setitem__(index="1", value="2")
            assert "Reported error codes are immutable" in str(e.value)

    def testErrorCodesMissing(self):
        with pytest.raises(Exception) as e:
            test = DeviceErrorCodes(apiClient="1", typeId="2", deviceId="3").__missing__(index="1")
            assert "Error code at index does not exist" in str(e.value)

    def testDeviceLogsSetItem(self):
        with pytest.raises(Exception) as e:
            DeviceLogs(apiClient="1", typeId="2", deviceId="3").__setitem__(key="1", value="2")
            assert "Log entries are immutable" in str(e.value)

    def testDeviceLogsMissing(self):
        with pytest.raises(Exception) as e:
            DeviceLogs(apiClient="1", typeId="2", deviceId="3").__missing__(key="1")
            assert "Log Entry does not exist" in str(e.value)
