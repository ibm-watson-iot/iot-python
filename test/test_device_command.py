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
    topic = "iot-2/cmd/commandid/fmt/json"
    payload = b'{"a":4}'


class FakeFakePahoMessageCommand:
    topic = "hi"
    payload = b'{"a":4}'


class TestDeviceCommand(testUtils.AbstractTest):
    def testCommand(self):
        pahoMessage = FakePahoMessageCommand()
        messageEncoderModules = {"json": wiotp.sdk.JsonCodec()}
        command = wiotp.sdk.device.Command(pahoMessage, messageEncoderModules)
        assert command.format == "json"
        assert command.commandId == "commandid"
        assert "a" in command.data
        assert command.data["a"] == 4

    def testCommandMissingCodec(self):
        with pytest.raises(wiotp.sdk.MissingMessageDecoderException) as e:
            pahoMessage = FakePahoMessageCommand()
            messageEncoderModules = {"fidaa": wiotp.sdk.JsonCodec()}
            command = wiotp.sdk.device.Command(pahoMessage, messageEncoderModules)
        assert e.value.format == "json"

    def testInvalidCommandTopic(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            pahoMessage = FakeFakePahoMessageCommand()
            messageEncoderModules = {"b": wiotp.sdk.JsonCodec()}
            command = wiotp.sdk.device.Command(pahoMessage, messageEncoderModules)
        assert e.value.reason == "Received command on invalid topic: hi"
