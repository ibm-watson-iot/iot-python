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

import ibmiotf
import json
import requests
import iso8601
from datetime import datetime



class ApiClient():

	devicesUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/devices'
	deviceUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/devices/%s/%s'
	historianOrgUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/historian'
	historianTypeUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/historian/%s'
	historianDeviceUrl = 'https://%s.internetofthings.ibmcloud.com/api/v0001/historian/%s/%s'
	
	def __init__(self, options):
		self.__options = options

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
	
	
	def getDeviceTypeInfo(self, deviceType):
		return 1
	
	
	def getHistoricalEvents(self, deviceType=None, deviceId=None, options=None):
		if deviceId is not None and deviceType is not None:
			url = ApiClient.historianDeviceUrl % (self.__options['org'], deviceType, deviceId)
		elif deviceType is not None:
			url = ApiClient.historianTypeUrl % (self.__options['org'], deviceType)
		else:
			url = ApiClient.historianOrgUrl % (self.__options['org'])
	
		r = requests.get(url, auth=self.credentials)
		r.status_code
		return r.json()
	
