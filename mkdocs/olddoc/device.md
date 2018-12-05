<h1 id="ibmiotf.device">ibmiotf.device</h1>


<h1 id="ibmiotf.device.Client">Client</h1>

```python
Client(self, options, logHandlers=None)
```

<h2 id="ibmiotf.device.Client.COMMAND_TOPIC">COMMAND_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.Client.on_connect">on_connect</h2>

```python
Client.on_connect(self, client, userdata, flags, rc)
```

This is called after the client has received a CONNACK message from the broker in response to calling connect().
The parameter rc is an integer giving the return code:

0: Success
1: Refused - unacceptable protocol version
2: Refused - identifier rejected
3: Refused - server unavailable
4: Refused - bad user name or password
5: Refused - not authorised

<h2 id="ibmiotf.device.Client.publishEvent">publishEvent</h2>

```python
Client.publishEvent(self, event, msgFormat, data, qos=0, on_publish=None)
```

Publish an event in IoTF.

Parameters:
    event - the name of this event
    msgFormat - the format of the data for this event
    data - the data for this event

Optional paramters:
    qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
    on_publish - a function that will be called when receipt of the publication is confirmed.  This
                 has different implications depending on the qos:
                 qos 0 - the client has asynchronously begun to send the event
                 qos 1 and 2 - the client has confirmation of delivery from IoTF

<h1 id="ibmiotf.device.ManagedClient">ManagedClient</h1>

```python
ManagedClient(self, options, logHandlers=None, deviceInfo=None)
```

<h2 id="ibmiotf.device.ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC">DM_FIRMWARE_DOWNLOAD_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_VERIFICATION_FAILED">UPDATESTATE_VERIFICATION_FAILED</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.RESPONSECODE_INTERNAL_ERROR">RESPONSECODE_INTERNAL_ERROR</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.DM_CANCEL_OBSERVE_TOPIC">DM_CANCEL_OBSERVE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATE_LOCATION_TOPIC">UPDATE_LOCATION_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.RESPONSECODE_FUNCTION_NOT_SUPPORTED">RESPONSECODE_FUNCTION_NOT_SUPPORTED</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_OUT_OF_MEMORY">UPDATESTATE_OUT_OF_MEMORY</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.RESPONSE_TOPIC">RESPONSE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.CLEAR_ERROR_CODES_TOPIC">CLEAR_ERROR_CODES_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_INVALID_URI">UPDATESTATE_INVALID_URI</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_UNSUPPORTED_IMAGE">UPDATESTATE_UNSUPPORTED_IMAGE</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.RESPONSECODE_ACCEPTED">RESPONSECODE_ACCEPTED</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.ADD_ERROR_CODE_TOPIC">ADD_ERROR_CODE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.DME_ACTION_TOPIC">DME_ACTION_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.DM_UPDATE_TOPIC">DM_UPDATE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.DM_FIRMWARE_UPDATE_TOPIC">DM_FIRMWARE_UPDATE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.DM_FACTORY_REESET">DM_FACTORY_REESET</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_DOWNLOADED">UPDATESTATE_DOWNLOADED</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.MANAGE_TOPIC">MANAGE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.CLEAR_LOG_TOPIC">CLEAR_LOG_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.RESPONSECODE_BAD_REQUEST">RESPONSECODE_BAD_REQUEST</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_IDLE">UPDATESTATE_IDLE</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.UNMANAGE_TOPIC">UNMANAGE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.DM_OBSERVE_TOPIC">DM_OBSERVE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_DOWNLOADING">UPDATESTATE_DOWNLOADING</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.DM_REBOOT_TOPIC">DM_REBOOT_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.ADD_LOG_TOPIC">ADD_LOG_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_CONNECTION_LOST">UPDATESTATE_CONNECTION_LOST</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.DM_RESPONSE_TOPIC">DM_RESPONSE_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_IN_PROGRESS">UPDATESTATE_IN_PROGRESS</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h2 id="ibmiotf.device.ManagedClient.NOTIFY_TOPIC">NOTIFY_TOPIC</h2>

str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
<h2 id="ibmiotf.device.ManagedClient.UPDATESTATE_SUCCESS">UPDATESTATE_SUCCESS</h2>

int(x=0) -> int or long
int(x, base=10) -> int or long

Convert a number or string to an integer, or return 0 if no arguments
are given.  If x is floating point, the conversion truncates towards zero.
If x is outside the integer range, the function returns a long instead.

If x is not a number or if base is given, then x must be a string or
Unicode object representing an integer literal in the given base.  The
literal can be preceded by '+' or '-' and be surrounded by whitespace.
The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
interpret the base from the string as an integer literal.
>>> int('0b100', base=0)
4
<h1 id="ibmiotf.device.HttpClient">HttpClient</h1>

```python
HttpClient(self, options, logHandlers=None)
```

A basic device client with limited capabilies that forgoes an active MQTT connection to the service.

<h2 id="ibmiotf.device.HttpClient.publishEvent">publishEvent</h2>

```python
HttpClient.publishEvent(self, event, msgFormat, data)
```

Publish an event over HTTP(s) as given supported format
Throws a ConnectionException with the message "Server not found" if the client is unable to reach the server
Otherwise it returns the HTTP status code, (200 - 207 for success)

<h1 id="ibmiotf.device.Command">Command</h1>

```python
Command(self, pahoMessage, messageEncoderModules)
```

<h1 id="ibmiotf.device.DeviceInfo">DeviceInfo</h1>

```python
DeviceInfo(self)
```

<h1 id="ibmiotf.device.DeviceFirmware">DeviceFirmware</h1>

```python
DeviceFirmware(self, version=None, name=None, url=None, verifier=None, state=None, updateStatus=None, updatedDateTime=None)
```

