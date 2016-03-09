# *****************************************************************************
# Copyright (c) 2015, 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David J Parker - Initial Contribution
# *****************************************************************************

import argparse
import json
import sys
import os
import logging

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


def exportTypes(destination):
	print("Exporting Device Types ...")
	_exportPageOfTypes(None, destination)

def _exportPageOfTypes(bookmark, destination):
	global client, cliArgs
	
	# Only export 10 devices types at a time (to better demonstrate paging, there is no real need for such a low limit)
	limit = 10
	
	typeList = client.api.getDeviceTypes(parameters = {"_limit": limit, "_bookmark": bookmark})
	resultArray = typeList['results']
	with open(destination, "a") as out_file:
		for deviceType in resultArray:
			if "metadata" not in deviceType:
				deviceType["metadata"] = {}
			if "description" not in deviceType:
				deviceType["description"] = None
			if "classId" not in deviceType:
				deviceType["classId"] = "Device"
			
			export = {
				"id": deviceType["id"], 
				"classId": deviceType["classId"], 
				"description": deviceType["description"], 
				"deviceInfo": deviceType["deviceInfo"], 
				"metadata": deviceType["metadata"]
			}
			out_file.write(json.dumps(export) + "\n")
		
	# Next page
	if "bookmark" in typeList and len(resultArray) > 0:
		bookmark = typeList["bookmark"]
		_exportPageOfTypes(bookmark, destination)


def exportDevices(destination):
	print("Exporting Devices ...")
	_exportPageOfDevices(None, destination)

def _exportPageOfDevices(bookmark, destination):
	global client, cliArgs
	
	# Only export 10 devices at a time (to better demonstrate paging, there is no real need for such a low limit)
	limit = 10
	
	deviceList = client.api.getDevices(parameters = {"_limit": limit, "_bookmark": bookmark, "_sort": "typeId,deviceId"})
	resultArray = deviceList['results']
	with open(destination, "a") as out_file:
		for device in resultArray:
			if "metadata" not in device:
				device["metadata"] = {}
			
			export = {
				"typeId": device["typeId"], 
				"deviceId": device["deviceId"], 
				"deviceInfo": device["deviceInfo"], 
				"metadata": device["metadata"]
			}
			out_file.write(json.dumps(export) + "\n")
		
	# Next page
	if "bookmark" in deviceList:
		bookmark = deviceList["bookmark"]
		_exportPageOfDevices(bookmark, destination)


def importTypes(source):
	# There is no bulk type registration in the API (yet)
	with open(source, "r") as in_file:
		for line in in_file:
			data = json.loads(line)
			try:
				result = client.api.addDeviceType(typeId=data["id"], description = data["description"], deviceInfo = data["deviceInfo"], metadata = data["metadata"], classId=data["classId"])
			except ibmiotf.APIException as e:
				print(e)
				print(e.response)
				sys.exit(1)
	
def importDevices(source):
	deviceArray = []
	with open(source, "r") as in_file:
		for line in in_file:
			data = json.loads(line)
			deviceArray.append(data)
	print(deviceArray)
	try:
		result = client.api.registerDevices(deviceArray)
	except ibmiotf.APIException as e:
		print(e)
		print(e.response)
		sys.exit(1)
	
if __name__ == "__main__":

	# Initialize the properties we need
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', required=True)
	parser.add_argument('-m', '--mode', required=True)
	parser.add_argument('-d', '--directory', required=True)

	args, unknown = parser.parse_known_args()

	client = None
	options = ibmiotf.application.ParseConfigFile(args.config)
	try:
		client = ibmiotf.application.Client(options)
		client.logger.setLevel(logging.DEBUG)
		# Note that we do not need to call connect to make API calls
		
		devicesFilePath = args.directory + "/devices.txt"
		typesFilePath = args.directory + "/types.txt"
		
		if args.mode == "import":
			importTypes(typesFilePath)
			importDevices(devicesFilePath)
			
		elif args.mode == "export":
			if os.path.isfile(typesFilePath):
				os.remove(typesFilePath)
			exportTypes(typesFilePath)
			
			if os.path.isfile(devicesFilePath):
				os.remove(devicesFilePath)
			exportDevices(devicesFilePath)
			
	except ibmiotf.ConfigurationException as e:
		print(str(e))
		sys.exit()
	except ibmiotf.UnsupportedAuthenticationMethod as e:
		print(str(e))
		sys.exit()
	except ibmiotf.ConnectionException as e:
		print(str(e))
		sys.exit()
	except ibmiotf.APIException as e:
		print(e.httpCode)
		print(str(e))
		sys.exit()
