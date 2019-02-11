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
from wiotp.sdk.api.registry.diag import DeviceLog, DeviceErrorCode
from wiotp.sdk.exceptions import ApiException

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
  
    