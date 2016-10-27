# *****************************************************************************
# Copyright (c) 2014, 2015 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   David Parker - Initial Contribution
# *****************************************************************************

import os
import re
import json
import iso8601
import uuid
from datetime import datetime

from ibmiotf import HttpAbstractClient, ConnectionException, MissingMessageEncoderException
from ibmiotf.codecs import jsonIotfCodec
from ibmiotf.codecs import jsonCodec
import ibmiotf.api
import paho.mqtt.client as paho

import requests
# Support Python 2.7 and 3.4 versions of configparser
try:
	import configparser
except ImportError:
	import ConfigParser as configparser


# Compile regular expressions for topic parsing
DEVICE_EVENT_RE = re.compile("iot-2/type/(.+)/id/(.+)/evt/(.+)/fmt/(.+)")
DEVICE_COMMAND_RE = re.compile("iot-2/type/(.+)/id/(.+)/cmd/(.+)/fmt/(.+)")
DEVICE_STATUS_RE = re.compile("iot-2/type/(.+)/id/(.+)/mon")
APP_STATUS_RE = re.compile("iot-2/app/(.+)/mon")

class Status:
	def __init__(self, message):
		result = DEVICE_STATUS_RE.match(message.topic)
		if result:
			self.payload = json.loads(message.payload.decode("utf-8"))
			self.deviceType = result.group(1)
			self.deviceId = result.group(2)
			self.device = self.deviceType + ":" + self.deviceId

			'''
			Properties from the "Connect" status are common in "Disconnect" status too
			{
			u'ClientAddr': u'195.212.29.68',
			u'Protocol': u'mqtt-tcp',
			u'ClientID': u'd:bcaxk:psutil:001',
			u'User': u'use-token-auth',
			u'Time': u'2014-07-07T06:37:56.494-04:00',
			u'Action': u'Connect',
			u'ConnectTime': u'2014-07-07T06:37:56.493-04:00',
			u'Port': 1883
			}
			'''

			self.clientAddr = self.payload['ClientAddr'] if ('ClientAddr' in self.payload) else None
			self.protocol = self.payload['Protocol'] if ('Protocol' in self.payload) else None
			self.clientId = self.payload['ClientID'] if ('ClientID' in self.payload) else None
			self.user = self.payload['User'] if ('User' in self.payload) else None
			self.time = iso8601.parse_date(self.payload['Time']) if ('Time' in self.payload) else None
			self.action = self.payload['Action'] if ('Action' in self.payload) else None
			self.connectTime = iso8601.parse_date(self.payload['ConnectTime']) if ('ConnectTime' in self.payload) else None
			self.port = self.payload['Port'] if ('Port' in self.payload) else None

			'''
			Additional "Disconnect" status properties
			{
			u'WriteMsg': 0,
			u'ReadMsg': 872,
			u'Reason': u'The connection has completed normally.',
			u'ReadBytes': 136507,
			u'WriteBytes': 32,
			}
			'''
			self.writeMsg = self.payload['WriteMsg'] if ('WriteMsg' in self.payload) else None
			self.readMsg = self.payload['ReadMsg'] if ('ReadMsg' in self.payload) else None
			self.reason = self.payload['Reason'] if ('Reason' in self.payload) else None
			self.readBytes = self.payload['ReadBytes'] if ('ReadBytes' in self.payload) else None
			self.writeBytes = self.payload['WriteBytes'] if ('WriteBytes' in self.payload) else None

		else:
			raise ibmiotf.InvalidEventException("Received device status on invalid topic: %s" % (message.topic))


class Event:
	def __init__(self, pahoMessage, messageEncoderModules):
		result = DEVICE_EVENT_RE.match(pahoMessage.topic)
		if result:
			self.deviceType = result.group(1)
			self.deviceId = result.group(2)
			self.device = self.deviceType + ":" + self.deviceId

			self.event = result.group(3)
			self.format = result.group(4)

			self.payload = pahoMessage.payload

			if self.format in messageEncoderModules:
				message = messageEncoderModules[self.format].decode(pahoMessage)
				self.timestamp = message.timestamp
				self.data = message.data
			else:
				raise ibmiotf.MissingMessageDecoderException(self.format)
		else:
			raise ibmiotf.InvalidEventException("Received device event on invalid topic: %s" % (pahoMessage.topic))


class Command:
	def	__init__(self, pahoMessage, messageEncoderModules):
		result = DEVICE_COMMAND_RE.match(pahoMessage.topic)
		if result:
			self.deviceType = result.group(1)
			self.deviceId = result.group(2)
			self.device = self.deviceType + ":" + self.deviceId

			self.command = result.group(3)
			self.format = result.group(4)

			self.payload = pahoMessage.payload

			if self.format in messageEncoderModules:
				message = messageEncoderModules[self.format].decode(pahoMessage)
				self.timestamp = message.timestamp
				self.data = message.data
			else:
				raise ibmiotf.MissingMessageDecoderException(self.format)
		else:
			raise ibmiotf.InvalidEventException("Received device event on invalid topic: %s" % (pahoMessage.topic))


class Client(ibmiotf.AbstractClient):

	def __init__(self, options, logHandlers=None):
		self._options = options

		# If we are disconnected we lose all our active subscriptions.  Keep track of all subscriptions
		# so that we can internally restore all subscriptions on reconnect
		self._subscriptions = []

		username = None
		password = None

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
		if 'auth-key' not in self._options or self._options['auth-key'] is None:
			# Configure for Quickstart
			self._options['org'] = "quickstart"
		else:
			# Get the orgId from the apikey (format: a-orgid-randomness)
			self._options['org'] = self._options['auth-key'].split("-")[1]

			if 'auth-token' not in self._options or self._options['auth-token'] == None:
				raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

			username = self._options['auth-key']
			password = self._options['auth-token']

		# Generate an application ID if one is not supplied
		if 'id' not in self._options or self._options['id'] == None:
			self._options['id'] = str(uuid.uuid4())

		clientIdPrefix = "a" if ('type' not in self._options or self._options['type'] == 'standalone') else "A"

		# Call parent constructor
		ibmiotf.AbstractClient.__init__(
			self,
			domain = self._options['domain'],
			organization = self._options['org'],
			clientId = clientIdPrefix + ":" + self._options['org'] + ":" + self._options['id'],
			username = username,
			password = password,
			logHandlers = logHandlers,
			cleanSession = self._options['clean-session'],
			port = self._options['port']
		)

		# Add handlers for events and status
		self.client.message_callback_add("iot-2/type/+/id/+/evt/+/fmt/+", self.__onDeviceEvent)
		self.client.message_callback_add("iot-2/type/+/id/+/mon", self.__onDeviceStatus)
		self.client.message_callback_add("iot-2/app/+/mon", self.__onAppStatus)

		# Add handler for commands if not connected to QuickStart
		if self._options['org'] != "quickstart":
			self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self.__onDeviceCommand)

		# Attach fallback handler
		self.client.on_message = self.__onUnsupportedMessage

		# Initialize user supplied callbacks (devices)
		self.deviceEventCallback = None
		self.deviceCommandCallback = None
		self.deviceStatusCallback = None

		# Initialize user supplied callbacks (applcations)
		self.appStatusCallback = None

		self.client.on_connect = self.on_connect
		self.setMessageEncoderModule('json', jsonCodec)
		self.setMessageEncoderModule('json-iotf', jsonIotfCodec)

		# Create an api client if not connected in QuickStart mode
		if self._options['org'] != "quickstart":
			self.api = ibmiotf.api.ApiClient(self._options, self.logger)


		self.orgId = self._options['org']
		self.appId = self._options['id']

	'''
	This is called after the client has received a CONNACK message from the broker in response to calling connect().
	The parameter rc is an integer giving the return code:
	0: Success
	1: Refused - unacceptable protocol version
	2: Refused - identifier rejected
	3: Refused - server unavailable
	4: Refused - bad user name or password (MQTT v3.1 broker only)
	5: Refused - not authorised (MQTT v3.1 broker only)
	'''
	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.connectEvent.set()
			self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))

			# Restoring previous subscriptions
			if len(self._subscriptions) > 0:
				for subscription in self._subscriptions:
					self.client.subscribe(subscription["topic"], qos=subscription["qos"])
				self.logger.debug("Restored %s previous subscriptions" % len(self._subscriptions))

		elif rc == 5:
			self.logAndRaiseException(ConnectionException("Not authorized: (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


	def subscribeToDeviceEvents(self, deviceType="+", deviceId="+", event="+", msgFormat="+", qos=0):
		if self._options['org'] == "quickstart" and deviceId == "+":
			self.logger.warning("QuickStart applications do not support wildcard subscription to events from all devices")
			return False

		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to events (%s, %s, %s) because application is not currently connected" % (deviceType, deviceId, event))
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)
			self.client.subscribe(topic, qos=qos)
			self._subscriptions.append({"topic": topic, "qos": qos})
			return True


	def subscribeToDeviceStatus(self, deviceType="+", deviceId="+"):
		if self._options['org'] == "quickstart" and deviceId == "+":
			self.logger.warning("QuickStart applications do not support wildcard subscription to device status")
			return False

		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to device status (%s, %s) because application is not currently connected" % (deviceType, deviceId))
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/mon' % (deviceType, deviceId)
			self.client.subscribe(topic, qos=0)
			self._subscriptions.append({"topic": topic, "qos": 0})
			return True


	def subscribeToDeviceCommands(self, deviceType="+", deviceId="+", command="+", msgFormat="+"):
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support commands")
			return False

		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to commands (%s, %s, %s) because application is not currently connected" % (deviceType, deviceId, command))
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)
			self.client.subscribe(topic, qos=1)
			self._subscriptions.append({"topic": topic, "qos": 1})
			return True

	'''
	Publish an event in IoTF as if the application were a device.
	Parameters:
		deviceType - the type of the device this event is to be published from
		deviceId - the id of the device this event is to be published from
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
	def publishEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
		if not self.connectEvent.wait():
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)

			if msgFormat in self._messageEncoderModules:
				payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now())
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
	Publish a command to a device.
	Parameters:
		deviceType - the type of the device this command is to be published to
		deviceId - the id of the device this command is to be published to
		command - the name of the command
		msgFormat - the format of the command payload
		data - the command data
	Optional paramters:
		qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
		on_publish - a function that will be called when receipt of the publication is confirmed.  This
					 has different implications depending on the qos:
					 qos 0 - the client has asynchronously begun to send the event
					 qos 1 and 2 - the client has confirmation of delivery from IoTF
	'''
	def publishCommand(self, deviceType, deviceId, command, msgFormat, data=None, qos=0, on_publish=None):
		if self._options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support sending commands")
			return False
		if not self.connectEvent.wait():
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)

			if msgFormat in self._messageEncoderModules:
				payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now())
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
	Internal callback for messages that have not been handled by any of the specific internal callbacks, these
	messages are not passed on to any user provided callback
	'''
	def __onUnsupportedMessage(self, client, userdata, message):
		self.logger.warning("Received messaging on unsupported topic '%s' on topic '%s'" % (message.payload, message.topic))

		with self._recvLock:
			self.recv = self.recv + 1


	'''
	Internal callback for device event messages, parses source device from topic string and
	passes the information on to the registerd device event callback
	'''
	def __onDeviceEvent(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1

		try:
			event = Event(pahoMessage, self._messageEncoderModules)
			self.logger.debug("Received event '%s' from %s:%s" % (event.event, event.deviceType, event.deviceId))
			if self.deviceEventCallback: self.deviceEventCallback(event)
		except ibmiotf.InvalidEventException as e:
			self.logger.critical(str(e))


	'''
	Internal callback for device command messages, parses source device from topic string and
	passes the information on to the registerd device command callback
	'''
	def __onDeviceCommand(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1

		try:
			command = Command(pahoMessage, self._messageEncoderModules)
			self.logger.debug("Received command '%s' from %s:%s" % (command.command, command.deviceType, command.deviceId))
			if self.deviceCommandCallback: self.deviceCommandCallback(command)
		except ibmiotf.InvalidEventException as e:
			self.logger.critical(str(e))


	'''
	Internal callback for device status messages, parses source device from topic string and
	passes the information on to the registerd device status callback
	'''
	def __onDeviceStatus(self, client, userdata, pahoMessage):
		with self._recvLock:
			self.recv = self.recv + 1

		try:
			status = Status(pahoMessage)
			self.logger.debug("Received %s action from %s:%s" % (status.action, status.deviceType, status.deviceId))
			if self.deviceStatusCallback: self.deviceStatusCallback(status)
		except ibmiotf.InvalidEventException as e:
			self.logger.critical(str(e))


	'''
	Internal callback for application command messages, parses source application from topic string and
	passes the information on to the registerd applicaion status callback
	'''
	def __onAppStatus(self, client, userdata, message):
		with self._recvLock:
			self.recv = self.recv + 1

		statusMatchResult = self.__appStatusPattern.match(message.topic)
		if statusMatchResult:
			self.logger.debug("Received application status '%s' on topic '%s'" % (message.payload, message.topic))
			status = json.loads(str(message.payload))
			if self.appStatusCallback: self.appStatusCallback(statusMatchResult.group(1), status)
		else:
			self.logger.warning("Received application status on invalid topic: %s" % (message.topic))


class HttpClient(HttpAbstractClient):
	def __init__(self, options, logHandlers=None):
		self._options = options

		username = None
		password = None

		### DEFAULTS ###
		if "domain" not in self._options:
			# Default to the domain for the public cloud offering
			self._options['domain'] = "internetofthings.ibmcloud.com"
		if "clean-session" not in self._options:
		    self._options['clean-session'] = "true"

		### REQUIRED ###
		if self._options['type'] == None:
			raise ConfigurationException("Missing required property: type")
		if self._options['id'] == None:
			raise ConfigurationException("Missing required property: id")
		if 'auth-key' not in self._options or self._options['auth-key'] is None:
			# Configure for Quickstart
			self._options['org'] = "quickstart"
		else:
			# Get the orgId from the apikey (format: a-orgid-randomness)
			self._options['org'] = self._options['auth-key'].split("-")[1]

			if 'auth-token' not in self._options or self._options['auth-token'] == None:
				raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

			username = self._options['auth-key']
			password = self._options['auth-token']

		HttpAbstractClient.__init__(self,
		clientId = "httpAppClient:" + self._options['org'] + ":" + self._options['type'] + ":" + self._options['id'],
 		logHandlers = logHandlers)
		self.setMessageEncoderModule('json', jsonCodec)
		self.setMessageEncoderModule('json-iotf', jsonIotfCodec)


		# Create an api client if not connected in QuickStart mode
		if self._options['org'] != "quickstart":
			self.api = ibmiotf.api.ApiClient(self._options, self.logger)

		self.orgId = self._options['org']
		self.appId = self._options['id']

	def publishEvent(self, deviceType, deviceId, event, data):
		'''
		This method is used by the application to publish events over HTTP(s)
		It accepts 4 parameters, deviceType, deviceId, event which denotes event type and data which is the message to be posted
		It throws a ConnectionException with the message "Server not found" if the application is unable to reach the server
		Otherwise it returns the HTTP status code, (200 - 207 for success)
		'''
		self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))

		templateUrl = 'https://%s.messaging.%s/api/v0002/application/types/%s/devices/%s/events/%s'

		orgid = self._options['org']
		if orgid == 'quickstart':
			authKey = None
			authToken = None
		else:
			authKey = self._options['auth-key']
			authToken = self._options['auth-token']

		credentials = (authKey, authToken)
		#String replacement from template to actual URL
		intermediateUrl = templateUrl % (orgid, self._options['domain'], deviceType, deviceId, event)

		try:
			msgFormat = "json"
			payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now())
			response = requests.post(intermediateUrl, auth = credentials, data = payload, headers = {'content-type': 'application/json'})
		except Exception as e:
			self.logger.error("POST Failed")
			self.logger.error(e)
			raise ConnectionException("Server not found")

		if response.status_code >= 300:
			self.logger.warning(response.headers)
		return response.status_code


	def publishCommand(self, deviceType, deviceId, event, cmdData):
		'''
		This method is used by the application to publish device command over HTTP(s)
		It accepts 4 parameters, deviceType, deviceId, event which denotes event type
		and cmdData which is the command to be posted.
		It throws a ConnectionException with the message "Server not found" if the
		application is unable to reach the server, Otherwise it returns the
		HTTP status code, (200 - 207 for success)
		'''
		self.logger.debug("Sending event %s with command format %s" % (event, json.dumps(cmdData)))
		templateUrl = 'https://%s.messaging.%s/api/v0002/application/types/%s/devices/%s/commands/%s'
		orgid = self._options['org']
		if orgid == 'quickstart':
			authKey = None
			authToken = None
		else:
			authKey = self._options['auth-key']
			authToken = self._options['auth-token']
		credentials = (authKey, authToken)
		#String replacement from template to actual URL
		intermediateUrl = templateUrl % (orgid, self._options['domain'], deviceType, deviceId, event)
		try:
			cmdFormat = "json"
			payload = self._messageEncoderModules[cmdFormat].encode(cmdData, datetime.now())
			response = requests.post(intermediateUrl, auth = credentials, data = payload, headers = {'content-type': 'application/json'})
		except Exception as e:
			self.logger.error("POST Failed")
			self.logger.error(e)
			raise ConnectionException("Server not found")
		if response.status_code >= 300:
			self.logger.warning(response.headers)
		return response.status_code


def ParseConfigFile(configFilePath):
	'''
	Parse a standard application configuration file
	'''
	parms = configparser.ConfigParser({
		"id": str(uuid.uuid4()),
		"domain": "internetofthings.ibmcloud.com",
		"port": "8883",
		"type": "standalone",
		"clean-session": "true"
	})
	sectionHeader = "application"

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
		appId = parms.get(sectionHeader, "id")
		appType = parms.get(sectionHeader, "type")

		authKey = parms.get(sectionHeader, "auth-key")
		authToken = parms.get(sectionHeader, "auth-token")
		cleanSession = parms.get(sectionHeader, "clean-session")
		port = parms.get(sectionHeader, "port")

	except IOError as e:
		reason = "Error reading application configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ibmiotf.ConfigurationException(reason)

	return {'domain': domain, 'org': organization, 'id': appId, 'auth-key': authKey,
	        'auth-token': authToken, 'type': appType, 'clean-session': cleanSession, 'port': port}


def ParseConfigFromBluemixVCAP():
	# Bluemix VCAP lookups
	try:
		application = json.loads(os.getenv('VCAP_APPLICATION'))
		service = json.loads(os.getenv('VCAP_SERVICES'))

		# For now, this method only supports the public cloud offering registered in public Bluemix
		domain = "internetofthings.ibmcloud.com"

		appId = application['application_name'] + "-" + str(application['instance_index'])
		appType = "standalone"

		authKey = service['iotf-service'][0]['credentials']['apiKey']
		authToken = service['iotf-service'][0]['credentials']['apiToken']

		return {'domain': domain, 'id': appId, 'auth-key': authKey, 'auth-token': authToken, 'type': appType}
	except Exception as e:
		raise ibmiotf.ConfigurationException(str(e))
