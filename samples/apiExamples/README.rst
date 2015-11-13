==========================================================================
Python Client Library - Internet of Things Foundation Connect API Support
==========================================================================

Introduction
-------------------------------------------------------------------------------

This client library describes how to use Internet of Things Foundation API with the Python ibmiotf client library. For help with getting started with this module, see `Python Client Library - Introduction <https://github.com/ibm-messaging/iot-python>`__. 

This client library is divided into Four sections, all included within the library. 

This section contains information on how applications can use the `Python ibmiotf Client Library <https://pypi.python.org/pypi/ibmiotf>`__ to interact with your organization in the IBM Internet of Things Foundation Connect through ReST APIs.

The Device section contains information on how devices can publish events and handle commands using the Python ibmiotf Client Library. 

Application section contains information on how applications can use the Python ibmiotf Client Library to interact with devices.

Constructor
-------------------------------------------------------------------------------

The constructor builds the client instance, and accepts a Properties object containing the following definitions:

* org - Your organization ID
* auth-method - Always "apikey"
* auth-key - API key
* auth-token - API key token

The Properties object creates definitions which are used to interact with the Internet of Things Foundation Connect module. 

The following code snippet shows how to construct the APIClient instance using the properties,

.. code:: python
    
	import ibmiotf
	import ibmiotf.application

	apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	apiCli = ibmiotf.api.ApiClient(apiOptions)
        

----

Response and Exception
----------------------

Each method in the APIClient responds with either a valid response (JSON or boolean) in the case of success or IoTFCReSTException in the case of failure. The IoTFCReSTException contains the following properties that application can parse to get more information about the failure.

* httpcode - HTTP Status Code
* message - Exception message containing the reason for the failure
* response - JsonElement containing the partial response if any otherwise null

So in the case of failure, application needs to parse the response to see if the action is partially successful or not.


----


Organization details
----------------------------------------------------

Application can use method getOrganizationDetails() to view the Organization details:

.. code:: Python

    orgDetail = apiCli.getOrganizationDetails();

Refer to the Organization Configuration section of the `IBM IoT Foundation API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

----

Bulk device operations
----------------------------------------------------

Applications can use bulk operations to get, add or remove devices in bulk from Internet of Things Foundation Connect.

Refer to the Bulk Operations section of the `IBM IoT Foundation API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

Get Devices in bulk
~~~~~~~~~~~~~~~~~~~

Method getAllDevices() can be used to retrieve all the registered devices in an organization from Internet of Things Foundation Connect, each request can contain a maximum of 512KB. 

.. code:: python

    response = apiClient.getAllDevices();
    

The response contains parameters and application needs to retrieve the dictionary *results* from the response to get the array of devices returned. Other parameters in the response are required to make further call, for example, the *_bookmark* element can be used to page through results. Issue the first request without specifying a bookmark, then take the bookmark returned in the response and provide it on the request for the next page. Repeat until the end of the result set indicated by the absence of a bookmark. Each request must use exactly the same values for the other parameters, or the results are undefined.

In order to pass the *_bookmark* or any other condition, the overloaded method must be used. The overloaded method takes the parameters in the form of org.apache.http.message.BasicNameValuePair as shown below,

.. code:: python

	import ibmiotf
	import ibmiotf.application
    
        ...
    
        try:
	    apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	    apiCli = ibmiotf.api.ApiClient(apiOptions)
    
            ...
	    print("Retrieved Devices = ", apiCli.getAllDevices({'typeId' : deviceTypeId}))		


Register Devices in bulk
~~~~~~~~~~~~~~~~~~~~~~~~

Method addMultipleDevices() can be used to register one or more devices to Internet of Things Foundation Connect, each request can contain a maximum of 512KB. For example, the following sample shows how to add a device using the bulk operation.


.. code:: python

	import ibmiotf
	import ibmiotf.application
    
        ...
    
        try:
	    apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	    apiCli = ibmiotf.api.ApiClient(apiOptions)
    
            ...
            print("\nBulk Registering new devices 4")	
            listOfDevices = [{'typeId' : deviceTypeId, 'deviceId' : '200020002004'}, {'typeId' : deviceTypeId, 'deviceId' : '200020002005'}]
            print("Registered Device = ", apiCli.addMultipleDevices(listOfDevices))

    
The response will contain the generated authentication tokens for all devices. Application must make sure to record these tokens when processing the response. The Internet of Things Foundation will not able to retrieve lost authentication tokens. 

Delete Devices in bulk
~~~~~~~~~~~~~~~~~~~~~~~~

Method deleteMultipleDevices() can be used to delete multiple devices from Internet of Things Foundation Connect, each request can contain a maximum of 512KB. For example, the following sample shows how to delete 2 devices using the bulk operation.



.. code:: python

	import ibmiotf
	import ibmiotf.application
    
        ...
    
        try:
	    apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	    apiCli = ibmiotf.api.ApiClient(apiOptions)
            ...
            print("\nDeleting bulk devices")
            listOfDevices = [ {'typeId' : deviceTypeId, 'deviceId' : '200020002004'}, {'typeId' : deviceTypeId, 'deviceId' : '200020002005'} ]
            deleted = apiCli.deleteMultipleDevices(listOfDevices)
            print("Device deleted = ", deleted)

----

Device Type operations
----------------------------------------------------

Applications can use device type operations to list all, create, delete, view and update device types in Internet of Things Foundation Connect.

Refer to the Device Types section of the `IBM IoT Foundation API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

Get all Device Types
~~~~~~~~~~~~~~~~~~~~~~~~

Method getAllDeviceTypes() can be used to retrieve all the registered device types in an organization from Internet of Things Foundation. For example,

.. code:: python

    response = apiCli.getAllDeviceTypes();


The response contains parameters and application needs to retrieve the dictionary *results* from the response to get the array of devices returned. Other parameters in the response are required to make further call, for example, the *_bookmark* element can be used to page through results. Issue the first request without specifying a bookmark, then take the bookmark returned in the response and provide it on the request for the next page. Repeat until the end of the result set indicated by the absence of a bookmark. Each request must use exactly the same values for the other parameters, or the results are undefined.
    
In order to pass the *_bookmark* or any other condition, the overloaded method must be used. The overloaded method takes the parameters in the form of a dictionary as shown below,

.. code:: python

     parameter = {'_limit' : 2}	
     print("All Retrieved Device = ", apiCli.getAllDeviceTypes(parameter))
		

Add a Device Type
~~~~~~~~~~~~~~~~~~~~~~~~

Method addDeviceType() can be used to register a device type to Internet of Things Foundation Connect. For example,

.. code:: python

     apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
     apiCli = ibmiotf.api.ApiClient(apiOptions)
     deviceInfo1 = {"serialNumber": "100087", "manufacturer": "ACME Co.", "model": "7865", "deviceClass": "A", "description": "My shiny device", "fwVersion": "1.0.0", "hwVersion": "1.0", "descriptiveLocation": "Office 5, D Block"}
     metadata1 = {"customField1": "customValue1", "customField2": "customValue2"}

     print("Registering a device type")
     print("Registered Device = ", apiCli.addDeviceType(deviceType = "myDeviceType5", description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
    

Delete a Device Type
~~~~~~~~~~~~~~~~~~~~~~~~

Method deleteDeviceType() can be used to delete a device type from Internet of Things Foundation. For example,

.. code:: python

     print("\nDeleting a device type")	
     deletion = apiCli.deleteDeviceType("myDeviceType5")
     print("Device Type deleted = ", deletion)
    
Get a Device Type
~~~~~~~~~~~~~~~~~~~~~~~~

In order to retrieve information about a given device type, use the method getDeviceType() and pass the deviceTypeId as a parameter as shown below

.. code:: python

     print("Retrieved Device = ", apiCli.getDeviceType("myDeviceType5"))

    
Update a Device Type
~~~~~~~~~~~~~~~~~~~~~~~~

Method updateDeviceType() can be used to modify one or more properties of a device type. The properties that needs to be modified should be passed in the form of a dictionary, as shown below

.. code:: python
    
     print("\nUpdating a device type")
     description = "mydescription"
     metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
     deviceInfo = {"serialNumber": "string", "manufacturer": "string", "model": "string", "deviceClass": "string", "fwVersion": "string", "hwVersion": "string","descriptiveLocation": "string"}
     print("Modified Device = ", apiCli.updateDeviceType("myDeviceType5", description, deviceInfo, metadata2))

----

Device operations
----------------------------------------------------

Applications can use device operations to list, add, remove, view, update, view location and view management information of a device in Internet of Things Foundation.

Refer to the Device section of the `IBM IoT Foundation API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

Get Devices of a particular Device Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method retrieveDevices() can be used to retrieve all the devices of a particular device type in an organization from Internet of Things Foundation. For example,

.. code:: python

     print("\nRetrieving All existing devices")	
     print("Retrieved Devices = ", apiCli.retrieveDevices(deviceTypeId))
    
The response contains parameters and application needs to retrieve the dictionary *results* from the response to get the array of devices returned. Other parameters in the response are required to make further call, for example, the *_bookmark* element can be used to page through results. Issue the first request without specifying a bookmark, then take the bookmark returned in the response and provide it on the request for the next page. Repeat until the end of the result set indicated by the absence of a bookmark. Each request must use exactly the same values for the other parameters, or the results are undefined.

In order to pass the *_bookmark* or any other condition, the overloaded method must be used. The overloaded method takes the parameters in the form of dictionary as shown below,

.. code:: python

    response = apiClient.retrieveDevices("iotsample-ardunio", parameters);
		
The above snippet sorts the response based on device id and uses the bookmark to page through the results.

Add a Device
~~~~~~~~~~~~~~~~~~~~~~~

Method registerDevice() can be used to register a device to Internet of Things Foundation. For example,

.. code:: python

     deviceId2 = "200020002000"
     authToken = "password"
     metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
     deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
     location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
     print("\nRegistering a new device with just deviceType and deviceId")	
     print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId2))


Delete a Device
~~~~~~~~~~~~~~~~~~~~~~~~

Method deleteDevice() can be used to delete a device from Internet of Things Foundation. For example,

.. code:: java

     deleted = apiCli.deleteDevice(deviceTypeId, deviceId)
     print("Device deleted = ", deleted)

    
Get a Device
~~~~~~~~~~~~~~~~~~~~~~~~

Method getDevice() can be used to retrieve a device from Internet of Things Foundation. For example,

.. code:: python

     print("\nRetrieving an existing device")	
     print("Retrieved Device = ", apiCli.getDevice(deviceTypeId, deviceId))
    

Get all Devices
~~~~~~~~~~~~~~~~~~~~~~~~

Method getAllDevices() can be used to retrieve all the device from Internet of Things Foundation. For example,

.. code:: python

     print("Retrieved Devices = ", apiCli.getAllDevices({'typeId' : deviceTypeId}))


Update a Device
~~~~~~~~~~~~~~~~~~~~~~~~

Method updateDevice() can be used to modify one or more properties of a device. For Example

.. code:: python
    
     print("\nUpdating an existing device")
     status = { "alert": { "enabled": True }  }
     print("Device Modified = ", apiCli.updateDevice(deviceTypeId, deviceId, metadata2, deviceInfo, status))


Get Location Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getDeviceLocation() can be used to get the location information of a device. For example, 

.. code:: python
    
    JsonObject response = apiClient.getDeviceLocation("iotsample-ardunio", "ardunio01");

Update Location Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method updateDeviceLocation() can be used to modify the location information for a device. For example,

.. code:: python
    
     print("\nUpdating device location")
     deviceLocation = { "longitude": 0, "latitude": 0, "elevation": 0, "accuracy": 0, "measuredDateTime": "2015-10-28T08:45:11.673Z"}
     print("Device Location = ", apiCli.updateDeviceLocation(deviceTypeId, deviceId, deviceLocation))

If no date is supplied, the entry is added with the current date and time. 

Get Device Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getDeviceLocation() can be used to retrieve the device location. For example,

.. code:: python
    
     print("\nRetrieving device location")
     print("Device Location = ", apiCli.getDeviceLocation(deviceTypeId, deviceId))


Get Device Management Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getDeviceManagementInformation() can be used to get the device management information for a device. For example, 

.. code:: python
    
     print("\nRetrieving device management information")
     info = apiCli.getDeviceManagementInformation("iotsample-arduino", "00aabbccde03")
     print("Device management info retrieved = ", info)

----

Device diagnostic operations
----------------------------------------------------

Applications can use Device diagnostic operations to clear logs, retrieve logs, add log information, delete logs, get specific log, clear error codes, get device error codes and add an error code to Internet of Things Foundation.

Refer to the Device Diagnostics section of the `IBM IoT Foundation API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

Get Diagnostic logs
~~~~~~~~~~~~~~~~~~~~~~

Method getAllDiagnosticLogs() can be used to get all diagnostic logs of the device. For example,

.. code:: python

     print("\nRetrieving All device diagnostics")
     print("Diagnostic Logs = ", apiCli.getAllDiagnosticLogs(deviceTypeId, deviceId)));
    
Clear Diagnostic logs 
~~~~~~~~~~~~~~~~~~~~~~

Method clearAllDiagnosticLogs() can be used to clear the diagnostic logs of the device. For example,

.. code:: python

     print("\nClearing All device diagnostics")
     print("Diagnostic Logs = ", apiCli.clearAllDiagnosticLogs(deviceTypeId, deviceId)));
    
Add a Diagnostic log
~~~~~~~~~~~~~~~~~~~~~~

Method addDiagnosticLog() can be used to add an entry in the log of diagnostic information for the device. The log may be pruned as the new entry is added. If no date is supplied, the entry is added with the current date and time. For example,

.. code:: python

     logs = { "message": "newMessage", "severity": 1, "data": "New log", "timestamp": "2015-10-29T07:43:57.109Z"}
     print("Diagnostic Logs creation = ", apiCli.addDiagnosticLog(deviceTypeId, deviceId, logs))

Get single Diagnostic log
~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getDiagnosticLog() can be used to retrieve a diagnostic log based on the log id. For example,

.. code:: python

     print("\nRetrieving single log")
     print("Diagnostic Logs = ", apiCli.getDiagnosticLog(deviceTypeId, deviceId, logId1))
    
Delete a Diagnostic log
~~~~~~~~~~~~~~~~~~~~~~~~~~

Method deleteDiagnosticLog() can be used to delete a diagnostic log based on the log id. For example,

.. code:: python

     print("Deleting single log")
     print("Diagnostic Logs = ", apiCli.deleteDiagnosticLog(deviceTypeId, deviceId, logId1))
    

Clear Diagnostic ErrorCodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method clearAllErrorCodes() can be used to clear the list of error codes of the device. The list is replaced with a single error code of zero. For example,

.. code:: python

     print("\nDeleting all error code")
     print("Error codes deleted = ", apiCli.clearAllErrorCodes(deviceTypeId, deviceId))
    
Get Diagnostic ErrorCodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getAllDiagnosticErrorCodes() can be used to retrieve all diagnostic ErrorCodes of the device. For example,

.. code:: python

     print("\nRetrieving all error code")
     print("Error codes retrieved = ", apiCli.getAllDiagnosticErrorCodes(deviceTypeId, deviceId))


Add single Diagnostic ErrorCode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method addErrorCode() can be used to add an error code to the list of error codes for the device. The list may be pruned as the new entry is added. For example,

.. code:: python

     print("\nAdding error code")
     errorCode = { "errorCode": 0, "timestamp": "2015-10-29T05:43:57.112Z" }
     print("Error code creation = ", apiCli.addErrorCode(deviceTypeId, deviceId, errorCode))

----

Connection problem determination
----------------------------------

Method getDeviceConnectionLogs() can be used to list connection log events for a device to aid in diagnosing connectivity problems. The entries record successful connection, unsuccessful connection attempts, intentional disconnection and server-initiated disconnection.

.. code:: python

     deviceTypeId = "iotsample-arduino"
     deviceId = "00aabbccde03"
     print("Device Logs = ", apiCli.getDeviceConnectionLogs(deviceTypeId, deviceId))

Refer to the Problem Determination section of the `IBM IoT Foundation Connect API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

----

Historical Event Retrieval
----------------------------------
Application can use this operation to view events from all devices, view events from a device type or to view events for a specific device.

Refer to the Historical Event Retrieval section of the `IBM IoT Foundation Connect API <https://docs.internetofthings.ibmcloud.com/swagger/v0002.html>`__ for information about the list of query parameters, the request & response model and http status code.

View events from all devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getHistoricalEvents() can be used to view events across all devices registered to the organization.

.. code:: python

     print("Historical Events = ", apiCli.getHistoricalEvents())

The response will contain some parameters and the application needs to retrieve the JSON element *events* from the response to get the array of events returned. Other parameters in the response are required to make further call, for example, the *_bookmark* element can be used to page through results. Issue the first request without specifying a bookmark, then take the bookmark returned in the response and provide it on the request for the next page. Repeat until the end of the result set indicated by the absence of a bookmark. Each request must use exactly the same values for the other parameters, or the results are undefined.

In order to pass the *_bookmark* or any other condition, the overloaded method must be used. The overloaded method takes the parameters in the form of dictionary as shown below,

.. code:: python

     startTime = math.floor(time.mktime((2013, 10, 10, 17, 3, 38, 0, 0, 0)) * 1000)
     endTime =  math.floor(time.mktime((2015, 10, 29, 17, 3, 38, 0, 0, 0)) * 1000)
     duration = {'start' : startTime, 'end' : endTime }
     print("Historical Events = ", apiCli.getHistoricalEvents(options = duration))

The above snippet returns the events between the start and end time.

View events from a device type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getHistoricalEvents() can be used to view events from all the devices of a particular device type. 

.. code:: python

     print("\nOnly device type passed")	
     print("Historical Events = ", apiCli.getHistoricalEvents(deviceType = 'iotsample-arduino', options = duration))

The response will contain some parameters and the application needs to retrieve the JSON element *events* from the response to get the array of events returned. As mentioned in the *view events from all devices* section, the overloaded method can be used to control the output.


View events from a device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method getHistoricalEvents() can be used to view events from a specific device.

.. code:: python

     print("\nBoth device type and device passed")				
     print("Historical Events = ", apiCli.getHistoricalEvents(deviceType = 'iotsample-arduino', deviceId = '00aabbccde03', options = duration))

The response will contain more parameters and application needs to retrieve the JSON element *events* from the response to get the array of events returned. 

----


Examples
-------------
* `bulkOperations.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/bulkOperations.py>`__ - Sample that showcases how to get, add or remove devices in bulk from Internet of Things Foundation.
* `deviceDiagnostics.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/deviceDiagnostics.py>`__ - A sample that showcases various Device Diagnostic operations like clear logs, retrieve logs, add log information, delete logs, get specific log, clear error codes, get device error codes and add an error code to Internet of Things Foundation.
* `deviceTypes.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/deviceTypes.py>`__ - Sample that showcases various Device Type API operations like list all, create, delete, view and update device types in Internet of Things Foundation.
* `devices.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/devices.py>`__ - A sample that showcases various Device operations like list, add, remove, view, update, view location and view management information of a device in Internet of Things Foundation.
* `historian.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/historian.py>`__ - A sample that showcases how to retrieve historical events from Internet of Things Foundation.
* `logConnection.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/logConnection.py>`__ - A sample that showcases device connectivity log operations that can be performed on Internet of Things Foundation.
* `organization.py <https://github.com/ibm-messaging/iot-python/blob/master/samples/apiExamples/organization.py>`__ - A sample that showcases organization operations that can be performed on Internet of Things Foundation.
