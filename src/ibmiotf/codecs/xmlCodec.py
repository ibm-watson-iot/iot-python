'''
This is the default encoder used by clients for all messages sent with format
defined as "xml".  This default can be changed by reconfiguring your client:

  deviceCli.setMessageEncoderModule("xml", myCustomEncoderModule)

'''
import json
import dicttoxml
import xmltodict
from datetime import datetime
import pytz
from ibmiotf import Message, InvalidEventException

'''
Convert Python dictionary object into a UTF-8 encoded XML string.  Timestamp information is
not passed into the encoded message.
'''
def encode(data=None, timestamp=None):
    return dicttoxml.dicttoxml(data)

'''
Convert XML data into Python Dictionary Object
The entire message is converted to JSON and treated as the message data
The timestamp of the message is the time that the message is RECEIVED
'''
def decode(message):
    try:
        jsonData = json.dumps(xmltodict.parse(message.payload))
        data = json.loads(jsonData.decode("utf-8"))
    except ValueError as e:
        raise InvalidEventException("Unable to parse XML.  payload=\"%s\" error=%s" % (message.payload, str(e)))
    timestamp = datetime.now(pytz.timezone('UTC'))
    return Message(data, timestamp)
