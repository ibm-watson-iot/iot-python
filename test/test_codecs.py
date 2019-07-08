# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import copy

import wiotp.sdk

import pytz
from datetime import datetime
import time
import uuid
import testUtils


class MyCodec(wiotp.sdk.MessageCodec):
    @staticmethod
    def encode(data=None, timestamp=None):
        """
        Dedicated encoder for supporting a very specific dataset, serialises a dictionary object
        of the following format: 
          {
            'hello' : 'world', 
            'x' : 10
          }
        
        into a simple comma-seperated message:
          world,10
        """
        return data["hello"] + "," + str(data["x"])

    @staticmethod
    def decode(message):
        """
        The decoder understands the comma-seperated format produced by the encoder and 
        allocates the two values to the correct keys:
        
          data['hello'] = 'world'
          data['x'] = 10

        The MQTT message is a byte array, after splitting it convert to string and int
          
        """
        (hello, x) = message.payload.decode("utf-8").split(",")

        data = {}
        data["hello"] = hello
        data["x"] = int(x)

        timestamp = datetime.now(pytz.timezone("UTC"))

        return wiotp.sdk.Message(data, timestamp)


class TestDevice(testUtils.AbstractTest):
    registeredDevice = None
    deviceClient = None
    managedClient = None

    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())

    @classmethod
    def setup_class(self):
        if self.DEVICE_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.api.registry.devicetypes.create({"id": self.DEVICE_TYPE})

        self.registeredDevice = self.appClient.registry.devices.create(
            {"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID}
        )

        self.options = {
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": self.registeredDevice.typeId,
                "deviceId": self.registeredDevice.deviceId,
            },
            "auth": {"token": self.registeredDevice.authToken},
        }

        self.deviceClient = wiotp.sdk.device.DeviceClient(self.options)

    @classmethod
    def teardown_class(self):
        del self.deviceClient
        self.appClient.registry.devices.delete({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})

    def testPublishEvent(self):
        global failed, calledBack
        calledBack = False
        failed = True

        def devPublishCallback():
            print("Device Publish Event done!!!")

        def myAppEventCallback(event):
            global failed, calledBack
            if event.data["hello"] == "world" and event.data["x"] == 100:
                failed = False
            calledBack = True

        self.appClient.setMessageCodec("custom", MyCodec)
        self.appClient.connect()
        self.appClient.subscribeToDeviceEvents(self.DEVICE_TYPE, self.DEVICE_ID, "greeting")
        self.appClient.deviceEventCallback = myAppEventCallback

        myData = {"name": "foo", "cpu": 60, "mem": 50}

        self.deviceClient.setMessageCodec("custom", MyCodec)
        self.deviceClient.connect()
        data = {"hello": "world", "x": 100}
        self.deviceClient.publishEvent("greeting", "custom", data, qos=1)

        x = 0
        while x < 10:
            x += 1
            time.sleep(1)

        assert calledBack == True
        assert failed == False

        self.deviceClient.disconnect()
        self.appClient.disconnect()
