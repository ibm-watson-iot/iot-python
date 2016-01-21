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

	
	deviceTypeId = "myDeviceType5"
	print("Registering a device type")
	print("Registered Device = ", apiCli.addDeviceType(deviceType = deviceTypeId, description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	time.sleep(2)

	deviceId = "200020002001"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("\nRegistering a new device 1")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId, authToken, deviceInfo, location, metadata2))
	time.sleep(2)
	
	deviceId2 = "200020002000"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("\nRegistering a new device 2")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId2, authToken, deviceInfo, location, metadata2))
	time.sleep(2)
	
	deviceId3 = "200020002002"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("\nRegistering a new device 3")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId3, authToken, deviceInfo, location, metadata2))
	time.sleep(2)

	print("\nBulk Registering new devices 4")	
	listOfDevices = [{'typeId' : deviceTypeId, 'deviceId' : '200020002004'}, {'typeId' : deviceTypeId, 'deviceId' : '200020002005'}]
	print("Registered Device = ", apiCli.addMultipleDevices(listOfDevices))
	time.sleep(2)

	print("\nRetrieving existing devices - 200020002004 and 200020002005")	
	print("Retrieved Devices = ", apiCli.getAllDevices({'typeId' : deviceTypeId}))
	time.sleep(2)
	
	print("\nDeleting bulk devices")
	listOfDevices = [ {'typeId' : deviceTypeId, 'deviceId' : '200020002000'}, {'typeId' : deviceTypeId, 'deviceId' : '200020002001'} ]
	deleted = apiCli.deleteMultipleDevices(listOfDevices)
	print("Device deleted = ", deleted)

	print("\nRetrieving All existing device")	
	print("Retrieved Devices = ", apiCli.retrieveDevices(deviceTypeId))
	time.sleep(2)

	print("\nDeleting bulk devices")
	listOfDevices = [ {'typeId' : deviceTypeId, 'deviceId' : '200020002004'}, {'typeId' : deviceTypeId, 'deviceId' : '200020002005'} ]
	deleted = apiCli.deleteMultipleDevices(listOfDevices)
	print("Device deleted = ", deleted)

	print("\nRetrieving All existing device")	
	print("Retrieved Devices = ", apiCli.retrieveDevices(deviceTypeId))
	time.sleep(2)

	print("\nDeleting last device")
	deleted = apiCli.deleteDevice(deviceTypeId, deviceId3)
	print("Device deleted = ", deleted)
	
	print("\nDeleting the device type")
	deleted = apiCli.deleteDeviceType(deviceTypeId)
	print("Device Type deleted = ", deleted)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
