# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************
import iso8601
import json
import re
from wiotp.sdk import InvalidEventException, MissingMessageDecoderException

# Compile regular expressions for topic parsing
DEVICE_EVENT_RE = re.compile("iot-2/type/(.+)/id/(.+)/evt/(.+)/fmt/(.+)")
DEVICE_COMMAND_RE = re.compile("iot-2/type/(.+)/id/(.+)/cmd/(.+)/fmt/(.+)")
DEVICE_STATUS_RE = re.compile("iot-2/type/(.+)/id/(.+)/mon")
THING_STATE_RE = re.compile("iot-2/thing/type/(.+)/id/(.+)/intf/(.+)/evt/state")
DEVICE_STATE_RE = re.compile("iot-2/type/(.+)/id/(.+)/intf/(.+)/evt/state")
ERROR_TOPIC_RE = re.compile("iot-2/type/(.+)/id/(.+)/err/data")
THING_ERROR_RE = re.compile("iot-2/thing/type/(.+)/id/(.+)/err/data")
APP_STATUS_RE = re.compile("iot-2/app/(.+)/mon")


class Status:
    def __init__(self, message):
        result = DEVICE_STATUS_RE.match(message.topic)
        if result:
            self.payload = json.loads(message.payload.decode("utf-8"))
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.device = self.typeId + ":" + self.deviceId

            """
            Properties from the "Connect" status are common in "Disconnect" status too
            {
            u'ClientAddr': u'195.212.29.68',
            u'Protocol': u'mqtt-tcp',
            u'ClientID': u'd:bcaxk:psutil:001',
            u'User': u'use-token-auth',
            u'Time': u'2014-07-07T06:37:56.494-04:00',
            u'Action': u'Connect',
            u'ConnectTime': u'2014-07-07T06:37:56.493-04:00',
            u'Port': 1883
            }
            """

            self.clientAddr = self.payload["ClientAddr"] if ("ClientAddr" in self.payload) else None
            self.protocol = self.payload["Protocol"] if ("Protocol" in self.payload) else None
            self.clientId = self.payload["ClientID"] if ("ClientID" in self.payload) else None
            self.user = self.payload["User"] if ("User" in self.payload) else None
            self.time = iso8601.parse_date(self.payload["Time"]) if ("Time" in self.payload) else None
            self.action = self.payload["Action"] if ("Action" in self.payload) else None
            self.connectTime = (
                iso8601.parse_date(self.payload["ConnectTime"]) if ("ConnectTime" in self.payload) else None
            )
            self.port = self.payload["Port"] if ("Port" in self.payload) else None

            """
            Additional "Disconnect" status properties
            {
            u'WriteMsg': 0,
            u'ReadMsg': 872,
            u'Reason': u'The connection has completed normally.',
            u'ReadBytes': 136507,
            u'WriteBytes': 32,
            }
            """
            self.writeMsg = self.payload["WriteMsg"] if ("WriteMsg" in self.payload) else None
            self.readMsg = self.payload["ReadMsg"] if ("ReadMsg" in self.payload) else None
            self.reason = self.payload["Reason"] if ("Reason" in self.payload) else None
            self.readBytes = self.payload["ReadBytes"] if ("ReadBytes" in self.payload) else None
            self.writeBytes = self.payload["WriteBytes"] if ("WriteBytes" in self.payload) else None
            self.closeCode = self.payload["CloseCode"] if ("CloseCode" in self.payload) else None
            self.retained = message.retain

        else:
            raise InvalidEventException("Received device status on invalid topic: %s" % (message.topic))


class Event:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = DEVICE_EVENT_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.device = self.typeId + ":" + self.deviceId

            self.eventId = result.group(3)
            self.format = result.group(4)

            self.payload = pahoMessage.payload

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received device event on invalid topic: %s" % (pahoMessage.topic))


class Command:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = DEVICE_COMMAND_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.device = self.typeId + ":" + self.deviceId

            self.commandId = result.group(3)
            self.format = result.group(4)

            self.payload = pahoMessage.payload

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received device event on invalid topic: %s" % (pahoMessage.topic))


class State:
    def __init__(self, pahoMessage):
        result = THING_STATE_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.thingId = result.group(2)
            self.thing = self.typeId + ":" + self.thingId

            self.logicalInterfaceId = result.group(3)
            self.payload = pahoMessage.payload
        else:
            raise InvalidEventException("Received thing state on invalid topic: %s" % (pahoMessage.topic))


class DeviceState:
    def __init__(self, pahoMessage):
        result = DEVICE_STATE_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.device = self.typeId + ":" + self.deviceId

            self.logicalInterfaceId = result.group(3)
            self.payload = pahoMessage.payload
        else:
            raise InvalidEventException("Received device state on invalid topic: %s" % (pahoMessage.topic))


class Error:
    def __init__(self, pahoMessage):
        result = ERROR_TOPIC_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.id = result.group(2)
            self.source = self.typeId + ":" + self.id
            self.payload = pahoMessage.payload
        else:
            raise InvalidEventException("Received error message on invalid topic: %s" % (pahoMessage.topic))


class ThingError:
    def __init__(self, pahoMessage):
        result = ERROR_TOPIC_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.id = result.group(2)
            self.source = self.typeId + ":" + self.id
            self.payload = pahoMessage.payload
        else:
            raise InvalidEventException("Received error message on invalid topic: %s" % (pahoMessage.topic))
