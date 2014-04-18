#Python PSUtil IoT Adapter

Sample code for sending system utilization data to the IBM Internet of Things QuickStart service from a Python 2.7 runtime environment.

The following data points are supported:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (KB/s)
 * Inbound network utilization across all network interfaces (KB/s)


## Raspbian (Raspberry Pi)
```
pi@raspberrypi ~ $ sudo apt-get update
pi@raspberrypi ~ $ sudo apt-get install python-dev
pi@raspberrypi ~ $ sudo apt-get install python-pip
pi@raspberrypi ~ $ sudo pip install paho-mqtt
pi@raspberrypi ~ $ sudo pip install psutil
pi@raspberrypi ~ $ sudo echo "184.172.124.189 messaging.quickstart.internetofthings.ibmcloud.com" >> /etc/hosts
pi@raspberrypi ~ $ wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/src/iot-psutil.py
pi@raspberrypi ~ $ python iot-psutil.py
Connected successfully - Your device ID is ca51af86af39
 * http://quickstart.internetofthings.ibmcloud.com/?deviceId=ca51af86af39
Visit the QuickStart portal to see this device's data visualized in real time and learn more about the IBM Internet of Things Cloud

(Press Ctrl+C to disconnect)

```

## CentOS / RHEL 6
See: [Setting up Django and Python 2.7 on Red Hat Enterprise 6 the easy way](http://developerblog.redhat.com/2013/02/14/setting-up-django-and-python-2-7-on-red-hat-enterprise-6-the-easy-way/)
```
[me@localhost ~]$ sudo su -
[root@localhost ~]# wget -qO- http://people.redhat.com/bkabrda/scl_python27.repo >> /etc/yum.repos.d/scl.repo
[root@localhost ~]# yum install python27
[root@localhost ~]# scl enable python27 bash
[root@localhost ~]# pip install paho-mqtt
[root@localhost ~]# pip install psutil
[root@localhost ~]# echo "184.172.124.189 messaging.quickstart.internetofthings.ibmcloud.com" >> /etc/hosts
[root@localhost ~]# exit
[me@localhost ~]$ wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/src/iot-psutil.py
[me@localhost ~]$ scl enable python27 bash
[me@localhost ~]$ python iot-psutil.py
Connected successfully - Your device ID is ca51af86af39
 * http://quickstart.internetofthings.ibmcloud.com/?deviceId=ca51af86af39
Visit the QuickStart portal to see this device's data visualized in real time and learn more about the IBM Internet of Things Cloud

(Press Ctrl+C to disconnect)


```


## Microsoft Windows
[Install Python 2.7](https://www.python.org/download/releases/2.7)

[Install pip-Win](https://sites.google.com/site/pydatalog/python/pip-for-windows) and use this to install the paho-mqtt Python package.  Windows 7 users should note that there is a [bug in paho-mqtt](https://bugs.eclipse.org/bugs/show_bug.cgi?id=431698), you may need to update with the latest version from the [repository](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/tree/src/paho/mqtt/client.py) until this bug fix makes it into a release.

Download and install [psutil](https://pypi.python.org/pypi?:action=display&name=psutil#downloads) using the appropriate Windows installer:
 * [psutil-2.1.0.win32-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win32-py2.7.exe#md5=cfe1b146fc38176e4e63290fa15029a1)
 * [psutil-2.1.0.win-amd64-py2.7.exe](https://pypi.python.org/packages/2.7/p/psutil/psutil-2.1.0.win-amd64-py2.7.exe#md5=db0ee08adb7f00386ee419dcf414d451)

Download [iot-psutil.py](https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/src/iot-psutil.py) from GitHub

```
C:\Users\Me> python iot-psutil.py
Connected successfully - Your device ID is ca51af86af39
 * http://quickstart.internetofthings.ibmcloud.com/?deviceId=ca51af86af39
Visit the QuickStart portal to see this device's data visualized in real time and learn more about the IBM Internet of Things Cloud

(Press Ctrl+C to disconnect)
```


##Visualize
Visit the [IBM Internet of Things QuickStart Portal](http://quickstart.internetofthings.ibmcloud.com) and enter your device ID to see real time visualizations of 
the data sent from your device.

