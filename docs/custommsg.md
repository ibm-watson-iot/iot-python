# Custom Message Formats

By default, the client library support encoding and decoding events and commands as `json` messages.  To add support
for your own custom message formats you can create and register implementations of `wiotp.sdk.MessageCodec`.  MessageCodecs work for both commands and events.  To Implement a MessageCodec you must support two static class methods:

## Encoding

The job of the `encode(data, timestamp)` method is to take `data` (any python object) and optionally a `timestamp` (a `datetime.datetime` object) and 
return a String representation of the message ready to be sent over MQTT.


## Decoding

The job of `decode(message)` is to decode an incoming MQTT message and return an instance of `ibmiotf.Message`


## Sample Code

```python
import yaml
import wiotp.sdk.device
import wiotp.sdk.Message
import wiotp.sdk.MessageCodec

class YamlCodec(ibmiotf.MessageCodec):
    
    @staticmethod
    def encode(data=None, timestamp=None):
        return yaml.dumps(data)
    
    @staticmethod
    def decode(message):
        try:
            data = yaml.loads(message.payload.decode("utf-8"))
        except ValueError as e:
            raise InvalidEventException("Unable to parse YAML.  payload=\"%s\" error=%s" % (message.payload, str(e)))
        
        timestamp = datetime.now(pytz.timezone('UTC'))
        
        return wiotp.sdk.Message(data, timestamp)

myConfig = ibmiotf.device.ParseConfigFile("device.yaml")
client = ibmiotf.device.Client(config=myConfig, logHandlers=None)
client.setMessageCodec("yaml", YamlCodec)
myData = { 'hello' : 'world', 'x' : 100}

# Publish the same event, in both json and yaml formats:
client.publishEvent("status", "json", myData)
client.publishEvent("status", "yaml", myData)
```

If you want to lookup which encoder is set for a specific message format use the `getMessageEncoderModule(msgFormt)`.  If an event is sent/received in an unknown format or if a client does not recognize the format, the client library will raise `wiotp.sdk.MissingMessageEncoderException` or `wiotp.sdk.MissingMessageDecoderException`.