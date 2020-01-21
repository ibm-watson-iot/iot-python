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


class TestDeviceCfg(testUtils.AbstractTest):
    def testMissingOptions(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({})
        assert e.value.reason == "Missing identity from configuration"
        assert str(e.value) == "Missing identity from configuration"

    def testMissingOrg(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {"identity": {"orgId": None, "typeId": "myType", "deviceId": "myDevice"}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason == "Missing identity.orgId from configuration"

    def testMissingType(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {"identity": {"orgId": "myOrg", "typeId": None, "deviceId": "myDevice"}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason == "Missing identity.typeId from configuration"

    def testMissingId(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": None}, "auth": {"token": "myToken"}}
            )
        assert e.value.reason == "Missing identity.deviceId from configuration"

    def testQuickstartWithAuth(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {
                    "identity": {"orgId": "quickstart", "typeId": "myType", "deviceId": "myDevice"},
                    "auth": {"token": "myToken"},
                }
            )
        assert e.value.reason == "Quickstart service does not support device authentication"

    def testMissingAuth(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient({"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"}})
        assert e.value.reason == "Missing auth from configuration"

    def testMissingAuthToken(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {"identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"}, "auth": {"token": None}}
            )
        assert e.value.reason == "Missing auth.token from configuration"

    def testPortNotInteger(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {
                    "identity": {"orgId": "quickstart", "typeId": "myType", "deviceId": "myDevice"},
                    "options": {"mqtt": {"port": "notAnInteger"}},
                }
            )
        assert e.value.reason == "Optional setting options.mqtt.port must be a number if provided"

    def testCleanStartNotBoolean(self):
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.DeviceClient(
                {
                    "identity": {"orgId": "myOrg", "typeId": "myType", "deviceId": "myDevice"},
                    "auth": {"token": "myToken"},
                    "options": {"mqtt": {"cleanStart": "notABoolean"}},
                }
            )
        assert e.value.reason == "Optional setting options.mqtt.cleanStart must be a boolean if provided"

    def testMissingConfigFile(self):
        deviceFile = "notAFile.yaml"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.parseConfigFile(deviceFile)
        assert (
            e.value.reason
            == "Error reading device configuration file 'notAFile.yaml' ([Errno 2] No such file or directory: 'notAFile.yaml')"
        )

    def testConfigFileWrongLogLevel(self):
        deviceFile = "test/testConfigFiles/test_device_configfile.yaml"
        with pytest.raises(wiotp.sdk.ConfigurationException) as e:
            wiotp.sdk.device.parseConfigFile(deviceFile)
        assert e.value.reason == "Optional setting options.logLevel must be one of error, warning, info, debug"

    def testMissingArgs(self):
        devCliInstance = wiotp.sdk.application.ApplicationClient(
            {}
        )  # Attempting to connect without any arguments - testing the autofill
        devCliInstance.connect()
        assert devCliInstance.isConnected() == True
        devCliInstance.disconnect()
