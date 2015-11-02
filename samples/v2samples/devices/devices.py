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
	print("Registering a device type")
	print("Registered Device = ", apiCli.addDeviceType(deviceType = deviceTypeId, description = "My first device type", deviceInfo = deviceInfo1, metadata = metadata1))
	time.sleep(2)

	deviceId = "200020002001"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("\nRegistering a new device")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId, authToken, deviceInfo, location, metadata2))
	time.sleep(2)
	
	deviceId2 = "200020002000"
	authToken = "password"
	metadata2 = {"customField1": "customValue3", "customField2": "customValue4"}
	deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A", "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
	location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0", "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
	
	print("\nRegistering a new device with just deviceType and deviceId")	
	print("Registered Device = ", apiCli.registerDevice(deviceTypeId, deviceId2))
	time.sleep(2)
	
	print("\nRetrieving an existing device")	
	print("Retrieved Device = ", apiCli.getDevice(deviceTypeId, deviceId))
	time.sleep(2)

	print("\nRetrieving All existing devices")	
	print("Retrieved Devices = ", apiCli.retrieveDevices(deviceTypeId))
	time.sleep(2)

	print("\nRetrieving All existing devices with getDevices() for backward compatibility")	
	print("Retrieved Devices = ", apiCli.getAllDevices({'typeId' : deviceTypeId}))
	time.sleep(2)

	print("\nUpdating an existing device")
	status = { "alert": { "enabled": True }  }
	print("Device Modified = ", apiCli.updateDevice(deviceTypeId, deviceId, metadata2, deviceInfo, status))
	time.sleep(2)
	
	print("\nRetrieving device location")
	print("Device Location = ", apiCli.getDeviceLocation(deviceTypeId, deviceId))
	time.sleep(2)
	
	print("\nUpdating device location")
	deviceLocation = { "longitude": 0, "latitude": 0, "elevation": 0, "accuracy": 0, "measuredDateTime": "2015-10-28T08:45:11.673Z"}
	print("Device Location = ", apiCli.updateDeviceLocation(deviceTypeId, deviceId, deviceLocation))
	time.sleep(2)
	
	print("\nDeleting an existing device")
	deleted = apiCli.deleteDevice(deviceTypeId, deviceId)
	print("Device deleted = ", deleted)
	
#	This has been commented as the ReST URL needs to be fixed	
#	print("\nRetrieving device management information")
#	info = apiCli.getDeviceManagementInformation("iotsample-arduino", "00aabbccde03")
#	print("Device management info retrieved = ", info)
	
	print("\nDeleting an existing device")
	deleted = apiCli.deleteDevice(deviceTypeId, deviceId2)
	print("Device deleted = ", deleted)

	print("\nDeleting an existing device type")
	deleted = apiCli.deleteDeviceType(deviceTypeId)
	print("Device Type deleted = ", deleted)
	
except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
