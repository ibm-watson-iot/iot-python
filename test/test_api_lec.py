# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import base64
import uuid
import os
import json

import pytest
from nose.tools import *
from nose import SkipTest

import testUtils
import ibmiotf.device
from datetime import datetime
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest
from ibmiotf.api.common import ApiException

import logging
logger = logging.getLogger()

class TestLEC(testUtils.AbstractTest):

    # =========================================================================
    # LEC tests
    # =========================================================================
    def testLEC(self, deviceType, device, authToken):
        
        # Ensure test device type and device exist
        assert_true(device.deviceId in deviceType.devices)
    
        # Connect the device and send an event
        deviceOptions={
            "identity": {
                "orgId": os.getenv("WIOTP_ORG_ID"),
                "typeId": device.typeId,
                "deviceId": device.deviceId
            },
            "auth": {
                "token": authToken
            }
        }
        
        deviceClient = ibmiotf.device.DeviceClient(deviceOptions)
        deviceClient.connect()
        deviceClient.publishEvent(event="test1", msgFormat="json", data={"foo": "bar1"}, qos=1)
        deviceClient.publishEvent(event="test2", msgFormat="json", data={"foo": "bar2"}, qos=1)
        deviceClient.disconnect()
        
        # Check the LEC
        lastEvent = self.appClient.lec.get(device, "test1")
        
        assert_equals(lastEvent.format, "json")
        assert_equals(lastEvent.deviceId, device.deviceId)
        assert_equals(lastEvent.typeId, device.typeId)
        assert_true(isinstance(lastEvent.timestamp, datetime))
        
        # Base64 decode the payload from the lEC and compare to the json dump of the data we sent
        decodedPayload = json.loads(base64.b64decode(lastEvent.payload).decode('utf-8'))
        assert_true("foo" in decodedPayload)
        assert_equals(decodedPayload["foo"], "bar1")

        lastEvents = self.appClient.lec.getAll(device)
        
        assert_equals(len(lastEvents), 2)
        
        # Results should be sorted by eventId ... "test1" event should be lsited first
        assert_equals(lastEvents[0].format, "json")
        assert_equals(lastEvents[0].deviceId, device.deviceId)
        assert_equals(lastEvents[0].typeId, device.typeId)
        decodedPayload1 = json.loads(base64.b64decode(lastEvents[0].payload).decode('utf-8'))
        assert_true("foo" in decodedPayload1)
        assert_equals(decodedPayload1["foo"], "bar1")
        
        assert_equals(lastEvents[1].format, "json")
        assert_equals(lastEvents[1].deviceId, device.deviceId)
        assert_equals(lastEvents[1].typeId, device.typeId)
        decodedPayload2 = json.loads(base64.b64decode(lastEvents[1].payload).decode('utf-8'))
        assert_true("foo" in decodedPayload2)
        assert_equals(decodedPayload2["foo"], "bar2")

