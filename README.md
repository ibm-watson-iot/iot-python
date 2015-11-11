IBM Internet of Things Foundation for Python
============================================

Python module for interacting with the [IBM Internet of Things Foundation](https://internetofthings.ibmcloud.com).

* [Python 3.4](https://www.python.org/downloads/release/python-343/)
* [Python 2.7](https://www.python.org/downloads/release/python-279/)

Note: Support for MQTT over SSL requires at least Python v2.7.9 or v3.4, and openssl v1.0.1


Dependencies
------------
* [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)
* [iso8601](https://pypi.python.org/pypi/iso8601)
* [pytz](https://pypi.python.org/pypi/pytz)
* [requests](https://pypi.python.org/pypi/requests)


Installation
------------
Install the latest version of the library with pip
```
[root@localhost ~]# pip install ibmiotf
```


Uninstall
---------
Uninstalling the module is simple.
```
[root@localhost ~]# pip uninstall ibmiotf
```

Migrating from v0.0.x to v0.1.x
-------------------------------
There is a significant change between the 0.0.x releases and 0.1.x that will require changes to client code.  Now that the library properly supports multiple 
message formats you will want to update calls to deviceClient.publishEvent, appClient.publishEvent and appClient.publishCommand to also supply the desired message format.

Sample code v0.0.9:
```python
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)
myData = { 'hello' : 'world', 'x' : x}
deviceCli.publishEvent(event="greeting", data=myData)
```

Sample code v0.1.1:
```python
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)
myData = { 'hello' : 'world', 'x' : x}
deviceCli.publishEvent(event="greeting", msgFormat="json", data=myData)
```

Also, as part of this change, events and commands sent as format "json" will not be assumed to meet the [IOTF JSON Payload Specification](https://docs.internetofthings.ibmcloud.com/messaging/payload.html#iotf-json-payload-specification).  The default client behaviour will be to parse commands and events with format "json" as a generic JSON object only.  Only messages sent as format "json-iotf" will default to being decoded in this specification.  This can be easily changed 
with the following code.

```python
import ibmiotf.device
from ibmiotf.codecs import jsonIotfCodec

deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
deviceCli = ibmiotf.device.Client(deviceOptions)
# Revert to v0.0.x parsing for json messages -- assume all JSON events and commands use the IOTF JSON payload specification
deviceCli.setMessageEncoderModule('json', jsonIotfCodec) 
```


Documentation
-------------
* [Device Client](https://docs.internetofthings.ibmcloud.com/libraries/python_cli_for_devices.html)
* [Application Client](https://docs.internetofthings.ibmcloud.com/libraries/python_cli_for_apps.html)
* [API Client](https://docs.internetofthings.ibmcloud.com/libraries/python_cli_for_api.html)
