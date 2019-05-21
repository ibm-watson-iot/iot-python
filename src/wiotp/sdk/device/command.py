# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import re
from datetime import datetime
from wiotp.sdk import InvalidEventException, MissingMessageEncoderException, MissingMessageDecoderException


class Command:
    """
    Represents a command sent to a device.
    
    # Parameters
    pahoMessage (?): ?
    messageEncoderModules (dict): Dictionary of Python modules, keyed to the 
        message format the module should use. 
    
    # Attributes
    command (string): Identifies the command.
    format (string): The format can be any string, for example JSON.
    data (dict): The data for the payload. Maximum length is 131072 bytes.
    timestamp (datetime): The date and time of the event.

    # Raises
    InvalidEventException: If the command was recieved on a topic that does 
        not match the regular expression `iot-2/cmd/(.+)/fmt/(.+)`
    """

    _TOPIC_REGEX = re.compile("iot-2/cmd/(.+)/fmt/(.+)")

    def __init__(self, pahoMessage, messageEncoderModules):
        result = Command._TOPIC_REGEX.match(pahoMessage.topic)
        if result:
            self.commandId = result.group(1)
            self.format = result.group(2)

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))
