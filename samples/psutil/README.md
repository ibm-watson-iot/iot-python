# Python PSUtil IoT Adapter

Sample code for sending system utilization data to the IBM Internet of Things

The following data points are supported:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (KB/s)
 * Inbound network utilization across all network interfaces (KB/s)


## Setup

### Raspbian (Raspberry Pi)
```
pi@raspberrypi ~ $ sudo apt-get update
pi@raspberrypi ~ $ sudo apt-get install python-dev
pi@raspberrypi ~ $ sudo apt-get install python-pip
pi@raspberrypi ~ $ sudo pip install paho-mqtt
pi@raspberrypi ~ $ sudo pip install psutil
pi@raspberrypi ~ $ wget https://github.com/ibm-messaging/iot-python/archive/master.zip
pi@raspberrypi ~ $ unzip master.zip
pi@raspberrypi ~ $ cd iot-python-master/samples/psutil
pi@raspberrypi ~ $ python iotpsutil.py
(Press Ctrl+C to disconnect)

```

### CentOS / RHEL 6
See: [Setting up Django and Python 2.7 on Red Hat Enterprise 6 the easy way](http://developerblog.redhat.com/2013/02/14/setting-up-django-and-python-2-7-on-red-hat-enterprise-6-the-easy-way/)
```
[me@localhost ~]$ sudo su -
[root@localhost ~]# wget -qO- http://people.redhat.com/bkabrda/scl_python27.repo >> /etc/yum.repos.d/scl.repo
[root@localhost ~]# yum install python27
[root@localhost ~]# scl enable python27 bash
[root@localhost ~]# pip install paho-mqtt
[root@localhost ~]# pip install psutil
[root@localhost ~]# exit
[me@localhost ~]$ wget https://github.com/ibm-messaging/iot-python/archive/master.zip
[me@localhost ~]$ unzip master.zip
[me@localhost ~]$ cd iot-python-master/samples/psutil
[me@localhost ~]$ scl enable python27 bash
[me@localhost ~]$ python iotpsutil.py
(Press Ctrl+C to disconnect)

```

### Microsoft Windows
[Install Python 2.7](https://www.python.org/download/releases/2.7)

[Install pip-Win](https://sites.google.com/site/pydatalog/python/pip-for-windows) and use this to install the paho-mqtt Python package.

Download and install [psutil](https://pypi.python.org/pypi?:action=display&name=psutil#downloads) using the appropriate Windows installer:
 * [psutil-2.1.0.win32-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win32-py2.7.exe#md5=cfe1b146fc38176e4e63290fa15029a1)
 * [psutil-2.1.0.win-amd64-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win-amd64-py2.7.exe#md5=db0ee08adb7f00386ee419dcf414d451)

Download and extract [master.zip](https://github.com/ibm-messaging/iot-python/archive/master.zip) from GitHub

```
C:\Users\Me> python iotpsutil.py
(Press Ctrl+C to disconnect)

```

## QuickStart Usage
With no command line options the device code will connect to [QuickStart](http://quickstart.internetofthings.ibmcloud.com)
```
[me@localhost ~]$ python iotpsutil.py
```

## Registered Usage
The device sample supports using either a device configuration file or command line arguments to connect to your [private organization](https://internetofthings.ibmcloud.com/dashboard/)
```
[me@localhost ~]$ python iotpsutil.py -c device.cfg
```

```
[me@localhost ~]$ python iotpsutil.py -o organization -t type -i id -T authToken
```


## Support Application
A sample application is provided that allows commands to be sent to the device when used in registered mode only.  This application requires a [configuration file](https://github.com/ibm-messaging/iot-python#using-a-configuration-file).

The application provides two functions:
 * Adjust the publish rate of the psutil device sample 
 * Print a debug message to the console on the device

```
[me@localhost ~]$ python psutilApp.py -c application.cfg
Command List:
 1. Change target device
(Ctrl+C to disconnect)
None:None>1

 0. Manually enter type and ID
 1. 001:psutil
Choose Device >1

Command List:
 1. Change target device
 2. Set publish rate of psutil:001
 3. Send message to console of psutil:001
(Ctrl+C to disconnect)
psutil:001>2

Enter Interval (seconds) >10

Command List:
 1. Change target device
 2. Set publish rate of psutil:001
 3. Send message to console of psutil:001
(Ctrl+C to disconnect)
psutil:001>
```
