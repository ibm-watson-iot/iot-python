<h1 id="ibmiotf.HttpAbstractClient">HttpAbstractClient</h1>

```python
HttpAbstractClient(self, clientId, logHandlers=None)
```

The underlying client object utilised for Platform connectivity
over HTPP in devices, gateways, and applications.

Restricted to HTTP only.  Unless for some technical reason
you are unable to use the full MQTT-enable client there really
is no need to use this alternative feature-limited client as
installing this library means you already have access to the
rich MQTT/HTTP client implementation.

The HTTP client supports four content-types for posted events:

- `application/xml`: for events/commands using message format `xml`
- `text/plain; charset=utf-8`: for events/commands using message format `plain`
- `application/octet-stream`: for events/commands using message format `bin`
- `application/json`: the default for all other message formats.

<h2 id="ibmiotf.HttpAbstractClient.setMessageEncoderModule">setMessageEncoderModule</h2>

```python
HttpAbstractClient.setMessageEncoderModule(self, messageFormat, module)
```

Set a Python module as the encoder/decoder for a specified message format.

__Arguments__

- __messageFormat (string)__: The message format to retreive the encoder for
- __module (module)__: The Python module to set as the encoder/decoder for `messageFormat`

<h2 id="ibmiotf.HttpAbstractClient.getMessageEncoderModule">getMessageEncoderModule</h2>

```python
HttpAbstractClient.getMessageEncoderModule(self, messageFormat)
```

Get the Python module that is currently defined as the encoder/decoder for a specified message format.

__Arguments__

- __messageFormat (string)__: The message format to retrieve the encoder for

__Returns__

`Boolean`: The python module, or `None` if there is no codec defined for the `messageFormat`

<h2 id="ibmiotf.HttpAbstractClient.connect">connect</h2>

```python
HttpAbstractClient.connect(self)
```

Connect is a no-op with HTTP-only client, but the presence of this method makes it easy
to switch between using HTTP & MQTT client implementation

<h2 id="ibmiotf.HttpAbstractClient.disconnect">disconnect</h2>

```python
HttpAbstractClient.disconnect(self)
```

Disconnect is a no-op with HTTP-only client, but the presence of this method makes it easy
to switch between using HTTP & MQTT client implementation

