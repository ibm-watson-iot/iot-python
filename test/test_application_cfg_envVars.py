# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import os
import testUtils
import wiotp.sdk.application
import pytest


class TestApplication(testUtils.AbstractTest):
    def testPortEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_PORT"] = "notANumber"
            wiotp.sdk.application.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_PORT must be a number"

    def testSessionExpiryEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_SESSIONEXPIRY"] = "notANumber"
            wiotp.sdk.application.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_SESSIONEXPIRY must be a number"

    def testKeepAliveEnvVarNotInteger(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_MQTT_KEEPALIVE"] = "notANumber"
            wiotp.sdk.application.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_MQTT_KEEPALIVE must be a number"

    def testLogLevelEnvVarNotValid(self, manageEnvVars):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            os.environ["WIOTP_OPTIONS_LOGLEVEL"] = "notALogLevel"
            wiotp.sdk.application.parseEnvVars()
        assert e.value.reason == "WIOTP_OPTIONS_LOGLEVEL must be one of error, warning, info, debug"
