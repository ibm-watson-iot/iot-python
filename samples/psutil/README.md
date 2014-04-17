Python PSUtil IoT Adapter
=========================

Sample code for sending system utilization data to the IBM Internet of Things QuickStart service from a Python 2.7 runtime environment.

The following data points are supported:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (KB/s)
 * Inbound network utilization across all network interfaces (KB/s)


Prepare
-------
[Install Python 2.7](https://www.python.org/download/releases/2.7).  

For RHEL 6/CentOS users there is an [easy way](http://developerblog.redhat.com/2013/02/14/setting-up-django-and-python-2-7-on-red-hat-enterprise-6-the-easy-way/) to install Python 2.7 alongside your existing Python 2.6 install.

```
[me@localhost ~]$ sudo sh -c 'wget -qO- http://people.redhat.com/bkabrda/scl_python27.repo >> /etc/yum.repos.d/scl.repo'
[me@localhost ~]$ sudo yum install python27
[me@localhost ~]$ scl -l
python27
[me@localhost ~]$ scl enable python27 bash
[me@localhost ~]$ python -V
Python 2.7.3
```


Once you have the Python 2.7 runtime available, the simplest way to install Python modules is using [pip](http://pip.readthedocs.org/en/latest/installing.html).  With pip configured, install the [paho-mqtt](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/) and [psutil](https://code.google.com/p/psutil/)  modules.
```
[me@localhost ~]$ pip install paho-mqtt
[me@localhost ~]$ pip install psutil
```

Windows users may find [pip-Win](https://sites.google.com/site/pydatalog/python/pip-for-windows) useful. A [Windows installer](https://pypi.python.org/pypi?:action=display&name=psutil#downloads) is also available for the psutil module.


Connect
-------
Download [iot-psutil.py](https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/src/iot-psutil.py) from GitHub
```
[me@localhost ~]$ wget https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/src/iot-psutil.py
```

Execute the script
```
[me@localhost ~]$ python iot-psutil.py
Connected successfully - Your device ID is ca51af86af39
 * http://quickstart.internetofthings.ibmcloud.com/?deviceId=ca51af86af39
Visit the QuickStart portal to see this device's data visualized in real time and learn more about the IBM Internet of Things Cloud

(Press Ctrl+C to disconnect)
```

Windows 7 Users: There is a [bug in Paho](https://bugs.eclipse.org/bugs/show_bug.cgi?id=431698) on Windows 7, you may need to update with the latest version from the [repository](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/tree/src/paho/mqtt/client.py) until this bug fix makes it into a release.

Visualize
---------
Visit the [IBM Internet of Things QuickStart Portal](http://quickstart.internetofthings.ibmcloud.com) and enter your device ID to see real time visualizations of 
the data sent from your device.

