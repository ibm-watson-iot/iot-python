# Gateway SDK

The `wiotp.sdk.gateway` package contains the following:

Two client implementations:

- `wiotp.sdk.gateway.GatewayClient`
- `wiotp.sdk.gateway.ManagedGatewayClient`

Support classes for working with the data model:

- `wiotp.sdk.gateway.Command`
- `wiotp.sdk.gateway.Notification`
- `wiotp.sdk.gateway.DeviceInfo`
- `wiotp.sdk.gateway.DeviceFirmware`

Support methods for handling device configuration:

- `wiotp.sdk.gateway.parseConfigFile`
- `wiotp.sdk.gateway.parseEnvVars`


## Configuration

Gateway configuration is passed to the client via the `config` parameter when you create the client instance.  See the [configure gateways](config.md) section for full details of all available options, and the built-in support for YAML file and environment variable sourced configuration.

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
client = wiotp.sdk.gateway.GatewayClient(config=myConfig)
```


## Connectivity

`connect()` & `disconnect()` methods are used to manage the MQTT connection to IBM Watson IoT Platform that allows the gateway to 
handle commands and publish events.


## Publishing Events

Events are the mechanism by which devices & gateway publish data to the Watson IoT Platform. The gateway
controls the content of the event and assigns a name for each event that it sends.

Events can be published with any of the three quality of service (QoS) levels that are defined
by the MQTT protocol. By default, events are published with a QoS level of 0.

`publishEvent()` takes up to 5 arguments and submits an event from the gateway itself:

- `eventId` Name of this event
- `msgFormat` Format of the data for this event
- `data` Data for this event
- `qos` MQTT quality of service level to use (`0`, `1`, or `2`)
- `onPublish` A function that will be called when receipt of the publication is confirmed.

`publishDeviceEvent()` takes up to 7 arguments and submits an event from a device connected to the gateway, rather than the gateway itself:

- `typeId` Type ID of the device connected to this gateway that the event belongs to
- `deviceId` Device ID of the device connected to this gateway that the event belongs to
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

Unlike devices, When the gateway client connects, it does **not** automatically subscribes to any commands. To 
process specific commands, you need to explicitly subscribe as well as registering a command callback method.

The messages are returned as an instance of the `Command` class with the following attributes:

- `typeId`: Identifies the typeId of the device the command is directed at
- `eventId`: Identifies the deviceId of the device the command is directed at
- `commandId`: Identifies the commandId
- `format`: Format that the command was encoded in, for example `json`
- `data`: Data for the payload converted to a Python dict by an impleentation of `MessageCodec`
- `timestamp`: Date and time that the event was recieved (as `datetime.datetime` object)

If a command is recieved in an unknown format or if the gateway does not recognize the format, the gateway
library raises `wiotp.sdk.MissingMessageDecoderException`.


## Sample Code

```python
import wiotp.sdk.gateway

def myCommandCallback(cmd):
    print("Command received for %s:%s: %s" % (cmd.typeId, cmd.deviceId, cmd.data))

# Configure
myConfig = wiotp.sdk.gateway.parseConfigFile("gateway.yaml")
client = wiotp.sdk.gateway.GatewayClient(config=myConfig, logHandlers=None)
client.commandCallback = myCommandCallback

# Connect
client.connect()

# Send data on behalf of the gateway itself
myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)

# Send data on behalf of a device connected to this gateway
aDeviceData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(eventId="status", msgFormat="json", data=aDeviceData, qos=0, onPublish=None)

# Disconnect
client.disconnect()
```
