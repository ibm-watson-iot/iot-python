# Registry - Types

`registry.devicetypes` provides a dictionary-like interface to simplify working with device types in your application:

- Get a device type: `registry.devicetypes[typeId]`
- Iterate over all device types: `for deviceType in registry.devicetypes`
- Delete a device type: `del registry.devicetypes[typeId]`
- Check for the existence of a device type: `if typeId in appClient.registry.devicetypes`

## DeviceType

`wiotp.sdk.api.registry.types.DeviceType` provides a number of properties and functions to simplify application development when working with device types:

- `id` The ID for the device type
- `description` The description string of the device type (`None` if no description is available)
- `classId` Identifies the device type as either a normal or gateway class of device
- `metadata` The metadata stored for the device type (`None` if no metadata is available)
- `json()` Returns the underlying JSON response body obtained from the API


## Get
```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

typeId = "myDeviceType"

try:
    deviceType = appClient.registry.devicetypes[typeId]
    print("- %s\n  :: %s" % (deviceType.id, deviceType.description))
except KeyError:
    Print("Device type does not exist")

```

## Delete
```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

typeId = "myDeviceType"

# Check for the existence of a specific device type
if typeId in appClient.registry.devicetypes:
    print("Device type %s exists" % (typeId))

    # Delete the device type
    del appClient.registry.devicetypes[typeId]
```

## List

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

# Display all device types and their descriptions
for deviceType in appClient.registry.devicetypes:
    print("- %s\n  :: %s" % (deviceType.id, deviceType.description))
```

## Create
The `registry.devicetypes.create(deviceType)` method accepts a dictionary object containing the data for the device type to be created:

- `id` Required.
- `description` Optional description of the device type
- `metadata` Optional freeform metadata about the device type
- `deviceInfo` Optional structured metadata about the device type (see `wiotp.sdk.api.registry.devices.DeviceInfo`)


```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

typeId = "myDeviceType"

# Retrieve a devicetype from the registry, if the devicetype doesn't exist create it
deviceType = None
try:
    deviceType = appClient.registry.devicetypes[typeId]
except KeyError as ke:
    print("Device Type %s did not exist, creating it now ..." % (typeId) )
    deviceType = appClient.registry.devicetypes.create({"typeId": typeId, "description": "I just created this using the WIoTP Python SDK"})

print(deviceType)
```

## Update
The `registry.devicetypes.update(typeId, description, deviceInfo, metadata)` method enabled updates to existing device types.  

- `typeId` indicates the device type to be updated
- `description`, `deviceInfo`, & `metadata` provide the content for the update

```python
import wiotp.sdk.application

options = wiotp.sdk.application.parseEnvVars()
appClient = wiotp.sdk.application.ApplicationClient(options)

typeId = "myDeviceType"

# Display the original data
deviceType = appClient.registry.devicetypes[typeId]
print("- %s\n  :: %s" % (deviceType.id, deviceType.description))

# Update the device type and capture the updated information
deviceType = appClient.registry.devicetypes.update(typeId, description="This is an updated description")
print("- %s\n  :: %s" % (deviceType.id, deviceType.description))
```
