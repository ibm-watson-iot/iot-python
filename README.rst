IBM Watson Internet of Things Platform for Python
============================================

Python module for interacting with the `IBM Watson Internet of Things
Platform <https://internetofthings.ibmcloud.com>`__.

-  `Python 3.5 <https://www.python.org/downloads/release/python-350/>`__
-  `Python 2.7 <https://www.python.org/downloads/release/python-2710/>`__

Note: Support for MQTT over SSL requires at least Python v2.7.9 or v3.4, and openssl v1.0.1

Dependencies
------------

-  `paho-mqtt <https://pypi.python.org/pypi/paho-mqtt>`__
-  `iso8601 <https://pypi.python.org/pypi/iso8601>`__
-  `pytz <https://pypi.python.org/pypi/pytz>`__
-  `requests <https://pypi.python.org/pypi/requests>`__

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

Migrating from v0.1.x to v0.2.x
-------------------------------

There is a significant change between the 0.1.x releases and 0.2.x that may require changes to client code.  Version 0.1 of the lirbary will remain available, if you do not
wish to update your device or application code for the 0.2 release simply install the library using ``pip install ibmiotf==0.1.8``

- The library now uses ``typeId``, ``deviceId``, and ``eventId`` consistently
- Changes to API support:

  - Mixed use of ``queryParameters`` & ``parameters`` consolidated to always use ``parameters``
  - ``retrieveDevices()`` & ``getAllDevices()`` removed.  Single ``getDevices()`` method remains
  - ``addMultipleDevices`` renamed to ``registerDevices()`` for consistency with ``registerDevice()`` method
  - ``getAllDeviceTypes()`` renamed to ``getDeviceTypes()`` for consistency with other getResourceTypePlural methods
  - ``IoTFCReSTException`` now ``APIException``
  - ``getDeviceConnectionLogs()`` renamed ``getConnectionLogs`` & restructured to support parameters object instead of ``deviceTypeId`` and ``deviceId``

- As of v0.2.1 the application client only requires two properties to be passed in ``options``: ``auth-token`` and ``auth-key``, ``orgId`` and ``auth-method`` are now determined from the API key provided.


Documentation
-------------

-  `Device Client <https://docs.internetofthings.ibmcloud.com/devices/libraries/python.html>`__
-  `Application Client <https://docs.internetofthings.ibmcloud.com/applications/libraries/python.html>`__
