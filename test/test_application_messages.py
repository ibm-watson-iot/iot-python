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

class FakeMessageStatus():
    topic = "iot-2/type/typeid/id/deviceid/mon"
    payload = b'{"a":4}'
    retain = False

class FakePahoMessageEvent(): 
    topic = "iot-2/type/1/id/2/evt/3/fmt/json"
    payload = b'{"a":4}'

class FakePahoMessageCommand(): 
    topic = "iot-2/type/typeid/id/deviceid/cmd/commandid/fmt/json"
    payload = b'{"a":4}'





class TestApplicationMsgStat(testUtils.AbstractTest):
    def testStatus (self):
        message = FakeMessageStatus()
        status = wiotp.sdk.application.Status(message)
        assert (status.typeId == "typeid")
        assert (status.deviceId == "deviceid")

    def invalidEventException(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            message = FakePahoMessageEvent()
            status = wiotp.sdk.application.Status(message)
        assert e.value.reason == "Received device status on invalid topic: iot-2/type/1/id/2/evt/3/fmt/json"
        assert str(e.value) == "Invalid Event: iot-2/type/1/id/2/evt/3/fmt/json"





class TestApplicationMsgEv(testUtils.AbstractTest):
    def testEvent (self):
        pahoMessage = FakePahoMessageEvent()
        messageEncoderModules = {"json":wiotp.sdk.JsonCodec()}
        event = wiotp.sdk.application.Event(pahoMessage, messageEncoderModules)
        assert (event.typeId == "1")
        assert (event.deviceId == "2")
        assert (event.eventId == "3")
        assert (event.format == "json")

    def testEventMissingCodec(self):
        with pytest.raises(wiotp.sdk.MissingMessageDecoderException) as e:
            pahoMessage = FakePahoMessageEvent()
            messageEncoderModules = {"fidaa":wiotp.sdk.JsonCodec()}
            event = wiotp.sdk.application.Event(pahoMessage, messageEncoderModules)
        assert e.value.format == 'json'
        assert str(e.value) == "No message decoder defined for message format: json"

    def testInvalidEventTopic(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            pahoMessage = FakeMessageStatus()
            messageEncoderModules = {"json":wiotp.sdk.JsonCodec()}
            event = wiotp.sdk.application.Event(pahoMessage, messageEncoderModules)
        assert e.value.reason == "Received device event on invalid topic: iot-2/type/typeid/id/deviceid/mon"





class TestApplicationMsgCom(testUtils.AbstractTest):
    def testCommand ( self):
        pahoMessage = FakePahoMessageCommand()
        messageEncoderModules = {"json":wiotp.sdk.JsonCodec()}
        command = wiotp.sdk.application.Command(pahoMessage, messageEncoderModules)
        assert (command.typeId == "typeid")
        assert (command.deviceId == "deviceid")
        assert (command.commandId == "commandid") 
        assert (command.format == "json")
        assert ( "a" in command.data)
        assert (command.data["a"] == 4)

    def testCommandMissingCodec(self):
        with pytest.raises(wiotp.sdk.MissingMessageDecoderException) as e:
            pahoMessage = FakePahoMessageCommand()
            messageEncoderModules = {"fidaa":wiotp.sdk.JsonCodec()}
            command = wiotp.sdk.application.Command(pahoMessage, messageEncoderModules)
        assert e.value.format == 'json' 

    def testInvalidCommandTopic(self):
        with pytest.raises(wiotp.sdk.InvalidEventException) as e:
            pahoMessage = FakePahoMessageEvent()
            messageEncoderModules = {"json":wiotp.sdk.JsonCodec()}
            command = wiotp.sdk.application.Command(pahoMessage, messageEncoderModules)
        assert e.value.reason == "Received device event on invalid topic: iot-2/type/1/id/2/evt/3/fmt/json"