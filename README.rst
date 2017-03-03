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
   :widths: 35 70
   :header-rows: 1

   * - Feature
     - Supported?
   * - Device Connectivity
     - Yes
   * - Gateway Connectivity
     - Yes
   * - Application connectivity
     - Yes
   * - Watson IoT API
     - Yes
   * - SSL/TLS
     - Yes
   * - Client side Certificate based authentication
     - No
   * - Device Management
     - Yes
   * - Device Management Extension
     - Yes
   * - Scalable Application
     - Yes
   * - Auto Reconnect
     - Yes
   * - Websocket
     - Yes
   * - Event/Command publish using MQTT
     - Yes
   * - Event/Command publish using HTTP
     - Yes
   * - Data Formats
     - JSON, XML and TEXT
