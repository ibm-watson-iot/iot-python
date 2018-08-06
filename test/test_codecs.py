# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta  - Initial Contribution
# *****************************************************************************

import copy

from ibmiotf import MessageCodec
import ibmiotf.device
import ibmiotf.application
import uuid
import os
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
import logging
import testUtils

class MyCodec(ibmiotf.MessageCodec):
    @staticmethod
    def encode(data=None, timestamp=None):
        '''
        Dedicated encoder for supporting a very specific dataset, serialises a dictionary object
        of the following format: 
          {
            'hello' : 'world', 
            'x' : 10
          }
        
        into a simple comma-seperated message:
          world,10
        '''
        return data['hello'] + "," + str(data['x'])
    
    @staticmethod
    def decode(message):
        '''
        The decoder understands the comma-seperated format produced by the encoder and 
        allocates the two values to the correct keys:
        
          data['hello'] = 'world'
          data['x'] = 10

        The MQTT message is a byte array, after splitting it convert to string and int
          
        '''
        (hello, x) = message.payload.decode('utf-8').split(',')
        
        data = {}
        data['hello'] = hello
        data['x'] = int(x)
        
        timestamp = datetime.now(pytz.timezone('UTC'))
        
        return Message(data, timestamp)

class TestDevice(testUtils.AbstractTest):
    registeredDevice = None
    deviceClient = None
    managedClient = None

    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())
    
    @classmethod
    def setup_class(self):
        try: 
            deviceType = self.setupAppClient.api.registry.devicetypes[self.DEVICE_TYPE]
        except ApiException as e:
            if e.httpCode == 404:
                deviceType = self.setupAppClient.api.registry.devicetypes.create(self.DEVICE_TYPE)
            else: 
                raise e
        
        self.registeredDevices = self.setupAppClient.api.registry.devices.create({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})
        
        self.options={
            "org": self.ORG_ID,
            "type": self.registeredDevices[0].typeId,
            "id": self.registeredDevices[0].deviceId,
            "auth-method": "token",
            "auth-token": self.registeredDevices[0].authToken
        }
        
        self.deviceClient = ibmiotf.device.Client(self.options)

    @classmethod
    def teardown_class(self):
        del self.deviceClient
        self.setupAppClient.api.registry.devices.delete({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})
    
    
    def testPublishEvent(self):
        global failed, calledBack
        calledBack = False
        failed = True
        def devPublishCallback():
            print("Device Publish Event done!!!")

        def myAppEventCallback(event):
            global failed, calledBack
            if event.data['hello'] == "world" and event.data['x'] == 100:
                failed = False
            calledBack = True

        self.setupAppClient.setMessageEncoderModule("custom", MyCodec)
        self.setupAppClient.connect()
        self.setupAppClient.subscribeToDeviceEvents(self.DEVICE_TYPE, self.DEVICE_ID, "greeting")
        self.setupAppClient.deviceEventCallback = myAppEventCallback
        
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        
        self.deviceClient.setMessageEncoderModule("custom", MyCodec)
        self.deviceClient.connect()
        data = { 'hello' : 'world', 'x' : 100}
        self.deviceClient.publishEvent("greeting", "custom", data, qos=1)
        
        x = 0
        while x < 10:
            x += 1
            time.sleep(1)
        
        assert_true(calledBack)
        assert_false(failed)
        
        self.deviceClient.disconnect()
        self.setupAppClient.disconnect()
