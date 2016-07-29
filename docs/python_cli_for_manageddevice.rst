======================================
Python Client Library - Managed Device
======================================

Introduction
-------------
This client library describes how to use devices with the Python ibmiotf client library. For a basic introduction to the broader module, see `Python Client Library - Introduction <https://github.com/ibm-messaging/iot-python>`__.

This section contains information on how devices can connect to the IBM Watson IoT Platform Device Management service using Python and perform device management operations like firmware update, location update, and diagnostics update.

The Device section contains information on how devices can publish events and handle commands using the Python ibmiotf Client Library.

The Applications section contains information on how applications can use the Python ibmiotf Client Library to interact with devices.


Device Management
-------------------------------------------------------------------------------
The `device management <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html>`__ feature enhances the IBM Watson IoT Platform Connect service with new capabilities for managing devices. Device management makes a distinction between managed and unmanaged devices:

* **Managed Devices** are defined as devices which have a management agent installed. The management agent sends and receives device metadata and responds to device management commands from the IBM Watson IoT Platform Connect.
* **Unmanaged Devices** are any devices which do not have a device management agent. All devices begin their lifecycle as unmanaged devices, and can transition to managed devices by sending a message from a device management agent to the IBM Watson IoT Platform Connect.


---------------------------------------------------------------------------
Connecting to the IBM Watson IoT Platform Connect Device Management Service
---------------------------------------------------------------------------

Create DeviceData
------------------------------------------------------------------------
The `device model <https://docs.internetofthings.ibmcloud.com/reference/device_model.html>`__ describes the metadata and management characteristics of a device. The device database in the IBM Watson IoT Platform Connect is the master source of device information. Applications and managed devices are able to send updates to the database such as a location or the progress of a firmware update. Once these updates are received by the IBM Watson IoT Platform Connect, the device database is updated, making the information available to applications.

The device model in the ibmiotf client library is represented as DeviceData and to create a DeviceData one needs to create the DeviceInfo and ManagedClient objects and call the respective methods such as ,

* setLocation
* setErrorCode

The following code snippet shows how to create the mandatory object DeviceInfo along with the ManagedClient:

.. code:: python

    client = None
    simpleDeviceInfo = ibmiotf.device.DeviceInfo()
    simpleDeviceInfo.description = deviceName
    simpleDeviceInfo.deviceClass = platform.machine()
    simpleDeviceInfo.manufacturer = platform.system()
    simpleDeviceInfo.fwVersion = platform.version()
    simpleDeviceInfo.hwVersion = None
    simpleDeviceInfo.model = None
    simpleDeviceInfo.serialNumber = None


    try:
        #By default the client is an unmanaged client and on disconnecting it again becomes unmanaged
        client = ibmiotf.device.ManagedClient(options, logHandlers=None, deviceInfo=simpleDeviceInfo)
        client.commandCallback = commandProcessor
        client.connect()
        client.manage(3600, supportDeviceActions=True, supportFirmwareActions=True)

        client.setErrorCode(1).wait(10)
        print("Error code setting returned back")
        time.sleep(interval)
        client.clearErrorCodes()

Construct ManagedDevice
-------------------------------------------------------------------------------
ManagedClient - A device class that connects the device as managed device to IBM Watson IoT Platform Connect and enables the device to perform one or more Device Management operations. Also the ManagedClient instance can be used to do normal device operations like publishing device events and listening for commands from application.

ManagedClient exposes the following constructor to support different user patterns by accepting the following

Constructs a ManagedClient instance by accepting the opts JSON object (which contains the following device data),

* org - Your organization ID.
* type - The type of your device.
* id - The ID of your device.
* auth-method - Method of authentication (The only value currently supported is "token").
* auth-token - Auth Token

And logHandler and DeviceInfo as optional parameters

All these properties are required to interact with the IBM Watson IoT Platform Connect.

The following code shows how to create a ManagedDevice instance:

.. code:: python

    organization = "MASKED"
    deviceType = "iotsample-arduino"
    deviceId = "00aabbccde05"
    deviceName = platform.node()
    authMethod = "token"
    authToken = "MASKED"
    configFilePath = None

    client = None
    options = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}

    try:
        #By default the client is an unmanaged client and on disconnecting it again becomes unmanaged
        client = ibmiotf.device.ManagedClient(options, logHandlers=None, deviceInfo=simpleDeviceInfo)


Manage
------------------------------------------------------------------
The device can invoke manage() method to participate in device management activities. The manage request will initiate a connect request internally if the device is not connected to the Internet of Things Platform Connect already:

.. code:: python

	client.manage();

The device can use overloaded manage (lifetime) method to register the device for a given timeframe. The timeframe specifies the length of time within which the device must send another **Manage device** request in order to avoid being reverted to an unmanaged device and marked as dormant.

.. code:: python

    client.manage(3600);

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html#/manage-device#manage-device>`__ for more information about the manage operation.

Unmanage
-----------------------------------------------------

A device can invoke unmanage() method when it no longer needs to be managed. The Internet of Things Platform Connect will no longer send new device management requests to this device and all device management requests from this device will be rejected other than a **Manage device** request.

.. code:: python

	client.unmanage();

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html#/unmanage-device#unmanage-device>`__ for more information about the Unmanage operation.

Location Update
-----------------------------------------------------

Devices that can determine their location can choose to notify the Internet of Things Platform Connect about location changes. In order to update the location, the device needs to call setLocation method in client object with longitude,latitude and accuracy as parameters.

.. code:: python

    client.setLocation(longitude=100, latitude=78, accuracy=100)

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html#/update-location#update-location>`__ for more information about the Location update.

Append/Clear ErrorCodes
-----------------------------------------------

Devices can choose to notify the Internet of Things Platform Connect about changes in their error status. In order to send the ErrorCodes the device needs to call setErrorCode() method in client object ,then wait for it to be completed (sync) as follows:

.. code:: python

	client.setErrorCode(1).wait()

Also, the ErrorCodes can be cleared from Internet of Things Platform Connect by calling the clearErrorCodes() method as follows:

.. code:: python

  client.clearErrorCodes()

Append/Clear Log messages
-----------------------------
Devices can choose to notify the Internet of Things Platform Connect about changes by adding a new log entry. Log entry includes a log messages and severity, as well as an optional base64-encoded binary diagnostic data as string. In order to send log messages, the device needs to to call addLog() method in client object ,then wait for it to be completed (sync) as follows:

.. code:: python

	client.addLog(msg="test",data="testdata",sensitivity=0).wait()

Also, the log messages can be cleared from Internet of Things Platform Connect by calling the clear method as follows:

.. code:: python

	client.clearLog()

The device diagnostics operations are intended to provide information on device errors, and does not provide diagnostic information relating to the devices connection to the Internet of Things Platform Connect.

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html#/update-location#update-location>`__ for more information about the Diagnostics operation.


Firmware Actions
-------------------------------------------------------------
The firmware update process is separated into two distinct actions:

* Downloading Firmware
* Updating Firmware.

The device needs to do the following activities to support Firmware Actions:

**1. Construct DeviceInfo Object (Optional)**

In order to perform Firmware actions the device can optionally construct the DeviceInfo object and pass it to ManagedClient as follows:

.. code:: python

  myDeviceInfo = ibmiotf.device.DeviceInfo()
  myDeviceInfo.description = "%s (%s)" % (dmidecode("system-version"), deviceName) if isDmidecodeAvailable() else deviceName
  myDeviceInfo.deviceClass = dmidecode("system-version") if isDmidecodeAvailable() else platform.machine()
  myDeviceInfo.manufacturer = dmidecode("system-manufacturer") if isDmidecodeAvailable() else platform.system()
  myDeviceInfo.fwVersion = dmidecode("bios-version") if isDmidecodeAvailable() else platform.version()
  myDeviceInfo.hwVersion = dmidecode("baseboard-product-name") if isDmidecodeAvailable() else None
  myDeviceInfo.model = dmidecode("system-product-name") if isDmidecodeAvailable() else None
  myDeviceInfo.serialNumber = dmidecode("system-serial-number") if isDmidecodeAvailable() else None

  if configFilePath is not None:
      options = ibmiotf.device.ParseConfigFile(configFilePath)
  else:
      options = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
  client = ibmiotf.device.ManagedClient(options, logHandlers=None, deviceInfo=myDeviceInfo)
  client.firmwereActionCallback = firmwereCallback
  client.connect()


The DeviceInfo object represents the current firmware of the device and will be used to report the status of the Firmware Download and Firmware Update actions to IBM Watson Internet of Things Platform. In case this DeviceInfo object is not constructed by the device, then the library creates an empty object and reports the status to Watson IoT Platform.

**2. Inform the server about the Firmware action support**

The device needs to set the firmware action flag to true in order for the server to initiate the firmware request. This can be achieved by invoking the manage() method with a true value for supportFirmwareActions parameter,

.. code:: python

    client.manage(3600, False, True)

Once the support is informed to the DM server, the server then forwards the firmware actions to the device.

**3. Create the Firmware Action Callback**

In order to support the Firmware action, the device needs to create a callback and assign it to firmwereActionCallback. The call back will be called with two parameters:

* action : download or  update
* info : device info object

.. code:: python

    def firmwereCallback(action,info):
    if action is 'download' :
        threading.Thread(target=  downloadHandler,args=(client,info)).start();
    if action is 'update' :
        client.setUpdateStatus(ManagedClient.UPDATESTATE_IN_PROGRESS)
        threading.Timer(5,client.setUpdateStatus,[ManagedClient.UPDATESTATE_SUCCESS]).start()

    ......
    ......
    ......

    client = ibmiotf.device.ManagedClient(options, logHandlers=None, deviceInfo=myDeviceInfo)
    client.firmwereActionCallback = firmwereCallback
    client.connect()

**3.1 Sample implementation of downloadFirmware**

The implementation must create a separate thread and add a logic to download the firmware and report the status of the download via DeviceFirmware object. If the Firmware Download operation is successful, then the state of the firmware to be set to DOWNLOADED by calling setState method in client object.

If an error occurs during Firmware Download the state should be set to IDLE and updateStatus should be set to one of the error status values by calling setUpdateStatus in client object:

* OUT_OF_MEMORY
* CONNECTION_LOST
* INVALID_URI

A sample Firmware Download implementation is shown below:

.. code:: python

  def downloadHandler(client,info):
    try:
        client.setState(ManagedClient.UPDATESTATE_DOWNLOADING)
        url = info.url
        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()
        client.setState(ManagedClient.UPDATESTATE_DOWNLOADED)
        verifiyImage(client, info, file_name)
    except urllib2.HTTPError:
        client.setUpdateStatus(ManagedClient.UPDATESTATE_CONNECTION_LOST)
    except urllib2.URLError:
        client.setUpdateStatus(ManagedClient.UPDATESTATE_INVALID_URI)
    except MemoryError:
        client.setUpdateStatus(ManagedClient.UPDATESTATE_OUT_OF_MEMORY)
    except Exception :
        print("exception in downloading")



  def firmwereCallback(action,info):
    if action is 'download' :
        threading.Thread(target=  downloadHandler,args=(client,info)).start();
    if action is 'update' :
        threading.Thread(target= updateHandler,args=(client,info)).start();


Device can check the integrity of the downloaded firmware image using the verifier and report the status back to IBM Watson Internet of Things Platform. The verifier can be set by the device during the startup (while creating the DeviceInfo Object) or as part of the Download Firmware request by the application. A sample code to verify the same is below:

.. code:: python

	def md5(fname):
		hash_md5 = hashlib.md5()
		with open(fname, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
		return hash_md5.hexdigest()

	def verifiyImage(client,info,filename):
		if info.verifier != None :
			hashVal = md5(filename)
			if hashVal != info.verifier :
				client.setUpdateStatus(ManagedClient.UPDATESTATE_VERIFICATION_FAILED)


The complete code can be found in the device management sample `<https://github.com/ibm-messaging/iot-python/tree/master/samples/managedDevice>`__.

**3.2 Sample implementation of updateFirmware**

The implementation must create a separate thread and add a logic to install the downloaded firmware and report the status of the update. If the Firmware Update operation is successful, then the state of the firmware should to be set to IDLE and setUpdateStatus should be set to SUCCESS.

If an error occurs during Firmware Update, updateStatus should be set to one of the error status values:

* OUT_OF_MEMORY
* UNSUPPORTED_IMAGE

A sample Firmware Update implementation is shown below:

.. code:: python

	def updateHandler(client,info):
		try:
			client.setUpdateStatus(ManagedClient.UPDATESTATE_IN_PROGRESS)
			threading.Timer(5,client.setUpdateStatus,[ManagedClient.UPDATESTATE_SUCCESS]).start()
		except MemoryError:
			client.setUpdateStatus(ManagedClient.UPDATESTATE_OUT_OF_MEMORY)
		except Exception :
			client.setUpdateStatus(ManagedClient.UPDATESTATE_UNSUPPORTED_IMAGE)

	def firmwereCallback(action,info):
		if action is 'download' :
			threading.Thread(target= downloadHandler,args=(client,info)).start();
		if action is 'update' :
			threading.Thread(target= updateHandler,args=(client,info)).start();


The complete code can be found in the device management sample `<https://github.com/ibm-messaging/iot-python/tree/master/samples/managedDevice>`__.

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/requests.html#/firmware-actions#firmware-actions>`__ for more information about the Firmware Actions.

Device Actions
------------------------
The IBM Watson Internet of Things Platform supports the following device actions:

* Reboot
* Factory Reset

The device needs to do the following activities to support Device Actions:

**1. Inform server about the Device Actions support**

In order to perform Reboot and Factory Reset, the device needs to inform the IBM Watson Internet of Things Platform about its support first. This can be achieved by invoking the manage() method with a True value for supportDeviceActions parameter,

.. code:: python

	// Second parameter represents the device action support
    	client.manage(3600, True, True)

Once the support is informed to the DM server, the server then forwards the device action requests to the device.

**2. Create the Device Action Callback**

In order to support the device action, the device needs to create a callback and assign it to deviceActionCallback. The call back will be called with two parameters:
 *action : 'reboot' or  'reset'
 * reqId : uuid of the request

.. code:: python

	def deviceActionCallback(reqId,action):
		print ("got action %s" % action)
		if isdeviceActionNotSupport :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_FUNCTION_NOT_SUPPORTED,"not supported")
			return False

		if action is 'reboot' :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_INTERNAL_ERROR,"reboot failed")
			#os.execl(sys.executable, sys.executable, *sys.argv)

		if action is 'reset' :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_ACCEPTED,"Factory Reset Sucess")
			print("do you factory reset work here")

    ......
    ......
    ......

    client.deviceActionCallback = deviceActionCallback
    client.connect()
    client.manage(3600, True, True)

**3. Sending the Device Action Response **

In order to inform the WIOTP about the device action status we need to call respondDeviceAction method in client object to with request Id , status and message.
There are three device action status available :

*FUNCTION_NOT_SUPPORTED
*ACCEPTED
*INTERNAL_ERROR

.. code:: python

	def deviceActionCallback(reqId,action):
		print ("got action %s" % action)
		if isdeviceActionNotSupport :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_FUNCTION_NOT_SUPPORTED,"not supported")
			return False

		if action is 'reboot' :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_INTERNAL_ERROR,"reboot failed")
			#os.execl(sys.executable, sys.executable, *sys.argv)

		if action is 'reset' :
			client.respondDeviceAction(reqId,ManagedClient.RESPONSECODE_ACCEPTED,"Factory Reset Sucess")
			print("do you factory reset work here")

The complete code can be found in the device management sample `<https://github.com/ibm-messaging/iot-python/tree/master/samples/managedDevice>`__.

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/requests.html#/device-actions-reboot#device-actions-reboot>`__ for more information about the Device Actions.

Device Management Extension (DME) Packages
-----------------------------------------------------
An extension package is a JSON document which defines a set of device management actions. The actions can be initiated 
against one or more devices which support those actions. The actions are initiated in the same way as the default device
management actions by using either the IoT Platform dashboard or the device management REST APIs.

For Device management extension package format, refer to `documentation <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/custom_actions.html>`__.

Supporting Custom Device Management Actions
------------------------------------------------------
Device management actions defined in an extension package may only be initiated against devices which support those actions.
A device specifies what types of actions it supports when it publishes a manage request to the IoT Platform. In order to
allow a device to receive custom actions defined in a particular extension package, the device must specify that extension’s
bundle identifier in the supports object when publishing a manage request.

Here is the sample python code to publish a mange request to indicate to IoT Platform that device supports DME Actions:

.. code:: python

	#Setup logger instance
	logger = logging.getLogger(“DME”)
	logger.setLevel(logging.INFO)

	#Initialize Client for API to carry out REST Calls
	appConfFile="application.conf"
	appOptions = ibmiotf.application.ParseConfigFile(appConfFile)
	apiClient = ibmiotf.api.ApiClient(appOptions , logger)

	#Initialize DME Package Information
	dmeData = {"bundleId": "example-dme-actions-v1",
                   "displayName": { "en_US": "example-dme Actions v1" },
                   "version": "1.0",
		   "actions": {
			"installPlugin": {
              			"actionDisplayName": { "en_US": "Install Plug-in" },
                   		"parameters": [ 
						{ 
						"name": "pluginURI",
                                     		"value": "http://example.dme.com",
                                    		"required": "true" 
						} 
					       ] 
					} 
				} 
		}

	# Create DME Package on the platform using API REST Call
	addResult = apiClient.createDeviceManagementExtensionPkg(dmeData)

	# Initialize ManagedClient
	deviceFile="device.conf"
	options = ibmiotf.device.ParseConfigFile(deviceFile)
	managedClient = ibmiotf.device.ManagedClient(options)

	#Register user define function as DME callback
	managedClient.dmeActionCallback = doDMEAction;

	# Send Manage request with DME actions set to true along with the bundle id to platform
	managedClient.connect()
	managedClient.unmanage()
	managedClient.manage(lifetime=0,supportDeviceMgmtExtActions=True,bundleId='example-dme-actions-v1')

In return, IoT Platform sends back response with rc=200 to device. For additional information about device manage requests,
refer to `Device Management Protocol <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/index.html>`__.

Initiating Custom Device Management Actions
--------------------------------------------------
Custom device management actions are initiated using the same REST API as the default device management actions. The
following information must be provided when initiating a request:

* The action <bundleId>/<actionId>

* A list of devices to initiate the action against, with a maximum of 5000 devices

* A list of parameters as defined in the custom action definition

Here is the sample python code to initiate DM request:

.. code:: python

	mgmtRequest = {
		"action": "example-dme-actions-v1/installPlugin",
                "parameters": [
				{ 
				"name": "pluginURI",
                                "value": "http://example.dme.com",
				}
				],
                "devices": [
				{ 
				"typeId": deviceType, 
				"deviceId": deviceId 
				}
			    ]
			}
        
	initResult = apiClient.initiateDeviceManagementRequest(mgmtRequest)
	reqId = initResult['reqId']
	
Handling Custom Device Management Actions
-------------------------------------------------
When a custom action is initiated against a device, an MQTT message will be published to the device. The message will
contain any parameters that were specified as part of the request. When the device receives this message, it is expected to
either execute the action or respond with an error code indicating that it cannot complete the action at this time.

To indicate that the action was completed successfully, a device should publish a response with rc set to 200.

As the device receives the MQTT message from the IoT Platform, the user registered DME callback function is expected to be
called and executed. The user defined DME callback function exactly receives 3 parameters from the device:

* **The topic** on which message is published by IoT Platform. Using this topic, DME callback is expected to determine the **bundleId** and **action** associated with the bundleId to carry out the required operation as part of the DME callback function. The topic is of the form - **iotdm-1/mgmt/custom/<bundleId>/<actionId>**

* **The user data** which contains the details about the parameters passed to the IoT platform while initiating the custom DM Action.

* **RequestId** for the reference. RequestId can be used to publish failure of action back to platform from the DME callback.

Based on the result of the performed action, the user defined DME callback should return a boolean value - True to indicate
Success / False to indicate Failure. Based on the return value from the DME callback, the device publishes back the response
to IoT platform to indicate whether the Custom Device Management action completed or failed.

Below given is the sample python code for user defined DME callback function:

.. code:: python

	def doDMEAction(topic,data,reqId):
            print("In DME Action Callabck")
            print("Received topic = "+topic)
            print("Received reqId = "+reqId)
            print("Received data = %s" %data)
            return True
        
Clearing of Custom Device Management Action
-------------------------------------------------------
As we finish of the custom device management action flow, we can clear of the requests from the IoT Platform and disconnect
the managed client instance as shown in the below given python code snippet:

.. code:: python

	# Remove the completed requests from the platform
	apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1')
	apiClient.deleteDeviceManagementRequest(reqId)

	# Unmanaged and disconnect the client
	managedClient.unmanage()
	managedClient.disconnect() 

The complete code can be found in the device management sample `<https://github.com/ibm-messaging/iot-python/tree/master/samples/managedDevice>`__.

For complete details on Device Management Extension, refer to `Extending Device Management <https://docs.internetofthings.ibmcloud.com/devices/device_mgmt/custom_actions.html>`__.	
