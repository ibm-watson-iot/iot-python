# Python SDK

[![Build Status](https://travis-ci.org/ibm-watson-iot/iot-python.svg?branch=master)](https://travis-ci.org/ibm-watson-iot/iot-python)
[![GitHub issues](https://img.shields.io/github/issues/ibm-watson-iot/iot-python.svg)](https://github.com/ibm-watson-iot/iot-python/issues)
[![GitHub](https://img.shields.io/github/license/ibm-watson-iot/iot-python.svg)](https://github.com/ibm-watson-iot/iot-python/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ibmiotf.svg)](https://pypi.org/project/ibmiotf/)



Python module for interacting with the [IBM Watson IoT Platform](https://internetofthings.ibmcloud.com).

-  [Python 3.7](https://www.python.org/downloads/release/python-370/)
-  [Python 2.7](https://www.python.org/downloads/release/python-2715/)

!!! note
    Support for MQTT with TLS requires at least Python v2.7.9 or v3.4, and openssl v1.0.1

Documentation for this SDK can be broken down into 4 distinct areas:


- Common Topics
    - [Basic Concepts](concepts.md)
    - [MQTT Primer](mqtt.md)
    - [Custom Message Formats](custommsg.md)
    - [Exceptions](exceptions.md)
- [Application Development](application/index.md)
- [Device Development](device/index.md)
- [Gateway Development](gateway/index.md)

Additional documentation for the library is available in IBM Cloud, but it's a "little" out of date in places:

-  [Application Developers](https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html)
-  [Device Developers](https://console.ng.bluemix.net/docs/services/IoT/devices/libraries/python.html)



## Dependencies

-  [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)
-  [iso8601](https://pypi.python.org/pypi/iso8601)
-  [pytz](https://pypi.python.org/pypi/pytz)
-  [requests](https://pypi.python.org/pypi/requests)


## Installation

Install the latest version of the library with pip

```
# pip install wiotp-sdk
```


## Uninstall

Uninstalling the module is simple.

```
# pip uninstall wiotp-sdk
```
