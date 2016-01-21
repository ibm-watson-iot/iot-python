# *****************************************************************************
# Copyright (c) 2014, 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David Parker 			- Initial Contribution
#   Amit M Mangalvedkar		- Modified as per ReST v2
# *****************************************************************************

import argparse
import time
import sys
import platform
import json
import signal
import iso8601
import pytz
from datetime import datetime
from uuid import getnode as get_mac


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


def deviceList():
	global client, cliArgs
	deviceList = client.api.getAllDevices()
	if cliArgs.json:
		print(deviceList)
	else:
		today = datetime.now(pytz.timezone('UTC'))
		print ("Today = ", today)
		resultArray = deviceList['results']
		for device in resultArray:
			#print("Device = ",device['uuid'])
			delta = today - iso8601.parse_date(device['registration']['date'])
			print("%-40sRegistered %s days ago by %s" % (device['deviceId'], delta.days, device['registration']['auth']['id']))


def deviceGet(deviceType, deviceId):
	global client, cliArgs
	device = client.api.getDevice(deviceType, deviceId)
	if cliArgs.json:
		print(device)
	else:
		today = datetime.now(pytz.timezone('UTC'))
		delta = today - iso8601.parse_date(device['registration']['date'])
		print("%-40sRegistered %s days ago by %s" % (device['deviceId'], delta.days, device['registration']['auth']['id']))


def deviceAdd(deviceType, deviceId, metadata):
	global client, cliArgs
	device = client.api.registerDevice(deviceType, deviceId, metadata)
	if cliArgs.json:
		print(device)
	else:
		print("%-40sGenerated Authentication Token = %s" % (device['deviceId'], device['authToken']))

def deviceRemove(deviceType, deviceId):
	global client
	try:
		client.api.deleteDevice(deviceType, deviceId)
	except Exception as e:
		print(str(e))
	
def historian(args):
	global client, cliArgs
	if len(args) == 2:
		result = client.api.getHistoricalEvents(deviceType=args[0], deviceId=args[1])
	elif len(args) == 1:
		result = client.api.getHistoricalEvents(deviceType=args[0])
	else:
		result = client.api.getHistoricalEvents()
	if cliArgs.json:
		print(result)
	else:
		i = 0
		for event in result['events']:
			i = i + 1
			if 'device_id' not in event:
				event['device_id'] = args[1]
			deviceId = event['device_id']
			print("%-4s%-20s%-20s%s" % (i, deviceId, event['evt_type'], event['evt']))
		

	
def usage():
	print("""
usage: cli -h
       cli -c CONFIG [-j] COMMAND
       cli -c CONFIG -i [-j]

Simple CLI for IBM IOT Foundation API

options:
  -h, --help                   show this help message and exit
  -c CONFIG, --config CONFIG   path to application config file  
  -i, --interactive            enable interactive mode
  -j, --json                   enable raw JSON response output""")
	cmdUsage()
	
	
def cmdUsage():
	print("""
commands:
  device list
  device add TYPE ID
  device get TYPE ID
  device remove TYPE ID
  device update TYPE ID METADATA
  historian [TYPE [ID]]""")

def processCommandInput(words):
	if len(words) < 1:
		cmdUsage()
		return False
	
	elif words[0] == "historian":
		historian(words[1:])
		return True
		
	elif words[0] == "device":
		if len(words) < 2:
			cmdUsage()
			return False
			
		elif words[1] == "list":
			deviceList()
			return True
			
		elif words[1] == "get":
			if len(words) < 4:
				cmdUsage()
				return False
			deviceGet(words[2], words[3])
			return True
			
		elif words[1] == "add":
			if len(words) < 4:
				cmdUsage()
				return False
			metadata = None
			if len(words) == 5:
				metadata = json.loads(words[4])
			deviceAdd(words[2], words[3], metadata)
			return True
			
		elif words[1] == "remove":
			if len(words) < 4:
				cmdUsage()
				return False
			deviceRemove(words[2], words[3])
			return True
			
		elif words[1] == "update":
			if len(words) < 4:
				cmdUsage()
				return False
			metadata = None
			if len(words) == 5:
				metadata = json.loads(words[4])
			updateDevice(words[2], words[3], metadata)
			return True
	
	cmdUsage()
	return False

if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	parser = argparse.ArgumentParser(description='Simple CLI for IBM IOT Foundation', add_help=False)
	parser.add_argument('-h', '--help', action='store_true')
	parser.add_argument('-c', '--config')
	parser.add_argument('-i', '--interactive', action='store_true')
	parser.add_argument('-j', '--json', action='store_true')
	parser.add_argument('commands', nargs='*', type=str)

	cliArgs = parser.parse_args()
	
	if cliArgs.help:
		usage()
		sys.exit(0)
	
	client = None
	try:
		if cliArgs.config is not None:
			options = ibmiotf.application.ParseConfigFile(cliArgs.config)
		else:
			sys.exit(1)
		client = ibmiotf.application.Client(options)
	except ibmiotf.ConfigurationException as e:
		print(str(e))
		sys.exit()
	except ibmiotf.UnsupportedAuthenticationMethod as e:
		print(str(e))
		sys.exit()
	except ibmiotf.ConnectionException as e:
		print(str(e))
		sys.exit()
	
	if not cliArgs.interactive:
		rc = processCommandInput(cliArgs.commands)
		if rc:
			sys.exit(0)
		else:
			sys.exit(1)
	else:
		print("(Press Ctrl+C to disconnect)")
		
		while True:
			try:
				command = input("%s@%s >" % (options['auth-key'], options['org']))
				words = command.split()
				processCommandInput(words)

			except KeyboardInterrupt:
				client.disconnect()
				sys.exit(0)

