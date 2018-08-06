# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
from datetime import datetime
import pytz
from ibmiotf import Message, InvalidEventException, MessageCodec

class JsonCodec(MessageCodec):
    """
    This is the default encoder used by clients for all messages sent with format 
    defined as "json".  This default can be changed by reconfiguring your client:
      
      deviceCli.setMessageEncoderModule("json", myCustomEncoderModule)
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
            raise InvalidEventException("Unable to parse JSON.  payload=\"%s\" error=%s" % (message.payload, str(e)))
        
        timestamp = datetime.now(pytz.timezone('UTC'))
        
        # TODO: Flatten JSON, covert into array of key/value pairs
        return Message(data, timestamp)
    

# Compatability support:
# Make old code using references to `ibmiotf.codecs.jsonCodec` carry on working without code modification
jsonCodec = JsonCodec
    