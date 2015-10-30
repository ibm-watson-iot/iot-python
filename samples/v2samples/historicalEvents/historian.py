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
from datetime import datetime
import math

# Initialize the application client.
try:
	apiOptions = {"org": "uguhsp", "id": "myapp", "auth-method": "apikey", "auth-key": "SOME KEY", "auth-token": "SOME TOKEN"}
	apiCli = ibmiotf.api.ApiClient(apiOptions)

	print("\nRetrieving historical events")
	deviceTypeId = "iotsample-arduino"
	deviceId = "00aabbccde03"

	startTime = math.floor(time.mktime((2013, 10, 10, 17, 3, 38, 0, 0, 0)) * 1000)
	endTime =  math.floor(time.mktime((2015, 10, 29, 17, 3, 38, 0, 0, 0)) * 1000)

	duration = {'start' : startTime, 'end' : endTime }
	
	print("\nBoth device type and device passed")				
	print("Historical Events = ", apiCli.getHistoricalEvents(deviceType = 'iotsample-arduino', deviceId = '00aabbccde03', options = duration))
	time.sleep(2)
	
	print("\nOnly device type passed")	
	print("Historical Events = ", apiCli.getHistoricalEvents(deviceType = 'iotsample-arduino', options = duration))
	time.sleep(2)


	print("\nNothing passed")	
	print("Historical Events = ", apiCli.getHistoricalEvents(options = duration))
	time.sleep(2)
	

except ibmiotf.IoTFCReSTException as e:
	print(e.httpCode)
	print(str(e))
	sys.exit()
