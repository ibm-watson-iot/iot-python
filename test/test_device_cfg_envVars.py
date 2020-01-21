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
    def testMissingOrgIDEnvVar(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            del os.environ["WIOTP_IDENTITY_ORGID"]
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_ORGID environment variable"

    def testMissingTypeIDEnvVar(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            del os.environ["WIOTP_IDENTITY_TYPEID"]
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_TYPEID environment variable"

    def testMissingDeviceIDEnvVar(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            del os.environ["WIOTP_IDENTITY_DEVICEID"]
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_IDENTITY_DEVICEID environment variable"

    def testMissingAuthTokenEnvVar(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            del os.environ["WIOTP_AUTH_TOKEN"]
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "Missing WIOTP_AUTH_TOKEN environment variable"

    def testPortEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_PORT"] = "notAnInteger"
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_PORT must be a number"

    def testSessionExpiryEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_PORT"] = "1"
            os.environ["WIOTP_OPTIONS_MQTT_SESSIONEXPIRY"] = "notAnInteger"
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_SESSIONEXPIRY must be a number"

    def testKeepAliveEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_KEEPALIVE"] = "notAnInteger"
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_KEEPALIVE must be a number"

    def testLogLevelEnvVarWrongValue(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_LOGLEVEL"] = "notALogLevel"
            wiotp.sdk.device.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_LOGLEVEL must be one of error, warning, info, debug"
