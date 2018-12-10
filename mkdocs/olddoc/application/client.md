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

Parameters
----------
deviceType : string, optional
deviceId : string, optional
command: string, optional
msfFormat : string, optional

Returns
-------
int
    If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then `None` will be returned.

<h2 id="ibmiotf.application.Client.publishCommand">publishCommand</h2>

```python
Client.publishCommand(self, deviceType, deviceId, command, msgFormat, data=None, qos=0, on_publish=None)
```

Publish a command to a device

Parameters
----------
deviceType : string
    The type of the device this command is to be published to
deviceId : string
    The id of the device this command is to be published to
command : string
    The name of the command
msgFormat : string
    The format of the command payload
data: dict
    The command data
qos: {0, 1, 2}, optional
    The equivalent MQTT semantics of quality of service using the same constants (defaults to `0`)
on_publish : function
    A function that will be called when receipt of the publication is confirmed.  This has
    different implications depending on the qos:
    - qos 0 : the client has asynchronously begun to send the event
    - qos 1 and 2 : the client has confirmation of delivery from WIoTP

<h2 id="ibmiotf.application.Client.on_connect">on_connect</h2>

```python
Client.on_connect(self, client, userdata, flags, rc)
```

This is called after the client has received a CONNACK message from the broker
in response to calling connect().

Parameters
----------
client : ?
userdata : ?
flags : ?
rc : {0,1,2,3,4,5}
    An integer giving the return code:
    0: Success
    1: Refused - unacceptable protocol version
    2: Refused - identifier rejected
    3: Refused - server unavailable
    4: Refused - bad user name or password (MQTT v3.1 broker only)
    5: Refused - not authorised (MQTT v3.1 broker only)

<h2 id="ibmiotf.application.Client.subscribeToDeviceStatus">subscribeToDeviceStatus</h2>

```python
Client.subscribeToDeviceStatus(self, deviceType='+', deviceId='+')
```

Subscribe to device status messages

Parameters
----------
deviceType : string, optional
deviceId : string, optional

Returns
-------
int
    If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then the return value will be `0`

<h2 id="ibmiotf.application.Client.subscribeToDeviceEvents">subscribeToDeviceEvents</h2>

```python
Client.subscribeToDeviceEvents(self, deviceType='+', deviceId='+', event='+', msgFormat='+', qos=0)
```

Subscribe to device event messages

Parameters
----------
deviceType : string, optional
deviceId : string, optional
event: string, optional
msfFormat : string, optional
qos: {0, 1, 2}

Returns
-------
int
    If the subscription was successful then the return Message ID (mid) for the subscribe request
    will be returned. The mid value can be used to track the subscribe request by checking against
    the mid argument if you register a subscriptionCallback method.
    If the subscription fails then the return value will be `0`

<h2 id="ibmiotf.application.Client.publishEvent">publishEvent</h2>

```python
Client.publishEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None)
```

Publish an event in IoTF as if the application were a device.

Parameters
----------
deviceType : string
    The type of the device this event is to be published from
deviceId : string
    The id of the device this event is to be published from
event : string
    The name of this event
msgFormat : string
    The format of the data for this event
data : string
    The data for this event
qos : {0, 1, 2}, optional
    The equivalent MQTT semantics of quality of service using the same constants (defaults to `0`)
on_publish : function
    A function that will be called when receipt of the publication is confirmed.  This
    has different implications depending on the qos:
    - qos 0 : the client has asynchronously begun to send the event
    - qos 1 and 2 : the client has confirmation of delivery from IoTF

