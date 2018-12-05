<h1 id="ibmiotf.ConnectionException">ConnectionException</h1>

```python
ConnectionException(self, reason)
```

Generic Connection exception

__Attributes__

- `reason (string)`: The reason why the connection exception occured

<h1 id="ibmiotf.ConfigurationException">ConfigurationException</h1>

```python
ConfigurationException(self, reason)
```

Specific Connection exception where the configuration is invalid

__Attributes__

- `reason (string)`: The reason why the configuration is invalid

<h1 id="ibmiotf.UnsupportedAuthenticationMethod">UnsupportedAuthenticationMethod</h1>

```python
UnsupportedAuthenticationMethod(self, method)
```

Specific Connection exception where the authentication method specified is not supported

__Attributes__

- `method (string)`: The authentication method that is unsupported

<h1 id="ibmiotf.InvalidEventException">InvalidEventException</h1>

```python
InvalidEventException(self, reason)
```

Specific exception where an Event object can not be constructed

__Attributes__

- `reason (string)`: The reason why the event could not be constructed

<h1 id="ibmiotf.MissingMessageDecoderException">MissingMessageDecoderException</h1>

```python
MissingMessageDecoderException(self, format)
```

Specific exception where there is no message decoder defined for the message format being processed

__Attributes__

- `format (string)`: The message format for which no encoder could be found

<h1 id="ibmiotf.MissingMessageEncoderException">MissingMessageEncoderException</h1>

```python
MissingMessageEncoderException(self, format)
```

Specific exception where there is no message encoder defined for the message format being processed

__Attributes__

- `format (string)`: The message format for which no encoder could be found

