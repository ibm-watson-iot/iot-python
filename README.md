# Python for IBM Watson IoT Platform

[![Build Status](https://travis-ci.org/ibm-watson-iot/iot-python.svg?branch=master)](https://travis-ci.org/ibm-watson-iot/iot-python)
[![GitHub issues](https://img.shields.io/github/issues/ibm-watson-iot/iot-python.svg)](https://github.com/ibm-watson-iot/iot-python/issues)
[![GitHub](https://img.shields.io/github/license/ibm-watson-iot/iot-python.svg)](https://github.com/ibm-watson-iot/iot-python/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ibmiotf.svg)](https://pypi.org/project/ibmiotf/)



Python module for interacting with the [IBM Watson IoT Platform](https://internetofthings.ibmcloud.com).

-  [Python 3.7](https://www.python.org/downloads/release/python-370/)
-  [Python 2.7](https://www.python.org/downloads/release/python-2715/)

Note: Support for MQTT with TLS requires at least Python v2.7.9 or v3.4, and openssl v1.0.1


## Dependencies

-  [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)
-  [iso8601](https://pypi.python.org/pypi/iso8601)
-  [pytz](https://pypi.python.org/pypi/pytz)
-  [requests](https://pypi.python.org/pypi/requests)
-  [requests_toolbelt](https://pypi.python.org/pypi/requests_toolbelt)


## Installation

Install the latest version of the library with pip

```
# pip install ibmiotf
```


## Uninstall

Uninstalling the module is simple.

```
# pip uninstall ibmiotf
```


## Documentation

Documentation is generated using [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown): http://ibm-watson-iot.github.io/iot-python/

Please note the documentation is very much a work in progress at the moment, and is being addressed under [Issue #112](https://github.com/ibm-watson-iot/iot-python/issues/112).  Additional documentation for the library is available in Bluemix, but it's a little out of date in places:

-  [Application Developers](https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html)
-  [Device Developers](https://console.ng.bluemix.net/docs/services/IoT/devices/libraries/python.html)


## Supported Features

- **Device Connectivity**: Connect your device(s) to Watson IoT Platform with ease using this library
- **Gateway Connectivity**: Connect your gateway(s) to Watson IoT Platform with ease using this library
- **Application connectivity**: Connect your application(s) to Watson IoT Platform with ease using this library
- **Watson IoT API**: Support for the interacting with the Watson IoT Platform through REST APIs
- **SSL/TLS**: By default, this library connects your devices, gateways and applications securely to Watson IoT Platform registered service. Ports `8883` (default) and `443` support secure connections using TLS with the MQTT and HTTP protocol. Support for MQTT with TLS requires at least Python v2.7.9 or v3.4, and openssl v1.0.1
- **Device Management for Device**: Connects your device(s) as managed device(s) to Watson IoT Platform.
- **Device Management for Gateway**: Connects your gateway(s) as managed device(s) to Watson IoT Platform.
- **Device Management Extensions**: Provides support for custom device management actions.
- **Scalable Applications**: Supports load balancing of MQTT subscriptions over multiple application instances.
- **Auto Reconnect**: All clients support automatic reconnect to the Platform in the event of a network interruption.
- **Event/Command publish**: Offers a pure HTTP client supporting messaging over HTTP in addition to the full features client that utilizes HTTP and MQTT technologies as appropriate 
- **Data Format Support**: JSON, XML, & user-defined.

## Unsupported Features
- **Client side Certificate based authentication**: [Client side Certificate based authentication](https://console.ng.bluemix.net/docs/services/IoT/reference/security/RM_security.html)n
- **Websockets**: Support device/gateway/application connectivity to Watson IoT Platform using WebSocket


