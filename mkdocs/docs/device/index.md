# Device SDK

The `wiotp.sdk.device` package contains the following:

Two client implementations:

- `wiotp.sdk.device.DeviceClient`
- `wiotp.sdk.device.ManagedDeviceClient`

Support classes for working with the data model:

- `wiotp.sdk.device.Command`
- `wiotp.sdk.device.DeviceInfo`
- `wiotp.sdk.device.DeviceFirmware`

Support methods for handling device configuration:

- `wiotp.sdk.device.parseConfigFile`
- `wiotp.sdk.device.parseEnvVars`


## Configuration

Device configuration is passed to the client via the `config` parameter when you create the client instance.  See the [configure devices](config.md) section for full details of all available options, and the built-in support for YAML file and environment variable sourced configuration.

```python
myConfig = { 
    "identity": {
        "orgId": "org1id",
        "typeId": "raspberry-pi-3"
        "deviceId": "00ef08ac05"
    }.
    "auth" {
        "token": "Ab$76s)asj8_s5"
    }
}
client = wiotp.sdk.device.DeviceClient(config=myConfig)
```


## Connectivity

`connect()` & `disconnect()` methods are used to manage the MQTT connection to IBM Watson IoT Platform that allows the device to 
handle commands and publish events.


## Publishing Events

Events are the mechanism by which devices publish data to the Watson IoT Platform. The device
controls the content of the event and assigns a name for each event that it sends.

When an event is received by Watson IoT Platform, the credentials of the received event identify
the sending device, which means that a device cannot impersonate another device.

Events can be published with any of the three quality of service (QoS) levels that are defined
by the MQTT protocol. By default, events are published with a QoS level of 0.

`publishEvent()` takes up to 5 arguments:

- `eventId` Name of this event
- `msgFormat` Format of the data for this event
- `data` Data for this event
- `qos` MQTT quality of service level to use (`0`, `1`, or `2`)
- `onPublish` A function that will be called when receipt of the publication is confirmed.

__Callback and QoS__

The use of the optional `onPublish` function has different implications depending
on the level of qos used to publish the event:

- qos 0: the client has asynchronously begun to send the event
- qos 1 and 2: the client has confirmation of delivery from the platform

```python
def eventPublishCallback():
    print("Device Publish Event done!!!")

client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=eventPublishCallback)
```


## Handling Commands

When the device client connects, it automatically subscribes to any command that is specified for
this device. To process specific commands, you need to register a command callback method.

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

If a command is recieved in an unknown format or if a device does not recognize the format, the device
library raises `wiotp.sdk.MissingMessageDecoderException`.


## Sample Code

```python
import wiotp.sdk.device

def myCommandCallback(cmd):
    print("Command received: %s" % cmd.data)

# Configure
myConfig = wiotp.sdk.device.parseConfigFile("device.yaml")
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.commandCallback = myCommandCallback

# Connect
client.connect()

# Send Data
myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)

# Disconnect
client.disconnect()
```
