# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   Amit M Mangalvedkar - Initial Contribution
# *****************************************************************************

import time
import sys
import pprint
import uuid


try:
	import ibmiotf.application
	import ibmiotf.gateway
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf.application" & "import ibmiotf.device"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.application
	import ibmiotf.gateway


def myAppEventCallback(event):
	print("Received live data from %s (%s) sent at %s: hello=%s x=%s" % (event.deviceId, event.deviceType, event.timestamp.strftime("%H:%M:%S"), event.data['hello'], event.data['x']))

def myOnPublishCallback():
	print("Confirmed event %s received by IBM Watson IoT Platform\n" % x)

organization = "MASKED"
gatewayType = "MASKED"
gatewayId = "MASKED"

authMethod = "token"
authToken = "MASKED"


# Initialize the device client.
try:
	gatewayOptions = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}
	gatewayCli = ibmiotf.gateway.Client(gatewayOptions)
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()


gatewayCli.connect()
for x in range (0,5):
	sensorValues = {"timestamp": "2016-01-20", "moisture" : 0.90, "pressure" : 1, "altitude": 23, "temperature": 273}
	timestamp = sensorValues["timestamp"]
	moisture = sensorValues["moisture"]
	pressure = sensorValues["pressure"]
	altitude = sensorValues["altitude"]
	temperature = sensorValues["temperature"]
	myData = {'timestamp': timestamp, 'moisture': moisture, 'pressure': pressure, 'altitude': altitude, 'temperature': temperature}

	gatewaySuccess = gatewayCli.publishGatewayEvent("greeting", "json", myData, qos=1, on_publish=myOnPublishCallback )
	deviceSuccess = gatewayCli.publishDeviceEvent("DEVICE TYPE OF AUTO REGISTERED DEVICE", "DEVICE ID OF AUTO REGSITERED DEVICE", "greeting", "json", myData, qos=1, on_publish=myOnPublishCallback )
								
	if not gatewaySuccess:
		print("Gateway not connected to IBM Watson IoT Platform while publishing from Gateway")
		
	if not deviceSuccess:
		print("Gateway not connected to IBM Watson IoT Platform while publishing from Gateway on behalf of a device")
		
	time.sleep(1)
		

# Disconnect the device and application from the cloud
gatewayCli.disconnect()

