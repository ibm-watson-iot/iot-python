'''
This is the default encoder used by clients for all messages sent with format 
defined as "json".  This default can be changed by reconfiguring your client:
  
  deviceCli.setMessageEncoderModule("json", myCustomEncoderModule)

'''
import json
from datetime import datetime
import pytz
from ibmiotf import Message, InvalidEventException

'''
Convert Python dictionary object into a UTF-8 encoded JSON string.  Timestamp information is
not passed into the encoded message.
'''
def encode(data=None, timestamp=None):
    return json.dumps(data)

'''
Convert a generic JSON message

* The entire message is converted to JSON and treated as the message data
* The timestamp of the message is the time that the message is RECEIVED
'''
def decode(message):
    try:
        data = json.loads(message.payload.decode("utf-8"))
    except ValueError as e:
        raise InvalidEventException("Unable to parse JSON.  payload=\"%s\" error=%s" % (message.payload, str(e)))
    
    timestamp = datetime.now(pytz.timezone('UTC'))
    
    # TODO: Flatten JSON, covert into array of key/value pairs
    return Message(data, timestamp)
