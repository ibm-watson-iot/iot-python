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
[Install Python](https://www.python.org/download/releases/2.7)

[Install pip](http://pip.readthedocs.org/en/latest/installing.html).  Windows users may prefer to use [pip-Win](https://sites.google.com/site/pydatalog/python/pip-for-windows)

Install the [paho-mqtt](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/) and [psutil](https://code.google.com/p/psutil/) Python modules.  Windows users may prefer to use the [psutil Windows Installer](https://pypi.python.org/pypi?:action=display&name=psutil#downloads)

```
pip install paho-mqtt
pip install psutil
```

Connect
-------
Download [iot-psutil.py](https://raw.githubusercontent.com/ibm-messaging/iot-python/master/samples/psutil/iot-psutil.py) from GitHub

Execute the script
```
$ python iot-psutil.py
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

