# *****************************************************************************
# Copyright (c) 2014 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David Parker  - Initial Contribution
# *****************************************************************************

import json
import re
import pytz
import uuid
import threading
import requests
import paho.mqtt.client as paho

from datetime import datetime

from ibmiotf import AbstractClient, InvalidEventException, UnsupportedAuthenticationMethod, ConfigurationException, ConnectionException, MissingMessageEncoderException, MissingMessageDecoderException
from ibmiotf.codecs import jsonCodec, jsonIotfCodec

# Support Python 2.7 and 3.4 versions of configparser
try:
	import configparser
except ImportError:
	import ConfigParser as configparser

COMMAND_RE = re.compile("iot-2/cmd/(.+)/fmt/(.+)")


class Command:
	def __init__(self, pahoMessage, messageEncoderModules):
		result = COMMAND_RE.match(pahoMessage.topic)
		if result:
			self.command = result.group(1)
			self.format = result.group(2)

			if self.format in messageEncoderModules:
				message = messageEncoderModules[self.format].decode(pahoMessage)
				self.timestamp = message.timestamp
				self.data = message.data
			else:
				raise MissingMessageDecoderException(self.format)
		else:
			raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))


class Client(AbstractClient):
	
	COMMAND_TOPIC = "iot-2/cmd/+/fmt/+"

	def __init__(self, options, logHandlers=None):
		self._options = options

		if self._options['org'] == None:
			raise ConfigurationException("Missing required property: org")
		if self._options['type'] == None: 
			raise ConfigurationException("Missing required property: type")
		if self._options['id'] == None: 
			raise ConfigurationException("Missing required property: id")
		
		if self._options['org'] != "quickstart":
			if self._options['auth-method'] == None: 
				raise ConfigurationException("Missing required property: auth-method")
				
			if (self._options['auth-method'] == "token"):
				if self._options['auth-token'] == None: 
					raise ConfigurationException("Missing required property for token based authentication: auth-token")
			else:
				raise UnsupportedAuthenticationMethod(options['authMethod'])


		AbstractClient.__init__(
			self, 
			organization = options['org'],
			clientId = "d:" + options['org'] + ":" + options['type'] + ":" + options['id'], 
			username = "use-token-auth" if (options['auth-method'] == "token") else None,
			password = options['auth-token'],
			logHandlers = logHandlers
		)


		# Add handler for commands if not connected to QuickStart
		if self._options['org'] != "quickstart":
			self.client.message_callback_add("iot-2/cmd/+/fmt/+", self.__onCommand)

		self.subscriptionsAcknowledged = threading.Event()
		
		# Initialize user supplied callback
		self.commandCallback = None

		self.client.on_connect = self.on_connect
		
		self.setMessageEncoderModule('json', jsonCodec)
		self.setMessageEncoderModule('json-iotf', jsonIotfCodec)

	
	'''
	This is called after the client has received a CONNACK message from the broker in response to calling connect(). 
	The parameter rc is an integer giving the return code:
	0: Success
	1: Refused - unacceptable protocol version
	2: Refused - identifier rejected
	3: Refused - server unavailable
	4: Refused - bad user name or password
	5: Refused - not authorised
	'''
	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.connectEvent.set()
			self.logger.info("Connected successfully: %s" % self.clientId)
			if self._options['org'] != "quickstart":
				self.__subscribeToCommands()
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))
	
	'''
	Publish an event in IoTF.  
	Parameters:
		event - the name of this event
		msgFormat - the format of the data for this event
		data - the data for this event
	Optional paramters:
		qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
		on_publish - a function that will be called when receipt of the publication is confirmed.  This
					 has different implications depending on the qos:
					 qos 0 - the client has asynchronously begun to send the event
					 qos 1 and 2 - the client has confirmation of delivery from IoTF
	'''
	def publishEvent(self, event, msgFormat, data, qos=0, on_publish=None):
		if not self.connectEvent.wait():
			self.logger.warning("Unable to send event %s because device is not currently connected")
			return False
		else:
			self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))
			topic = 'iot-2/evt/'+event+'/fmt/' + msgFormat
			
			if msgFormat in self._messageEncoderModules:
				payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now(pytz.timezone('UTC')))
				
				try:
					# need to take lock to ensure on_publish is not called before we know the mid
					if on_publish is not None:
						self._messagesLock.acquire()
					
					result = self.client.publish(topic, payload=payload, qos=qos, retain=False)
					if result[0] == paho.MQTT_ERR_SUCCESS:
						if on_publish is not None:
							self._onPublishCallbacks[result[1]] = on_publish
						return True
					else:
						return False
				finally:
					if on_publish is not None:
						self._messagesLock.release()
			else:
				raise MissingMessageEncoderException(msgFormat)


	'''
	This method is used by the device to publish events over HTTP(s)
	It accepts 2 parameters, event which denotes event type and data which is the message to be posted
	It throws a ConnectionException with the message "Server not found" if the client is unable to reach the server
	Otherwise it returns the HTTP status code, (200 - 207 for success)
	'''
	def publishEventOverHTTP(self, event, data):
		self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))

#		Kept this as a template 
#		orgUrl = 'http://quickstart.internetofthings.ibmcloud.com/api/v0002/device/types/arduino/devices/00aabbccde02/events/status'
		templateUrl = '%s://%s.internetofthings.ibmcloud.com/api/v0002/device/types/%s/devices/%s/events/%s'

#		Extracting all the values needed for the ReST operation
#		Checking each value for 'None' is not needed as the device itself would not have got created, if it had any 'None' values
		orgid = self._options['org']
		deviceType = self._options['type']
		deviceId = self._options['id']
		authMethod = self._options['auth-method'] 
		authToken = self._options['auth-token']
		credentials = (authMethod, authToken)

		if orgid == 'quickstart':
			protocol = 'http'
		else:
			protocol = 'https'

#		String replacement from template to actual URL
		intermediateUrl = templateUrl % (protocol, orgid, deviceType, deviceId, event)

		try:
			msgFormat = "json"
			payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now(pytz.timezone('UTC')))
			response = requests.post(intermediateUrl, auth = credentials, data = payload, headers = {'content-type': 'application/json'})
		except Exception as e:
			self.logger.error("POST Failed")
			self.logger.error(e)			
			raise ConnectionException("Server not found")

#		print ("Response status = ", response.status_code, "\tResponse ", response.headers)
		if response.status_code >= 300:
			self.logger.warning(response.headers)
		return response.status_code


	def __subscribeToCommands(self):
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support commands")
			return False
		
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to commands because device is not currently connected")
			return False
		else:
			topic = 'iot-2/cmd/+/fmt/json'
			self.client.subscribe(topic, qos=1)
			return True

	'''
	Internal callback for device command messages, parses source device from topic string and 
	passes the information on to the registerd device command callback
	'''
	def __onCommand(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1
		try:
			command = Command(pahoMessage, self._messageEncoderModules)
		except InvalidEventException as e:
			self.logger.critical(str(e))
		else:
			self.logger.debug("Received command '%s'" % (command.command))
			if self.commandCallback: self.commandCallback(command)



class DeviceInfo(object):
	def __init__(self):
		self.serialNumber = None
		self.manufacturer = None
		self.model = None
		self.deviceClass = None
		self.description = None
		self.fwVersion = None
		self.hwVersion = None
		self.descriptiveLocation = None
	
	def __str__(self):
		return json.dumps(self.__dict__, sort_keys=True)
	
	
class ManagedClient(Client):

	# Publish MQTT topics
	MANAGE_TOPIC = 'iotdevice-1/mgmt/manage'
	UNMANAGE_TOPIC = 'iotdevice-1/mgmt/unmanage'
	UPDATE_LOCATION_TOPIC = 'iotdevice-1/device/update/location'
	ADD_ERROR_CODE_TOPIC = 'iotdevice-1/add/diag/errorCodes'
	CLEAR_ERROR_CODES_TOPIC = 'iotdevice-1/clear/diag/errorCodes'
	NOTIFY_TOPIC = 'iotdevice-1/notify'
	
	# Subscribe MQTT topics
	DM_RESPONSE_TOPIC = 'iotdm-1/response'
	DM_OBSERVE_TOPIC = 'iotdm-1/observe'
	
	def __init__(self, options, logHandlers=None, deviceInfo=None):
		if options['org'] == "quickstart":
			raise Exception("Unable to create ManagedClient instance.  QuickStart devices do not support device management")

		Client.__init__(self, options, logHandlers)
		# TODO: Raise fatal exception if tries to create managed device client for QuickStart
		
		# Add handler for supported device management commands
		self.client.message_callback_add("iotdm-1/#", self.__onDeviceMgmtResponse)
		self.client.on_subscribe = self.on_subscribe
		
		self.readyForDeviceMgmt = threading.Event()
		
		# List of DM requests that have not received a response yet
		self._deviceMgmtRequestsPendingLock = threading.Lock()
		self._deviceMgmtRequestsPending = {}

		# List of DM notify hook 
		self._deviceMgmtObservationsLock = threading.Lock()
		self._deviceMgmtObservations = []

		# Initialize local device data model
		self.metadata = {}
		if deviceInfo is not None:
			self._deviceInfo = deviceInfo
		else:
			self._deviceInfo = DeviceInfo()
		
		self._location = None
		self._errorCode = None
	
	
	def setSerialNumber(self, serialNumber):
		self._deviceInfo.serialNumber = serialNumber
		return self.notifyFieldChange("deviceInfo.serialNumber", serialNumber)

	def setManufacturer(self, manufacturer):
		self._deviceInfo.serialNumber = manufacturer
		return self.notifyFieldChange("deviceInfo.manufacturer", manufacturer)
	
	def setModel(self, model):
		self._deviceInfo.serialNumber = model
		return self.notifyFieldChange("deviceInfo.model", model)

	def setdeviceClass(self, deviceClass):
		self._deviceInfo.deviceClass = deviceClass
		return self.notifyFieldChange("deviceInfo.deviceClass", deviceClass)

	def setDescription(self, description):
		self._deviceInfo.description = description
		return self.notifyFieldChange("deviceInfo.description", description)

	def setFwVersion(self, fwVersion):
		self._deviceInfo.fwVersion = fwVersion
		return self.notifyFieldChange("deviceInfo.fwVersion", fwVersion)

	def setHwVersion(self, hwVersion):
		self._deviceInfo.hwVersion = hwVersion
		return self.notifyFieldChange("deviceInfo.hwVersion", hwVersion)

	def setDescriptiveLocation(self, descriptiveLocation):
		self._deviceInfo.descriptiveLocation = descriptiveLocation
		return self.notifyFieldChange("deviceInfo.descriptiveLocation", descriptiveLocation)
	

	def notifyFieldChange(self, field, value):
		with self._deviceMgmtObservationsLock:
			if field in self._deviceMgmtObservations:
				if not self.readyForDeviceMgmt.wait():
					self.logger.warning("Unable to notify service of field change because device is not ready for device management")
					return threading.Event().set()
		
				reqId = str(uuid.uuid4())
				message = {
					"d": {
						"field": field, 
						"value": value
					},
					"reqId": reqId
				}
				
				resolvedEvent = threading.Event()
				self.client.publish(ManagedClient.NOTIFY_TOPIC, payload=json.dumps(message), qos=1, retain=False)
				with self._deviceMgmtRequestsPendingLock:
					self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.NOTIFY_TOPIC, "message": message, "event": resolvedEvent}
				
				return resolvedEvent
			else:
				return threading.Event().set()
	'''
	This is called after the client has received a CONNACK message from the broker in response to calling connect(). 
	The parameter rc is an integer giving the return code:
	0: Success
	1: Refused - unacceptable protocol version
	2: Refused - identifier rejected
	3: Refused - server unavailable
	4: Refused - bad user name or password
	5: Refused - not authorised
	'''
	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.connectEvent.set()
			self.logger.info("Connected successfully: %s" % self.clientId)
			if self._options['org'] != "quickstart":
				self.client.subscribe( [(ManagedClient.DM_RESPONSE_TOPIC, 1), (ManagedClient.DM_OBSERVE_TOPIC, 1), (Client.COMMAND_TOPIC, 1)] )
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))
	
	
	def on_subscribe(self, client, userdata, mid, granted_qos):
		# Once IoTF acknowledges the subscriptions we are able to process commands and responses from device management server 
		self.subscriptionsAcknowledged.set()
		self.manage()
	
	
	def manage(self, lifetime=3600, supportDeviceActions=False, supportFirmwareActions=False):
		# TODO: throw an error, minimum lifetime this client will support is 1 hour, but for now set lifetime to infinite if it's invalid
		if lifetime < 3600:
			lifetime = 0
		
		if not self.subscriptionsAcknowledged.wait():
			self.logger.warning("Unable to send register for device management because device subscriptions are not in place")
			return threading.Event().set()
		
		reqId = str(uuid.uuid4())
		message = {
			'd': {
				"lifetime": lifetime,
				"supports": {
					"deviceActions": supportDeviceActions,
					"firmwareActions": supportFirmwareActions
				},
				"deviceInfo" : self._deviceInfo.__dict__,
				"metadata" : self.metadata
			},
			'reqId': reqId
		}
		
		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.MANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.MANAGE_TOPIC, "message": message, "event": resolvedEvent} 
		
		# Register the future call back to IoT Foundation 2 minutes before the device lifetime expiry
		if lifetime != 0:
			threading.Timer(lifetime-120, self.manage, [lifetime, supportDeviceActions, supportFirmwareActions]).start()
		
		return resolvedEvent
	
	
	def unmanage(self):
		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to set device to unmanaged because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			'reqId': reqId
		}
		
		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.UNMANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.UNMANAGE_TOPIC, "message": message, "event": resolvedEvent} 
		
		return resolvedEvent
	
	def setLocation(self, longitude, latitude, elevation=None, accuracy=None):
		# TODO: Add validation (e.g. ensure numeric values)
		if self._location is None:
			self._location = {}
		
		self._location['longitude'] = longitude
		self._location['latitude'] = latitude
		if elevation:
			self._location['elevation'] = elevation
		
		self._location['measuredDateTime'] = datetime.now(pytz.timezone('UTC')).isoformat()

		if accuracy:
			self._location['accuracy'] = accuracy
		elif "accuracy" in self._location:
			del self._location["accuracy"]

		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to publish device location because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			"d": self._location,
			"reqId": reqId
		}
		
		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.UPDATE_LOCATION_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.UPDATE_LOCATION_TOPIC, "message": message, "event": resolvedEvent}
		
		return resolvedEvent
	
	
	def setErrorCode(self, errorCode=0):
		if errorCode is None:
			errorCode = 0;
			
		self._errorCode = errorCode
		
		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to publish error code because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			"d": { "errorCode": errorCode },
			"reqId": reqId
		}
		
		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.ADD_ERROR_CODE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.ADD_ERROR_CODE_TOPIC, "message": message, "event": resolvedEvent} 
		
		return resolvedEvent

	def clearErrorCodes(self):
		self._errorCode = None
		
		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to clear error codes because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			"reqId": reqId
		}
		
		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.CLEAR_ERROR_CODES_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.CLEAR_ERROR_CODES_TOPIC, "message": message, "event": resolvedEvent} 
		
		return resolvedEvent
	
	
	def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1
		
		try:
			data = json.loads(pahoMessage.payload.decode("utf-8"))
			
			rc = data['rc']
			reqId = data['reqId']
		except ValueError as e:
			raise Exception("Unable to parse JSON.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))
		else:
			request = None
			with self._deviceMgmtRequestsPendingLock:
				try:
					request = self._deviceMgmtRequestsPending.pop(reqId)
				except KeyError:
					self.logger.warning("Received unexpected response from device management: %s" % (reqId))
				else:
					self.logger.debug("Remaining unprocessed device management requests: %s" % (len(self._deviceMgmtRequestsPending)))
					
			
			if request is None:
				return False
				
			if request['topic'] == ManagedClient.MANAGE_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Manage action completed: %s" % (rc, json.dumps(request['message'])))
					self.readyForDeviceMgmt.set()
				else:
					self.logger.critical("[%s] Manage action failed: %s" % (rc, json.dumps(request['message'])))
					
			elif request['topic'] == ManagedClient.UNMANAGE_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Unmanage action completed: %s" % (rc, json.dumps(request['message'])))
					self.readyForDeviceMgmt.clear()
				else:
					self.logger.critical("[%s] Unmanage action failed: %s" % (rc, json.dumps(request['message'])))
			
			elif request['topic'] == ManagedClient.UPDATE_LOCATION_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Location update action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Location update action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == ManagedClient.ADD_ERROR_CODE_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Add error code action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Add error code action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == ManagedClient.CLEAR_ERROR_CODES_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Clear error codes action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Clear error codes action failed: %s" % (rc, json.dumps(request['message'])))
			
			else:		
				self.logger.warning("[%s] Unknown action response: %s" % (rc, json.dumps(request['message'])))
			
			# Now clear the event, allowing anyone that was waiting on this to proceed
			request["event"].set()
			return True

	



def ParseConfigFile(configFilePath):
	parms = configparser.ConfigParser()
	sectionHeader = "device"
	try:
		with open(configFilePath) as f:
			try:
				parms.read_file(f)
				organization = parms.get(sectionHeader, "org", fallback=None)
				deviceType = parms.get(sectionHeader, "type", fallback=None)
				deviceId = parms.get(sectionHeader, "id", fallback=None)
				authMethod = parms.get(sectionHeader, "auth-method", fallback=None)
				authToken = parms.get(sectionHeader, "auth-token", fallback=None)
			except AttributeError:
				# Python 2.7 support
				# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_file
				parms.readfp(f)
				organization = parms.get(sectionHeader, "org", None)
				deviceType = parms.get(sectionHeader, "type", None)
				deviceId = parms.get(sectionHeader, "id", None)
				authMethod = parms.get(sectionHeader, "auth-method", None)
				authToken = parms.get(sectionHeader, "auth-token", None)
		
	except IOError as e:
		reason = "Error reading device configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ConfigurationException(reason)
		
	return {'org': organization, 'type': deviceType, 'id': deviceId, 'auth-method': authMethod, 'auth-token': authToken}
