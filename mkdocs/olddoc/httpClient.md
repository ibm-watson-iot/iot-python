<h1 id="ibmiotf.device.HttpClient">HttpClient</h1>

```python
HttpClient(self, options, logHandlers=None)
```

A basic device client with limited capabilies that forgoes
an active MQTT connection to the service.  Extends `ibmiotf.HttpAbstractClient`.

__Parameters__

- __options (dict)__: Configuration options for the client
- __logHandlers (list<logging.Handler>)__: Log handlers to configure.  Defaults to `None`,
    which will result in a default log handler being created.

__Configuration Options__

The options parameter expects a Python dictionary containing the following keys:

- `orgId` Your organization ID.
- `type` The type of the device. Think of the device type is analagous to a model number.
- `id` A unique ID to identify a device. Think of the device id as analagous to a serial number.
- `auth-method` The method of authentication. The only method that is currently supported is `token`.
- `auth-token` An authentication token to securely connect your device to Watson IoT Platform.


The HTTP client supports four content-types for posted events:

- `application/xml`: for events/commands using message format `xml`
- `text/plain; charset=utf-8`: for events/commands using message format `plain`
- `application/octet-stream`: for events/commands using message format `bin`
- `application/json`: the default for all other message formats.

<h2 id="ibmiotf.device.HttpClient.publishEvent">publishEvent</h2>

```python
HttpClient.publishEvent(self, event, msgFormat, data)
```

Publish an event over HTTP(s) as given supported format

__Raises__

- `MissingMessageEncoderException`: If there is no registered encoder for `msgFormat`
- `Exception`: If something went wrong

__Returns__

`int`: The HTTP status code for the publish

