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
#   Lokesh Haralakatta - Added DME Support
# *****************************************************************************

import json
import re
import pytz
import uuid
import threading
import requests
import paho.mqtt.client as paho

from datetime import datetime

from ibmiotf import AbstractClient, HttpAbstractClient, InvalidEventException, UnsupportedAuthenticationMethod,ConfigurationException, ConnectionException, MissingMessageEncoderException,MissingMessageDecoderException
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

		### DEFAULTS ###
		if "domain" not in self._options:
			# Default to the domain for the public cloud offering
			self._options['domain'] = "internetofthings.ibmcloud.com"
		if "clean-session" not in self._options:
			self._options['clean-session'] = "true"

		if "org" not in self._options:
			# Default to the quickstart
			self._options['org'] = "quickstart"

		if "port" not in self._options and self._options["org"] != "quickstart":
			self._options["port"] = 8883;

		if self._options["org"] == "quickstart":
			self._options["port"] = 1883;

		### REQUIRED ###
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
				raise UnsupportedAuthenticationMethod(options['auth-method'])

		AbstractClient.__init__(
			self,
			domain = self._options['domain'],
			organization = self._options['org'],
			clientId = "d:" + self._options['org'] + ":" + self._options['type'] + ":" + self._options['id'],
			username = "use-token-auth" if (self._options['auth-method'] == "token") else None,
			password = self._options['auth-token'],
			logHandlers = logHandlers,
			cleanSession = self._options['clean-session'],
			port = self._options['port']
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


	def on_connect(self, client, userdata, flags, rc):
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
		if rc == 0:
			self.connectEvent.set()
			self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))
			if self._options['org'] != "quickstart":
				self.__subscribeToCommands()
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))

	def publishEvent(self, event, msgFormat, data, qos=0, on_publish=None):
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


	def __subscribeToCommands(self):
		'''
		Subscribe to commands sent to this device.
		'''
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support commands")
			return False

		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to commands because device is not currently connected")
			return False
		else:
			self.client.subscribe(Client.COMMAND_TOPIC, qos=1)
			return True

	def __onCommand(self, client, userdata, pahoMessage):
		'''
		Internal callback for device command messages, parses source device from topic string and
		passes the information on to the registerd device command callback
		'''
		with self._recvLock:
			self.recv = self.recv + 1
		try:
			command = Command(pahoMessage, self._messageEncoderModules)
		except InvalidEventException as e:
			self.logger.critical(str(e))
		else:
			self.logger.debug("Received command '%s'" % (command.command))
			if self.commandCallback: self.commandCallback(command)


class HttpClient(HttpAbstractClient):
	"""
	A basic device client with limited capabilies that forgoes an active MQTT connection to the service.
	"""

	def __init__(self, options, logHandlers=None):
		self._options = options

		### DEFAULTS ###
		if "domain" not in self._options:
			# Default to the domain for the public cloud offering
			self._options['domain'] = "internetofthings.ibmcloud.com"
		if "clean-session" not in self._options:
			self._options['clean-session'] = "true"

		### REQUIRED ###
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

		HttpAbstractClient.__init__(self,
		clientId = "httpDevClient:" + self._options['org'] + ":" + self._options['type'] + ":" + self._options['id'],
 		logHandlers = logHandlers)
		self.setMessageEncoderModule('json', jsonCodec)



	def publishEvent(self, event, data):
		"""
		Publish an event over HTTP(s) as JSON
		Throws a ConnectionException with the message "Server not found" if the client is unable to reach the server
		Otherwise it returns the HTTP status code, (200 - 207 for success)
		"""
		self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))

		templateUrl = 'https://%s.messaging.%s/api/v0002/device/types/%s/devices/%s/events/%s'

		orgid = self._options['org']
		deviceType = self._options['type']
		deviceId = self._options['id']
		authMethod = "use-token-auth"
		authToken = self._options['auth-token']
		credentials = (authMethod, authToken)

		if orgid == 'quickstart':
			authMethod = None
			authToken = None

		intermediateUrl = templateUrl % (orgid, self._options['domain'], deviceType, deviceId, event)
		self.logger.debug("URL: %s",intermediateUrl)
		try:
			msgFormat = "json"
			payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now(pytz.timezone('UTC')))
			response = requests.post(intermediateUrl, auth = credentials, data = payload, headers = {'content-type': 'application/json'})
		except Exception as e:
			self.logger.error("POST Failed")
			self.logger.error(e)
			raise ConnectionException("Server not found")

		if response.status_code >= 300:
			self.logger.warning(response.headers)
		return response.status_code



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


class DeviceFirmware(object):
	def __init__(self,version = None,name = None,url = None,verifier = None,state = None,updateStatus = None,updatedDateTime = None):
		self.version = version
		self.name = name
		self.url = url
		self.verifier = verifier
		self.state = state
		self.updateStatus = updateStatus
		self.updatedDateTime = updatedDateTime

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
	RESPONSE_TOPIC = 'iotdevice-1/response'
	ADD_LOG_TOPIC = 'iotdevice-1/add/diag/log'
	CLEAR_LOG_TOPIC = 'iotdevice-1/clear/diag/log'

	# Subscribe MQTT topics
	DM_RESPONSE_TOPIC = 'iotdm-1/response'
	DM_OBSERVE_TOPIC = 'iotdm-1/observe'
	DM_REBOOT_TOPIC = 'iotdm-1/mgmt/initiate/device/reboot'
	DM_FACTORY_REESET ='iotdm-1/mgmt/initiate/device/factory_reset'
	DM_UPDATE_TOPIC = 'iotdm-1/device/update'
	DM_CANCEL_OBSERVE_TOPIC = 'iotdm-1/cancel'
	DM_FIRMWARE_DOWNLOAD_TOPIC = 'iotdm-1/mgmt/initiate/firmware/download'
	DM_FIRMWARE_UPDATE_TOPIC = 'iotdm-1/mgmt/initiate/firmware/update'
	DME_ACTION_TOPIC = 'iotdm-1/mgmt/custom/#'

	#ResponceCode
	RESPONSECODE_FUNCTION_NOT_SUPPORTED = 501
	RESPONSECODE_ACCEPTED = 202
	RESPONSECODE_INTERNAL_ERROR = 500
	RESPONSECODE_BAD_REQUEST = 400

	UPDATESTATE_IDLE = 0
	UPDATESTATE_DOWNLOADING = 1
	UPDATESTATE_DOWNLOADED = 2
	UPDATESTATE_SUCCESS = 0
	UPDATESTATE_IN_PROGRESS = 1
	UPDATESTATE_OUT_OF_MEMORY = 2
	UPDATESTATE_CONNECTION_LOST = 3
	UPDATESTATE_VERIFICATION_FAILED = 4
	UPDATESTATE_UNSUPPORTED_IMAGE = 5
	UPDATESTATE_INVALID_URI = 6


	def __init__(self, options, logHandlers=None, deviceInfo=None):
		if options['org'] == "quickstart":
			raise Exception("Unable to create ManagedClient instance.  QuickStart devices do not support device management")

		Client.__init__(self, options, logHandlers)
		# TODO: Raise fatal exception if tries to create managed device client for QuickStart

		# Initialize user supplied callback
		self.deviceActionCallback = None
		self.firmwereActionCallback  = None
		self.dmeActionCallback = None

		# Add handler for supported device management commands
		self.client.message_callback_add("iotdm-1/#", self.__onDeviceMgmtResponse)
		self.client.message_callback_add(ManagedClient.DM_REBOOT_TOPIC, self.__onRebootRequest)
		self.client.message_callback_add(ManagedClient.DM_FACTORY_REESET, self.__onFactoryResetRequest)
		self.client.message_callback_add(ManagedClient.DM_FIRMWARE_UPDATE_TOPIC,self.__onFirmwereUpdate)
		self.client.message_callback_add(ManagedClient.DM_OBSERVE_TOPIC,self.__onFirmwereObserve)
		self.client.message_callback_add(ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC,self.__onFirmwereDownload)
		self.client.message_callback_add(ManagedClient.DM_UPDATE_TOPIC,self.__onUpdatedDevice)
		self.client.message_callback_add(ManagedClient.DM_CANCEL_OBSERVE_TOPIC,self.__onFirmwereCancel)
		self.client.message_callback_add(ManagedClient.DME_ACTION_TOPIC,self.__onDMEActionRequest)

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
		self.__firmwareUpdate = None

		self.manageTimer = None

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
			self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))
			if self._options['org'] != "quickstart":
				self.client.subscribe( [(ManagedClient.DM_RESPONSE_TOPIC, 1), (ManagedClient.DM_OBSERVE_TOPIC, 1),
				(ManagedClient.DM_REBOOT_TOPIC,1),(ManagedClient.DM_FACTORY_REESET,1),(ManagedClient.DM_UPDATE_TOPIC,1),
				(ManagedClient.DM_FIRMWARE_UPDATE_TOPIC,1),(ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC,1),
				(ManagedClient.DM_CANCEL_OBSERVE_TOPIC,1),(Client.COMMAND_TOPIC, 1),(ManagedClient.DME_ACTION_TOPIC,1)] )
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


	def on_subscribe(self, client, userdata, mid, granted_qos):
		# Once IoTF acknowledges the subscriptions we are able to process commands and responses from device management server
		self.subscriptionsAcknowledged.set()
		self.manage()


	def manage(self, lifetime=3600, supportDeviceActions=True, supportFirmwareActions=True,
					supportDeviceMgmtExtActions=False, bundleIds=[]):
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
											"firmwareActions": supportFirmwareActions,
										},
							"deviceInfo" : self._deviceInfo.__dict__,
							"metadata" : self.metadata
						},
					'reqId': reqId
				}
		if supportDeviceMgmtExtActions and len(bundleIds) > 0:
			for bundleId in bundleIds:
				message['d']['supports'][bundleId] = supportDeviceMgmtExtActions

		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.MANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.MANAGE_TOPIC, "message": message, "event": resolvedEvent}

		# Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
		if lifetime != 0:
			if self.manageTimer is not None:
				self._logger.debug("Cancelling existing manage timer")
				self.manageTimer.cancel()
			self.manageTimer = threading.Timer(lifetime-120, self.manage,
		    [lifetime, supportDeviceActions, supportFirmwareActions, supportDeviceMgmtExtActions, bundleIds]).start()

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

	def addLog(self, msg="",data="",sensitivity=0):
		timestamp = datetime.now().isoformat()
		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to publish error code because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			"d": {
				"message": msg,
                "timestamp": timestamp,
                "data": data,
                "severity": sensitivity
                 },
			"reqId": reqId
		}

		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.ADD_LOG_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.ADD_LOG_TOPIC, "message": message, "event": resolvedEvent}

		return resolvedEvent

	def clearLog(self):

		if not self.readyForDeviceMgmt.wait():
			self.logger.warning("Unable to clear log because device is not ready for device management")
			return threading.Event().set()

		reqId = str(uuid.uuid4())
		message = {
			"reqId": reqId
		}

		resolvedEvent = threading.Event()
		self.client.publish(ManagedClient.CLEAR_LOG_TOPIC, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.CLEAR_LOG_TOPIC, "message": message, "event": resolvedEvent}

		return resolvedEvent


	def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):

		with self._recvLock:
			self.recv = self.recv + 1

		try:
			data = json.loads(pahoMessage.payload.decode("utf-8"))
			if 'rc' not in data:
				return True
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

			elif request['topic'] == ManagedClient.ADD_LOG_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Add log action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Add log action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == ManagedClient.CLEAR_LOG_TOPIC:
				if rc == 200:
					self.logger.info("[%s] Clear log action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Clear log action failed: %s" % (rc, json.dumps(request['message'])))
			else:
				self.logger.warning("[%s] Unknown action response: %s" % (rc, json.dumps(request['message'])))

			# Now clear the event, allowing anyone that was waiting on this to proceed
			request["event"].set()
			return True

	#Device Action Handlers
	def __onRebootRequest(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_REBOOT_TOPIC,pahoMessage.payload.decode("utf-8")))
		try:
			data = json.loads(pahoMessage.payload.decode("utf-8"))
			reqId = data['reqId']
			if self.deviceActionCallback : self.deviceActionCallback(reqId,"reboot")
		except ValueError as e:
			raise Exception("Unable to process Reboot request.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))

	def __onFactoryResetRequest(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_FACTORY_REESET,pahoMessage.payload.decode("utf-8")))
		try:
			data = json.loads(pahoMessage.payload.decode("utf-8"))
			reqId = data['reqId']
			if self.deviceActionCallback : self.deviceActionCallback(reqId,"reset")
		except ValueError as e:
			raise Exception("Unable to process Factory Reset request.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))

	def respondDeviceAction(self,reqId,responseCode=202,message=""):
		response ={
				        "rc": responseCode,
				        "message": message,
				        "reqId": reqId
				}
		payload=json.dumps(response)
		self.logger.info("Publishing Device Action response with payload :%s" % payload)
		self.client.publish('iotdevice-1/response', payload,qos=1, retain=False)

	#Firmware Handlers
	def __onFirmwereDownload(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC,pahoMessage.payload.decode("utf-8")))
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		reqId = data['reqId']
		rc = ManagedClient.RESPONSECODE_ACCEPTED
		msg =""
		if self.__firmwareUpdate.state != ManagedClient.UPDATESTATE_IDLE :
			rc = ManagedClient.RESPONSECODE_BAD_REQUEST
			msg = "Cannot download as the device is not in idle state"
		threading.Thread(target= self.respondDeviceAction,args=(reqId,rc,msg)).start()
		if self.firmwereActionCallback :
			self.firmwereActionCallback("download",self.__firmwareUpdate)


	def __onFirmwereCancel(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_CANCEL_OBSERVE_TOPIC,pahoMessage.payload.decode("utf-8")))
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		reqId = data['reqId']
		threading.Thread(target= self.respondDeviceAction,args=(reqId,200,"")).start()

	def __onFirmwereObserve(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_OBSERVE_TOPIC,pahoMessage.payload.decode("utf-8")))
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		reqId = data['reqId']
		#TODO : Proprer validation for fields in payload
		threading.Thread(target= self.respondDeviceAction,args=(reqId,200,"")).start()

	def __onUpdatedDevice(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_UPDATE_TOPIC,pahoMessage.payload.decode("utf-8")))
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		reqId = data['reqId']
		d=data['d']
		value = None
		for obj in d['fields'] :
			if 'field' in obj :
				if obj['field'] == "mgmt.firmware" :
					value = obj["value"]
		if value != None :
			self.__firmwareUpdate = DeviceFirmware(value['version'],value['name'],value['uri'],value['verifier'],value['state'],value['updateStatus'],value['updatedDateTime'])
		threading.Thread(target= self.respondDeviceAction,args=(reqId,204,"")).start()

	def setState(self,status):
		notify = {"d":{"fields":[{"field":"mgmt.firmware","value":{"state":status}}]}}
		if self.__firmwareUpdate != None :
			self.__firmwareUpdate.state = status

		self.logger.info("Publishing state Update with payload :%s" % json.dumps(notify))
		threading.Thread(target= self.client.publish,args=('iotdevice-1/notify',json.dumps(notify),1, False)).start()

	def setUpdateStatus(self,status):
		notify = {"d":{"fields":[{"field":"mgmt.firmware","value":{"state":ManagedClient.UPDATESTATE_IDLE,"updateStatus":status}}]}}
		if self.__firmwareUpdate != None :
			self.__firmwareUpdate.state = ManagedClient.UPDATESTATE_IDLE
			self.__firmwareUpdate.updateStatus = status

		self.logger.info("Publishing  Update Status  with payload :%s" % json.dumps(notify))
		threading.Thread(target= self.client.publish,args=('iotdevice-1/notify',json.dumps(notify),1, False)).start()

	def __onFirmwereUpdate(self,client,userdata,pahoMessage):
		self.logger.info("Message received on topic :%s with payload %s" % (ManagedClient.DM_FIRMWARE_UPDATE_TOPIC,pahoMessage.payload.decode("utf-8")))
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		reqId = data['reqId']
		rc = ManagedClient.RESPONSECODE_ACCEPTED
		msg =""
		if self.__firmwareUpdate.state != ManagedClient.UPDATESTATE_DOWNLOADED :
			rc = ManagedClient.RESPONSECODE_BAD_REQUEST
			msg = "Firmware is still not successfully downloaded."
		threading.Thread(target= self.respondDeviceAction,args=(reqId,rc,msg)).start()
		if self.firmwereActionCallback :
			self.firmwereActionCallback("update",self.__firmwareUpdate)

	def __onDMEActionRequest(self,client,userdata,pahoMessage):
		data = json.loads(pahoMessage.payload.decode("utf-8"))
		self.logger.info("Message received on topic :%s with payload %s"
		      % (ManagedClient.DME_ACTION_TOPIC,data))
		reqId = data['reqId']
		if self.dmeActionCallback :
			if self.dmeActionCallback(pahoMessage.topic,data,reqId):
				msg = "DME Action successfully completed from Callback"
				threading.Thread(target= self.respondDeviceAction,args=(reqId,200,msg)).start()
			else:
				msg = "Unexpected device error"
				threading.Thread(target= self.respondDeviceAction,args=(reqId,500,msg)).start()

		else :
			threading.Thread(target= self.respondDeviceAction,args=(reqId,501,"Operation not implemented")).start()


def ParseConfigFile(configFilePath):
	parms = configparser.ConfigParser({"domain": "internetofthings.ibmcloud.com",
	                                   "port": "8883","clean-session": "true"})
	sectionHeader = "device"
	try:
		with open(configFilePath) as f:
			try:
				parms.read_file(f)
			except AttributeError:
				# Python 2.7 support
				# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_file
				parms.readfp(f)

		domain = parms.get(sectionHeader, "domain")
		organization = parms.get(sectionHeader, "org")
		deviceType = parms.get(sectionHeader, "type")
		deviceId = parms.get(sectionHeader, "id")
		authMethod = parms.get(sectionHeader, "auth-method")
		authToken = parms.get(sectionHeader, "auth-token")
		cleanSession = parms.get(sectionHeader, "clean-session")
		port = parms.get(sectionHeader, "port")

	except IOError as e:
		reason = "Error reading device configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ConfigurationException(reason)

	return {'domain': domain, 'org': organization, 'type': deviceType,
	        'id': deviceId, 'auth-method': authMethod, 'auth-token': authToken,
			'clean-session': cleanSession, 'port': port}
