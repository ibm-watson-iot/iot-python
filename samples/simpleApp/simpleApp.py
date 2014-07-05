# *****************************************************************************
# Copyright (c) 2014 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   IBM - Initial Contribution
# *****************************************************************************

import getopt
import signal
import threading
import time
import sys
import json

try:
	import ibmiotc.application
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotc"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotc.application


def myEventCallback(type, id, event, format, data):
	print "%s event '%s' received from device [%s:%s]: %s" % (format, event, type, id, json.dumps(data))

def myStatusCallback(type, id, status):
	print "Status of device [%s:%s] changed to %s" % (type, id, json.dumps(status))
	
def interruptHandler(signal, frame):
	client.disconnect()
	sys.exit(0)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:i:k:t:c:T:I:E:", ["help", "org=", "id=", "key=", "token=", "config=", "devicetype", "deviceid", "event"])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	verbose = False
	organization = "quickstart"
	appId = "mySampleApp"
	authMethod = None
	authKey = None
	authToken = None
	configFilePath = None
	deviceType = "+"
	deviceId = "+"
	event = "+"
	
	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-o", "--organizatoin"):
			organization = a
		elif o in ("-i", "--id"):
			appId = a
		elif o in ("-k", "--key"):
			authMethod = "apikey"
			authKey = a
		elif o in ("-t", "--token"):
			authToken = a
		elif o in ("-c", "--cfg"):
			configFilePath = a
		elif o in ("-T", "--devicetype"):
			deviceType = a
		elif o in ("-I", "--deviceid"):
			deviceId = a
		elif o in ("-E", "--event"):
			event = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option" + o

	client = None
	if configFilePath is not None:
		options = ibmiotc.application.ParseConfigFile(configFilePath)
	else:
		options = {"org": organization, "id": appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
	
	try:
		client = ibmiotc.application.Client(options)
	except ibmiotc.ConfigurationException as e:
		print str(e)
		sys.exit()
	except ibmiotc.UnsupportedAuthenticationMethod as e:
		print str(e)
		sys.exit()
	except ibmiotc.ConnectionException as e:
		print str(e)
		sys.exit()

	
	client.eventCallback = myEventCallback
	client.statusCallback = myStatusCallback
	
	client.subscribeToDeviceEvents(type=deviceType, id=deviceId, event=event)
	client.subscribeToDeviceStatus(type=deviceType, id=deviceId)

	while True:
		time.sleep(1)
		
