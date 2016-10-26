# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Amit M Mangalvedkar  - Initial Contribution
#   Lokesh K Haralakatta - Added API Support for Gateway
# *****************************************************************************

import json
import re
import pytz
import uuid
import threading
import requests
import logging
import paho.mqtt.client as paho

from datetime import datetime

from ibmiotf import AbstractClient, InvalidEventException, UnsupportedAuthenticationMethod,ConfigurationException, ConnectionException, MissingMessageEncoderException,MissingMessageDecoderException
from ibmiotf.codecs import jsonCodec, jsonIotfCodec
from ibmiotf import api

# Support Python 2.7 and 3.4 versions of configparser
try:
	import configparser
except ImportError:
	import ConfigParser as configparser

COMMAND_RE = re.compile("iot-2/type/(.+)/id/(.+)/cmd/(.+)/fmt/(.+)")


class Command:
	def __init__(self, pahoMessage, messageEncoderModules):
		result = COMMAND_RE.match(pahoMessage.topic)
		if result:
			self.type = result.group(1)
			self.id = result.group(2)
			self.command = result.group(3)
			self.format = result.group(4)

			if self.format in messageEncoderModules:
				message = messageEncoderModules[self.format].decode(pahoMessage)
				self.timestamp = message.timestamp
				self.data = message.data
			else:
				raise MissingMessageDecoderException(self.format)
		else:
			raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))


class Client(AbstractClient):

	COMMAND_TOPIC = "iot-2/type/+/id/+/cmd/+/fmt/+"

	def __init__(self, options, logHandlers=None):
		self._options = options

		#Defaults
		if "domain" not in self._options:
			# Default to the domain for the public cloud offering
			self._options['domain'] = "internetofthings.ibmcloud.com"

		if "org" not in self._options:
			# Default to the quickstart ode
			self._options['org'] = "quickstart"

		if "clean-session" not in self._options:
			self._options['clean-session'] = "true"

		if "port" not in self._options and self._options["org"] != "quickstart":
			self._options["port"] = 8883;

		if self._options["org"] == "quickstart":
			self._options["port"] = 1883;

		#Check for any missing required properties
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
		self._options['subscriptionList'] = {}

		AbstractClient.__init__(
			self,
			domain = self._options['domain'],
			organization = self._options['org'],
			clientId = "g:" + self._options['org'] + ":" + self._options['type'] + ":" + self._options['id'],
			username = "use-token-auth" if (self._options['auth-method'] == "token") else None,
			password = self._options['auth-token'],
			logHandlers = logHandlers,
			port = self._options['port']
		)


		# Add handler for commands if not connected to QuickStart
		if self._options['org'] != "quickstart":
			gatewayCommandTopic = "iot-2/type/" + options['type'] + "/id/" + options['id'] + "/cmd/+/fmt/json"
			messageNotificationTopic = "iot-2/type/" + options['type'] + "/id/" + options['id'] + "/notify"
			#localTopic = "iot-2/type/iotsample-raspberrypi2/id/89898889/cmd/greeting/fmt/json"
			self.client.message_callback_add(gatewayCommandTopic, self.__onCommand)
			self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self.__onDeviceCommand)
			self.client.message_callback_add(messageNotificationTopic, self.__onMessageNotification)


		self.subscriptionsAcknowledged = threading.Event()

		# Initialize user supplied callback
		self.commandCallback = None
		self.deviceCommandCallback = None
		self.notificationCallback = None
		self.client.on_connect = self.on_connect
		self.setMessageEncoderModule('json', jsonCodec)
		self.setMessageEncoderModule('json-iotf', jsonIotfCodec)

		# Create api key for gateway authentication
		self.gatewayApiKey = "g/" + self._options['org'] + '/' + self._options['type'] + '/' + self._options['id']
		self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
		self.logger.setLevel(logging.INFO)
		self.apiClient = api.ApiClient({"org": self._options['org'], "auth-token": self._options['auth-token'], "auth-key": self.gatewayApiKey },self.logger)

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
			#if self._options['org'] != "quickstart":
				#self.subscribeToGatewayCommands()
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


	'''
	Publish an event in Watson IoT.
	Parameters:
		event - the name of this event
		msgFormat - the format of the data for this event
		data - the data for this event
		deviceType - the device type of the device on the behalf of which the gateway is publishing the event

	Optional paramters:
		qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
		on_publish - a function that will be called when receipt of the publication is confirmed.  This
					 has different implications depending on the qos:
					 qos 0 - the client has asynchronously begun to send the event
					 qos 1 and 2 - the client has confirmation of delivery from Watson IoT
	'''
	def publishDeviceEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
		if not self.connectEvent.wait():
			self.logger.warning("Unable to send event %s because gateway as a device is not currently connected")
			return False
		else:
			self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))
			topic = 'iot-2/type/' + deviceType + '/id/' + deviceId +'/evt/'+event+'/fmt/' + msgFormat

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
	Publish an event in Watson IoT as a device.
	Parameters:
		event - the name of this event
		msgFormat - the format of the data for this event
		data - the data for this event
	Optional paramters:
		qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
		on_publish - a function that will be called when receipt of the publication is confirmed.  This
					 has different implications depending on the qos:
					 qos 0 - the client has asynchronously begun to send the event
					 qos 1 and 2 - the client has confirmation of delivery from Watson IoT
	'''
	def publishGatewayEvent(self, event, msgFormat, data, qos=0, on_publish=None):
		gatewayType = self._options['type']
		gatewayId = self._options['id']

		if not self.connectEvent.wait():
			self.logger.warning("Unable to send event %s because gateway as a device is not currently connected")
			return False
		else:
			self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))
			topic = 'iot-2/type/' + gatewayType + '/id/' + gatewayId +'/evt/'+event+'/fmt/' + msgFormat

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


	def subscribeToDeviceCommands(self, deviceType, deviceId, command='+', format='json', qos=1):
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart not supported in Gateways")
			return False

		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to device commands because gateway is not currently connected")
			return False
		else:
			topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
			self.client.subscribe(topic, qos=qos)
			self._options['subscriptionList'][topic] = qos
			return True



	def subscribeToGatewayCommands(self, command='+', format='json', qos=1):
		deviceType = self._options['type']
		deviceId = self._options['id']
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart not supported in Gateways")
			return False
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to gateway commands because gateway is not currently connected")
			return False
		else:
			topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
			self.client.subscribe(topic)
			self._options['subscriptionList'][topic] = qos
			return True


	def subscribeToGatewayNotifications(self):
		deviceType = self._options['type']
		deviceId = self._options['id']
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart not supported in Gateways")
			return False
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to notifications because gateway is not currently connected")
			return False
		else:
			topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/notify'
			self.client.subscribe(topic)
			#self._options['subscriptionList'][topic] = qos
			return True


	'''
	Internal callback for device command messages, parses source device from topic string and
	passes the information on to the registered device command callback
	'''
	def __onCommand(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1
		try:
			command = Command(pahoMessage, self._messageEncoderModules)
		except InvalidEventException as e:
			self.logger.critical(str(e))
		else:
			self.logger.debug("Received device command '%s'" % (command.command))
			if self.commandCallback: self.commandCallback(command)

	'''
	Internal callback for gateway command messages, parses source device from topic string and
	passes the information on to the registered device command callback
	'''
	def __onDeviceCommand(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1
		try:
			command = Command(pahoMessage, self._messageEncoderModules)
		except InvalidEventException as e:
			self.logger.critical(str(e))
		else:
			self.logger.debug("Received gateway command '%s'" % (command.command))
			if self.deviceCommandCallback: self.deviceCommandCallback(command)

	'''
	Internal callback for gateway notification messages, parses source device from topic string and
	passes the information on to the registered device command callback
	'''
	def __onMessageNotification(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1
		try:
			command = Command(pahoMessage, self._messageEncoderModules)
		except InvalidEventException as e:
			self.logger.critical(str(e))
		else:
			self.logger.debug("Received Notification '%s'" % (command.command))
			if self.notificationCallback: self.notificationCallback(command)



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


class ManagedGateway(Client):

	# Publish MQTT topics
	'''
	MANAGE_TOPIC = 'iotdevice-1/mgmt/manage'
	UNMANAGE_TOPIC = 'iotdevice-1/mgmt/unmanage'
	UPDATE_LOCATION_TOPIC = 'iotdevice-1/device/update/location'
	ADD_ERROR_CODE_TOPIC = 'iotdevice-1/add/diag/errorCodes'
	CLEAR_ERROR_CODES_TOPIC = 'iotdevice-1/clear/diag/errorCodes'
	NOTIFY_TOPIC = 'iotdevice-1/notify'

	# Subscribe MQTT topics
	DM_RESPONSE_TOPIC = 'iotdm-1/response'
	DM_OBSERVE_TOPIC = 'iotdm-1/observe'
	'''

	MANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/manage'
	UNMANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/unmanage'
	UPDATE_LOCATION_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/device/update/location'
	ADD_ERROR_CODE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/add/diag/errorCodes'
	CLEAR_ERROR_CODES_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/clear/diag/errorCodes'
	NOTIFY_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/notify'

	# Subscribe MQTT topics
	DM_RESPONSE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/response'
	DM_OBSERVE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/observe'

	def __init__(self, options, logHandlers=None, deviceInfo=None):
		if options['org'] == "quickstart":
			raise Exception("Unable to create ManagedGateway instance.  QuickStart devices do not support device management")

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

		self._gatewayType = self._options['type']
		self._gatewayId = self._options['id']


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
					self.logger.warning("Unable to notify service of field change because gateway is not ready for gateway management")
					return threading.Event().set()

				reqId = str(uuid.uuid4())
				message = {
					"d": {
						"field": field,
						"value": value
					},
					"reqId": reqId
				}

				notify_topic = ManagedGateway.NOTIFY_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
				resolvedEvent = threading.Event()

				self.client.publish(notify_topic, payload=json.dumps(message), qos=1, retain=False)
				with self._deviceMgmtRequestsPendingLock:
					self._deviceMgmtRequestsPending[reqId] = {"topic": notify_topic, "message": message, "event": resolvedEvent}

				return resolvedEvent
			else:
				return threading.Event().set()

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.connectEvent.set()
			self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))
			if self._options['org'] != "quickstart":
				dm_response_topic = ManagedGateway.DM_RESPONSE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
				dm_observe_topic = ManagedGateway.DM_OBSERVE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
				self.client.subscribe( [(dm_response_topic, 1), (dm_observe_topic, 1), (Client.COMMAND_TOPIC, 1)] )
		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


	def on_subscribe(self, client, userdata, mid, granted_qos):
		# Once Watson IoT acknowledges the subscriptions we are able to process commands and responses from device management server
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

		manage_topic = ManagedGateway.MANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
		resolvedEvent = threading.Event()

		self.client.publish(manage_topic, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": manage_topic, "message": message, "event": resolvedEvent}

		# Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
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

		unmanage_topic = ManagedGateway.UNMANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
		resolvedEvent = threading.Event()

		self.client.publish(unmanage_topic, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": unmanage_topic, "message": message, "event": resolvedEvent}

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

		update_location_topic = ManagedGateway.UPDATE_LOCATION_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
		resolvedEvent = threading.Event()

		self.client.publish(update_location_topic, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": update_location_topic, "message": message, "event": resolvedEvent}

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

		add_error_code_topic = ManagedGateway.ADD_ERROR_CODE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
		resolvedEvent = threading.Event()

		self.client.publish(add_error_code_topic, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": add_error_code_topic, "message": message, "event": resolvedEvent}

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

		clear_error_codes_topic = ManagedGateway.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
		resolvedEvent = threading.Event()

		self.client.publish(clear_error_codes_topic, payload=json.dumps(message), qos=1, retain=False)
		with self._deviceMgmtRequestsPendingLock:
			self._deviceMgmtRequestsPending[reqId] = {"topic": clear_error_codes_topic, "message": message, "event": resolvedEvent}

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

			manage_topic = ManagedGateway.MANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
			unmanage_topic = ManagedGateway.UNMANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
			update_location_topic = ManagedGateway.UPDATE_LOCATION_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
			add_error_code_topic = ManagedGateway.ADD_ERROR_CODE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
			clear_error_codes_topic = ManagedGateway.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)

			if request['topic'] == manage_topic:
				if rc == 200:
					self.logger.info("[%s] Manage action completed: %s" % (rc, json.dumps(request['message'])))
					self.readyForDeviceMgmt.set()
				else:
					self.logger.critical("[%s] Manage action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == unmanage_topic:
				if rc == 200:
					self.logger.info("[%s] Unmanage action completed: %s" % (rc, json.dumps(request['message'])))
					self.readyForDeviceMgmt.clear()
				else:
					self.logger.critical("[%s] Unmanage action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == update_location_topic:
				if rc == 200:
					self.logger.info("[%s] Location update action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Location update action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == add_error_code_topic:
				if rc == 200:
					self.logger.info("[%s] Add error code action completed: %s" % (rc, json.dumps(request['message'])))
				else:
					self.logger.critical("[%s] Add error code action failed: %s" % (rc, json.dumps(request['message'])))

			elif request['topic'] == clear_error_codes_topic:
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
	parms = configparser.ConfigParser({"domain": "internetofthings.ibmcloud.com",
	                                   "port": "8883","clean-session": "true"})
	sectionHeader = "device"
	try:
		with open(configFilePath) as f:
			try:
				parms.read_file(f)

				domain = parms.get(sectionHeader, "domain", fallback="internetofthings.ibmcloud.com")
				organization = parms.get(sectionHeader, "org", fallback=None)
				deviceType = parms.get(sectionHeader, "type", fallback=None)
				deviceId = parms.get(sectionHeader, "id", fallback=None)
				authMethod = parms.get(sectionHeader, "auth-method", fallback=None)
				authToken = parms.get(sectionHeader, "auth-token", fallback=None)
				cleanSession = parms.get(sectionHeader, "clean-session")
				port = parms.get(sectionHeader, "port")
			except AttributeError:
				# Python 2.7 support
				# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_file
				parms.readfp(f)

				domain = parms.get(sectionHeader, "domain", "internetofthings.ibmcloud.com")
				organization = parms.get(sectionHeader, "org", None)
				deviceType = parms.get(sectionHeader, "type", None)
				deviceId = parms.get(sectionHeader, "id", None)
				authMethod = parms.get(sectionHeader, "auth-method", None)
				authToken = parms.get(sectionHeader, "auth-token", None)
				cleanSession = parms.get(sectionHeader, "clean-session",None)
				port = parms.get(sectionHeader, "port",None)

	except IOError as e:
		reason = "Error reading gateway configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ConfigurationException(reason)

	return {'domain': domain, 'org': organization, 'type': deviceType, 'id': deviceId,
	    	'auth-method': authMethod, 'auth-token': authToken,
			'clean-session': cleanSession, 'port': port}
