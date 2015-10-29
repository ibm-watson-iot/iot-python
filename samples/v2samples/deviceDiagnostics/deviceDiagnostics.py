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

import ibmiotf
import ibmiotf.application
import json
import sys
import time

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
	time.sleep(2)
	
	print("\nAdding device diagnostic logs")
	logs = { "message": "string", "severity": 0, "data": "string", "timestamp": "2015-10-29T05:43:57.109Z"}
	print("Diagnostic Logs creation = ", apiCli.createDiagnosticLogs(deviceTypeId, deviceId, logs))
	time.sleep(2)

	print("\nRetrieving device diagnostics")
	print("Diagnostic Logs = ", apiCli.getDiagnosticLogs(deviceTypeId, deviceId))
	time.sleep(2)
		
	print("\nDeleting device diagnostics")
	print("Diagnostic Logs delete = ", apiCli.deleteDiagnosticLogs(deviceTypeId, deviceId))
	time.sleep(2)
		
	print("\nDeleting an existing device")
	deleted = apiCli.removeDevice(deviceTypeId, deviceId)
	print("Device deleted = ", deleted)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
