#Python PSUtil Adapter

Contains QuickStart, SDKs and samples for connecting a machine running Python to the IBM Internet of Things cloud and sending system utilization data.

Enables publishing of basic system utilization statistics to the IBM Internet of Things Cloud service from any machine that supports a Python 2.7 runtime.

The following data points are supported:
 * CPU utilization (%)
 * Memory utilization (%)
 * Outbound network utilization across all network interfaces (kb/s)
 * Inbound network utilization across all network interfaces (kb/s)


Platform
------------
* [Python 2.7](https://www.python.org/download/releases/2.7)

Dependencies
------------
* [paho-mqtt](http://git.eclipse.org/c/paho/org.eclipse.paho.mqtt.python.git/)
* [psutil](https://code.google.com/p/psutil/)
