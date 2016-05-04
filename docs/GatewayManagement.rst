==========================================
Python  Client Library  - Managed Gateway
==========================================

Introduction
-------------

Gateway plays an important role in the device management of devices connected to it. Many of these devices will be too basic to be managed. For a managed device, the device management agent on the gateway acts as a proxy for the connected device. The protocol used by the gateway to manage the connected devices is arbitrary, and there need not be a device management agent on the connected devices. It is only necessary for the gateway to ensure that devices connected to it perform their responsibilities as managed devices, performing any translation and processing required to achieve this. The management agent in gateway will act as more than a transparent tunnel between the attached device and the Watson IoT Platform.

For example, It is unlikely that a device connected to a gateway will be able to download the firmware itself. In this case, the gateway’s device management agent will intercept the request to download the firmware and perform the download to its own storage. Then, when the device is instructed to perform the upgrade, the gateway’s device management agent will push the firmware to the device and update it.

This section contains information on how gateways (and attached devices) can connect to the Internet of Things Platform Device Management service using Python  and perform device management operations like firmware update, location update, and diagnostics update.

Create DeviceData
------------------------------------------------------------------------
The `device model <https://docs.internetofthings.ibmcloud.com/reference/device_model.html>`__ describes the metadata and management characteristics of a device. The device database in the IBM Watson IoT Platform Connect is the master source of device information. Applications and managed devices are able to send updates to the database such as a location or the progress of a firmware update. Once these updates are received by the IBM Watson IoT Platform Connect, the device database is updated, making the information available to applications.

The device model in the IBMWIoTP client library is represented as DeviceInfo.

The following code snippet shows how to create the mandatory object DeviceInfo along with the DeviceManagement:

.. code:: Python

  simpleGatewayInfo = ibmiotf.gateway.DeviceInfo()
  simpleGatewayInfo.description = gatewayName
  simpleGatewayInfo.deviceClass = platform.machine()
  simpleGatewayInfo.manufacturer = platform.system()
  simpleGatewayInfo.fwVersion = platform.version()
  simpleGatewayInfo.hwVersion = None
  simpleGatewayInfo.model = None
  simpleGatewayInfo.serialNumber = None



Each gateway and attached devices must have its own DeviceData to represent itself in the Platform. In the case of gateway, the DeviceData will be passed to the library as part of constructing the ManagedGateway instance, and in the case of attached device, the DeviceData will be passed as part of the managedDevice().

----

Construct ManagedGateway
-------------------------------------------------------------------------------
ManagedGateway - A gateway class that connects the gateway as managed gateway to IBM Watson Internet of Things Platform and enables the gateway to perform one or more Device Management operations for itself and attached devices. Also the ManagedGateway instance can be used to do normal gateway operations like publishing gateway events, attached device events and listening for commands from application.


Constructs a ManagedGateway instance by accepting the DeviceData and the following properties,

* Organization-ID - Your organization ID.
* Gateway-Type - The type of your gateway device.
* Gateway-ID - The ID of your gateway device.
* Authentication-Method - Method of authentication (The only value currently supported is "token").
* Authentication-Token - API key token

All these properties are required to interact with the IBM Watson Internet of Things Platform.

The following code shows how to create a ManagedGateway instance:

.. code:: Python

  options = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}

  client = ibmiotf.gateway.ManagedGateway(options, logHandlers=None, deviceInfo=simpleGatewayInfo)
  client.commandCallback = commandProcessor
  client.connect()


----

Manage request - gateway
-------------------------------------------------------

The gateway can invoke managedGateway() method to participate in device management activities. The manage request will initiate a connect request internally if the device is not connected to the IBM Watson Internet of Things Platform already.

Manage method will take following parameters,
* *lifetime* The length of time in seconds within which the gateway must send another **Manage** request in order to avoid being reverted to an unmanaged device and marked as dormant. If set to 0, the managed gateway will not become dormant. When set, the minimum supported setting is 3600 (1 hour).
* *supportFirmwareActions* Tells whether the gateway supports firmware actions or not. The gateway must add a firmware handler to handle the firmware requests.
* *supportDeviceActions* Tells whether the gateway supports Device actions or not. The gateway must add a Device action handler to handle the reboot and factory reset requests.

And an optional wait() method call to make the manage request process synchronously.


.. code:: Python

    client.manage(3600, supportDeviceActions=True, supportFirmwareActions=True).wait()


Unmanage request - gateway
-----------------------------------------------------

A gateway can invoke unmanagedGateway() method when it no longer needs to be managed. The IBM Watson Internet of Things Platform will no longer send new device management requests for this gateway and all device management requests from the gateway (only for the gateway and not for the attached devices) will be rejected other than a **Manage** request.

.. code:: Python

	client.unmanage();


----

Location update - gateway
-----------------------------------------------------

Gateways that can determine their location can choose to notify the IBM Watson Internet of Things Platform about location changes. The gateway can invoke one of the updateLocation() method to update the location of the device.

.. code:: Python

    client.setLocation(longitude=85, latitude=85, accuracy=100)


----

Append/Clear ErrorCodes - gateway
-----------------------------------------------

Gateways can choose to notify the Internet of Things Platform Connect about changes in their error status. In order to send the ErrorCodes the device needs to call setErrorCode() method in client object ,then wait for it to be completed (sync) as follows:

.. code:: python

	client.setErrorCode(1).wait()

Also, the ErrorCodes can be cleared from Internet of Things Platform Connect by calling the clearErrorCodes() method as follows:

.. code:: python

  client.clearErrorCodes()
