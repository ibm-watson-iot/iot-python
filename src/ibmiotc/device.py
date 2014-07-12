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
import ibmiotc
import ConfigParser
import re
from datetime import datetime


COMMAND_RE = re.compile("iot-2/cmd/(.+)/fmt/(.+)")


class Command(ibmiotc.Message):
	def	__init__(self, message):
		result = COMMAND_RE.match(message.topic)
		if result:
			ibmiotc.Message.__init__(self, message)
			
			self.command = result.group(1)
			self.format = result.group(2)
		else:
			raise ibmiotc.InvalidEventException("Received command on invalid topic: %s" % (message.topic))


class Client(ibmiotc.AbstractClient):

	def __init__(self, options):
		self.__options = options

		if self.__options['org'] == None:
			raise ibmiotc.ConfigurationException("Missing required property: org")
		if self.__options['type'] == None: 
			raise ibmiotc.ConfigurationException("Missing required property: type")
		if self.__options['id'] == None: 
			raise ibmiotc.ConfigurationException("Missing required property: id")
		
		if self.__options['org'] != "quickstart":
			if self.__options['auth-method'] == None: 
				raise ibmiotc.ConfigurationException("Missing required property: auth-method")
				
			if (self.__options['auth-method'] == "token"):
				if self.__options['auth-token'] == None: 
					raise ibmiotc.ConfigurationException("Missing required property for token based authentication: auth-token")
			else:
				raise ibmiotc.UnsupportedAuthenticationMethod(options['authMethod'])


		ibmiotc.AbstractClient.__init__(
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

		self.connect()
		
		if self.__options['org'] != "quickstart":
			self.__subscribeToCommands()
		

	def publishEvent(self, event, data):
		if not self.connectEvent.wait():
			self.logger.warning("Unable to send event %s because device is not currently connected")
			return False
		else:
			self.logger.debug("Sending event %s with data %s" % (event, json.dumps(data)))
			topic = 'iot-2/evt/'+event+'/fmt/json'
			
			# Note: Python JSON serialization doesn't know what to do with a datetime object on it's own
			payload = { 'd' : data, 'ts': datetime.now().isoformat() }
			self.client.publish(topic, payload=json.dumps(payload), qos=0, retain=False)
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
			self.client.subscribe(topic, qos=0)
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
		except ibmiotc.InvalidEventException as e:
			self.logger.critical(str(e))



def ParseConfigFile(configFilePath):
	parms = ConfigParser.ConfigParser()
	sectionHeader = "device"
	try:
		with open(configFilePath) as f:
			parms.readfp(ibmiotc.ConfigFile(f, sectionHeader))
		
		organization = parms.get(sectionHeader, "org", None)
		deviceType = parms.get(sectionHeader, "type", None)
		deviceId = parms.get(sectionHeader, "id", None)
		authMethod = parms.get(sectionHeader, "auth-method", None)
		authToken = parms.get(sectionHeader, "auth-token", None)
		
	except IOError as e:
		reason = "Error reading device configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ibmiotc.ConfigurationException(reason)
		
	return {'org': organization, 'type': deviceType, 'id': deviceId, 'auth-method': authMethod, 'auth-token': authToken}
