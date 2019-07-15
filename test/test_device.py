# *****************************************************************************
# Copyright (c) 2016-2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import copy
import uuid
import testUtils
import pytest
import wiotp.sdk.device
import wiotp.sdk.application
from wiotp.sdk.exceptions import ApiException, ConnectionException, MissingMessageEncoderException


class TestDevice(testUtils.AbstractTest):
    def testDeviceInfoInstance(self):
        deviceInfoObj = wiotp.sdk.device.DeviceInfo()
        deviceInfoObj.serialNumber = "0101"
        deviceInfoObj.manufacturer = "0202"
        deviceInfoObj.model = "0303"
        deviceInfoObj.deviceClass = "0404"
        deviceInfoObj.description = "0505"
        deviceInfoObj.fwVersion = "0606"
        deviceInfoObj.hwVersion = "0707"
        deviceInfoObj.descriptiveLocation = "0808"
        assert isinstance(deviceInfoObj, wiotp.sdk.device.DeviceInfo)
        print(deviceInfoObj)
        assert deviceInfoObj.serialNumber == "0101"
        assert deviceInfoObj.manufacturer == "0202"
        assert deviceInfoObj.model == "0303"
        assert deviceInfoObj.deviceClass == "0404"
        assert deviceInfoObj.description == "0505"
        assert deviceInfoObj.fwVersion == "0606"
        assert deviceInfoObj.hwVersion == "0707"
        assert deviceInfoObj.descriptiveLocation == "0808"

    def testDeviceFirmwareInstance(self):
        deviceFWObj = wiotp.sdk.device.DeviceFirmware()
        assert isinstance(deviceFWObj, wiotp.sdk.device.DeviceFirmware)
        print(deviceFWObj)

    def testNotAuthorizedConnect(self, device):
        client = wiotp.sdk.device.DeviceClient(
            {
                "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
                "auth": {"token": "MGhUixxxxxxxxxxxx"},
            }
        )
        with pytest.raises(ConnectionException) as e:
            client.connect()
            assert e.value.msg == "Not authorized"
            assert client.isConnected() == False

    def testMissingMessageEncoder(self, device):
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        assert isinstance(deviceClient, wiotp.sdk.device.DeviceClient)
        with pytest.raises(MissingMessageEncoderException) as e:
            myData = {"name": "foo", "cpu": 60, "mem": 50}
            deviceClient.connect()
            deviceClient.publishEvent("missingMsgEncode", "jason", myData)

    def testPublishEvent(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        myData = {"name": "foo", "cpu": 60, "mem": 50}
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort1883(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 1883}},
        }
        myData = {"name": "foo", "cpu": 60, "mem": 50}
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    @pytest.mark.skip(reason="Currently, port 80 only works with websockets, not tcp :/")
    def testPublishEventPort80(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 80}},
        }
        myData = {"name": "foo", "cpu": 60, "mem": 50}
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort80ws(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 80, "transport": "websockets"}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort1883ws(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 1883, "transport": "websockets"}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort8883(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 8883}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort8883ws(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 1883, "transport": "websockets"}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort443(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 443}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testPublishEventPort443ws(self, device):
        def devPublishCallback():
            print("Device Publish Event done!!!")

        myData = {"name": "foo", "cpu": 60, "mem": 50}
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": device.typeId, "deviceId": device.deviceId},
            "auth": {"token": device.authToken},
            "options": {"mqtt": {"port": 443, "transport": "websockets"}},
        }
        deviceClient = wiotp.sdk.device.DeviceClient(options)
        deviceClient.connect()
        assert (
            deviceClient.publishEvent("testPublishJsonEvent", "json", myData, onPublish=devPublishCallback, qos=2)
            == True
        )
        deviceClient.disconnect()

    def testConfigPortInvalid(self):
        options = {
            "identity": {"orgId": self.ORG_ID, "typeId": "xxx", "deviceId": "xxx"},
            "auth": {"token": "xxx"},
            "options": {"mqtt": {"port": 100}},
        }
        with pytest.raises(Exception) as e:
            deviceClient = wiotp.sdk.device.DeviceClient(options)

            assert str(e.value) == "Unsupported value for port override: 100.  Supported values are 1883 & 8883."
