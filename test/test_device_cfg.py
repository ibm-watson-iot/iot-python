# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# *****************************************************************************

import wiotp.sdk.device
import testUtils
import pytest
import os

class TestDeviceCfg(testUtils.AbstractTest):

    def testMissingOptions(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({})
        assert e.value.reason == 'Missing identity from configuration'

    def testMissingOrg(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": None, "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : "myToken" }
            })
        assert e.value.reason == 'Missing identity.orgId from configuration'

    def testMissingType(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": None, "deviceId": "myDevice"
                },
                "auth": { "token" : "myToken" }
            })
        assert e.value.reason == 'Missing identity.typeId from configuration'

    def testMissingId(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": None
                },
                "auth": { "token" : "myToken" }
            })
        assert e.value.reason == 'Missing identity.deviceId from configuration'

    def testMissingAuthToken(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : None }
            })
            wiotp.sdk.device.DeviceClient({"org": self.ORG_ID, "type": self.registeredDevice.typeId, "id": self.registeredDevice.deviceId,
                                   "auth-method": None, "auth-token": self.registeredDevice.authToken})
        assert e.value.reason == 'Missing auth.token from configuration'

    def testMissingConfigFile(self):
        deviceFile="InvalidFile.out"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.parseConfigFile(deviceFile)
        assert e.value.reason == "Error reading device configuration file 'InvalidFile.out' ([Errno 2] No such file or directory: 'InvalidFile.out')"


    def testMissingOrgIDEnvVar(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"

           del os.environ['WIOTP_IDENTITY_ORGID']
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_ORGID environment variable"
    
    def testMissingTypeIDEnvVar(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"

           del os.environ['WIOTP_IDENTITY_TYPEID']
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_TYPEID environment variable"

    def testMissingDeviceIDEnvVar(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"

           del os.environ['WIOTP_IDENTITY_DEVICEID']
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_DEVICEID environment variable"