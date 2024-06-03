# Working with Device Commands

## Publishing Commands to Devices

Applications can publish commands to connected devices.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.ParseConfigFile("app.yaml")
client = wiotp.sdk.application.ApplicationClient(options)

client.connect()
commandData={'rebootDelay' : 50}
client.publishCommand(myDeviceType, myDeviceId, "reboot", "json", commandData)
```


## Handling Commands

An application can subscribe to commands sent to devices to monitor the command channel, the application must explicitly subscribe to any commands it wishes to monitor. 


To process specific commands, you need to register a command callback method.

```python
def myCommandCallback(cmd):
    print("Command received: %s" % cmd.data)

client.commandCallback = myCommandCallback
```

The messages are returned as an instance of the `Command` class with the following attributes:

- `commandId`: Identifies the command
- `format`: Format that the command was encoded in, for example `json`
- `data`: Data for the payload converted to a Python dict by an impleentation of `MessageCodec`
- `timestamp`: Date and time that the event was recieved (as `datetime.datetime` object)

If a command is recieved in an unknown format or if a device does not recognize the format, the device library raises `wiotp.sdk.MissingMessageDecoderException`.
