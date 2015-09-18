# Setup on RHEL/CentOS

Install [Python](https://www.python.org/downloads/) & the [``ibmiotf``](https://pypi.python.org/pypi/ibmiotf/) and 
[``psutil``](https://pypi.python.org/pypi/psutil/) modules.  Note that we will build Python 2.7.10 and install it 
alongside the existing Python 2.6 install so that we can use an encrypted connection (TLS 1.2 support was only 
introduced in Python 2.7.9).

```
[user@host ~]$ sudo su -
[root@host ~]# yum install gcc
[root@host ~]# wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
[root@host ~]# tar xzf Python-2.7.10.tgz
[root@host ~]# cd Python-2.7.10
[root@host Python-2.7.10]# ./configure
[root@host Python-2.7.10]# make altinstall
[root@host Python-2.7.10]# wget https://pypi.python.org/packages/source/d/distribute/distribute-0.7.3.zip#md5=c6c59594a7b180af57af8a0cc0cf5b4a
[root@host Python-2.7.10]# unzip distribute-0.7.3.zip
[root@host Python-2.7.10]# cd distribute-0.7.3
[root@host distribute-0.7.3]# python2.7 setup.py install
[root@host distribute-0.7.3]# easy_install-2.7 pip
[root@host distribute-0.7.3]# pip2.7 install ibmiotf psutil
```

## Install the device client
```
[root@host ~]# wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/managedDevice/iotpsutilManaged.py
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
[root@host ~]# python2.7 iotpsutilManaged.py -c device.cfg
(Press Ctrl+C to disconnect)

```
