========================================
Python Client Library - Gateway Devices
========================================

Constructor
-------------------------------------------------------------------------------

The constructor builds the Gateway client instance, and accepts a Properties object containing the following definitions:

* org - Your organization ID.
* type - The type of your Gateway device.
* id - The ID of your Gateway.
* auth-method - Method of authentication (The only value currently supported is "token").
* auth-token - API key token.

The Properties object creates definitions which are used to interact with the Watson Internet of Things Platform module.

The following code snippet shows how to construct the GatewayClient instance,

.. code:: python

  organization = "MASKED"
  gatewayType = "MASKED"
  gatewayId = "MASKED"

  authMethod = "token"
  authToken = "MASKED"
  gatewayOptions = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}
	gatewayCli = ibmiotf.gateway.Client(gatewayOptions)

Connecting to the Watson Internet of Things Platform
----------------------------------------------------

Connect to the Watson Internet of Things Platform by calling the *connect* function.

.. code:: python

  gatewayOptions = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}
  gatewayCli = ibmiotf.gateway.Client(gatewayOptions)
  gatewayCli.connect()


After the successful connection to the IBM Watson IoT Platform, the Gateway client can perform the following operations,

* Publish events for itself and on behalf of devices connected behind the Gateway.
* Subscribe to commands for itself and on behalf of devices behind the Gateway.



Register devices using the Watson IoT Platform API
-------------------------------------------------------------------------
There are different ways to register the devices behind the Gateway to IBM Watson IoT Platform,

* **Auto registration**: The device gets added automatically in IBM Watson IoT Platform when Gateway publishes any event/subscribes to any commands for the devices connected to it.

Publishing events
-------------------------------------------------------------------------------
Events are the mechanism by which Gateways/devices publish data to the Watson IoT Platform. The Gateway/device controls the content of the event and assigns a name for each event it sends.

**The Gateway can publish events from itself and on behalf of any device connected via the Gateway**.

When an event is received by the IBM Watson IoT Platform the credentials of the connection on which the event was received are used to determine from which Gateway the event was sent. With this architecture it is impossible for a Gateway to impersonate another device.

Events can be published at any of the three `quality of service levels <../messaging/mqtt.html#/>`__ defined by the MQTT protocol.  By default events will be published as qos level 0.

Publish Gateway event
~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

  def myOnPublishCallback():
	 print("Confirmed event %s received by IBM Watson IoT Platform\n" % x)

  .........
  .........
  .........

  sensorValues = {"timestamp": "2016-01-20", "moisture" : 0.90, "pressure" : 1, "altitude": 23, "temperature": 273}
	timestamp = sensorValues["timestamp"]
	moisture = sensorValues["moisture"]
	pressure = sensorValues["pressure"]
	altitude = sensorValues["altitude"]
	temperature = sensorValues["temperature"]
	myData = "{'g' : { 'timestamp': timestamp, 'moisture': moisture, 'pressure': pressure, 'altitude': altitude, 'temperature': temperature}}"

	gatewayCli.setMessageEncoderModule('json', jsonCodec)

	gatewaySuccess = gatewayCli.publishGatewayEvent("greeting", "json", myData, qos=1, on_publish=myOnPublishCallback )


Publishing events from devices
-------------------------------------------------------------------------------

The Gateway can publish events on behalf of any device connected via the Gateway by passing the appropriate typeId and deviceId based on the origin of the event:

.. code:: python

  deviceSuccess = gatewayCli.publishDeviceEvent("DEVICE TYPE OF AUTO REGISTERED DEVICE", "DEVICE ID OF AUTO REGSITERED DEVICE", "greeting", "json", myData, qos=1, on_publish=myOnPublishCallback )


One can use the overloaded publishDeviceEvent() method to publish the device event in the desired quality of service. Refer to `MQTT Connectivity for Gateways <https://docs.internetofthings.ibmcloud.com/gateways/mqtt.html>`__ documentation to know more about the topic structure used.

----


Handling commands
-------------------------------------------------------------------------------
The Gateway can subscribe to commands directed at the gateway itself and to any device connected via the gateway. When the Gateway client connects, it automatically subscribes to any commands for this Gateway. But to subscribe to any commands for the devices connected via the Gateway, use one of the overloaded subscribeToDeviceCommands() method, for example,

.. code:: python

  gatewayCli.subscribeToGatewayCommands(command='greeting', format='json', qos=2)

  gatewayCli.subscribeToDeviceCommands(deviceType='DEVICE TYPE OF AUTO REGISTERED DEVICE', deviceId='DEVICE ID OF AUTO REGSISTERED DEVICE', command='greeting',format='json',qos=2)


To process specific commands you need to register a command callback method. The messages are returned as an instance of the Command class which has the following properties:

* type - The device type for which the command is received.
* id - The device id for which the command is received, Could be the Gateway or any device connected via the Gateway.
* data - The command payload.
* format - The format of the command payload, currently only JSON format is supported in the python Client Library.
* command - The name of the command.
* timestamp - Date time of the command.


A sample implementation of the Command callback is shown below,

.. code:: python


  def myGatewayCommandCallback(command):
    print("Id = %s (of type = %s) received the gateway command %s at %s" % (command.id, command.type, command.data, command.timestamp))

  def myDeviceCommandCallback(command):
    print("Id = %s (of type = %s) received the device command %s at %s" % (command.id, command.type, command.data, command.timestamp))



Once the Command callback is added to the GatewayClient, the processCommand() method is invoked whenever any command is published on the subscribed criteria, The following snippet shows how to add the command call back into GatewayClient instance,

.. code:: python

  gatewayCli.subscribeToGatewayCommands(command='greeting', format='json', qos=2)
  gatewayCli.commandCallback = myGatewayCommandCallback


  gatewayCli.subscribeToDeviceCommands(deviceType='DEVICE TYPE OF AUTO REGISTERED DEVICE', deviceId='DEVICE ID OF AUTO REGSISTERED DEVICE', command='greeting',format='json',qos=2)
  gatewayCli.deviceCommandCallback = myDeviceCommandCallback



Handling Errors
-------------------------------------------------------------------------------
When errors occur during the validation of the publish or subscribe topic, or during automatic registration, a notification will be sent to the gateway device.
For consuming those notification an callback should be registered, this callback method will be called whenever the notification is received.The messages are returned as an instance of the Command class which has the following properties:

* type - The device type for which the command is received.
* id - The device id for which the command is received, Could be the Gateway or any device connected via the Gateway.
* data - The command payload.
* format - The format of the command payload, currently only JSON format is supported in the python Client Library.
* command - The name of the command.
* timestamp - Date time of the command.

data object contains following properties describing the error occurred,

*    Request: Request type Either publish or subscribe
*    Time: Timestamp in ISO 8601 Format
*    Topic: The request topic from the gateway
*    Type: The device type from the topic
*    Id: The device id from the topic
*    Client: The client id of the request
*    RC: The return code
*    Message: The error message

A sample implementation of the error callback is shown below,

.. code:: python

  def myGatewayNotificationCallback(command):
    print("Id = %s (of type = %s) received the notification message %s at %s" % (command.id, command.type, command.data, command.timestamp))


Once the Command callback is added to the GatewayClient, the processError() method is invoked whenever any error notification comes , The following snippet shows how to add the error call back into GatewayClient instance,

.. code:: python

  gatewayCli.subscribeToGatewayNotifications()
  gatewayCli.notificationCallback = myGatewayNotificationCallback

Refer to the `documentation <https://docs.internetofthings.ibmcloud.com/gateways/mqtt.html#/gateway-notifications#gateway-notifications>`__ for more information about the error notification.
