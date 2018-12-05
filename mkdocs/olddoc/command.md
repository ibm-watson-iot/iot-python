<h1 id="ibmiotf.device.Command">Command</h1>

```python
Command(self, pahoMessage, messageEncoderModules)
```

Represents a command sent to a device.

__Parameters__

- __pahoMessage (?)__: ?
- __messageEncoderModules (dict)__: Dictionary of Python modules, keyed to the
    message format the module should use.

__Attributes__

- `command (string)`: Identifies the command.
- `format (string)`: The format can be any string, for example JSON.
- `data (dict)`: The data for the payload. Maximum length is 131072 bytes.
- `timestamp (datetime)`: The date and time of the event.

__Raises__

- `InvalidEventException`: If the command was recieved on a topic that does
    not match the regular expression `iot-2/cmd/(.+)/fmt/(.+)`

