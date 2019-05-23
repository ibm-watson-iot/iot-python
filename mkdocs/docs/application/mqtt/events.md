# Working with Device Events

## Publishing Device Events

Events are the mechanism by which devices publish data to the Watson IoT Platform. The device controls the content of the event and assigns a name for each event that it sends.  **Depending on the permissions set in the API key that your application connects with** your application will have the ability to publish events as if they originated from any registered device.

As with devices, events can be published with any of the three quality of service (QoS) levels that are defined by the MQTT protocol. By default, events are published with a QoS level of 0.

`publishEvent()` takes up to 5 arguments:

- `event` Name of this event
- `msgFormat` Format of the data for this event
- `data` Data for this event
- `qos` MQTT quality of service level to use (`0`, `1`, or `2`)
- `on_publish` A function that will be called when receipt of the publication is confirmed.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.ParseConfigFile("app.yaml")
client = wiotp.sdk.application.ApplicationClient(options)

client.connect()
myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(myDeviceType, myDeviceId, "status", "json", myData)
```

__Callback and QoS__

The use of the optional `on_publish` function has different implications depending on the level of qos used to publish the event:

- qos 0: the client has asynchronously begun to send the event
- qos 1 and 2: the client has confirmation of delivery from the platform


```python
def eventPublishCallback():
    print("Device Publish Event done!!!")

client.publishEvent(typeId="foo", deviceId="bar", eventId="status", msgFormat="json", data=myData, qos=0, onPublish=eventPublishCallback)
```


## Subscribing to Device Events

`subscribeToDeviceEvents()` allows the application to recieve real-time device events as they are published.  With no parameters provided the method would subscribe the application to all events from all connected devices. In most use cases this is **not** what you want to do.  Use the optional `typeId`, `deviceId`, `eventId`, and `msgFormat` parameters to control the scope of the subscription. 

A single client can support multiple subscriptions. The following code samples show how you can use deviceType, deviceId, event, and msgFormat parameters to define the scope of a subscription:


```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseConfigFile("app.yaml")
client = wiotp.sdk.application.ApplicationClient(options)

client.connect()

# Subscribing to all events from all devices
client.subscribeToDeviceEvents()

# Subscribing to all events from all devices of a specific type
client.subscribeToDeviceEvents(typeId=myDeviceType)

# Subscribing to a specific event from all devices
client.subscribeToDeviceEvents(eventId=myEvent)

# Subscribing to a specific event from two or more different devices
client.subscribeToDeviceEvents(typeId=myDeviceType, deviceId=myDeviceId, eventId=myEvent)
client.subscribeToDeviceEvents(typeId=myOtherDeviceType, eventId=myEvent)

# Subscribing to all events that are published in JSON format
client.subscribeToDeviceEvents(msgFormat="json")
```

## Handling Device Events
To process the events that are received by your subscriptions, you need to register an event callback method. The messages are returned as an instance of the Event class:

- `event.eventId`	Typically used to group specific events, for example "status", "warning" and "data".
- `event.typeId` Identifies the device type. Typically, the deviceType is a grouping for devices that perform a specific task, for example "weatherballoon".
- `event.deviceId` Represents the ID of the device. Typically, for a given device type, the deviceId is a unique identifier of that device, for example a serial number or MAC address.
- `event.device` Uniquely identifies the device across all types of devices in the organization
- `event.format` The format can be any string, for example JSON.
- `event.data` The data for the message payload.
- `event.timestamp`	The date and time of the event

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseConfigFile("app.yaml")
client = wiotp.sdk.application.ApplicationClient(options)

def myEventCallback(event):
    str = "%s event '%s' received from device [%s]: %s"
    print(str % (event.format, event.eventId, event.device, json.dumps(event.data)))

client.connect()
client.deviceEventCallback = myEventCallback
client.subscribeToDeviceEvents()
```
