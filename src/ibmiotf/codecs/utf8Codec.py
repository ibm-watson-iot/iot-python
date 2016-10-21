'''
This is the default encoder used by clients for all messages sent with format
defined as "text" or "xml".  This default can be changed by reconfiguring your client:

  deviceCli.setMessageEncoderModule("text", utf8Codec)

'''
from datetime import datetime
import pytz
from ibmiotf import Message, InvalidEventException

'''
Convert data into a UTF-8 encoded string.  Timestamp information is
not passed into the encoded message.
'''
def encode(data=None,timestamp=None):
    return data.encode('utf-8')

'''
Convert UTF-8 encoded string to text message

* The message payload is converted to text and treated as the message data
* The timestamp of the message is the time that the message is RECEIVED
'''
def decode(message):
    try:
        data = message.payload.decode("utf-8")
    except ValueError as e:
        raise InvalidEventException("Unable to parse text message.  payload=\"%s\" error=%s" % (message.payload, str(e)))

    timestamp = datetime.now(pytz.timezone('UTC'))

    return Message(data, timestamp)
