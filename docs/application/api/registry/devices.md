# Registry - Devices


## DeviceUid

Every device in your organization is uniquely identifiable by the combination of it's `typeId` and `deviceId`.  Two devices of different types can have the same `deviceId`.  It helps to think of `typeId` as a model number and `deviceId` as a serial number.  Two seperate types may independently have the same serial number pattern (e.g. simple sequential numbering), but because identity in WIoTP is a combination of `typeId` and `deviceId` this does not cause a clash.

Globally, your organization ID is applied to the deviceUID creating a globally unique identifier for every device connected to Watson IoT Platform.

- **typeId**: `myDeviceType`
- **deviceId**: `myDevice`
- **deviceUid**: `myDeviceType:myDevice`
- **deviceGuid**: `myOrg:myDeviceType:myDevice`

The `wiotp.sdk.registry.devices.DeviceUID` class provides a structure to encapsulate a device unique ID.  You can use it interchangeably throughout the SDK with a simple Python dictionary.  It's a code style choice.

```python

from pprint import pprint
import wiotp.sdk.application
import wiotp.sdk.api.registry.devices.DeviceUid as DeviceUid

deviceIdAsClass = DeviceUid(typeId="myDeviceType", deviceId="myDevice")
deviceIdAsDict = {"typeId": "myDeviceType", "deviceId": "myDevice"}

# All three output "myDeviceType:myDevice"
print(deviceIdAsClass.typeId + ":" + deviceIdAsClass.deviceId)
print(deviceIdAsClass)
print(deviceIdAsDict["typeId"] + ":" + deviceIdAsDict["deviceId"])

# Outputs {"typeId": "myDeviceType", "deviceId": "myDevice"}
pprint(deviceIdAsClass)

# These two calls are identical, the same applies anywhere that a 
# deviceUid is needed, it is your choice which style you prefer 
# in your code.
appClient.registry.devices.delete(deviceIdAsClass)
appClient.registry.devices.delete(deviceIdAsDict)
```


## Get


## Delete


## List


## Create

`wiotp.sdk.api.regsitry.devices.DeviceCreateRequest` exists to aid in the registration of new devices.  It's use is entirely optional, and you can use a standard python dictionary instead if you prefer.  To create an instance of this class provide the following named parameters:

- `typeId` Required
- `deviceId` Required
- `authToken` Optional, if you do not specify a token on creation one will be generated automatically for you.  If you take a generated toekn, you must capture the token from the device registration response as it can not be retrieved later.
- `deviceInfo` Optional.  A python dictionary, or a `DeviceInfo` instance
- `location` Optional
- `metadata` Optional dictionary containing freeform metadata

```python
import uuid
import wiotp.sdk.application
import wiotp.sdk.api.registry.devices.DeviceCreateRequest as DeviceCreateRequest
import wiotp.sdk.api.registry.devices.DeviceInfo as DeviceInfo

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Device registration using the helper classes
deviceToRegister1 = DeviceCreateRequest(
    typeId="myDeviceType", 
    deviceId=str(uuid.uuid4()), 
    authToken="NotVerySecretPassw0rd",
    deviceInfo=DeviceInfo(serialNumber="123", descriptiveLocation="Floor 3, Room 2")
)
        
appClient.registry.devices.create(deviceToRegister1)

# Device registration using simple Python dictionaries
deviceToRegister2 = {
    "typeId": "myDeviceType", 
    "deviceId": str(uuid.uuid4()), 
    "authToken": "NotVerySecretPassw0rd",
    "deviceInfo": {
        "serialNumber": "123", 
        "descriptiveLocation": "Floor 3, Room 2"
    }
}
        
appClient.registry.devices.create(deviceToRegister2)
```

`registry.devices.create()` also allows you to pass a list of devices to perform bulk device registration.

```python
import uuid
import wiotp.sdk.application
import wiotp.sdk.api.registry.devices.DeviceCreateRequest as DeviceCreateRequest

# Register 100 devices with random UUIDs as deviceIds
devicesToRegister = []
for i in range(100)
    dReq = DeviceCreateRequest(typeId="myDeviceType", deviceId=str(uuid.uuid4())
    devicesToRegister.append(dReq)

registrationResult = appClient.registry.devices.create(devicesToRegister)

```


## Update




