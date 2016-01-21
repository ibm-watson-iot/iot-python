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

	print("Registering a device type")
	print("Registered Device = ", apiCli.addDeviceType(deviceType = "myDeviceType5", description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	print("Registered Another Device = ", apiCli.addDeviceType(deviceType = "myDeviceType6", description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	print("Registered Yet Another Device = ", apiCli.addDeviceType(deviceType = "myDeviceType7", description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	
	time.sleep(2)

	print("\nRetrieving a device type")	
	print("Retrieved Device = ", apiCli.getDeviceType("myDeviceType5"))
	time.sleep(2)

	print("\nRetrieving 2 device types")	
	parameter = {'_limit' : 2}	
	print("All Retrieved Device = ", apiCli.getAllDeviceTypes(parameter))

	time.sleep(2)

	print("\nRetrieving all device type")
	print("All Retrieved Device = ", apiCli.getAllDeviceTypes())
	time.sleep(2)

	print("\nUpdating a device type")
	description = "mydescription"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "string", "manufacturer": "string", "model": "string", "deviceClass": "string", "fwVersion": "string", "hwVersion": "string","descriptiveLocation": "string"}
	print("Modified Device = ", apiCli.updateDeviceType("myDeviceType5", description, deviceInfo, metadata2))
	time.sleep(2)
	
	print("\nDeleting a device type")	
	deletion = apiCli.deleteDeviceType("myDeviceType5")
	print("Device Type deleted = ", deletion)
	
	deletion = apiCli.deleteDeviceType("myDeviceType6")
	print("\nDevice Type deleted = ", deletion)

	deletion = apiCli.deleteDeviceType("myDeviceType7")
	print("\nDevice Type deleted = ", deletion)


except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
