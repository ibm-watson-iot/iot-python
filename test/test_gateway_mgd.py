# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import pytest
import testUtils
import wiotp.sdk

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
        managedGateway = wiotp.sdk.gateway.ManagedGatewayClient(self.options)
        assert isinstance(managedGateway, wiotp.sdk.gateway.ManagedGatewayClient)

    def testManagedgatewayQSException(self):
        with pytest.raises(wiotp.sdk.ConfigurationException)as e:
            options={
                "identity": {
                    "orgId": "quickstart", 
                    "typeId": self.registeredGateway["typeId"], 
                    "deviceId": self.registeredGateway["deviceId"]
                },
            }
            wiotp.sdk.gateway.ManagedGatewayClient(options)
        assert "QuickStart does not support device management" == e.value.reason

    def testManagedGatewayConnectException(self):
        badOptions = {
            "identity": {
                "orgId": self.ORG_ID, "typeId": self.registeredGateway["typeId"], "deviceId": self.registeredGateway["deviceId"] 
            },
            "auth": {
                "token": "xxxxxxxxxxxxxxxxxx"
            }
        }
        gatewayInfoObj = wiotp.sdk.gateway.DeviceInfo()
        managedGateway = wiotp.sdk.gateway.ManagedGatewayClient(badOptions, deviceInfo=gatewayInfoObj)
        with pytest.raises(wiotp.sdk.ConnectionException) as e:
            managedGateway.connect()

