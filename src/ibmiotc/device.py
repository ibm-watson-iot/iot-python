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
import sys
import ConfigParser

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
				raise ibmiotc.UnsupportedAuthenticationMethod(authMethod)


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
			payload = { 'd' : data }
			self.client.publish(topic, payload=json.dumps(payload), qos=0, retain=False)
			return True


'''
See: http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
'''			
class ConfigFile(object):
	def __init__(self, fp):
		self.fp = fp
		self.sechead = '[device]\n'
	
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
		
		organization = parms.get("device", "org", None)
		type = parms.get("device", "type", None)
		id = parms.get("device", "id", None)
		authMethod = parms.get("device", "auth-method", None)
		authToken = parms.get("device", "auth-token", None)
		
	except IOError as e:
		reason = "Error reading device configuration file '%s' (%s)" % (configFilePath,e[1])
		raise ibmiotc.ConfigurationException(reason)
		
	return {'org': organization, 'type': type, 'id': id, 'auth-method': authMethod, 'auth-token': authToken}
