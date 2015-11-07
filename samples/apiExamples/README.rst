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
    

The response will contain more parameters and application needs to retrieve the JSON element *results* from the response to get a list of devices. Other parameters in the response are required to make further call, for example, the *_bookmark* element can be used to page through results. Issue the first request without specifying a bookmark, then take the bookmark returned in the response and provide it on the request for the next page. Repeat until the end of the result set indicated by the absence of a bookmark. Each request must use exactly the same values for the other parameters, or the results are undefined.

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
