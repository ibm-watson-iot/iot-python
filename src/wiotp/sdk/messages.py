# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
import pytz
from datetime import datetime
from wiotp.sdk.exceptions import InvalidEventException


class MessageCodec(object):
    @staticmethod
    def encode(data=None, timestamp=None):
        raise NotImplementedError()

    @staticmethod
    def decode(message):
        raise NotImplementedError()


class JsonCodec(MessageCodec):
    """
    This is the default encoder used by clients for all messages sent with format 
    defined as "json".  This default can be changed by reconfiguring your client:
      
      deviceCli.setMessageCodec("json", myCustomEncoderModule)
    """

    @staticmethod
    def encode(data=None, timestamp=None):
        """
        Convert Python dictionary object into a UTF-8 encoded JSON string.  Timestamp information is
        not passed into the encoded message.
        """
        return json.dumps(data)

    @staticmethod
    def decode(message):
        """
        Convert a generic JSON message
        
        * The entire message is converted to JSON and treated as the message data
        * The timestamp of the message is the time that the message is RECEIVED
        """
        try:
            data = json.loads(message.payload.decode("utf-8"))
        except ValueError as e:
            raise InvalidEventException('Unable to parse JSON.  payload="%s" error=%s' % (message.payload, str(e)))

        timestamp = datetime.now(pytz.timezone("UTC"))

        # TODO: Flatten JSON, covert into array of key/value pairs
        return Message(data, timestamp)


class RawCodec(MessageCodec):
    """
    Support sending and receiving bytearray, useful for transmitting raw data files.  This is the default encoder used by clients for all messages sent with format 
    defined as "raw".  This default can be changed by reconfiguring your client:
      
      deviceCli.setMessageCodec("raw", myCustomEncoderModule)
    """

    @staticmethod
    def encode(data=None, timestamp=None):
        # str is just an immutable bytearray at the end of the day!
        if not isinstance(data, (bytes, bytearray)):
            raise InvalidEventException("Unable to encode data, it is not a bytearray")
        return data

    @staticmethod
    def decode(message):
        if not isinstance(message.payload, (bytearray)):
            raise InvalidEventException("Unable to decode message, it is not a bytearray")

        data = message.payload

        timestamp = datetime.now(pytz.timezone("UTC"))

        return Message(data, timestamp)


class Utf8Codec(MessageCodec):
    """
    Support sending and receiving simple UTF-8 strings.  This is the default encoder used by clients for all messages sent with format 
    defined as "utf8".  This default can be changed by reconfiguring your client:
      
      deviceCli.setMessageCodec("utf8", myCustomEncoderModule)
    """

    @staticmethod
    def encode(data=None, timestamp=None):
        if not isinstance(data, str):
            raise InvalidEventException("Unable to encode data, it is not a string")
        return data.encode("UTF-8")

    @staticmethod
    def decode(message):
        try:
            data = message.payload.decode("UTF-8")
        except Exception as e:
            raise InvalidEventException(
                'Unable to decode event to UTF-8 string.  payload="%s" error=%s' % (message.payload, str(e))
            )

        timestamp = datetime.now(pytz.timezone("UTC"))

        return Message(data, timestamp)


class Message:
    """
    Represents an abstract message recieved over Mqtt.  All implementations of 
    a Codec must return an object of this type.
    
    # Attributes
    data (dict): The message payload
    timestamp (datetime): Timestamp intended to denote the time the message was sent, 
        or `None` if this information is not available. 
    
    """

    def __init__(self, data, timestamp=None):
        self.data = data
        self.timestamp = timestamp
