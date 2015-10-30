# *****************************************************************************
# Copyright (c) 2015 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David Parker - Initial Contribution
#   Amit M Mangalvedkar - v2 API Support
# *****************************************************************************

import ibmiotf
import json
import requests
import iso8601
from datetime import datetime

import logging
from symbol import parameters


class ApiClient():

	devicesUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/devices'
	deviceUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/devices/%s/%s'
	historianOrgUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/historian'
	historianTypeUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/historian/%s'

	historianOrgUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/historian'
	historianTypeUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/historian/types/%s'
	historianDeviceUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/historian/types/%s/devices/%s'
		
	
	#v2 ReST URL
	#Organization URL
	organizationUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/'
	
	
	#Bulk Operations URL
	bulkRetrievev2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/bulk/devices'
	bulkAddUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/bulk/devices/add'	
	bulkRemoveUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/bulk/devices/remove'
	
	
	#Device Types URL
	deviceTypesUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types'
	deviceTypeUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s'		

	
	#Device URL
	devicesUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices'
	deviceUrlv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s'
	deviceUrlLocationv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/location'
	deviceUrlMgmtv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/mgmt'
	
	
	#Log Events URL
	deviceLogsv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/logs/connection'
	
	
	#Diagnostics URL
	deviceDiagLogsv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/diag/logs'
	deviceDiagLogsLogIdv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/diag/logs/%s'
	deviceDiagErrorCodesv2 = 'https://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/diag/errorCodes'
					
					
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
			
			self.credentials = (self.__options['auth-key'], self.__options['auth-token'])
		elif self.__options['auth-method'] is not None:
			raise ibmiotf.UnsupportedAuthenticationMethod(options['authMethod'])


	def registerDevice(self, deviceType, deviceId, metadata=None):
		url = ApiClient.devicesUrl % (self.__options['org'])
		payload = {'type': deviceType, 'id': deviceId, 'metadata': metadata}

		r = requests.post(url, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		r.status_code
		return r.json()

		
	def updateDevice(self, deviceType, deviceId, metadata):
		url = ApiClient.deviceUrl % (self.__options['org'], deviceType, deviceId)
		payload = {'metadata': json.dumps(metadata)}

		r = requests.post(url, auth=self.credentials, data=payload)
		r.status_code
		return r.json()

		
	def deleteDevice(self, deviceType, deviceId):
		url = ApiClient.deviceUrl % (self.__options['org'], deviceType, deviceId)

		r = requests.delete(url, auth=self.credentials)
		if r.status_code != 204:
			raise Exception("Unable to delete device %s:%s" % (deviceType, deviceId))

		
	def getDevices(self):
		'''
		Sample reponse:
		[{
			'registration': {
				'auth': {'type': 'person', 'id': 'parkerda@uk.ibm.com'}, 
				'date': '2014-12-01T17:31:30Z'
			},
			'type': '001', 
			'metadata': {}, 
			'uuid': 'd:hldtxx:001:001', 
			'id': '001'
		}]
		'''	
		url = ApiClient.devicesUrl % (self.__options['org'])
		
		r = requests.get(url, auth=self.credentials)
		r.status_code
		return r.json()

		
	def getDevice(self, deviceType, deviceId):
		url = ApiClient.deviceUrl % (self.__options['org'], deviceType, deviceId)
		
		r = requests.get(url, auth=self.credentials)
		r.status_code
		return r.json()
	
	#Not sure why this method was written it returns only 1
	def getDeviceTypeInfo(self, deviceType):
		return 1


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
			url = ApiClient.organizationUrlv2 % (self.__options['org'])
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
		bulkRetrieve = ApiClient.bulkRetrievev2 % (self.__options['org'] )
		r = requests.get(bulkRetrieve, auth = self.credentials, params = parameters)
		
		status = r.status_code

		print("Status = ", status)

		if status == 200:
			self.logger.info("Bulk retrieval successful")
			print("Bulk retrieval successful")
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
		bulkAdd = ApiClient.bulkAddUrlv2 % (self.__options['org'] )
		r = requests.post(bulkAdd, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'})
		
		status = r.status_code

		print("Status = ", status)
		print("List = ", listOfDevices)
		if status == 201:
			self.logger.info("Bulk registration successful")
			print("Bulk registration successful")
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
		bulkRemove = ApiClient.bulkRemoveUrlv2 % (self.__options['org'] )
		r = requests.post(bulkRemove, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'})
		
		status = r.status_code
		if status == 202:
			self.logger.info("Some devices deleted successfully")
			print("Some devices deleted successfully")
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
		Retrieves al existing device types.
		It accepts accepts an optional query parameters (Dictionary)
		In case of failure it throws IoTFCReSTException			
		"""
		deviceTypeUrl = ApiClient.deviceTypesUrlv2 % (self.__options['org'])
		r = requests.get(deviceTypeUrl, auth=self.credentials, params = queryParameters)
		status = r.status_code
		if status == 200:
			self.logger.info("All Device types successfully retrieved")
			print("All Device types successfully retrieved")
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
		deviceTypesUrl = ApiClient.deviceTypesUrlv2 % (self.__options['org'])
		payload = {'id' : deviceType, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata}

		r = requests.post(deviceTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 201:
			self.logger.info("Device Type Created")
			print("Device Type created")
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
		deviceTypeUrl = ApiClient.deviceTypeUrlv2 % (self.__options['org'], deviceType)

		r = requests.delete(deviceTypeUrl, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Device type was successfully deleted")
			print("Device type was successfully deleted")
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
		deviceTypeUrl = ApiClient.deviceTypeUrlv2 % (self.__options['org'], deviceType)
		r = requests.get(deviceTypeUrl, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Device type was successfully retrieved")
			print("Device type was successfully retrieved")
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
		deviceTypeUrl = ApiClient.deviceTypeUrlv2 % (self.__options['org'], deviceType)
		deviceTypeUpdate = {'description' : description, 'deviceInfo' : deviceInfo, 'metadata' : metadata}
		r = requests.put(deviceTypeUrl, auth=self.credentials, data=json.dumps(deviceTypeUpdate), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 200:
			self.logger.info("Device type was successfully modified")
			print("Device type was successfully modified")
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


	def retrieveDevices(self, deviceTypeId, expand = None):
		"""
		Gets device details.
		It accepts deviceType (string) and expand (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.devicesUrlv2 % (self.__options['org'], deviceTypeId)

		r = requests.get(deviceUrl, auth=self.credentials, params = expand)
		status = r.status_code
		if status == 200:
			self.logger.info("Devices were successfully retrieved")
			print("Devices were successfully retrieved")
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
	
		

	def registerDevice(self, deviceTypeId, deviceId, authToken, deviceInfo, location, metadata=None):
		"""
		Registers a new device.
		It accepts deviceType (string), deviceId (string), authToken (string), location (JSON) and metadata (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		devicesUrl = ApiClient.devicesUrlv2 % (self.__options['org'], deviceTypeId)
		payload = {'deviceId' : deviceId, 'authToken' : authToken, 'deviceInfo' : deviceInfo, 'location' : location, 'metadata': metadata}

		r = requests.post(devicesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		status = r.status_code
		if status == 201:
			self.logger.info("Device Instance Created")
			print("Device Instance created")
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


	def retrieveSingleDevice(self, deviceTypeId, deviceId, expand = None):
		"""
		Gets device details.
		It accepts deviceType (string), deviceId (string) and expand (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlv2 % (self.__options['org'], deviceTypeId, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials, params = expand)
		status = r.status_code
		if status == 200:
			self.logger.info("Device was successfully retrieved")
			print("Device was successfully retrieved")
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
		deviceUrl = ApiClient.deviceUrlv2 % (self.__options['org'], deviceTypeId, deviceId)

		r = requests.delete(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Device was successfully removed")
			print("Device was successfully removed")
			return True
		elif status == 401:
			raise ibmiotf.IoTFCReSTException(401, "The authentication token is empty or invalid", None)
		elif status == 403:
			raise ibmiotf.IoTFCReSTException(403, "The authentication method is invalid or the api key used does not exist", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
	
	
	def modifyDevice(self, deviceTypeId, deviceId, deviceInfo, status, metadata = None):
		"""
		Modify an existing device.
		It accepts deviceTypeId (string), deviceId (string), deviceInfo (JSON), metadata (JSON) and status(JSON) as parameters
		In case of failure it throws IoTFCReSTException
		"""
		deviceUrl = ApiClient.deviceUrlv2 % (self.__options['org'], deviceTypeId, deviceId)

		payload = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'})
		
		status = r.status_code		
		if status == 200:
			self.logger.info("Device was successfully modified")
			print("Device was successfully modified")
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
		deviceUrl = ApiClient.deviceUrlLocationv2 % (self.__options['org'], deviceTypeId, deviceId)

		r = requests.get(deviceUrl, auth=self.credentials)
		status = r.status_code
		if status == 200:
			self.logger.info("Device Location was successfully obtained")
			print("Device Location was successfully obtained")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device location information not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)

		
	def modifyDeviceLocation(self, deviceTypeId, deviceId, deviceLocation):
		"""
		Modify Device Location.
		It accepts deviceType (string), deviceId (string) and deviceLocation (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlLocationv2 % (self.__options['org'], deviceTypeId, deviceId)

		r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(deviceLocation), headers = {'content-type': 'application/json'} )
		status = r.status_code
		if status == 200:
			self.logger.info("Device Location was successfully modified")
			print("Device Location was successfully modified")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device location information not found", None)
		elif status == 409:
			raise ibmiotf.IoTFCReSTException(404, "The update could not be completed due to a conflict", r.json())
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)


	def getDeviceManagement(self, deviceTypeId, deviceId):
		"""
		Retrieve Device Location.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceUrl = ApiClient.deviceUrlMgmtv2 % (self.__options['org'], deviceTypeId, deviceId)
		print("DeviceURL = ", deviceUrl)
		r = requests.get(deviceUrl, auth=self.credentials)
		status = r.status_code
		print("Status = ", status)
		if status == 200:
			self.logger.info("Device Management Information was successfully obtained")
			print("Device Management Information was successfully obtained")
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
		deviceLogs = ApiClient.deviceLogsv2 % (self.__options['org'])
		logParameters = { 'typeId' : deviceTypeId, 'deviceId' : deviceId}
		r = requests.get(deviceLogs, auth=self.credentials, params = logParameters)
		status = r.status_code
		if status == 200:
			self.logger.info("Device Connection Logs were successfully obtained")
			print("Device Connection Logs were successfully obtained")
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
		deviceDiagnostics = ApiClient.deviceDiagLogsv2 % (self.__options['org'], deviceTypeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		status = r.status_code
		if status == 200:
			self.logger.info("All Diagnostic logs successfully retrieved")
			print("All Diagnostic logs successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	
	def deleteAllDiagnosticLogs(self, deviceTypeId, deviceId):
		"""
		Deletes All Device Diagnostic Logs.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsv2 % (self.__options['org'], deviceTypeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("All Diagnostic logs successfully cleared")
			print("All Diagnostic logs successfully cleared")
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


	def createDiagnosticLog(self, deviceTypeId, deviceId, logs):
		"""
		Add Device Diagnostic Logs.
		It accepts deviceType (string), deviceId (string) and logs (JSON) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsv2 % (self.__options['org'], deviceTypeId, deviceId)
		print("URL = ", deviceDiagnostics, "\tLogs = ", logs)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(logs), headers = {'content-type': 'application/json'} )
		
		status = r.status_code
		print("Status = ", status)
		if status == 201:
			self.logger.info("Diagnostic entry was successfully added")
			print("Diagnostic entry was successfully added")
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
		deviceDiagnostics = ApiClient.deviceDiagLogsLogIdv2 % (self.__options['org'], deviceTypeId, deviceId, logId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		status = r.status_code
		print("Status = ", status)
		if status == 200:
			self.logger.info("Diagnostic log successfully retrieved")
			print("Diagnostic log successfully retrieved")
			return r.json()
		elif status == 404:
			raise ibmiotf.IoTFCReSTException(404, "Device not found", None)
		elif status == 500:
			raise ibmiotf.IoTFCReSTException(500, "Unexpected error", None)
		else:
			raise ibmiotf.IoTFCReSTException(None, "Unexpected error", None)
		

	
	def deleteDiagnosticLog(self, deviceTypeId, deviceId, logId):
		"""
		Delete Device Diagnostic Logs.
		It accepts deviceType (string), deviceId (string) and logId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagLogsLogIdv2 % (self.__options['org'], deviceTypeId, deviceId, logId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials)
		status = r.status_code
		if status == 204:
			self.logger.info("Diagnostic log successfully cleared")
			print("Diagnostic log successfully cleared")
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
		deviceDiagnostics = ApiClient.deviceDiagErrorCodesv2 % (self.__options['org'], deviceTypeId, deviceId)
		r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(errorCode), headers = {'content-type': 'application/json'} )
		
		status = r.status_code
		print("Status = ", status)
		if status == 201:
			self.logger.info("Error code was successfully added")
			print("Error code was successfully added")
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


	def retrieveAllErrorCodes(self, deviceTypeId, deviceId):
		"""
		Gets diagnostic error codes for a device.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodesv2 % (self.__options['org'], deviceTypeId, deviceId)
		r = requests.get(deviceDiagnostics, auth=self.credentials )
		
		status = r.status_code
		print("Status = ", status)
		if status == 200:
			self.logger.info("Error codes were successfully retrieved")
			print("Error code were successfully retrieved")
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


	def deleteAllErrorCodes(self, deviceTypeId, deviceId):
		"""
		Clears the list of error codes for the device. The list is replaced with a single error code of zero.
		It accepts deviceType (string) and deviceId (string) as parameters
		In case of failure it throws IoTFCReSTException		
		"""
		deviceDiagnostics = ApiClient.deviceDiagErrorCodesv2 % (self.__options['org'], deviceTypeId, deviceId)
		r = requests.delete(deviceDiagnostics, auth=self.credentials )
		
		status = r.status_code
		print("Status = ", status)
		if status == 204:
			self.logger.info("Error codes successfully cleared")
			print("Error code were successfully retrieved")
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
			url = ApiClient.historianDeviceUrlv2 % (self.__options['org'], deviceType, deviceId)
		elif deviceType is not None:
			url = ApiClient.historianTypeUrlv2 % (self.__options['org'], deviceType)
		else:
			url = ApiClient.historianOrgUrlv2 % (self.__options['org'])
		print ("URL = ", url)	
		r = requests.get(url, auth=self.credentials, params = options)
		status = r.status_code
		
		print("Status code 2 = ", status)
		return r.json()
	
	
