# Setup on Windows
Install [Python](https://www.python.org/downloads/) & the [ibmiotf](https://pypi.python.org/pypi/ibmiotf/) module.
```
C:\Users\Me> pip install ibmiotf
```

## Install psutil
Install [psutil](https://pypi.python.org/pypi?:action=display&name=psutil#downloads) using the appropriate Windows installer:
 * [psutil-2.1.0.win32-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win32-py2.7.exe#md5=cfe1b146fc38176e4e63290fa15029a1)
 * [psutil-2.1.0.win-amd64-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win-amd64-py2.7.exe#md5=db0ee08adb7f00386ee419dcf414d451)


## Install dmidecode
[dmidecode for Windows](http://gnuwin32.sourceforge.net/packages/dmidecode.htm) is a tool for 
dumping a computer's DMI (some say SMBIOS) table contents in a human-readable 
format. This table contains a description of the system's hardware components, as well as other
useful pieces of information such as serial numbers and BIOS revision.


## Install the device client
Download [iotpsutilManaged.py](https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/managedDevice/iotpsutilManaged.py) from GitHub


## Create a device configuration file
After registering the device create a configuration file with the correct type ID, device ID and authentication token
for your new device.

```
[device]
org=$orgId
type=$myDeviceType
id=$myDeviceId
auth-method=token
auth-token=$token
```

## Launch the device client
```
C:\Users\Me\iot-python> python iotpsutilManaged.py -c device.cfg
(Press Ctrl+C to disconnect)
```
