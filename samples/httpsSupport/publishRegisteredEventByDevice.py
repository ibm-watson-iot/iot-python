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

import ibmiotf.device
import sys

try:
	deviceOptions = {"org": "uguhsp", "type": "iotsample-arduino", "id": "00aabbccde03", "auth-method": "token", "auth-token": "MASKED PASSWORD"}

	deviceCli = ibmiotf.device.Client(deviceOptions)

except Exception as e:
	print("Caught exception")
	sys.exit()

myData = { 'hello' : 'world', 'x' : 23}
try:
	success = deviceCli.publishEventOverHTTP("greeting", myData)
	print ("Post Operation HTTP response = ", success)

except Exception as e:
	print(e)
	sys.exit()
	
