# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import testUtils
import wiotp.sdk
import pytest


class FakePahoMessageCommand:
    topic = "iot-2/type/typeid/id/deviceid/cmd/commandid/fmt/json"
    payload = b'{"a":4}'


class FakePahoMessageNotification:
    topic = "iot-2/type/typeid/id/deviceid/notify"
    payload = b'{"a":4}'


class TestGatewayMsg(testUtils.AbstractTest):
    def testCommand(self):
        # create pahoMessage
        pahoMessage = FakePahoMessageCommand()
        # Create messageEncoderModules
        messageEncoderModules = {"json": wiotp.sdk.JsonCodec()}
        # Creating instance of command
        command = wiotp.sdk.gateway.Command(pahoMessage, messageEncoderModules)
        assert command.typeId == "typeid"
        assert command.deviceId == "deviceid"
        assert command.commandId == "commandid"
        assert command.format == "json"
        assert "a" in command.data
        assert command.data["a"] == 4

    def testCommandMissingCodec(self):
        with pytest.raises(wiotp.sdk.MissingMessageDecoderException) as e:
            # create pahoMessage
            pahoMessage = FakePahoMessageCommand()
            # Create messageEncoderModules
            messageEncoderModules = {"fidaa": wiotp.sdk.JsonCodec()}
            # Creating instance of command
            command = wiotp.sdk.gateway.Command(pahoMessage, messageEncoderModules)
        assert e.value.format == "json"

    def testInvalidCommandTopic(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            # create pahoMessage
            pahoMessage = FakePahoMessageNotification()
            # Create messageEncoderModules
            messageEncoderModules = {"json": wiotp.sdk.JsonCodec()}
            # Creating instance of command
            command = wiotp.sdk.gateway.Command(pahoMessage, messageEncoderModules)
        assert e.value.reason == "Received command on invalid topic: iot-2/type/typeid/id/deviceid/notify"


class TestGatewayMsgNoti(testUtils.AbstractTest):
    def testNotification(self):
        # create pahoMessage
        pahoMessage = FakePahoMessageNotification()
        # Create messageEncoderModules
        messageEncoderModules = {"json": wiotp.sdk.JsonCodec()}
        # Creating instance of notification
        notification = wiotp.sdk.gateway.Notification(pahoMessage, messageEncoderModules)
        assert notification.typeId == "typeid"
        assert notification.deviceId == "deviceid"
        assert notification.format == "json"
        assert "a" in notification.data
        assert notification.data["a"] == 4

    def testNotificationMissingCodec(self):
        with pytest.raises(wiotp.sdk.MissingMessageDecoderException) as e:
            # create pahoMessage
            pahoMessage = FakePahoMessageNotification()
            # Create messageEncoderModules
            messageEncoderModules = {"fidaa": wiotp.sdk.JsonCodec()}
            # Creating instance of notification
            notification = wiotp.sdk.gateway.Notification(pahoMessage, messageEncoderModules)
        assert e.value.format == "json"

    def testInvalidNotificationTopic(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            # create pahoMessage
            pahoMessage = FakePahoMessageCommand()
            # Create messageEncoderModules
            messageEncoderModules = {"json": wiotp.sdk.JsonCodec()}
            # Creating instance of command
            notification = wiotp.sdk.gateway.Notification(pahoMessage, messageEncoderModules)
        assert (
            e.value.reason
            == "Received notification on invalid topic: iot-2/type/typeid/id/deviceid/cmd/commandid/fmt/json"
        )
