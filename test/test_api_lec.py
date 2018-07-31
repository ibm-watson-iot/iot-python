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

from nose.tools import *
from nose import SkipTest

import testUtils
import ibmiotf.device
from datetime import datetime
from ibmiotf.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest
from ibmiotf.api.common import ApiException

class TestLEC(testUtils.AbstractTest):

    # =========================================================================
    # Bulk operations tests
    # =========================================================================
    def testLEC(self):
        device1Id = DeviceUid(typeId="test", deviceId=str(uuid.uuid4()))
        
        registeredDevices = self.registry.devices.create(device1Id)
        
        myDeviceType = self.registry.devicetypes["test"]
        assert_true(device1Id.deviceId in myDeviceType.devices)
    
        # Connect the device and send an event
        deviceOptions={
            "org": os.getenv("WIOTP_ORG_ID"),
            "type": device1Id.typeId,
            "id": device1Id.deviceId,
            "auth-method": "token",
            "auth-token": registeredDevices[0]["authToken"]
        }
        
        deviceClient = ibmiotf.device.Client(deviceOptions)
        deviceClient.connect()
        deviceClient.publishEvent(event="test1", msgFormat="json", data={"foo": "bar1"}, qos=1)
        deviceClient.publishEvent(event="test2", msgFormat="json", data={"foo": "bar2"}, qos=1)
        deviceClient.disconnect()
        
        # Check the LEC
        lastEvent = self.lec.get(device1Id, "test1")
        
        assert_equals(lastEvent.format, "json")
        assert_equals(lastEvent.deviceId, device1Id.deviceId)
        assert_equals(lastEvent.typeId, device1Id.typeId)
        assert_true(isinstance(lastEvent.timestamp, datetime))
        
        # Base64 decode the payload from the lEC and compare to the json dump of the data we sent
        decodedPayload = json.loads(base64.b64decode(lastEvent.payload).decode('utf-8'))
        assert_true("foo" in decodedPayload)
        assert_equals(decodedPayload["foo"], "bar1")

        lastEvents = self.lec.getAll(device1Id)
        
        assert_equals(len(lastEvents), 2)
        
        # Results should be sorted by eventId ... "test1" event should be lsited first
        assert_equals(lastEvents[0].format, "json")
        assert_equals(lastEvents[0].deviceId, device1Id.deviceId)
        assert_equals(lastEvents[0].typeId, device1Id.typeId)
        decodedPayload1 = json.loads(base64.b64decode(lastEvents[0].payload).decode('utf-8'))
        assert_true("foo" in decodedPayload1)
        assert_equals(decodedPayload1["foo"], "bar1")
        
        assert_equals(lastEvents[1].format, "json")
        assert_equals(lastEvents[1].deviceId, device1Id.deviceId)
        assert_equals(lastEvents[1].typeId, device1Id.typeId)
        decodedPayload2 = json.loads(base64.b64decode(lastEvents[1].payload).decode('utf-8'))
        assert_true("foo" in decodedPayload2)
        assert_equals(decodedPayload2["foo"], "bar2")
        
        self.registry.devices.delete(device1Id)
        assert_false(device1Id.deviceId in myDeviceType.devices)

