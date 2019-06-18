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

    def testQuickstartWithAuth(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "quickstart", "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : "myToken" }
            })
        assert e.value.reason == 'Quickstart service does not support device authentication'

    def testQuickstartMissingAuth(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"
                },
            })
        assert e.value.reason == 'Missing auth from configuration'

    def testMissingAuthToken(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : None }
            })
        assert e.value.reason == 'Missing auth.token from configuration'

    def testPortNotInteger(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : "myToken" },
                "options": { "mqtt" : {"port" : "notAnInteger"} }
            })
        assert e.value.reason == 'Optional setting options.mqtt.port must be a number if provided'

    def testCleanStartNotBoolean(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({
                "identity": {
                    "orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"
                },
                "auth": { "token" : "myToken" },
                "options": { "mqtt" : {"cleanStart" : "notABoolean"} }
            })
        assert e.value.reason == 'Optional setting options.mqtt.cleanStart must be a boolean if provided'

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

    def testMissingAuthTokenEnvVar(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"
           del os.environ['WIOTP_AUTH_TOKEN']
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_AUTH_TOKEN environment variable"


    def testPortEnvVarNotInteger(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"
           os.environ['WIOTP_OPTIONS_MQTT_PORT'] = "notAnInteger"
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_PORT must be a number"

    def testSessionExpiryEnvVarNotInteger(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"
           os.environ['WIOTP_OPTIONS_MQTT_PORT'] = "0"
           os.environ['WIOTP_OPTIONS_MQTT_SESSIONEXPIRY'] = "notAnInteger"
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_SESSIONEXPIRY must be a number"

    def testKeepAliveEnvVarNotInteger(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"
           os.environ['WIOTP_OPTIONS_MQTT_PORT'] = "0"
           os.environ['WIOTP_OPTIONS_MQTT_SESSIONEXPIRY'] = "0"
           os.environ['WIOTP_OPTIONS_MQTT_KEEPALIVE'] = "notAnInteger"
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_KEEPALIVE must be a number"

    def testLogLevelEnvVarWrongValue(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
           os.environ['WIOTP_IDENTITY_ORGID'] = "myOrg"
           os.environ['WIOTP_IDENTITY_TYPEID'] = "myType"
           os.environ['WIOTP_IDENTITY_DEVICEID'] = "myDevice"
           os.environ['WIOTP_AUTH_TOKEN'] = "myToken"
           os.environ['WIOTP_OPTIONS_MQTT_PORT'] = "0"
           os.environ['WIOTP_OPTIONS_MQTT_SESSIONEXPIRY'] = "0"
           os.environ['WIOTP_OPTIONS_MQTT_KEEPALIVE'] = "0"
           os.environ['WIOTP_OPTIONS_LOGLEVEL'] = "myLogLevel"
           wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_LOGLEVEL must be one of error, warning, info, debug"
    
    