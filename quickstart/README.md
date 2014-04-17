#Python PSUtil QuickStart Adapter

Prerequisites
--------------
1 [Install Python](https://www.python.org/download/releases/2.7)

2 [Install pip](http://pip.readthedocs.org/en/latest/installing.html).  Windows users may prefer to use [pip-Win](https://sites.google.com/site/pydatalog/python/pip-for-windows)

3 Install the [paho-mqtt](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/) and [psutil](https://code.google.com/p/psutil/) Python modules.  Windows users may prefer to use the [psutil Windows Installer](https://pypi.python.org/pypi?:action=display&name=psutil#downloads)

```
pip install paho-mqtt
pip install psutil
```

Getting Started
---------------
1 Download [iotqs-pypsutil.py](https://raw.githubusercontent.com/durera/iot-py-psutil/master/quickstart/iotqs-pypsutil.py) from GitHub

2 Launch the program
```
$ python iotqs-pypsinfo.py
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

