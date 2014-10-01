IBM Internet of Things Foundation for Python
============================================

Python module for interacting with the IBM Internet of Things Foundation with Python.

Platform
--------
Note: TLS v1.2 is the minimum supported protocol supported by the Internet of Things Foundation, this is not supported in Python 2.
* [Python 3.4](https://www.python.org/download/releases/3.4.1)

Dependencies
------------
* [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)
* [iso8601](https://pypi.python.org/pypi/iso8601)
* [pytz](https://pypi.python.org/pypi/pytz)


Installation
------------
Install the latest version of the library with pip
```
[root@localhost ~]# pip install ibmiotc
```

Uninstall
---------
Uninstalling the module is simple.
```
[root@localhost ~]# pip uninstall ibmiotc
```

Documentation
-------------

###Application Client


####Constructor
The Client constructor accepts an options dict containing:
 * org - Your organization ID
 * id - The unique ID of your application within your organization
 * authMethod - Method of authentication (the only value of authMethod currently supported is "apikey")
 * authKey - API key (required if authMethod is "apikey")
 * authToken - API key token (required if authMethod is "apikey")

```python
import ibmiotc.application
try:
  options = {"org": organization, "id": appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
  client = ibmiotc.application.Client(options)
  except ibmiotc.ConnectionException  as e:
  ...
```

#####Using a Configuration File
```python
import ibmiotc.application
try:
  options = ibmiotc.application.ParseConfigFile(configFilePath)
  client = ibmiotc.application.Client(options)
except ibmiotc.ConnectionException  as e:
  ...
```

The application configuration file must be in the following format:
```
[application]
org=$orgId
id=$myApplication
auth-method=apikey
auth-key=$key
auth-token=$token
```

####Subscribing to Device events
By default, this will subscribe to all events from all connected devices.  Use the type, id and event parameters to control the scope of the subscription.  A single client can support multiple subscriptions.

#####Subscribe to all events from all devices
```python
client.subscribeToDeviceEvents()
```

#####Subscribe to all events from all devices of a specific type
```python
client.subscribeToDeviceEvents(deviceType=myDeviceType)
```

#####Subscribe to a specific event from all devices
```python
client.subscribeToDeviceEvents(event=myEvent)
```

#####Subscribe to a specific event from two different devices
```python
client.subscribeToDeviceEvents(deviceType=myDeviceType, deviceId=myDeviceId, event=myEvent)
lient.subscribeToDeviceEvents(deviceType=myOtherDeviceType, deviceId=myOtherDeviceId, event=myEvent)
```

####Handling events from Devices
To process the events received by your subscroptions you need to register an event callback method.  The messages are returned as an instance of the Event class:
 * event.device - string (uniquely identifies the device across all types of devices in the organization $deviceType:$deviceId)
 * event.deviceType - string
 * event.deviceId - string
 * event.event - string
 * event.format - string
 * event.data - dict
 * event.timestamp - datetime
 
```python
def myEventCallback(event):
  print "%s event '%s' received from device [%s]: %s" % (event.format, event.event, event.device, json.dumps(event.data))

...
client.eventCallback = myEventCallback
client.subscribeToDeviceEvents()
```


####Subscribing to Device status
By default, this will subscribe to status updates for all connected devices. Use the type and id parameters to control the scope of the subscription.  A single client can support multiple subscriptions.

#####Subscribe to status updates for all devices
```python
client.subscribeToDeviceStatus()
```

#####Subscribe to status updates for all devices of a specific type
```python
client.subscribeToDeviceStatus(deviceType=myDeviceType)
```

#####Subscribe to status updates for two different devices
```python
client.subscribeToDeviceStatus(deviceType=myDeviceType, deviceId=myDeviceId)
lient.subscribeToDeviceStatus(deviceType=myOtherDeviceType, deviceId=myOtherDeviceId)
```

####Handling status updates from Devices
To process the status updates received by your subscriptions you need to register an event callback method.  The messages are returned as an instance of the Status class:

The following properties are set for both "Connect" and "Disconnect" status events:
 * status.clientAddr - string  
 * status.protocol - string  
 * status.clientId - string  
 * status.user - string  
 * status.time - datetime  
 * status.action - string  
 * status.connectTime - datetime  
 * status.port - int

The following properties are only set when the action is "Disconnect":
 * status.writeMsg - int
 * status.readMsg - int
 * status.reason - string  
 * status.readBytes - int  
 * status.writeBytes - int  

```python
def myStatusCallback(status):
  if status.action == "Disconnect":
    print("%s - device %s - %s (%s)" % (status.time.isoformat(), status.device, status.action, status.reason))
  else:
    print("%s - %s - %s" % (status.time.isoformat(), status.device, status.action))

...
client.statusCallback = myStatusCallback
client.subscribeToDeviceStstus()
```

####Publishing Events "from" Devices
Applications can publish events as if they originated from a Device
```python
myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(myDeviceType, myDeviceId, "status", myData)
```

####Publishing Commands to Devices
Applications can publish commands to connected Devices
```python
commandData={'rebootDelay' : 50}
client.publishCommand(myDeviceType, myDeviceId, "reboot", myData)
```
