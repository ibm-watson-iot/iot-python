# Setup on Ubuntu

Install [Python](https://www.python.org/downloads/) & the [``ibmiotf``](https://pypi.python.org/pypi/ibmiotf/) and 
[``psutil``](https://pypi.python.org/pypi/psutil/) modules.  Note that ``python-dev`` is required to compile 
the ``psutil`` module.

```
user@host:~$ sudo su -
root@host:~# apt-get install python python-dev
root@host:~# pip install ibmiotf
root@host:~# pip install psutil
```

## Install the device client
```
user@host:~$ wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/managedDevice/iotpsutilManaged.py
```

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
The client must be ran as root user (otherwise it can not query dmidecode to access information about your device)
```
user@host:~$ sudo su -
root@host:~$ python iotpsutilManaged.py -c device.cfg
(Press Ctrl+C to disconnect)

```
