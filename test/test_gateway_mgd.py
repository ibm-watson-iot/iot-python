# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
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
        if self.DEVICE_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.registry.devicetypes.create({"id": self.DEVICE_TYPE})
        
        self.registeredDevice = self.appClient.registry.devices.create({"typeId": self.DEVICE_TYPE, "deviceId": self.DEVICE_ID})
        
        # Register a Gateway
        if self.GATEWAY_TYPE not in self.appClient.registry.devicetypes:
            self.appClient.registry.devicetypes.create({"id": self.GATEWAY_TYPE})

        self.registeredGateway = self.appClient.registry.devices.create({"typeId": self.GATEWAY_TYPE, "deviceId": self.GATEWAY_ID})
        
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
        del self.appClient.registry.devicetypes[self.DEVICE_TYPE].devices[self.DEVICE_ID]
        del self.appClient.registry.devicetypes[self.GATEWAY_TYPE].devices[self.GATEWAY_ID]


    def testManagedGatewayInstance(self):
        managedGateway = ibmiotf.gateway.ManagedGatewayClient(self.options)
        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedGatewayClient)

    def testManagedgatewayQSException(self):
        with assert_raises(ConfigurationException)as e:
            options={
                "identity": {
                    "orgId": "quickstart", 
                    "typeId": self.registeredGateway["typeId"], 
                    "deviceId": self.registeredGateway["deviceId"]
                },
            }
            ibmiotf.gateway.ManagedGatewayClient(options)
        assert_equals("QuickStart does not support device management", e.exception.reason)

    def testManagedGatewayConnectException(self):
        badOptions = {
            "identity": {
                "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] 
            },
            "auth": {
                "token": "xxxxxxxxxxxxxxxxxx"
            }
        }
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedGatewayClient(badOptions, deviceInfo=gatewayInfoObj)
        with assert_raises(ConnectionException) as e:
            managedGateway.connect()

    @SkipTest
    def testManagedGatewayInstanceWithDeviceInfo(self):
        gatewayInfoObj = ibmiotf.gateway.DeviceInfo()
        managedGateway = ibmiotf.gateway.ManagedGatewayClient(self.options, deviceInfo=gatewayInfoObj)

        assert_is_instance(managedGateway, ibmiotf.gateway.ManagedGatewayClient)

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
