# *****************************************************************************
# Copyright (c) 2015 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   David Parker
#   Paul Slater
#   Amit M Mangalvedkar
#   Lokesh K Haralakatta
# *****************************************************************************

import ibmiotf
import json
import requests
import iso8601
import base64
import json
from datetime import datetime

import logging
from symbol import parameters


class ApiClient():
	#Organization URL
	organizationUrl = 'https://%s/api/v0002/'

	#Bulk Operations URL
	bulkRetrieve = 'https://%s/api/v0002/bulk/devices'
	bulkAddUrl = 'https://%s/api/v0002/bulk/devices/add'
	bulkRemoveUrl = 'https://%s/api/v0002/bulk/devices/remove'

	#Device Types URL
	deviceTypesUrl = 'https://%s/api/v0002/device/types'
	deviceTypeUrl = 'https://%s/api/v0002/device/types/%s'

	#Device URL
	devicesUrl = 'https://%s/api/v0002/device/types/%s/devices'
	deviceUrl = 'https://%s/api/v0002/device/types/%s/devices/%s'
	deviceUrlLocation = 'https://%s/api/v0002/device/types/%s/devices/%s/location'
	deviceUrlMgmt = 'https://%s/api/v0002/device/types/%s/devices/%s/mgmt'

	#Device Event Cache URLs
	deviceEventListCacheUrl = 'https://%s/api/v0002/device/types/%s/devices/%s/events'
	deviceEventCacheUrl = 'https://%s/api/v0002/device/types/%s/devices/%s/events/%s'

	#Log Events URL
	deviceLogs = 'https://%s/api/v0002/logs/connection'

	#Diagnostics URL
	deviceDiagLogs = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs'
	deviceDiagLogsLogId = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs/%s'
	deviceDiagErrorCodes = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/errorCodes'

	#Usage Management URL
	usageMgmt = 'https://%s/api/v0002/usage'

	#Service Status URL
	serviceStatus = 'https://%s/api/v0002/service-status'

	#Device Management URL
	mgmtRequests = 'https://%s/api/v0002/mgmt/requests'
	mgmtSingleRequest = 'https://%s/api/v0002/mgmt/requests/%s'
	mgmtRequestStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus'
	mgmtRequestSingleDeviceStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus/%s/%s'

	#Device Management Extensions (dme) URL
	dmeRequests = 'https://%s/api/v0002/mgmt/custom/bundle'
	dmeSingleRequest = 'https://%s/api/v0002/mgmt/custom/bundle/%s'

	def __init__(self, options, logger=None):
		self.__options = options

		# Configure logging
		if logger is None:
			logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
			logger.setLevel(logging.INFO)

		self.logger = logger

		if 'auth-key' not in self.__options or self.__options['auth-key'] is None:
			raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-key")
		if 'auth-token' not in self.__options or self.__options['auth-token'] is None:
			raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

		# Get the orgId from the apikey
		self.__options['org'] = self.__options['auth-key'][2:8]

		if "domain" not in self.__options:
			# Default to the domain for the public cloud offering
			self.__options['domain'] = "internetofthings.ibmcloud.com"

		self.host = self.__options['org'] + "." + self.__options['domain']
		self.credentials = (self.__options['auth-key'], self.__options['auth-token'])

		# To support development systems this can be overridden to False
		self.verify = True


	def deleteDevice(self, typeId, deviceId):
		"""
		Delete an existing device.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

		r = requests.delete(deviceUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("Device was successfully removed")
			return True
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)




	#This method returns the organization
	def getOrganizationDetails(self):
		"""
		Get details about an organization
		It does not need any parameter to be passed
		In case of failure it throws APIException
		"""
		if self.__options['org'] is None:
			raise ibmiotf.ConfigurationException("Missing required property: org")
		else:
			url = ApiClient.organizationUrl % (self.host)
		r = requests.get(url, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Organization retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The organization does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDevices(self, parameters = None):
		"""
		Retrieve bulk devices
		It accepts accepts a list of parameters
		In case of failure it throws APIException
		"""
		bulkRetrieve = ApiClient.bulkRetrieve % (self.host )
		r = requests.get(bulkRetrieve, auth = self.credentials, params = parameters, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Bulk retrieval successful")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the API key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The organization or device type does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def registerDevices(self, listOfDevices):
		"""
		Register multiple new devices, each request can contain a maximum of 512KB.
		The response body will contain the generated authentication tokens for all devices.
		You must make sure to record these tokens when processing the response.
		We are not able to retrieve lost authentication tokens
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws APIException
		"""
		bulkAdd = ApiClient.bulkAddUrl % (self.host )
		r = requests.post(bulkAdd, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code

		if status == 201:
			self.logger.debug("Bulk registration successful")
			return r.json()
		elif status == 202:
			raise ibmiotf.APIException(400, "Some devices registered successfully", r.json())
		elif status == 400:
			raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 403:
			raise ibmiotf.APIException(403, "Maximum number of devices exceeded", r.json())
		elif status == 413:
			raise ibmiotf.APIException(413, "Request content exceeds 512KB", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def deleteMultipleDevices(self, listOfDevices):
		"""
		Delete multiple devices, each request can contain a maximum of 512Kb
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws APIException
		"""
		bulkRemove = ApiClient.bulkRemoveUrl % (self.host )
		r = requests.post(bulkRemove, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code
		if status == 202:
			self.logger.debug("Some devices deleted successfully")
			return r.json()
		elif status == 400:
			raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 413:
			raise ibmiotf.APIException(413, "Request content exceeds 512KB", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)



	def getDeviceTypes(self, parameters = None):
		"""
		Retrieves all existing device types.
		It accepts accepts an optional query parameters (Dictionary)
		In case of failure it throws APIException
		"""
		deviceTypeUrl = ApiClient.deviceTypesUrl % (self.host)
		r = requests.get(deviceTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device types successfully retrieved")
			self.logger.debug(json.dumps(r.json()))
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)



	def addDeviceType(self, typeId, description = None, deviceInfo = None, metadata = None, classId = "Device"):
		"""
		Creates a device type.
		It accepts typeId (string), description (string), deviceInfo(dict) and metadata(dict) as parameter
		In case of failure it throws APIException
		"""
		deviceTypesUrl = ApiClient.deviceTypesUrl % (self.host)
		payload = {'id' : typeId, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata,'classId': classId}

		r = requests.post(deviceTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 201:
			self.logger.debug("Device Type Created")
			return r.json()
		elif status == 400:
			raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 409:
			raise ibmiotf.APIException(403, "The device type already exists", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def deleteDeviceType(self, typeId):
		"""
		Deletes a device type.
		It accepts typeId (string) as the parameter
		In case of failure it throws APIException
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)

		r = requests.delete(deviceTypeUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("Device type was successfully deleted")
			return True
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)

	def getDeviceType(self, typeId):
		"""
		Gets device type details.
		It accepts typeId (string) as the parameter
		In case of failure it throws APIException
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)
		r = requests.get(deviceTypeUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device type was successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The device type does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def updateDeviceType(self, typeId, description, deviceInfo, metadata = None):
		"""
		Updates a device type.
		It accepts typeId (string), description (string), deviceInfo (JSON) and metadata(JSON) as the parameters
		In case of failure it throws APIException
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)
		deviceTypeUpdate = {'description' : description, 'deviceInfo' : deviceInfo, 'metadata' : metadata}
		r = requests.put(deviceTypeUrl, auth=self.credentials, data=json.dumps(deviceTypeUpdate), headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device type was successfully modified")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The device type does not exist", None)
		elif status == 409:
			raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)

	"""
	===========================================================================
	Device API methods
	 - register a new device
	 - get a single device
	 - remove device
	 - update device
	===========================================================================
	"""

	def registerDevice(self, typeId, deviceId, authToken = None, deviceInfo = None, location = None, metadata=None):
		"""
		Registers a new device.
		It accepts typeId (string), deviceId (string), authToken (string), location (JSON) and metadata (JSON) as parameters
		In case of failure it throws APIException
		"""
		devicesUrl = ApiClient.devicesUrl % (self.host, typeId)
		payload = {'deviceId' : deviceId, 'authToken' : authToken, 'deviceInfo' : deviceInfo, 'location' : location, 'metadata': metadata}

		r = requests.post(devicesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 201:
			self.logger.debug("Device Instance Created")
			return r.json()
		elif status == 400:
			raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 409:
			raise ibmiotf.APIException(403, "The device already exists", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDevice(self, typeId, deviceId, expand = None):
		"""
		Gets device details.
		It accepts typeId (string), deviceId (string) and expand (JSON) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials, params = expand, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device was successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The device does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def removeDevice(self, typeId, deviceId):
		"""
		Delete an existing device.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

		r = requests.delete(deviceUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("Device was successfully removed")
			return True
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def updateDevice(self, typeId, deviceId, metadata, deviceInfo = None, status = None):
		"""
		Updates a device.
		It accepts typeId (string), deviceId (string), metadata (JSON), deviceInfo (JSON) and status(JSON) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

		payload = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code
		if status == 200:
			self.logger.debug("Device was successfully modified")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The organization, device type or device does not exist", None)
		elif status == 409:
			raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Last Event Cache Methods
	 - get event(s) from cache for device
	===========================================================================
	"""

	def getLastEvent(self, typeId, deviceId, eventId):
		"""
		Retrieves Last Cached Event.
		"""
		events = ApiClient.deviceEventCacheUrl % (self.host, typeId, deviceId, eventId)
		r = requests.get(events, auth=self.credentials, verify=self.verify)

		status = r.status_code
		if status == 200:
			response = r.json()
			if response["format"] == "json":
				# Convert from base64 to byte to string to dictionary
				jsonPayload = json.loads(base64.b64decode(response["payload"]))
				response["data"] = jsonPayload
			return response

		elif status == 404:
			raise ibmiotf.APIException(404, "Event not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getLastEvents(self, typeId, deviceId):
		"""
		Retrieves all last cached events
		"""
		events = ApiClient.deviceEventListCacheUrl % (self.host, typeId, deviceId)
		r = requests.get(events, auth=self.credentials, verify=self.verify)

		status = r.status_code
		if status == 200:
			response = r.json()
			for event in response:
				if event["format"] == "json":
					# Convert from base64 to byte to string to dictionary
					jsonPayload = json.loads(base64.b64decode(event["payload"]))
					event["data"] = jsonPayload
			return response

		elif status == 404:
			raise ibmiotf.APIException(404, "Event not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Extended Device Model Methods
	 - get location for device
	 - update location for device
	 - get device management information
	===========================================================================
	"""

	def getDeviceLocation(self, typeId, deviceId):
		"""
		Retrieve Device Location.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrlLocation % (self.host, typeId, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device Location was successfully obtained")
			return r.json()
		elif status == 404:
			raise ibmiotf.APIException(404, "Device location information not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def updateDeviceLocation(self, typeId, deviceId, deviceLocation):
		"""
		Updates the location information for a device. If no date is supplied, the entry is added with the current date and time.
		It accepts typeId (string), deviceId (string) and deviceLocation (JSON) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrlLocation % (self.host, typeId, deviceId)

		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(deviceLocation), headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device Location was successfully modified")
			return r.json()
		elif status == 404:
			raise ibmiotf.APIException(404, "Device location information not found", None)
		elif status == 409:
			raise ibmiotf.APIException(404, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDeviceManagementInformation(self, typeId, deviceId):
		"""
		Gets device management information for a device.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceUrl = ApiClient.deviceUrlMgmt % (self.host, typeId, deviceId)
		r = requests.get(deviceUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device Management Information was successfully obtained")
			return r.json()
		#This also throws a 403, which has not been documented
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getConnectionLogs(self, parameters):
		"""
		List connection log events for a device to aid in diagnosing connectivity problems.
		The entries record successful connection, unsuccessful connection attempts, intentional disconnection and server-initiated disconnection.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		logs = ApiClient.deviceLogs % (self.host)
		r = requests.get(logs, auth=self.credentials, params = parameters, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Connection Logs were successfully obtained")
			return r.json()
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)

	"""
	===========================================================================
	Device Diagnostics - Logs
	 - get logs
	 - clear logs
	 - add log
	 - get log
	===========================================================================
	"""

	def getAllDiagnosticLogs(self, typeId, deviceId):
		"""
		Retrieves All Device Diagnostic Logs.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("All Diagnostic logs successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)



	def clearAllDiagnosticLogs(self, typeId, deviceId):
		"""
		Deletes All Device Diagnostic Logs.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("All Diagnostic logs successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def addDiagnosticLog(self, typeId, deviceId, logs):
		"""
		Add Device Diagnostic Logs.
		It accepts typeId (string), deviceId (string) and logs (JSON) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(logs), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code
		if status == 201:
			self.logger.debug("Diagnostic entry was successfully added")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDiagnosticLog(self, typeId, deviceId, logId):
		"""
		Retrieves Device Diagnostic Logs.
		It accepts typeId (string), deviceId (string) and logId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, typeId, deviceId, logId)
		r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Diagnostic log successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def clearDiagnosticLog(self, typeId, deviceId, logId):
		"""
		Delete Device Diagnostic Logs.
		It accepts typeId (string), deviceId (string) and logId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, typeId, deviceId, logId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("Diagnostic log successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Device Diagnostics - Error Codes
	 - add error code
	 - get all error codes
	 - clear all error codes
	===========================================================================
	"""

	def addErrorCode(self, typeId, deviceId, errorCode):
		"""
		Adds an error code to the list of error codes for the device. The list may be pruned as the new entry is added.
		It accepts typeId (string), deviceId (string) and errorCode (JSON) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(errorCode), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code
		if status == 201:
			self.logger.debug("Error code was successfully added")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getAllDiagnosticErrorCodes(self, typeId, deviceId):
		"""
		Gets diagnostic error codes for a device.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)

		status = r.status_code
		if status == 200:
			self.logger.debug("Error codes were successfully retrieved")
			return r.json()
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def clearAllErrorCodes(self, typeId, deviceId):
		"""
		Clears the list of error codes for the device. The list is replaced with a single error code of zero.
		It accepts typeId (string) and deviceId (string) as parameters
		In case of failure it throws APIException
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)

		status = r.status_code
		if status == 204:
			self.logger.debug("Error codes successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Service Status API
	- Retrieve service status
	===========================================================================
	"""

	def getServiceStatus(self):
		"""
		Retrieve the organization-specific status of each of the services offered by the IBM Watson IoT Platform.
		In case of failure it throws APIException
		"""
		serviceStatus = ApiClient.serviceStatus % (self.host)
		r = requests.get(serviceStatus, auth=self.credentials, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Service status successfully retrieved")
			return r.json()
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)

	"""
	===========================================================================
	Usage API
	- Active Devices
	- Data Traffic
	- Storage
	===========================================================================
	"""

	def getActiveDevices(self, options):
		"""
		Retrieve the number of active devices over a period of time.
		In case of failure it throws APIException
		"""
		activeDevices = (ApiClient.usageMgmt + '/active-devices') % (self.host)
		r = requests.get(activeDevices, auth=self.credentials, params=options, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Active Devices = ", r.json() )
			return r.json()
		elif status == 400:
			raise ibmiotf.APIException(400, "Bad Request", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDataTraffic(self, options):
		"""
		Retrieve the amount of data used.
		In case of failure it throws APIException
		"""
		dataTraffic = (ApiClient.usageMgmt + '/data-traffic') % (self.host)
		r = requests.get(dataTraffic, auth=self.credentials, params=options, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Data Traffic = ", r.json() )
			return r.json()
		elif status == 400:
			raise ibmiotf.APIException(400, "Bad Request", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Device Management API
	- Get all requests
	- Initiate new request
	- Delete request
	- Get request
	- Get request status
	- Get request status for specific device
	===========================================================================
	"""

	def getAllDeviceManagementRequests(self):
		"""
		Gets a list of device management requests, which can be in progress or recently completed.
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtRequests % (self.host)
		r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Retrieved all device management requests")
			return r.json()
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def initiateDeviceManagementRequest(self, deviceManagementRequest):
		"""
		Initiates a device management request, such as reboot.
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtRequests % (self.host)
		r = requests.post(mgmtRequests, auth=self.credentials, data=json.dumps(deviceManagementRequest), headers = {'content-type': 'application/json'}, verify=self.verify)

		status = r.status_code
		if status == 202:
			self.logger.debug("The request has been accepted for processing")
			return r.json()
		elif status == 403:
			raise ibmiotf.APIException(500, "Devices don't support the requested operation", r.json())
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def deleteDeviceManagementRequest(self, requestId):
		"""
		Clears the status of a device management request.
		You can use this operation to clear the status for a completed request, or for an in-progress request which may never complete due to a problem.
		It accepts requestId (string) as parameters
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
		r = requests.delete(mgmtRequests, auth=self.credentials, verify=self.verify)

		status = r.status_code
		if status == 204:
			self.logger.debug("Request status cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Request Id not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDeviceManagementRequest(self, requestId):
		"""
		Gets details of a device management request.
		It accepts requestId (string) as parameters
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
		r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Retrieving single management request")
			return r.json()
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Request Id not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDeviceManagementRequestStatus(self, requestId):
		"""
		Get a list of device management request device statuses.
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtRequestStatus % (self.host, requestId)
		r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Retrieved all device management request statuses")
			return r.json()
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Request status not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	def getDeviceManagementRequestStatusByDevice(self, requestId, typeId, deviceId):
		"""
		Get an individual device mangaement request device status.
		In case of failure it throws APIException
		"""
		mgmtRequests = ApiClient.mgmtRequestSingleDeviceStatus % (self.host, requestId, typeId, deviceId)
		r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

		status = r.status_code

		if status == 200:
			self.logger.debug("Retrieved device management request status of single device")
			return r.json()
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "Request status not found", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)

	"""
	===========================================================================
	API Support to Gateway
	- addGatewayDeviceType
	- registerDeviceUnderGateway
	- getDevicesConnectedThroughGateway
	===========================================================================
	"""
	def addGatewayDeviceType(self, gatewayTypeId, description = None, deviceInfo = None, metadata = None, classId = "Gateway"):
		"""
		Creates a gateway device type with the given gatewayTypeId.
		It accepts typeId (string), description (string), deviceInfo(dict) and metadata(dict) as parameter
		In case of failure it throws APIException
		"""
		return(self.addDeviceType(gatewayTypeId,description,deviceInfo,metadata,classId))

	def registerDeviceUnderGateway(self, gatewayTypeId, deviceId, authToken = None, deviceInfo = None, location = None, metadata=None):
		"""
		Registers a new device under given gateway type.
		It accepts typeId (string), deviceId (string), authToken (string), location (JSON) and metadata (JSON) as parameters
		In case of failure it throws APIException
		"""
		return(self.registerDevice(gatewayTypeId, deviceId, authToken, deviceInfo, location, metadata))

	def getDevicesConnectedThroughGateway(self, gatewayType, gatewayId=''):
		"""
		This method returns all devices that are connected through the specified
		gateway(typeId, deviceId) to Watson IoT Platform.
		"""
		if gatewayId != '':
			deviceUrl = ApiClient.deviceUrl % (self.host, gatewayType,gatewayId)
		else:
			deviceUrl = ApiClient.devicesUrl % (self.host, gatewayType)

		r = requests.get(deviceUrl, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Devices successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.APIException(404, "The device does not exist", None)
		elif status == 500:
			raise ibmiotf.APIException(500, "Unexpected error", None)
		else:
			raise ibmiotf.APIException(None, "Unexpected error", None)


	"""
	===========================================================================
	Device Management Extension API
		- List all device management extension packages
		- Create a new device management extension package
		- Delete a device management extension package
		- Get a specific device management extension package
		- Update a device management extension package
	===========================================================================
	"""

	def getAllDeviceManagementExtensionPkgs(self):
		"""
		List all device management extension packages
		"""
		dmeReq = ApiClient.dmeRequests % (self.host)
		r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Retrieved all Device Management Extension Packages")
			return r.json()
		else:
			raise ibmiotf.APIException(status,"HTTP Error in getAllDeviceManagementExtensionPkgs", r)

	def createDeviceManagementExtensionPkg(self, dmeData):
		"""
		Create a new device management extension package
		In case of failure it throws APIException
		"""
		dmeReq = ApiClient.dmeRequests % (self.host)
		r = requests.post(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
		              headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 201:
			self.logger.debug("The DME package request has been accepted for processing")
			return r.json()
		else:
			raise ibmiotf.APIException(status,"HTTP Error in createDeviceManagementExtensionPkg", r)

	def deleteDeviceManagementExtensionPkg(self, bundleId):
		"""
		Delete a device management extension package
		It accepts bundleId (string) as parameters
		In case of failure it throws APIException
		"""
		dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
		r = requests.delete(dmeReq, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 204:
			self.logger.debug("Device Management Extension Package removed")
			return True
		else:
			raise ibmiotf.APIException(status,"HTTP Error in deleteDeviceManagementExtensionPkg", r)

	def getDeviceManagementExtensionPkg(self, bundleId):
		"""
		Get a specific device management extension package
		It accepts bundleId (string) as parameters
		In case of failure it throws APIException
		"""
		dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
		r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device Management Extension Package retrieved")
			return r.json()
		else:
			raise ibmiotf.APIException(status,"HTTP Error in getDeviceManagementExtensionPkg", r)

	def updateDeviceManagementExtensionPkg(self, bundleId, dmeData):
		"""
		Update a device management extension package
		It accepts bundleId (string) as parameters
		In case of failure it throws APIException
		"""
		dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
		r = requests.put(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
		              headers = {'content-type': 'application/json'}, verify=self.verify)
		status = r.status_code
		if status == 200:
			self.logger.debug("Device Management Extension Package updated")
			return r.json()
		else:
			raise ibmiotf.APIException(status,"HTTP Error in updateDeviceManagementExtensionPkg", r)
