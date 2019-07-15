# *****************************************************************************
# Copyright (c) 2018-2019 IBM Corporation and other Contributors.
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
import time
import pytest
import testUtils
from datetime import datetime
from wiotp.sdk.device import DeviceClient
from wiotp.sdk.api.registry.devices import DeviceUid, DeviceInfo, DeviceCreateRequest
from wiotp.sdk.exceptions import ApiException


class TestLEC(testUtils.AbstractTest):

    # =========================================================================
    # LEC tests
    # =========================================================================
    def testLEC(self, deviceType, device, authToken):

        # Ensure test device type and device exist
        assert device.deviceId in deviceType.devices

        # Connect the device and send an event
        deviceOptions = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": authToken},
        }

        deviceClient = DeviceClient(deviceOptions)
        deviceClient.connect()
        deviceClient.publishEvent(eventId="test1", msgFormat="json", data={"foo": "bar1"}, qos=1)
        deviceClient.publishEvent(eventId="test2", msgFormat="json", data={"foo": "bar2"}, qos=1)
        deviceClient.disconnect()

        # Wait 30 seconds to increase likelihood that the message has been processed/cached
        time.sleep(30)

        # Check the LEC
        lastEvent = self.appClient.lec.get(device, "test1")

        assert lastEvent.format == "json"
        assert lastEvent.deviceId == device.deviceId
        assert lastEvent.typeId == device.typeId
        assert isinstance(lastEvent.timestamp, datetime)

        # Base64 decode the payload from the lEC and compare to the json dump of the data we sent
        decodedPayload = json.loads(base64.b64decode(lastEvent.payload).decode("utf-8"))
        assert "foo" in decodedPayload
        assert decodedPayload["foo"] == "bar1"

        lastEvents = self.appClient.lec.getAll(device)

        assert len(lastEvents) == 2

        # Results should be sorted by eventId ... "test1" event should be lsited first
        assert lastEvents[0].format == "json"
        assert lastEvents[0].deviceId == device.deviceId
        assert lastEvents[0].typeId == device.typeId

        decodedPayload1 = json.loads(base64.b64decode(lastEvents[0].payload).decode("utf-8"))
        assert "foo" in decodedPayload1
        assert decodedPayload1["foo"] == "bar1"

        assert lastEvents[1].format == "json"
        assert lastEvents[1].deviceId == device.deviceId
        assert lastEvents[1].typeId == device.typeId

        decodedPayload2 = json.loads(base64.b64decode(lastEvents[1].payload).decode("utf-8"))
        assert "foo" in decodedPayload2
        assert decodedPayload2["foo"] == "bar2"
