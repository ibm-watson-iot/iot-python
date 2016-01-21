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

=======
import ibmiotf.application
import sys

try:
	appOptions = {"org": "quickstart", "id": "a:quickstart:myapp02", "auth-key": None, "auth-token": None}
	appCli = ibmiotf.application.Client(appOptions)

except Exception as e:
	print("Caught exception", e)
	sys.exit()

myData = { 'hello' : 'world', 'x' : 23}
	
try:
	success = appCli.publishEventOverHTTP("iotsample-arduino", "00aabbccde02", "greeting", myData)
	print ("Post Operation HTTP response = ", success)

except Exception as e:
	print(e)
	sys.exit()
	
