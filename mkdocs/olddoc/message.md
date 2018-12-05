<h1 id="ibmiotf.Message">Message</h1>

```python
Message(self, data, timestamp=None)
```

Represents an abstract message recieved over Mqtt.  All implementations of
a Codec must return an object of this type.

__Attributes__

- `data (dict)`: The message payload
- `timestamp (datetime)`: Timestamp intended to denote the time the message was sent,
    or `None` if this information is not available.


