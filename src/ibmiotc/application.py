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

import re
import ibmiotc
import time
import json
import logging
import ConfigParser

class Client(ibmiotc.AbstractClient):

	def __init__(self, options):
		self.options = options

		if self.options['org'] == None:
			raise ibmiotc.ConfigurationException("Missing required property: org")
		if self.options['id'] == None: 
			raise ibmiotc.ConfigurationException("Missing required property: type")
		
		if self.options['org'] != "quickstart":
			if self.options['auth-method'] == None: 
				raise ibmiotc.ConfigurationException("Missing required property: auth-method")
				
			if (self.options['auth-method'] == "apikey"):
				if self.options['auth-key'] == None: 
					raise ibmiotc.ConfigurationException("Missing required property for API key based authentication: auth-key")
				if self.options['auth-token'] == None: 
					raise ibmiotc.ConfigurationException("Missing required property for API key based authentication: auth-token")
			else:
				raise ibmiotc.UnsupportedAuthenticationMethod(authMethod)

		ibmiotc.AbstractClient.__init__(
			self, 
			organization = options['org'],
			clientId = "a:" + options['org'] + ":" + options['id'], 
			username = options['auth-key'] if (options['auth-method'] == "apikey") else None,
			password = options['auth-token']
		)

		# Attach application specific callbacks
		self.client.on_message = self.on_message
		
		# Initialize user supplied callbacks
		self.eventCallback = None
		self.statusCallback = None
		
		self.connect()

	def subscribeToDeviceEvents(self, type="+", id="+", event="+"):
		if self.options['org'] == "quickstart" and id == "+":
			self.logger.warning("QuickStart applications do not support wildcard subscription to events from all devices")
			return False
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to events (%s, %s, %s) because application is not currently connected" % (type, id, event))
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/json' % (type, id, event)
			self.client.subscribe(topic, qos=0)
			return True

	def subscribeToDeviceStatus(self, type="+", id="+"):
		if self.options['org'] == "quickstart" and id == "+":
			self.logger.warning("QuickStart applications do not support wildcard subscription to device status")
			return False
		if not self.connectEvent.wait():
			self.logger.warning("Unable to subscribe to device status (%s, %s) because application is not currently connected" % (type, id))
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/mon' % (type, id)
			self.client.subscribe(topic, qos=0)
			return True

	
	def publishEvent(self, type, id, event, data):
		if not self.connectEvent.wait():
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/json' % (type, id, event)
			payload = { 'd' : data }
			self.client.publish(topic, payload=json.dumps(payload), qos=0, retain=False)
			return True

	
	def publishCommand(self, type, id, command, data=None):
		if self.options['org'] == "quickstart":
			self.logger.warning("QuickStart applications do not support sending commands")
			return False
		if not self.connectEvent.wait():
			return False
		else:
			topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/json' % (type, id, command)
			payload = { 'd' : data }
			self.client.publish(topic, payload=json.dumps(payload), qos=0, retain=False)
			return True
			
	
	def on_message(self, client, userdata, message):
		self.logger.debug("Received message '%s' on topic '%s' with QoS %s" % (message.payload, message.topic, message.qos))
		self.recv = self.recv + 1

		# Is the message an event from a device?
		deviceEventPattern = re.compile("iot-2/type/(.+)/id/(.+)/evt/(.+)/fmt/(.+)")
		eventMatchResult = deviceEventPattern.match(message.topic)

		# Is the message status from a device?
		deviceStatusPattern = re.compile("iot-2/type/(.+)/id/(.+)/mon")
		statusMatchResult = deviceStatusPattern.match(message.topic)
		
		if self.eventCallback and eventMatchResult:
			data = json.loads(str(message.payload))
			self.eventCallback(eventMatchResult.group(1), eventMatchResult.group(2), eventMatchResult.group(3), eventMatchResult.group(4), data['d'])
		elif self.statusCallback and statusMatchResult:
			status = json.loads(str(message.payload))
			self.statusCallback(statusMatchResult.group(1), statusMatchResult.group(2), status)
		else:
			self.logger.debug("topic %s does not match any expected pattern" % (message.topic))


'''
See: http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
'''			
class ConfigFile(object):
	def __init__(self, fp):
		self.fp = fp
		self.sechead = '[application]\n'
	
	def readline(self):
		if self.sechead:
			try: 
				return self.sechead
			finally: 
				self.sechead = None
		else: 
			return self.fp.readline()


def ParseConfigFile(configFilePath):
	parms = ConfigParser.ConfigParser()

	try:
		with open(configFilePath) as f:
			parms.readfp(ConfigFile(f))
		
		organization = parms.get("application", "org", None)
		id = parms.get("application", "id", None)
		authMethod = parms.get("application", "auth-method", None)
		authKey = parms.get("application", "auth-key", None)
		authToken = parms.get("application", "auth-token", None)
		
	except IOError as e:
		reason = "Error reading application configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ibmiotc.ConfigurationException(reason)
		
	return {'org': organization, 'id': id, 'auth-method': authMethod, 'auth-key': authKey, 'auth-token': authToken}
			
