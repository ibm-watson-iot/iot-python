# *****************************************************************************
# Copyright (c) 2015, 2016 IBM Corporation and other Contributors.
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
	deviceTypeId = "myDeviceType4"

	deviceId = "200020002000"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("Registering a new device")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId, authToken, deviceInfo, location, metadata2))
	time.sleep(1)
	
	print("\nAdding device diagnostic logs")
	logs = { "message": "oldMessage", "severity": 0, "data": "Old log", "timestamp": "2015-10-29T05:43:57.109Z"}
	print("Diagnostic Logs creation = ", apiCli.addDiagnosticLog(deviceTypeId, deviceId, logs))
	time.sleep(1)

	print("\nAdding device diagnostic logs")
	logs = { "message": "newMessage", "severity": 1, "data": "New log", "timestamp": "2015-10-29T07:43:57.109Z"}
	print("Diagnostic Logs creation = ", apiCli.addDiagnosticLog(deviceTypeId, deviceId, logs))
	time.sleep(1)

	print("\nRetrieving All device diagnostics")
	print("Diagnostic Logs = ", apiCli.getAllDiagnosticLogs(deviceTypeId, deviceId))
	time.sleep(1)

#	logId1 = raw_input("Enter the log id that you want to retrieve ")
#	print("\nRetrieving single log")
#	print("Diagnostic Logs = ", apiCli.getDiagnosticLog(deviceTypeId, deviceId, logId1))
#	time.sleep(1)

#	logId1 = raw_input("\nEnter the log id that you want to delete ")
#	print("Deleting single log")
#	print("Diagnostic Logs = ", apiCli.deleteDiagnosticLog(deviceTypeId, deviceId, logId1))
#	time.sleep(1)

	print("\nAdding error code")
	errorCode = { "errorCode": 0, "timestamp": "2015-10-29T05:43:57.112Z" }
	print("Error code creation = ", apiCli.addErrorCode(deviceTypeId, deviceId, errorCode))
	time.sleep(1)

	print("\nRetrieving all error code")
	print("Error codes retrieved = ", apiCli.getAllDiagnosticErrorCodes(deviceTypeId, deviceId))
	time.sleep(1)

	print("\nDeleting all error code")
	print("Error codes deleted = ", apiCli.clearAllErrorCodes(deviceTypeId, deviceId))
	time.sleep(1)

	
	print("\nDeleting All device diagnostics")
	print("Diagnostic Logs delete = ", apiCli.clearAllDiagnosticLogs(deviceTypeId, deviceId))
	time.sleep(1)
		
	print("\nDeleting an existing device")
	deleted = apiCli.deleteDevice(deviceTypeId, deviceId)
	print("Device deleted = ", deleted)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
