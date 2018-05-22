<h1 id="ibmiotf">ibmiotf</h1>


<h2 id="ibmiotf.AbstractClient">AbstractClient</h2>

```python
AbstractClient(self, domain, organization, clientId, username, password, port=8883, logHandlers=None, cleanSession='true', transport='tcp')
```

Represents an abstract message recieved over Mqtt.  All implementations of a Codec must return an object of this type.

__Parameters__

- __domain (string)__: Domain denoting the instance of IBM Watson IoT Platform to connect to
- __organization (string)__: IBM Watson IoT Platform organization ID to connect to
- __clientId (string)__: MQTT clientId for the underlying Paho client
- __username (string)__: MQTT username for the underlying Paho client
- __password (string)__: MQTT password for the underlying Paho client
- __port (int)__: MQTT port for the underlying Paho client to connect using.  Defaults to `8883`
- __logHandlers (list<logging.Handler>)__: Log handlers to configure.  Defaults to `None`,
    which will result in a default log handler being created.
- __cleanSession (string)__: Defaults to `true`.  Although this is a true|false parameter,
    it is being handled as a string for some reason
- __transport (string)__: Defaults to `tcp`

__Attributes__

- `client (paho.mqtt.client.Client)`: Built-in Paho MQTT client handling connectivity for the client.
- `logger (logging.logger)`: Client logger.

<h3 id="ibmiotf.AbstractClient.stats">stats</h3>

```python
AbstractClient.stats(self)
```

I think we killed the use of this and this is dead code

TODO: clean all this up .. should we really be tracking these stats within the client itself in the first place?

<h3 id="ibmiotf.AbstractClient.getMessageEncoderModule">getMessageEncoderModule</h3>

```python
AbstractClient.getMessageEncoderModule(self, messageFormat)
```

Get the Python module that is currently defined as the encoder/decoder for a specified message format.

__Arguments__

- __messageFormat (string)__: The message format to retrieve the encoder for

__Returns__

`Boolean`: The python module, or `None` if there is no codec defined for the `messageFormat`

<h3 id="ibmiotf.AbstractClient.logAndRaiseException">logAndRaiseException</h3>

```python
AbstractClient.logAndRaiseException(self, e)
```

Logs an exception at log level `critical` before raising it.

__Arguments__

- __e (Exception)__: The exception to log/raise

<h3 id="ibmiotf.AbstractClient.setMessageEncoderModule">setMessageEncoderModule</h3>

```python
AbstractClient.setMessageEncoderModule(self, messageFormat, module)
```

Set a Python module as the encoder/decoder for a specified message format.

__Arguments__

- __messageFormat (string)__: The message format to retreive the encoder for
- __module (module)__: The Python module to set as the encoder/decoder for `messageFormat`

<h3 id="ibmiotf.AbstractClient.on_disconnect">on_disconnect</h3>

```python
AbstractClient.on_disconnect(self, mqttc, obj, rc)
```

Called when the client disconnects from IBM Watson IoT Platform.

__Parameters__

- __mqttc (paho.mqtt.client.Client)__: The client instance for this callback
- __obj (?)__: The private user data as set in Client() or user_data_set()
- __rc (int)__: indicates the disconnection state.  If `MQTT_ERR_SUCCESS` (0), the callback was
    called in response to a `disconnect()` call. If any other value the disconnection was
    unexpected, such as might be caused by a network error.

- __See https__://github.com/eclipse/paho.mqtt.python#on_disconnect for more information

<h3 id="ibmiotf.AbstractClient.connect">connect</h3>

```python
AbstractClient.connect(self)
```

Connect the client to IBM Watson IoT Platform using the underlying Paho MQTT client

__Raises__

- `ConnectionException`: If there is a problem establishing the connection.

<h3 id="ibmiotf.AbstractClient.disconnect">disconnect</h3>

```python
AbstractClient.disconnect(self)
```

Disconnect the client from IBM Watson IoT Platform

<h3 id="ibmiotf.AbstractClient.on_log">on_log</h3>

```python
AbstractClient.on_log(self, mqttc, obj, level, string)
```

Called when the client has log information.

__Parameters__

- __mqttc (paho.mqtt.client.Client)__: The client instance for this callback
- __obj (?)__: The private user data as set in Client() or user_data_set()
- __level (int)__: The severity of the message, will be one of `MQTT_LOG_INFO`,
    `MQTT_LOG_NOTICE`, `MQTT_LOG_WARNING`, `MQTT_LOG_ERR`, and `MQTT_LOG_DEBUG`.
- __string (string)__: The log message itself

- __See https__://github.com/eclipse/paho.mqtt.python#on_log for more information

<h2 id="ibmiotf.Message">Message</h2>

```python
Message(self, data, timestamp=None)
```

Represents an abstract message recieved over Mqtt.  All implementations of a Codec must return an object of this type.

__Parameters__

- __data (dict)__: The message payload
- __timestamp (datetime)__: Timestamp intended to denote the time the message was sent,
    or `None` if this information is not available.


