# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import re
from wiotp.sdk import MissingMessageDecoderException, InvalidEventException

COMMAND_RE = re.compile("iot-2/type/(.+)/id/(.+)/cmd/(.+)/fmt/(.+)")


class Command:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = COMMAND_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.commandId = result.group(3)
            self.format = result.group(4)

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))


NOTIFY_RE = re.compile("iot-2/type/(.+)/id/(.+)/notify")


class Notification:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = NOTIFY_RE.match(pahoMessage.topic)
        if result:
            self.typeId = result.group(1)
            self.deviceId = result.group(2)
            self.format = "json"

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received notification on invalid topic: %s" % (pahoMessage.topic))
