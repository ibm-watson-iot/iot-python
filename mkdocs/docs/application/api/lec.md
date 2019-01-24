# Last Event Cache

Last Event Cache is an **optional** feature in Watson IoT Platform, which when enabled allows the caching of the last event sent for each eventId by each registered device.  By default this feature is disabled, to use this feature you must enable it from your dashboard at `https://MYORGID.internetofthings.ibmcloud.com/dashboard/settings`.


## Get Last Cached Event

The `lec.get(device, eventId)` method allows you to retrieve the last event isntance of a specific eventId sent by a device.  The method supports multiple ways to identify the device, as demonstrated below.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

eventId = "test1"

# Get the last event using a python dictionary to define the device
device = {"typeId": "myType", "deviceId": "myDevice"}
lastEvent = appClient.lec.get(device, eventId)

# Get the last event using a DeviceUid support class to define the device
import wiotp.sdk.api.registry.devices.DeviceUid
device = DeviceUid(typeId: "myType", deviceId: "myDevice")
lastEvent = appClient.lec.get(device, eventId)

# Get the last event using the result of a lookup from the device registry
try:
    device = client.registry.devicetypes["myType"].devices["myDevice"]
    lastEvent = appClient.lec.get(device, eventId)
except KeyError as e:
    print("Device does not exist %s" % (e))
```


## Get All Last Cached Events

The `lec.getAll(device)` method returns a list of the last cached event for all eventIds for a single device.  As with the `lec.get()` method, this supports multiple ways to define the device.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Get the last events using a python dictionary to define the device
device = {"typeId": "myType", "deviceId": "myDevice"}
lastEvents = appClient.lec.getAll(device)

# Get the last events using a DeviceUid support class to define the device
import wiotp.sdk.api.registry.devices.DeviceUid
device = DeviceUid(typeId: "myType", deviceId: "myDevice")
lastEvents = appClient.lec.getAll(device)

# Get the last events using the result of a lookup from the device registry
try:
    device = client.registry.devicetypes["myType"].devices["myDevice"]
    lastEvents = appClient.lec.getAll(device)
except KeyError as e:
    print("Device does not exist %s" % (e))
```


## Handling the LastEvent data

The `wiotp.sdk.api.lec.LastEvent` class extends defaultdict allowing you to treat the reponse as a simple Python dictionary if you so choose, however it's designed to make it easy to interact with the Last Event Cache API results by providing convenient properties representing the data available from the API:

- `eventId` The eventId of the cached event
- `typeId` The typeId of the device that sent the cached event
- `deviceId` The devieId of the device that sent the cached event
- `format` The format that the cached event was sent using
- `timestamp` The date and time **when the event was cached**.  This is not the time the event was published by the device.  Events are cached in batches, so although this will usually be a good approximation of the time the event was sent, you can not rely on this timestamp representing the precise time the event was sent, only the time that it reached the cache.
- `payload` The **base64 encoded** message content (payload) of the cached event.  The payload is base64 encoded to allow for any content-type to be safely cached and retrieved.  use the information in the format to determine how to handle the payload correctly.


```python
import wiotp.sdk.application
import base64
options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Get the last events using a python dictionary to define the device
device = {"typeId": "myType", "deviceId": "myDevice"}
lastEvents = appClient.lec.getAll(device)

for event in lastEvents:
    print("Event from device: %s:%s" % (event.typeId, event.deviceId))
    print("- Event ID: %s " % (event.eventId))
    print("- Format: %s" % (event.format))
    print("- Cached at: %s" % (event.timestamp.isoformat()))
    
    # The payload is always returned base64 encoded by the API
    print("- Payload (base64 encoded): %s" % (event.payload))

    # Depending on the content of the message this may not be a good idea (e.g. if it was originally binary data)
    print("- Payload (decoded): %s" % (base64.b64decode(event.payload).decode('utf-8')))
```