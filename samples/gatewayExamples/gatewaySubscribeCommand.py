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

import signal
import sys
from time import sleep

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


def interruptHandler(signal, frame):
	gatewayCli.disconnect()
	sys.exit(0)


def myGatewayCommandCallback(command):
	print("Id = %s (of type = %s) received the gateway command %s at %s" % (command.id, command.type, command.data, command.timestamp))

def myDeviceCommandCallback(command):
	print("Id = %s (of type = %s) received the device command %s at %s" % (command.id, command.type, command.data, command.timestamp))

def myGatewayNotificationCallback(command):
	print("Id = %s (of type = %s) received the notification message %s at %s" % (command.id, command.type, command.data, command.timestamp))
		
signal.signal(signal.SIGINT, interruptHandler)
organization = "MASKED"
gatewayType = "MASKED"
gatewayId = "MASKED"

authMethod = "token"
authToken = "MASKED"


print("Waiting for commands...")
# Initialize the device client.
try:
	gatewayOptions = {"org": organization, "type": gatewayType, "id": gatewayId, "auth-method": authMethod, "auth-token": authToken}
	gatewayCli = ibmiotf.gateway.Client(gatewayOptions)
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()



gatewayCli.connect()
print("After connect.....")

gatewayCli.subscribeToGatewayCommands(command='greeting', format='json', qos=2)
gatewayCli.commandCallback = myGatewayCommandCallback

#gatewayCli.subscribeToDeviceCommands(deviceType='DEVICE TYPE OF AUTO REGISTERED DEVICE', deviceId='DEVICE ID OF AUTO REGSISTERED DEVICE', command='greeting',format='json',qos=2)
#gatewayCli.deviceCommandCallback = myDeviceCommandCallback

#gatewayCli.subscribeToGatewayNotifications()
#gatewayCli.notificationCallback = myGatewayNotificationCallback



while True:
	sleep(1)
# Disconnect the device and application from the cloud
gatewayCli.disconnect()
