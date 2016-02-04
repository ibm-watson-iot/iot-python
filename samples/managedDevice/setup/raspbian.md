# Setup on Raspbian

Install Raspbian using the [minimal Raspbian unattended netinstaller for Raspberry Pi Model 1B, 1B+ and 2B](https://github.com/debian-pi/raspbian-ua-netinst)

Install [Python](https://www.python.org/downloads/) & the [``ibmiotf``](https://pypi.python.org/pypi/ibmiotf/) and 
[``psutil``](https://pypi.python.org/pypi/psutil/) modules.

```
root@pi:~# apt-get install sudo zip build-essential checkinstall
root@pi:~# apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
root@pi:~# cd /usr/src
root@pi:/usr/src# wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
root@pi:/usr/src# tar xzf Python-2.7.10.tgz
root@pi:/usr/src# cd Python-2.7.10
root@pi:/usr/src/Python-2.7.10# ./configure
root@pi:/usr/src/Python-2.7.10# make altinstall
root@pi:/usr/src/Python-2.7.10# wget https://pypi.python.org/packages/source/d/distribute/distribute-0.7.3.zip#md5=c6c59594a7b180af57af8a0cc0cf5b4a
root@pi:/usr/src/Python-2.7.10# unzip distribute-0.7.3.zip
root@pi:/usr/src/Python-2.7.10# cd distribute-0.7.3
root@pi:/usr/src/Python-2.7.10/distribute-0.7.3# python2.7 setup.py install
root@pi:/usr/src/Python-2.7.10/distribute-0.7.3# easy_install-2.7 pip
root@pi:/usr/src/Python-2.7.10/distribute-0.7.3# pip2.7 install ibmiotf psutil
```

## Install the device client
```
root@pi:~# wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/managedDevice/iotpsutilManaged.py
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
root@pi:~# python iotpsutilManaged.py -c device.cfg
(Press Ctrl+C to disconnect)

```
