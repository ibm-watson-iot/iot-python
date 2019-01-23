# Working with Device Status

## Subscribing to Device Status
`subscribeToDeviceStatus()` allows the application to recieve real-time notification when devices connect and disconnect from the service.  With no parameters provided the method would subscribe to notifications for all devies. Use the `typeId` and `deviceId` parameters to control the scope of the subscription. A single client can support multiple subscriptions.

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseConfigFile("app.conf")
client = wiotp.sdk.application.ApplicationClient(options)

client.connect()

# Subscribing to status updates for all devices
client.subscribeToDeviceStatus()

# Subscribing to status updates for all devices of a specific type
client.subscribeToDeviceStatus(typeId=myDeviceType)

# Subscribing to status updates for two different devices
client.subscribeToDeviceStatus(typeId=myDeviceType, deviceId=myDeviceId)
client.subscribeToDeviceStatus(typeId=myOtherDeviceType, deviceId=myOtherDeviceId)
```

## Handling Device Status

To process the status updates that are received by your subscriptions, you need to register an event callback method. The messages are returned as an instance of the `Status` class.  There are two types of status events, **Connect** events and **Disconnect** events. All status events include the following properties:

- `clientAddr`
- `protocol`
- `clientId`
- `user`
- `time`
- `action`
- `connectTime`
- `port`

The `action` property determines whether a status event is of type Connect or Disconnect.   Disconnect status events include the following additional properties:

- `writeMsg`
- `readMsg`
- `reason`
- `readBytes`
- `writeBytes`

```python
import wiotp.sdk.application

options = wiotp.sdk.application.ParseConfigFile(configFilePath)
client = wiotp.sdk.application.ApplicationClient(options)

def myStatusCallback(status):

  if status.action == "Disconnect":
    str = "%s - device %s - %s (%s)"
    print(str % (status.time.isoformat(), status.device, status.action, status.reason))
    else:
      print("%s - %s - %s" % (status.time.isoformat(), status.device, status.action))

client.connect()
client.deviceStatusCallback = myStatusCallback
client.subscribeToDeviceStstus()
```
