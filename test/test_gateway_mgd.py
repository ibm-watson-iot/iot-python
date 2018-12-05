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

import ibmiotf.gateway
import ibmiotf.application
import uuid
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
import testUtils

class TestGateway(testUtils.AbstractTest):
    registeredDevice = None
    registeredGateway = None
    
    DEVICE_TYPE = "test_device"
    DEVICE_ID = str(uuid.uuid4())
    
    GATEWAY_TYPE = "test_gateway"
    GATEWAY_ID = str(uuid.uuid4())

    
    @classmethod
    def setup_class(self):
        # Register a Device
        if self.DEVICE_TYPE not in self.setupAppClient.api.registry.devicetypes:
            self.setupAppClient.api.registry.devicetypes.create({"id": self.DEVICE_TYPE})
        
        self.registeredDevice = self.setupAppClient.api.registry.devices.create({"typeId": self.TYPE_ID, "deviceId": self.DEVICE_ID})
        
        # Register a Gateway
        if self.GATEWAY_TYPE not in self.setupAppClient.api.registry.devicetypes:
            self.setupAppClient.api.registry.devicetypes.create({"id": self.GATEWAY})

        self.registeredGateway = self.setupAppClient.api.registry.devices.create({"typeId": self.GATEWAY_TYPE, "deviceId": self.GATEWAY_ID})
        
        self.options={
            "identity": {
                "orgId": self.ORG_ID,
                "typeId": self.registeredGateway["typeId"],
                "deviceId": self.registeredGateway["deviceId"]
            },
            "auth": {
                "token": self.registeredGateway["authToken"]
            }
        }
        

    @classmethod
    def teardown_class(self):
        del self.setupAppClient.api.registry.devicetypes[self.DEVICE_TYPE].devices[self.DEVICE_ID]
        del self.setupAppClient.api.registry.devicetypes[self.GATEWAY_TYPE].devices[self.GATEWAY_ID]


    def testManagedGatewayInstance(self):
        managedGateway = ibmiotf.gateway.ManagedClient(self.options)
        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedClient)

    def testManagedgatewayQSException(self):
        with assert_raises(Exception)as e:
            options={
                "identity": {
                    "orgId": "quickstart", 
                    "typeId": self.registeredGateway["typeId"], 
                    "deviceId": self.registeredGateway["deviceId"]
                },
            }
            ibmiotf.gateway.managedClient(options)
        assert_equals("QuickStart does not support device management", e.exception.reason)

    def testManagedGatewayConnectException(self):
        badOptions = {"org": self.ORG_ID, "type": self.registeredGateway["typeId"], "id": self.registeredGateway["deviceId"], "auth-method":"token", "auth-token":"xxxxxxxxxxxxxxxxxx" }
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedClient(badOptions, deviceInfo=gatewayInfoObj)
        with assert_raises(ConnectionException) as e:
            managedGateway.connect()

    @SkipTest
    def testManagedGatewayInstanceWithDeviceInfo(self):
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedClient(self.options, deviceInfo=gatewayInfoObj)

        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedClient)

        #Connect managedGateway
        managedGateway.connect()

        #Define device properties to be notified whenever reset
        managedGateway._deviceMgmtObservations = ["deviceInfo.manufacturer", "deviceInfo.descriptiveLocation",
                                                  "deviceInfo.fwVersion", "deviceInfo.model", "deviceInfo.description",
                                                  "deviceInfo.deviceClass", "deviceInfo.hwVersion", "deviceInfo.serialNumber"]

        #Reset managedgateway properties
        managedGateway.setErrorCode(1)
        managedGateway.setLocation(longitude=100, latitude=78, accuracy=100,elevation=45)
        managedGateway.setSerialNumber('iot-pgateway-12345')
        managedGateway.setManufacturer("IBM India Pvt Ltd")
        managedGateway.setModel("2016")
        managedGateway.setdeviceClass("Smart Gateway")
        managedGateway.setDescription("Sample Smart IoT Gateway")
        managedGateway.setFwVersion("1.0")
        managedGateway.setHwVersion("2.0")
        managedGateway.setDescriptiveLocation("ISL Lab Bangalore")

        managedGateway.clearErrorCodes()

        #Disconnect ManagedGateway
        managedGateway.unmanage()
        managedGateway.disconnect()
