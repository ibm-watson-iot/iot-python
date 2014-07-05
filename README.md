IBM Internet of Things Cloud for Python
=======================================

Contains samples for working with the IBM Internet of Things Cloud from a Python 2.7 runtime environment.

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
 * org
 * appId
 * authMethod (the only value of authMethod currently supported is "apikey")
 * authKey (required if authMethod is "apikey")
 * authToken (required if authMethod is "apikey")

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
By default, will subscribe to all events from all connected devices.
Use the type, id and event parameters to control the scope of the subscription.  A single client can support multiple subscriptions.

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

#####Subscribe to a specific event from two specific devices
```
client.subscribeToDeviceEvents(type=myDeviceType, id=myDeviceId, event=myEvent)
lient.subscribeToDeviceEvents(type=myDeviceType, id=myOtherDeviceId, event=myEvent)
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
