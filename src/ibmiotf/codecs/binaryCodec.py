'''
This is the default encoder used by clients for all messages sent with format
defined as "binary".  This default can be changed by reconfiguring your client:

  deviceCli.setMessageEncoderModule("bin", binaryCodec)

'''
from datetime import datetime
import pytz
import base64
from ibmiotf import Message, InvalidEventException

'''
Convert Python dictionary object into a Base64 encoded string.  Timestamp information is
not passed into the encoded message.
'''
def encode(data=None,timestamp=None):
    return base64.b64encode(data)


'''
Convert Base64 encoded string back to binary

* The message.payload is converted back to binary and treated as the message data
* The timestamp of the message is the time that the message is RECEIVED
'''
def decode(message):
    try:
        data = base64.b64decode(message.payload)
    except ValueError as e:
        raise InvalidEventException("Error while decoding base64 string.  payload=\"%s\" error=%s" % (message.payload, str(e)))

    timestamp = datetime.now(pytz.timezone('UTC'))

    return Message(data, timestamp)
