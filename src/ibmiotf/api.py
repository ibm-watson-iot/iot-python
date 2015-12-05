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
# *****************************************************************************

import ibmiotf
import json
import requests
import iso8601
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
	
	#Log Events URL
	deviceLogs = 'https://%s/api/v0002/logs/connection'
	
	#Diagnostics URL
	deviceDiagLogs = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs'
	deviceDiagLogsLogId = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs/%s'
	deviceDiagErrorCodes = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/errorCodes'
	
	#Usage Management URL
	usageMgmt = 'https://%s/api/v0002/usage'
	
	# Historian
	historianOrgUrl = 'https://%s/api/v0002/historian'
	historianTypeUrl = 'https://%s/api/v0002/historian/types/%s'
	historianDeviceUrl = 'https://%s/api/v0002/historian/types/%s/devices/%s'
	
	#Service Status URL
	serviceStatus = 'https://%s/api/v0002/service-status'
	
	#Device Management URL
	mgmtRequests = 'https://%s/api/v0002/mgmt/requests'
	mgmtSingleRequest = 'https://%s/api/v0002/mgmt/requests/%s'
	mgmtRequestStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus'
	mgmtRequestSingleDeviceStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus/%s/%s'
		
					
	def __init__(self, options):
		self.__options = options

		# Configure logging
		self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
		self.logger.setLevel(logging.INFO)

		if 'org' not in self.__options or self.__options['org'] == None:
			raise ibmiotf.ConfigurationException("Missing required property: org")
		if 'id' not in self.__options or self.__options['id'] == None: 
			raise ibmiotf.ConfigurationException("Missing required property: type")
		if 'auth-method' not in self.__options:
			raise ibmiotf.ConfigurationException("Missing required property: auth-method")
			
		if (self.__options['auth-method'] == "apikey"):
			# Check for required API Key and authentication token
			if 'auth-key' not in self.__options or self.__options['auth-key'] == None: 
				raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-key")
			if 'auth-token' not in self.__options or self.__options['auth-token'] == None: 
				raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")
			
			self.host = self.__options['org'] + ".internetofthings.ibmcloud.com"
			self.credentials = (self.__options['auth-key'], self.__options['auth-token'])
		elif self.__options['auth-method'] is not None:
			raise ibmiotf.UnsupportedAuthenticationMethod(options['authMethod'])
	

	def deleteDevice(self, deviceType, deviceId):
		"""
		Delete an existing device.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, deviceType, deviceId)

		r = requests.delete(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Device was successfully removed")
			return True
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	def getDevices(self, parameters = None):
		"""
		Retrieve bulk devices
		This method needs to be deprecated and has been maintained just for backward compatibility
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws IoTFCReSTException
		"""
		return getAllDevices(self)


	#This method returns the organization
	def getOrganizationDetails(self):
		"""
		Get details about an organization
		It does not need any parameter to be passed
		In case of failure it throws IoTFCReSTException
		"""
		if self.__options['org'] is None:
			raise ibmiotf.ConfigurationException("Missing required property: org")
		else:
			url = ApiClient.organizationUrl % (self.host)
		r = requests.get(url, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Organization retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The organization does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	def getAllDevices(self, parameters = None):
		"""
		Retrieve bulk devices
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws IoTFCReSTException
		"""
		bulkRetrieve = ApiClient.bulkRetrieve % (self.host )
		r = requests.get(bulkRetrieve, auth = self.credentials, params = parameters)
		
		status = r.status_code

		if status == 200:
			self.logger.info("Bulk retrieval successful")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)			
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the API key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The organization or device type does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		 
		

	def addMultipleDevices(self, listOfDevices):
		"""
		Register multiple new devices, each request can contain a maximum of 512KB.
		The response body will contain the generated authentication tokens for all devices. 
		You must make sure to record these tokens when processing the response. 
		We are not able to retrieve lost authentication tokens
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws IoTFCReSTException
		"""
		bulkAdd = ApiClient.bulkAddUrl % (self.host )
		r = requests.post(bulkAdd, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'})
		
		status = r.status_code
		
		if status == 201:
			self.logger.info("Bulk registration successful")
			return r.json()
		elif status == 202:
			raise ibmiotf.IoTFCReSTException(400, "Some devices registered successfully", r.json())			
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "Maximum number of devices exceeded", r.json())
		elif status == 413:
			raise ibmiotf.IoTFCReSTException(413, "Request content exceeds 512KB", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	def deleteMultipleDevices(self, listOfDevices):
		"""
		Delete multiple devices, each request can contain a maximum of 512Kb
		It accepts accepts a list of devices (List of Dictionary of Devices)
		In case of failure it throws IoTFCReSTException
		"""
		bulkRemove = ApiClient.bulkRemoveUrl % (self.host )
		r = requests.post(bulkRemove, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'})
		
		status = r.status_code
		if status == 202:
			self.logger.info("Some devices deleted successfully")
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
		elif status == 413:
			raise ibmiotf.IoTFCReSTException(413, "Request content exceeds 512KB", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		


	def getAllDeviceTypes(self, queryParameters = None):
		"""
		Retrieves all existing device types.
		It accepts accepts an optional query parameters (Dictionary)
		In case of failure it throws IoTFCReSTException			
		"""
		deviceTypeUrl = ApiClient.deviceTypesUrl % (self.host)
		r = requests.get(deviceTypeUrl, auth=self.credentials, params = queryParameters)
		status = r.status_code
		if status == 200:
			self.logger.info("All Device types successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	
	def addDeviceType(self, deviceType, description, deviceInfo, metadata):
		"""
		Creates a device type.
		It accepts deviceType (string), description (string), deviceInfo(JSON) and metadata(JSON) as parameter
		In case of failure it throws IoTFCReSTException		
		"""
		deviceTypesUrl = ApiClient.deviceTypesUrl % (self.host)
		payload = {'id' : deviceType, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata}

		r = requests.post(deviceTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 201:
			self.logger.info("Device Type Created")
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())			
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(403, "The device type already exists", r.json())			
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		
		
	def deleteDeviceType(self, deviceType):
		"""
		Deletes a device type.
		It accepts deviceType (string) as the parameter
		In case of failure it throws IoTFCReSTException			
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, deviceType)

		r = requests.delete(deviceTypeUrl, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Device type was successfully deleted")
			return True
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceType(self, deviceType):
		"""
		Gets device type details.
		It accepts deviceType (string) as the parameter
		In case of failure it throws IoTFCReSTException			
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, deviceType)
		r = requests.get(deviceTypeUrl, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Device type was successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The device type does not exist", None)			
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	def updateDeviceType(self, deviceType, description, deviceInfo, metadata = None):
		"""
		Updates a device type.
		It accepts deviceType (string), description (string), deviceInfo (JSON) and metadata(JSON) as the parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, deviceType)
		deviceTypeUpdate = {'description' : description, 'deviceInfo' : deviceInfo, 'metadata' : metadata}
		r = requests.put(deviceTypeUrl, auth=self.credentials, data=json.dumps(deviceTypeUpdate), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 200:
			self.logger.info("Device type was successfully modified")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The device type does not exist", None)			
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(409, "The update could not be completed due to a conflict", r.json())			
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


#	This has been purposely named as retrieveDevices to differentiate it with getDevices() / getAllDevices() which have similar arguments
	def retrieveDevices(self, deviceTypeId, expand = None):
		"""
		Gets device details.

		It accepts deviceType (string) and expand (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.devicesUrl % (self.host, deviceTypeId)

		r = requests.get(deviceUrl, auth=self.credentials, params = expand)
		status = r.status_code
		if status == 200:
			self.logger.info("Devices were successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The device does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
	
		

	def registerDevice(self, deviceTypeId, deviceId, authToken = None, deviceInfo = None, location = None, metadata=None):
		"""
		Registers a new device.
		It accepts deviceType (string), deviceId (string), authToken (string), location (JSON) and metadata (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		devicesUrl = ApiClient.devicesUrl % (self.host, deviceTypeId)
		payload = {'deviceId' : deviceId, 'authToken' : authToken, 'deviceInfo' : deviceInfo, 'location' : location, 'metadata': metadata}

		r = requests.post(devicesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 201:
			self.logger.info("Device Instance Created")
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())			
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(403, "The device already exists", r.json())			
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDevice(self, deviceType, deviceId, expand = None):
		"""
		Gets device details.
		It accepts deviceType (string), deviceId (string) and expand (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, deviceType, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials, params = expand)
		status = r.status_code
		if status == 200:
			self.logger.info("Device was successfully retrieved")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The device does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
	

	def removeDevice(self, deviceTypeId, deviceId):
		"""
		Delete an existing device.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, deviceTypeId, deviceId)

		r = requests.delete(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Device was successfully removed")
			return True
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
	
	
	def updateDevice(self, deviceType, deviceId, metadata, deviceInfo = None, status = None):
		"""
		Updates a device.
		It accepts deviceType (string), deviceId (string), metadata (JSON), deviceInfo (JSON) and status(JSON) as parameters
		In case of failure it throws IoTFCReSTException
		"""
		deviceUrl = ApiClient.deviceUrl % (self.host, deviceType, deviceId)

		payload = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		
		status = r.status_code		
		if status == 200:
			self.logger.info("Device was successfully modified")
			return r.json()
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "The organization, device type or device does not exist", None)
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(409, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceLocation(self, deviceTypeId, deviceId):
		"""
		Retrieve Device Location.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlLocation % (self.host, deviceTypeId, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Device Location was successfully obtained")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device location information not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	def updateDeviceLocation(self, deviceType, deviceId, deviceLocation):
		"""
		Updates the location information for a device. If no date is supplied, the entry is added with the current date and time.
		It accepts deviceType (string), deviceId (string) and deviceLocation (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlLocation % (self.host, deviceType, deviceId)

		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(deviceLocation), headers = {'content-type': 'application/json'} )
		status = r.status_code
		if status == 200:
			self.logger.info("Device Location was successfully modified")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device location information not found", None)
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(404, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceManagementInformation(self, deviceType, deviceId):
		"""
		Gets device management information for a device.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlMgmt % (self.host, deviceType, deviceId)
		r = requests.get(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Device Management Information was successfully obtained")
			return r.json()
		#This also throws a 403, which has not been documented
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	def getDeviceConnectionLogs(self, deviceTypeId, deviceId):
		"""
		List connection log events for a device to aid in diagnosing connectivity problems. 
		The entries record successful connection, unsuccessful connection attempts, intentional disconnection and server-initiated disconnection.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceLogs = ApiClient.deviceLogs % (self.host)
		logParameters = { 'typeId' : deviceTypeId, 'deviceId' : deviceId}
		r = requests.get(deviceLogs, auth=self.credentials, params = logParameters)
		status = r.status_code
		if status == 200:
			self.logger.info("Device Connection Logs were successfully obtained")
			return r.json()
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		
	
	def getAllDiagnosticLogs(self, deviceTypeId, deviceId):
		"""
		Retrieves All Device Diagnostic Logs.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, deviceTypeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		status = r.status_code
		if status == 200:
			self.logger.info("All Diagnostic logs successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	
	def clearAllDiagnosticLogs(self, deviceTypeId, deviceId):
		"""
		Deletes All Device Diagnostic Logs.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, deviceTypeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("All Diagnostic logs successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def addDiagnosticLog(self, deviceTypeId, deviceId, logs):
		"""
		Add Device Diagnostic Logs.
		It accepts deviceType (string), deviceId (string) and logs (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, deviceTypeId, deviceId)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(logs), headers = {'content-type': 'application/json'} )
		
		status = r.status_code
		if status == 201:
			self.logger.info("Diagnostic entry was successfully added")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDiagnosticLog(self, deviceTypeId, deviceId, logId):
		"""
		Retrieves Device Diagnostic Logs.
		It accepts deviceType (string), deviceId (string) and logId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, deviceTypeId, deviceId, logId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		status = r.status_code
		if status == 200:
			self.logger.info("Diagnostic log successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	
	def clearDiagnosticLog(self, deviceTypeId, deviceId, logId):
		"""
		Delete Device Diagnostic Logs.
		It accepts deviceType (string), deviceId (string) and logId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, deviceTypeId, deviceId, logId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Diagnostic log successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	def addErrorCode(self, deviceTypeId, deviceId, errorCode):
		"""
		Adds an error code to the list of error codes for the device. The list may be pruned as the new entry is added.
		It accepts deviceType (string), deviceId (string) and errorCode (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, deviceTypeId, deviceId)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(errorCode), headers = {'content-type': 'application/json'} )
		
		status = r.status_code
		if status == 201:
			self.logger.info("Error code was successfully added")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getAllDiagnosticErrorCodes(self, deviceTypeId, deviceId):
		"""
		Gets diagnostic error codes for a device.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, deviceTypeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		
		status = r.status_code
		if status == 200:
			self.logger.info("Error codes were successfully retrieved")
			return r.json()
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def clearAllErrorCodes(self, deviceTypeId, deviceId):
		"""
		Clears the list of error codes for the device. The list is replaced with a single error code of zero.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, deviceTypeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials )
		
		status = r.status_code
		if status == 204:
			self.logger.info("Error codes successfully cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Error Code not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getHistoricalEvents(self, deviceType=None, deviceId=None, options=None):
		if deviceId is not None and deviceType is not None:
			url = ApiClient.historianDeviceUrl % (self.host, deviceType, deviceId)
		elif deviceType is not None:
			url = ApiClient.historianTypeUrl % (self.host, deviceType)
		else:
			url = ApiClient.historianOrgUrl % (self.host)
		r = requests.get(url, auth=self.credentials, params = options)
		status = r.status_code
		
		if status == 200:
			return r.json()
		else:
			raise ibmiotf.IoTFCReSTException(status, "Unexpected error", None)
	
	
	def getServiceStatus(self):
		"""
		Retrieve the organization-specific status of each of the services offered by the Internet of Things Foundation.
		In case of failure it throws IoTFCReSTException		
		"""
		serviceStatus = ApiClient.serviceStatus % (self.host)
		r = requests.get(serviceStatus, auth=self.credentials )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Service status successfully retrieved")
			return r.json()
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getActiveDevices(self, options):
		"""
		Retrieve the number of active devices over a period of time.
		In case of failure it throws IoTFCReSTException		
		"""
		activeDevices = (ApiClient.usageMgmt + '/active-devices') % (self.host)
		r = requests.get(activeDevices, auth=self.credentials, params=options )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Active Devices = ", r.json() )
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Bad Request", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDataTraffic(self, options):
		"""
		Retrieve the amount of data used.
		In case of failure it throws IoTFCReSTException		
		"""
		dataTraffic = (ApiClient.usageMgmt + '/data-traffic') % (self.host)
		r = requests.get(dataTraffic, auth=self.credentials, params=options )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Data Traffic = ", r.json() )
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Bad Request", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getHistoricalDataUsage(self, options):
		"""
		Retrieve the amount of storage being used by historical event data.
		In case of failure it throws IoTFCReSTException		
		"""
		historicalData = (ApiClient.usageMgmt + '/historical-data') % (self.host)
		r = requests.get(historicalData, auth=self.credentials, params=options )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Historical Data = ", r.json() )
			return r.json()
		elif status == 400:
			raise ibmiotf.IoTFCReSTException(400, "Bad Request", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getAllDeviceManagementRequests(self):
		"""
		Gets a list of device management requests, which can be in progress or recently completed.
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtRequests % (self.host)
		r = requests.get(mgmtRequests, auth=self.credentials )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Retrieved all device management requests")
			return r.json()
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def initiateDeviceManagementRequest(self, deviceManagementRequest):
		"""
		Initiates a device management request, such as reboot.
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtRequests % (self.host)
		r = requests.post(mgmtRequests, auth=self.credentials, data=json.dumps(deviceManagementRequest), headers = {'content-type': 'application/json'})
		
		status = r.status_code
		if status == 202:
			self.logger.info("The request has been accepted for processing")
			return r.json()
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(500, "Devices don't support the requested operation", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def deleteDeviceManagementRequest(self, requestId):
		"""
		Clears the status of a device management request. 
		You can use this operation to clear the status for a completed request, or for an in-progress request which may never complete due to a problem.
		It accepts requestId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
		r = requests.delete(mgmtRequests, auth=self.credentials )
		
		status = r.status_code
		if status == 204:
			self.logger.info("Request status cleared")
			return True
		#403 and 404 error code needs to be added in Swagger documentation
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Request Id not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceManagementRequest(self, requestId):
		"""
		Gets details of a device management request.
		It accepts requestId (string) as parameters		
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
		r = requests.get(mgmtRequests, auth=self.credentials )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Retrieving single management request")
			return r.json()
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Request Id not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceManagementRequestStatus(self, requestId):
		"""
		Get a list of device management request device statuses.
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtRequestStatus % (self.host, requestId)
		r = requests.get(mgmtRequests, auth=self.credentials )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Retrieved all device management request statuses")
			return r.json()
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)			
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Request status not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceManagementRequestStatusByDevice(self, requestId, deviceType, deviceId):
		"""
		Get an individual device mangaement request device status.
		In case of failure it throws IoTFCReSTException		
		"""
		mgmtRequests = ApiClient.mgmtRequestSingleDeviceStatus % (self.host, requestId, deviceType, deviceId)
		r = requests.get(mgmtRequests, auth=self.credentials )
		
		status = r.status_code
		
		if status == 200:
			self.logger.info("Retrieved device management request status of single device")
			return r.json()
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Request status not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
