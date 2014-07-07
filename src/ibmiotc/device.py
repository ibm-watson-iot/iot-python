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
from datetime import datetime

class Client(ibmiotc.AbstractClient):

	def __init__(self, options):
		self.options = options

		if self.options['org'] == None:
			raise ibmiotc.ConfigurationException("Missing required property: org")
		if self.options['type'] == None: 
			raise ibmiotc.ConfigurationException("Missing required property: type")
		if self.options['id'] == None: 
			raise ibmiotc.ConfigurationException("Missing required property: id")
		
		if self.options['org'] != "quickstart":
			if self.options['auth-method'] == None: 
				raise ibmiotc.ConfigurationException("Missing required property: auth-method")
				
			if (self.options['auth-method'] == "token"):
				if self.options['auth-token'] == None: 
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

		self.connect()
		

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
