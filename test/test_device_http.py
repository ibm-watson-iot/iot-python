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

import ibmiotf.device
import ibmiotf.application
import uuid
import os
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
import logging
import testUtils

class TestDevice(testUtils.AbstractTest):
    registeredDevice = None
    httpClient = None

    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())
    
    @classmethod
    def setup_class(self):
        try: 
            deviceType = self.setupAppClient.api.getDeviceType(self.DEVICE_TYPE)
        except APIException as e:
            if e.httpCode == 404:
                deviceType = self.setupAppClient.api.addDeviceType(self.DEVICE_TYPE)
            else: 
                raise e
        
        self.registeredDevice = self.setupAppClient.api.registerDevice(self.DEVICE_TYPE, self.DEVICE_ID)
        
        self.options={
            "org": self.ORG_ID,
            "type": self.registeredDevice["typeId"],
            "id": self.registeredDevice["deviceId"],
            "auth-method": "token",
            "auth-token": self.registeredDevice["authToken"]
        }
        
        self.httpClient = ibmiotf.device.HttpClient(self.options)
    

    @classmethod
    def teardown_class(self):
        del self.httpClient
        self.setupAppClient.api.deleteDevice(self.DEVICE_TYPE, self.DEVICE_ID)
    
    
    def testPublishEventOverHTTPs(self):
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(self.httpClient.publishEvent("testPublishEventHTTPs", "json",myData),200)
    
    
    def testPublishEventOverHTTP(self):
        client = ibmiotf.device.HttpClient({"org": "quickstart", "type": self.registeredDevice["typeId"], "id": self.registeredDevice["deviceId"],
                                        "auth-method":"None", "auth-token":"None" })
        myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
        assert_equals(client.publishEvent("testPublishEventHTTP", "json",myData),200)
    