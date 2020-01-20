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
    def testApplicationSharedSubscriptions(self):
        appId = str(uuid.uuid4())
        appCliInstance1 = wiotp.sdk.application.ApplicationClient(
            {
                "identity": {"appId": appId},
                "auth": {"key": os.getenv("WIOTP_API_KEY"), "token": os.getenv("WIOTP_API_TOKEN")},
                "options": {"mqtt": {"instanceId": str(uuid.uuid4())}},
            }
        )
        assert isinstance(appCliInstance1, wiotp.sdk.application.ApplicationClient)

        appCliInstance2 = wiotp.sdk.application.ApplicationClient(
            {
                "identity": {"appId": appId},
                "auth": {"key": os.getenv("WIOTP_API_KEY"), "token": os.getenv("WIOTP_API_TOKEN")},
                "options": {"mqtt": {"instanceId": str(uuid.uuid4())}},
            }
        )
        assert isinstance(appCliInstance2, wiotp.sdk.application.ApplicationClient)

        appCliInstance1.connect()
        appCliInstance2.connect()
        assert appCliInstance1.isConnected() == True
        assert appCliInstance2.isConnected() == True

        appCliInstance1.disconnect()
        appCliInstance2.disconnect()
        assert appCliInstance1.isConnected() == False
        assert appCliInstance2.isConnected() == False

    def testMissingAuthKey(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.ApplicationClient(
                {
                    "identity": {"appId": "myAppId"},
                    "auth": {"token": "myToken"},
                    "options": {"mqtt": {"instanceId": "myInstance"}},
                }
            )
        assert e.value.reason == "Missing auth.key from configuration"

    def testMissingAuthToken(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.ApplicationClient(
                {
                    "identity": {"appId": "myAppId"},
                    "auth": {"key": "myKey"},
                    "options": {"mqtt": {"instanceId": "myInstance"}},
                }
            )
        assert e.value.reason == "Missing auth.token from configuration"

    def testPortMustBeANumber(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.ApplicationClient(
                {
                    "identity": {"appId": "myAppId"},
                    "auth": {"key": "myKey", "token": "myToken"},
                    "options": {"mqtt": {"instanceId": "myInstance", "port": "notAnInteger"}},
                }
            )
        assert e.value.reason == "Optional setting options.port must be a number if provided"

    def testCleanMustBeABoolean(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.ApplicationClient(
                {
                    "identity": {"appId": "myAppId"},
                    "auth": {"key": "myKey", "token": "myToken"},
                    "options": {"mqtt": {"instanceId": "myInstance", "port": 1, "cleanSession": "notABoolean"}},
                }
            )
        assert e.value.reason == "Optional setting options.cleanSession must be a boolean if provided"

    def testMissingArgs(self):
        appId = str(uuid.uuid4())
        appCliInstance = wiotp.sdk.application.ApplicationClient(
            {}
        )  # Attempting to connect without any arguments - testing the autofill
        appCliInstance.connect()
        assert appCliInstance.isConnected() == True
        appCliInstance.disconnect()

    def testMissingConfigFile(self):
        applicationFile = "test/notAFile.yaml"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.parseConfigFile(applicationFile)
        assert (
            e.value.reason
            == "Error reading device configuration file 'test/notAFile.yaml' ([Errno 2] No such file or directory: 'test/notAFile.yaml')"
        )

    def testConfigFileWrongLogLevel(self):
        applicationFile = "test/testConfigFiles/test_application_configfile_invalidLogLevel.yaml"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.application.parseConfigFile(applicationFile)
        assert e.value.reason == "Optional setting options.logLevel must be one of error, warning, info, debug"
