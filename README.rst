Python for IBM Watson IoT Platform
==================================

Python module for interacting with the `IBM Watson IoT Platform <https://internetofthings.ibmcloud.com>`__.

-  `Python 3.6 <https://www.python.org/downloads/release/python-360/>`__
-  `Python 2.7 <https://www.python.org/downloads/release/python-2713/>`__

Note: Support for MQTT with TLS requires at least Python v2.7.9 or v3.4, and openssl v1.0.1


Dependencies
------------

-  `paho-mqtt <https://pypi.python.org/pypi/paho-mqtt>`__
-  `iso8601 <https://pypi.python.org/pypi/iso8601>`__
-  `pytz <https://pypi.python.org/pypi/pytz>`__
-  `requests <https://pypi.python.org/pypi/requests>`__
-  `requests_toolbelt <https://pypi.python.org/pypi/requests_toolbelt>`__
-  `dicttoxml <https://pypi.python.org/pypi/dicttoxml>`__
-  `xmltodict <https://pypi.python.org/pypi/xmltodict>`__


Installation
------------

Install the latest version of the library with pip

::

    [root@localhost ~]# pip install ibmiotf


Uninstall
---------

Uninstalling the module is simple.

::

    [root@localhost ~]# pip uninstall ibmiotf


Documentation
-------------

Documentation for the library is now located inside Bluemix:

-  `Application Developers <https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html>`__
-  `Device Developers <https://console.ng.bluemix.net/docs/services/IoT/devices/libraries/python.html>`__


Supported Features
------------------
.. list-table::
   :widths: 35 15 100
   :header-rows: 1

   * - Feature
     - Supported?
     - Description
   * - Device Connectivity
     - Yes
     - Connect your device(s) to Watson IoT Platform with ease using this library. Refer to `documentation <https://console.ng.bluemix.net/docs/services/IoT/devices/libraries/python.html>`_ for more details. 
   * - Gateway Connectivity
     - Yes
     - Connect your gateway(s) to Watson IoT Platform with ease using this library. Refer to `documentation <https://github.com/ibm-watson-iot/iot-python/blob/master/docs/Gateway.rst>`_ for more details.
   * - Application connectivity
     - Yes
     - Connect your application(s) to Watson IoT Platform with ease using this library. Refer to `documentation <https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html>`_ for more details.
   * - Watson IoT API
     - Yes
     - Shows how applications can use this library to interact with the Watson IoT Platform through REST APIs. Refer to `documentation <https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html>`_ for more details. 
   * - SSL/TLS
     - Yes
     - By default, this library connects your devices, gateways and applications securely to Watson IoT Platform registered service. Ports 8883(default one) and 443 support secure connections using TLS with the MQTT and HTTP protocol. Also, note that the library uses port 1883(unsecured) to connect to the Quickstart service. Support for MQTT with TLS requires at least Python v2.7.9 or v3.4, and openssl v1.0.1.
   * - Client side Certificate based authentication
     - No
     - `Client side Certificate based authentication <https://console.ng.bluemix.net/docs/services/IoT/reference/security/RM_security.html>`_ not supported now and will be added soon
   * - Device Management for Devices
     - Yes
     - Connects your device(s) as managed device(s) to Watson IoT Platform. Refer to `Managed Device documentation <https://github.com/ibm-watson-iot/iot-python/blob/master/docs/python_cli_for_manageddevice.rst>`_ for more details.
   * - Device Management for Gateways
     - Yes
     - Connects your gateway(s) as managed gateway(s) to Watson IoT Platform. Refer to `Managed Gateway documentation <https://github.com/ibm-watson-iot/iot-python/blob/master/docs/GatewayManagement.rst>`_ for more details.
   * - Device Management Extension
     - Yes
     - Provides support for custom device management actions. Refer to Device Management Extension(DME) Packages section in the `documentation <https://github.com/ibm-watson-iot/iot-python/blob/master/docs/python_cli_for_manageddevice.rst>`_ for more details.
   * - Scalable Application
     - Yes
     - Provides support for load balancing for applications. Skip providing type in configuration details to make application as scalable application.
   * - Auto Reconnect
     - No
     - Enables device/gateway/application to automatically reconnect to Watson IoT Platform while they are in a disconnected state.
   * - Websocket
     - No
     - Enables device/gateway/application to connect to Watson IoT Platform using WebSockets
   * - Event/Command publish using MQTT
     - Yes
     - Enables device/gateway/application to publish messages using MQTT. Refer to `Device <https://console.ng.bluemix.net/docs/services/IoT/devices/libraries/python.html#publishing_events>`_ , `Gateway <https://github.com/ibm-watson-iot/iot-python/blob/master/docs/Gateway.rst>`_ and `Application <https://console.ng.bluemix.net/docs/services/IoT/applications/libraries/python.html#publishing_device_events>`_ documentations for more details.
   * - Event/Command publish using HTTP
     - Yes
     - Enables device/gateway/application to publish messages using HTTP.
   * - Data Formats
     - JSON, XML, user-defined
     - Mulitple Data formats support.
