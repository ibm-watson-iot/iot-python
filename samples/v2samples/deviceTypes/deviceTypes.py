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

	print("Registering a device type")
	print("Registered Device = ", apiCli.registerDeviceType(deviceType = "myDeviceType4", description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	time.sleep(2)

	print("Retrieving a device type")	
	print("Retrieved Device = ", apiCli.getDeviceType("myDeviceType4"))
	time.sleep(2)

#	print("Modifying a device type")
#	description = "mydescription"
#	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
#	deviceInfo = {"serialNumber": "string", "manufacturer": "string", "model": "string", "deviceClass": "string", "fwVersion": "string", "hwVersion": "string","descriptiveLocation": "string"}
#	print("Modified Device = ", apiCli.modifyDeviceType("myDeviceType4", description, deviceInfo, metadata2))
#	time.sleep(2)
	
	print("Deleting a device type")	
	deletion = apiCli.deleteDeviceType("myDeviceType4")
	print("Device deleted = ", deletion)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
