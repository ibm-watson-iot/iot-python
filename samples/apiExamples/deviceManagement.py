# *****************************************************************************
# Copyright (c) 2015 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   Amit M Mangalvedkar - Initial Contribution
# *****************************************************************************

import json
import sys
import time
from pip._vendor.distlib.compat import raw_input

try:
	import ibmiotf
	import ibmiotf.application
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.application


# Initialize the application client.
try:
	apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	apiCli = ibmiotf.api.ApiClient(apiOptions)
	deviceInfo1 = {"serialNumber": "100087", "manufacturer": "ACME Co.", "model": "7865", "deviceClass": "A", "description": "My shiny device", "fwVersion": "1.0.0", "hwVersion": "1.0", "descriptiveLocation": "Office 5, D Block"}
	metadata1 = {"customField1": "customValue1", "customField2": "customValue2"}
	deviceTypeId = "iotsample-arduino"

	deviceId = "200020002000"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("Registering a new device")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId, authToken, deviceInfo, location, metadata2))
	time.sleep(1)

	requestId = raw_input("\nEnter the request Id whose status needs to be found out for a device of a device type= ")
	print("Retrieving the single device status")
	print("Status retrieved = ", apiCli.getDeviceManagementRequestStatusByDevice(requestId, deviceTypeId, deviceId))
	time.sleep(1)

	requestId = raw_input("\nEnter the request Id whose status needs to be found out = ")
	print("Retrieving the status")
	print("Status retrieved = ", apiCli.getDeviceManagementRequestStatus(requestId))
	time.sleep(1)

	requestId = raw_input("\nEnter the request Id to be deleted = ")
	print("Retrieving the request id")
	print("Request id retrieved = ", apiCli.getDeviceManagementRequest(requestId))
	time.sleep(1)

	requestId = raw_input("\nEnter the request Id whose status needs to be found out = ")
	print("Retrieving the status")
	print("Status retrieved = ", apiCli.getAllDeviceManagementRequestStatus(requestId))
	time.sleep(1)
	
	requestId = raw_input("\nEnter the request Id to be deleted = ")
	print("Removing the request id")
	print("Request id removed = ", apiCli.deleteDeviceManagementRequest(requestId))
	time.sleep(1)
	
	print("\nInitiating device management requests")
	mgmtRequest = {"action": "device/reboot", "parameters": [{"name": "string","value": "string" }], "devices": [{ "typeId": deviceTypeId, "deviceId": deviceId }]}
	print("Device Management Requests = ", apiCli.initiateDeviceManagementRequest(mgmtRequest))
	time.sleep(1)

	print("\nRetrieving device management requests")
	print("Device Management Requests = ", apiCli.getAllDeviceManagementRequests())
	time.sleep(1)
	
	print("\nDeleting an existing device")
	deleted = apiCli.deleteDevice(deviceTypeId, deviceId)
	print("Device deleted = ", deleted)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
