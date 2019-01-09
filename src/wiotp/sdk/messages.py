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
            raise InvalidEventException("Unable to parse JSON.  payload=\"%s\" error=%s" % (message.payload, str(e)))
        
        timestamp = datetime.now(pytz.timezone('UTC'))
        
        # TODO: Flatten JSON, covert into array of key/value pairs
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

