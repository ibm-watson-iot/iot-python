'''
This is the default encoder used by clients for all messages sent with format 
defined as "json-iotf".  This default can be changed by reconfiguring your client:
  
  deviceCli.setMessageEncoderModule("json-iotf", myCustomEncoderModule)

'''
import json
from datetime import datetime
import pytz
import iso8601
from ibmiotf import Message, InvalidEventException


'''
Convert a Python dictionary object into a UTF-8 encoded JSON string. The data is placed 
inside a top levle "d" element with a timestamp added to "ts".

* The entire message is converted to JSON
* The top level d element is considered as the message data
* The timestamp of the message is set to the value read from the ts element
* If no ts element is present the timestamp defaults to the time the message is received
'''
def encode(data=None, timestamp=None):
    ts = timestamp.isoformat()
    
    payload = { 'd': data, 'ts': ts }
    return json.dumps(payload)

'''
Convert a JSON message where all data is under a top level "d" element and an optional "ts" element exists, containing a timestamp for the message.

* The entire message is converted to JSON
* The top level d element is considered as the message data
* The timestamp of the message is set to the value read from the ts element
* If no ts element is present the timestamp defaults to the time the message is received
'''
def decode(message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except ValueError as e:
        raise InvalidEventException("Unable to parse JSON.  payload=\"%s\" error=%s" % (message.payload, str(e)))
        
    data = None
    timestamp = None
    
    # Try to parse a timestamp
    try:
        if 'ts' in payload:
            dt = iso8601.parse_date(payload['ts'])
            timestamp = dt.astimezone(pytz.timezone('UTC'))
        else:
            timestamp = datetime.now(pytz.timezone('UTC'))
    except iso8601.ParseError as e:
        raise InvalidEventException("Unable to parse event timestamp: %s" % str(e))

    # Try to parse the data
    if 'd' in payload:
        data = payload['d']
        
        # TODO: Flatten JSON, covert into array of key/value pairs
    
    return Message(data, timestamp)
