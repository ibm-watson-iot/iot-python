<h1 id="ibmiotf.application.Client">Client</h1>

```python
Client(self, options, logHandlers=None)
```

Extends `ibmiotf.AbstractClient` to implement an application client supporting
messaging over MQTT

__Parameters__

- __options (dict)__: Configuration options for the client
- __logHandlers (list<logging.Handler>)__: Log handlers to configure.  Defaults to `None`,
    which will result in a default log handler being created.

__Configuration Options__

The options parameter expects a Python dictionary containing the following keys:

- `auth-key` The API key to to securely connect your application to Watson IoT Platform.
- `auth-token` An authentication token to securely connect your application to Watson IoT Platform.
- `clean-session` A boolean value indicating whether to use MQTT clean session.

<h2 id="ibmiotf.application.Client.subscribeToDeviceCommands">subscribeToDeviceCommands</h2>

```python
Client.subscribeToDeviceCommands(self, deviceType='+', deviceId='+', command='+', msgFormat='+')
```

Subscribe to device command messages

__Parameters__

- __deviceType (string)__: typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
- __deviceId (string)__: deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
- __command (string)__: commandId for the subscription, optional.  Defaults to all commands (MQTT `+` wildcard)
- __msgFormat (string)__: msgFormat for the subscription, optional.  Defaults to all formats (MQTT `+` wildcard)
- __qos (int)__: MQTT quality of service level to use (`0`, `1`, or `2`)

__Returns__

`int`: If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then the return value will be `0`

<h2 id="ibmiotf.application.Client.publishCommand">publishCommand</h2>

```python
Client.publishCommand(self, deviceType, deviceId, command, msgFormat, data=None, qos=0, on_publish=None)
```

Publish a command to a device

__Parameters__

- __deviceType (string) __: The type of the device this command is to be published to
- __deviceId (string)__: The id of the device this command is to be published to
- __command (string) __: The name of the command
- __msgFormat (string) __: The format of the command payload
- __data (dict) __: The command data
- __qos (int) __: The equivalent MQTT semantics of quality of service using the same constants (optional, defaults to `0`)
- __on_publish (function) __: A function that will be called when receipt of the publication is confirmed.  This has
- __different implications depending on the qos__:
- __- qos 0 __: the client has asynchronously begun to send the event
- __- qos 1 and 2 __: the client has confirmation of delivery from WIoTP

<h2 id="ibmiotf.application.Client.subscribeToDeviceStatus">subscribeToDeviceStatus</h2>

```python
Client.subscribeToDeviceStatus(self, deviceType='+', deviceId='+')
```

Subscribe to device status messages

__Parameters__

- __deviceType (string)__: typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
- __deviceId (string)__: deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)

__Returns__

`int`: If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then the return value will be `0`

<h2 id="ibmiotf.application.Client.subscribeToDeviceEvents">subscribeToDeviceEvents</h2>

```python
Client.subscribeToDeviceEvents(self, deviceType='+', deviceId='+', event='+', msgFormat='+', qos=0)
```

Subscribe to device event messages

__Parameters__

- __deviceType (string)__: typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
- __deviceId (string)__: deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
- __event (string)__: eventId for the subscription, optional.  Defaults to all events (MQTT `+` wildcard)
- __msgFormat (string)__: msgFormat for the subscription, optional.  Defaults to all formats (MQTT `+` wildcard)
- __qos (int)__: MQTT quality of service level to use (`0`, `1`, or `2`)

__Returns__

`int`: If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then the return value will be `0`

<h2 id="ibmiotf.application.Client.publishEvent">publishEvent</h2>

```python
Client.publishEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None)
```

Publish an event on behalf of a device.

__Parameters__

- __deviceType (string)__: The typeId of the device this event is to be published from
- __deviceId (string)__: The deviceId of the device this event is to be published from
- __event (string)__: The name of this event
- __msgFormat (string)__: The format of the data for this event
- __data (dict) __: The data for this event
- __qos (int) __: The equivalent MQTT semantics of quality of service using the same constants (optional, defaults to `0`)
- __on_publish (function) __: A function that will be called when receipt of the publication is confirmed.  This
- __has different implications depending on the qos__:
- __- qos 0 __: the client has asynchronously begun to send the event
- __- qos 1 and 2 __: the client has confirmation of delivery from IoTF

