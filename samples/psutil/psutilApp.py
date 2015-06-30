# *****************************************************************************
# Copyright (c) 2014 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David Parker - Initial Contribution
# *****************************************************************************

import getopt
import signal
import sys

try:
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

	
def interruptHandler(signal, frame):
	client.disconnect()
	sys.exit(0)


def usage():
	print(
		"commandSender: Basic application connected to the IBM Internet of Things Cloud service." + "\n" +
		"\n" +
		"Options: " + "\n" +
		"  -h, --help          Display help information" + "\n" + 
		"  -c, --config        Load application configuration file (ignore -o, -i, -k, -t options)" + "\n" + 
		"  -T, --devicetype    Restrict subscription to events from devices of the specified type" + "\n" + 
		"  -I, --deviceid      Restrict subscription to events from devices of the specified id" + "\n"
	)


connectedDevices = {}

def myStatusCallback(status):
	global connectedDevices
	if status.action == "Disconnect":
		if status.device in connectedDevices:
			del connectedDevices[status.device]
	else:
		connectedDevices[status.device] = {'type': status.deviceType, 'id': status.deviceId}


def printOptions():
	global deviceType, deviceId
	print("Command List:")
	print(" 1. Change target device")
	if deviceType == None or deviceId == None:
		pass
	else:
		print(" 2. Set publish rate of %s:%s" % (deviceType, deviceId))
		print(" 3. Send message to console of %s:%s" % (deviceType, deviceId))
	print("(Ctrl+C to disconnect)")

def setTarget():
	global deviceType, deviceId, connectedDevices
	deviceList = []
	deviceList.append(None)
	n = 0
	
	print("Device Selection:")
	print(" 0. Manually enter type and ID")
	for key, device in connectedDevices.items():
		deviceList.append(device)
		n += 1
		print(" " + str(n) + ". " + device['id'] + ":" + device['type'])
	
	i = int(input("Choose Device >"))
	print("")
	if i == 0:
		setTargetType()
		setTargetId()
		print("")
	else:
		deviceType = deviceList[i]['type']
		deviceId = deviceList[i]['id']

def setTargetType():
	global deviceType
	deviceType = input("Enter Device Type >")

def setTargetId():
	global deviceId
	deviceId = input("Enter Device Id >")

def changePublishRate():
	global client, deviceType, deviceId
	interval = int(input("Enter Interval (seconds) >"))
	print("")
	client.publishCommand(deviceType, deviceId, "setInterval", {'interval': interval})

def sendMessage():
	global client, deviceType, deviceId
	message = input("Enter message to be displayed >")
	print("")
	client.publishCommand(deviceType, deviceId, "print", "json", {'message': message})


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hc:T:I:", ["help", "config=", "devicetype=", "deviceid="])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

	configFilePath = None
	deviceType = None
	deviceId = None
	
	for o, a in opts:
		if o in ("-c", "--cfg"):
			configFilePath = a
		elif o in ("-T", "--devicetype"):
			deviceType = a
		elif o in ("-I", "--deviceid"):
			deviceId = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option" + o

	client = None
	options = ibmiotf.application.ParseConfigFile(configFilePath)
	
	try:
		client = ibmiotf.application.Client(options)
		client.deviceStatusCallback = myStatusCallback
		client.connect()
		client.subscribeToDeviceStatus()
	except Exception as e:
		print(str(e))
		sys.exit()

	
	while True:
		printOptions()
		try:
			option = int(input("%s:%s>" % (deviceType, deviceId)))
			print("")
			if option == 1:
				setTarget()
			elif option == 2:
				changePublishRate()	
			elif option == 3:
				sendMessage()	
		except KeyboardInterrupt:
			client.disconnect()
			sys.exit()



