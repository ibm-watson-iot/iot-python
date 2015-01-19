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
import ibmiotf
import re
import pytz
from datetime import datetime

# Support Python 2.7 and 3.4 versions of configparser
try:
	import configparser
except ImportError:
	import ConfigParser as configparser

COMMAND_RE = re.compile("iot-2/cmd/(.+)/fmt/(.+)")


class Command(ibmiotf.Message):
	def	__init__(self, message):
		result = COMMAND_RE.match(message.topic)
		if result:
			ibmiotf.Message.__init__(self, message)
			
			self.command = result.group(1)
			self.format = result.group(2)
		else:
			raise ibmiotf.InvalidEventException("Received command on invalid topic: %s" % (message.topic))


class Client(ibmiotf.AbstractClient):

	def __init__(self, options):
		self.__options = options

		if self.__options['org'] == None:
			raise ibmiotf.ConfigurationException("Missing required property: org")
		if self.__options['type'] == None: 
			raise ibmiotf.ConfigurationException("Missing required property: type")
		if self.__options['id'] == None: 
			raise ibmiotf.ConfigurationException("Missing required property: id")
		
		if self.__options['org'] != "quickstart":
			if self.__options['auth-method'] == None: 
				raise ibmiotf.ConfigurationException("Missing required property: auth-method")
				
			if (self.__options['auth-method'] == "token"):
				if self.__options['auth-token'] == None: 
					raise ibmiotf.ConfigurationException("Missing required property for token based authentication: auth-token")
			else:
				raise ibmiotf.UnsupportedAuthenticationMethod(options['authMethod'])


		ibmiotf.AbstractClient.__init__(
			self, 
			organization = options['org'],
			clientId = "d:" + options['org'] + ":" + options['type'] + ":" + options['id'], 
			username = "use-token-auth" if (options['auth-method'] == "token") else None,
			password = options['auth-token']
		)


		# Add handler for commands if not connected to QuickStart
		if self.__options['org'] != "quickstart":
			self.client.message_callback_add("iot-2/cmd/+/fmt/+", self.__onCommand)
		
		# Initialize user supplied callback
		self.commandCallback = None

		self.client.on_connect = self.on_connect

		#self.connect()
		
		
	
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
			if self.__options['org'] != "quickstart":
				self.__subscribeToCommands()
		elif rc == 5:
			self.__logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
		else:
			self.__logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))
	

	def publishEvent(self, event, data, qos=0):
		if not self.connectEvent.wait():
			self.logger.warning("Unable to send event %s because device is not currently connected")
			return False
		else:
			self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))
			topic = 'iot-2/evt/'+event+'/fmt/json'
			
			# Note: Python JSON serialization doesn't know what to do with a datetime object on it's own
			payload = { 'd' : data, 'ts': datetime.now(pytz.timezone('UTC')).isoformat() }
			self.client.publish(topic, payload=json.dumps(payload), qos=qos, retain=False)
			return True


	def __subscribeToCommands(self):
		if self.__options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support commands")
			return False
		
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to commands because device is not currently connected")
			return False
		else:
			topic = 'iot-2/cmd/+/fmt/json'
			self.client.subscribe(topic, qos=2)
			return True

	'''
	Internal callback for device command messages, parses source device from topic string and 
	passes the information on to the registerd device command callback
	'''
	def __onCommand(self, client, userdata, message):
		self.recv = self.recv + 1

		try:
			command = Command(message)
			self.logger.debug("Received command '%s'" % (command.command))
			if self.commandCallback: self.commandCallback(command)
		except ibmiotf.InvalidEventException as e:
			self.logger.critical(str(e))


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
		raise ibmiotf.ConfigurationException(reason)
		
	return {'org': organization, 'type': deviceType, 'id': deviceId, 'auth-method': authMethod, 'auth-token': authToken}
