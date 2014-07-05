IBM Internet of Things Cloud for Python
=======================================

Python module for interacting with the IBM Internet of Things Cloud with Python.

Platform
--------
* [Python 2.7](https://www.python.org/download/releases/2.7)

Dependencies
------------
* [paho-mqtt](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/)


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

```
import ibmiotc.application
try:
  options = {"org": organization, "id": appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
  client = ibmiotc.application.Client(options)
  except ibmiotc.ConnectionException  as e:
  ...
```

#####Using a Configuration File
```
import ibmiotc.application
try:
  options = ibmiotc.application.ParseConfigFile(configFilePath)
  client = ibmiotc.application.Client(options)
except ibmiotc.ConnectionException  as e:
  ...
```

The application configuration file must be in the following format:
```
org=$orgId
id=$myApplication
auth-method=apikey
auth-key=$key
auth-token=$token
```

####Subscribing to Device events
By default, this will subscribe to all events from all connected devices.  Use the type, id and event parameters to control the scope of the subscription.  A single client can support multiple subscriptions.

#####Subscribe to all events from all devices
```
client.subscribeToDeviceEvents()
```

#####Subscribe to all events from all devices of a specific type
```
client.subscribeToDeviceEvents(type=myDeviceType)
```

#####Subscribe to a specific event from all devices
```
client.subscribeToDeviceEvents(event=myEvent)
```

#####Subscribe to a specific event from two different devices
```
client.subscribeToDeviceEvents(type=myDeviceType, id=myDeviceId, event=myEvent)
lient.subscribeToDeviceEvents(type=myOtherDeviceType, id=myOtherDeviceId, event=myEvent)
```

####Handling events from Devices
To process the events received by your subscroptions you need to register an event callback method.
```
def myEventCallback(type, id, event, format, data):
  print "%s event '%s' received from device [%s:%s]: %s" % (format, event, type, id, json.dumps(data))

...
client.eventCallback = myEventCallback
client.subscribeToDeviceEvents()
```


####Subscribing to Device status
By default, this will subscribe to status updates for all connected devices. Use the type and id parameters to control the scope of the subscription.  A single client can support multiple subscriptions.

#####Subscribe to status updates for all devices
```
client.subscribeToDeviceStatus()
```

#####Subscribe to status updates for all devices of a specific type
```
client.subscribeToDeviceStatus(type=myDeviceType)
```

#####Subscribe to status updates for two different devices
```
client.subscribeToDeviceStatus(type=myDeviceType, id=myDeviceId)
lient.subscribeToDeviceStatus(type=myOtherDeviceType, id=myOtherDeviceId)
```

####Handling status updates from Devices
To process the status updates received by your subscroptions you need to register an event callback method.
```
def myStatusCallback(type, id, status):
	print "Status of device [%s:%s] changed to %s" % (type, id, json.dumps(status))

...
client.statusCallback = myStatusCallback
client.subscribeToDeviceStstus()
```

####Publishing Events "from" Devices
Applications can publish events as if they originated from a Device
```
myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
client.publishEvent(type=myDeviceType, id=myDeviceId, event="status", data=myData)
```

####Publishing Commands to Devices
Applications can publish commands to connected Devices
```
commandData={'delay' : 50}
client.publishCommand(type=myDeviceType, id=myDeviceId, command="reboot", data=myData)
```
