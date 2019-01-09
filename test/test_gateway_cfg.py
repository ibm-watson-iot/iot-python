# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# *****************************************************************************

from nose.tools import *
import wiotp.sdk.gateway
import testUtils

class TestDeviceCfg(testUtils.AbstractTest):

    def testMissingOptions(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({})
        assert_equal(e.exception.reason, 'Missing identity from configuration')

    def testMissingOrg(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({
                "identity": {
                    "orgId": None, "typeId": "myType", "deviceId": "myId"
                },
                "auth": { "token" : "myToken" }
            })
        assert_equal(e.exception.reason, 'Missing identity.orgId from configuration')

    def testMissingType(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({
                "identity": {
                    "orgId": "myOrg", "typeId": None, "deviceId": "myId"
                },
                "auth": { "token" : "myToken" }
            })
        assert_equal(e.exception.reason, 'Missing identity.typeId from configuration')

    def testMissingId(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": None
                },
                "auth": { "token" : "myToken" }
            })
        assert_equal(e.exception.reason, 'Missing identity.deviceId from configuration')

    def testMissingAuthToken(self):
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.gateway.GatewayClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myId"
                },
                "auth": { "token" : None }
            })
            wiotp.sdk.gateway.GatewayClient({"org": self.ORG_ID, "type": self.registeredDevice.typeId, "id": self.registeredDevice.deviceId,
                                   "auth-method": None, "auth-token": self.registeredDevice.authToken})
        assert_equal(e.exception.reason, 'Missing auth.token from configuration')
    
    def testMissingConfigFile(self):
        deviceFile="InvalidFile.out"
        with assert_raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.ParseConfigFile(deviceFile)
        assert_equal(e.exception.reason, "Error reading device configuration file 'InvalidFile.out' ([Errno 2] No such file or directory: 'InvalidFile.out')")
