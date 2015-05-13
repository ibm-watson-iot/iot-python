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

import sys
import os
import time
import json
import socket
import ssl
import logging
import paho.mqtt.client as paho
import threading
import iso8601
import pytz
from datetime import datetime
from pkg_resources import get_distribution

__version__ = "0.0.10"

class Message:
	def __init__(self, message):
		self.payload = json.loads(message.payload.decode("utf-8"))
		self.timestamp = self.__parseMessageTimestamp()
		self.data = self.__parseMessageData()

		
	def __parseMessageTimestamp(self):
		try:
			if 'ts' in self.payload:
				dt = iso8601.parse_date(self.payload['ts'])
				return dt.astimezone(pytz.timezone('UTC'))
			else:
				#dt = datetime.utcfromtimestamp(time.time())
				#return pytz.utc.localize(dt)
				return datetime.now(pytz.timezone('UTC'))
		except iso8601.ParseError as e:
			raise InvalidEventException("Unable to parse event timestamp: %s" % str(e))
	
	
	def __parseMessageData(self):
		if 'd' in self.payload:
			return self.payload['d']
		else:
			return None

class AbstractClient:
	def __init__(self, organization, clientId, username, password, logDir=None):
		self.organization = organization
		self.username = username
		self.password = password
		self.address = organization + ".messaging.internetofthings.ibmcloud.com"
		self.port = 1883
		self.keepAlive = 60
		
		self.connectEvent = threading.Event()
		
		self.messages = 0
		self.recv = 0

		self.clientId = clientId
		
		# Configure logging
		self.logDir = logDir
		
		self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

		logFileName = '%s.log' % (clientId.replace(":", "_"))
		self.logFile = os.path.join(self.logDir, logFileName) if (self.logDir is not None) else logFileName 

		# create file handler, set level to debug & set format
		fhFormatter = logging.Formatter('%(asctime)-25s %(name)-25s ' + ' %(levelname)-7s %(message)s')
		fh = logging.FileHandler(self.logFile)
		fh.setFormatter(fhFormatter)
		
		self.logger.addHandler(fh)

		self.client = paho.Client(self.clientId, clean_session=True)
		
		try:
			self.tlsVersion = ssl.PROTOCOL_TLSv1_2
		except:
			self.tlsVersion = None
		
		# Configure authentication
		if self.username is not None:
			# In environments where either ssl is not available, or TLSv1.2 is not available we will fallback to MQTT over TCP
			if self.tlsVersion is not None:
				self.port = 8883
				# Path to certificate
				caFile = os.path.dirname(os.path.abspath(__file__)) + "/messaging.pem"
				self.client.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
				# Pre Python 3.2 the Paho MQTT client will use a bespoke hostname check which does not support wildcard certificates
				# Fix is included in 1.1 - https://bugs.eclipse.org/bugs/show_bug.cgi?id=440547
				if float(get_distribution('paho-mqtt').version) < 1.1 and (sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2)):
					self.logger.warning("Disabling TLS certificate hostname checking - Versions of the Paho MQTT client pre 1.1 do not support TLS wildcarded certificates on Python 3.2 or earlier: https://bugs.eclipse.org/bugs/show_bug.cgi?id=440547")
					self.client.tls_insecure_set(True)
			else:
				self.logger.warning("Unable to encrypt messages because TLSv1.2 is unavailable (MQTT over SSL requires at least Python v2.7.9 or 3.4 and openssl v1.0.1)")
			self.client.username_pw_set(self.username, self.password)
			
		#attach MQTT callbacks
		self.client.on_log = self.on_log
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		self.client.on_publish = self.on_publish

		self.start = time.time()

	def logAndRaiseException(self, e):
		self.logger.critical(str(e))
		raise e
	
	def connect(self):
		self.logger.debug("Connecting... (address = %s, port = %s, clientId = %s, username = %s, password = %s)" % (self.address, self.port, self.clientId, self.username, self.password))
		try:
			self.connectEvent.clear()
			self.client.connect(self.address, port=self.port, keepalive=self.keepAlive)
			self.client.loop_start()
			if not self.connectEvent.wait(timeout=10):
				self.logAndRaiseException(ConnectionException("Operation timed out connecting to the IBM Internet of Things service: %s" % (self.address)))
				
		except socket.error as serr:
			self.client.loop_stop()
			self.logAndRaiseException(ConnectionException("Failed to connect to the IBM Internet of Things service: %s - %s" % (self.address, str(serr))))

	def disconnect(self):
		#self.logger.info("Closing connection to the IBM Internet of Things Foundation")
		self.client.disconnect()
		# If we don't call loop_stop() it appears we end up with a zombie thread which continues to process 
		# network traffic, preventing any subsequent attempt to reconnect using connect()
		self.client.loop_stop()
		#self.stats()
		self.logger.info("Closed connection to the IBM Internet of Things Foundation")
			
	def stats(self):
		elapsed = ((time.time()) - self.start)
		
		msgPerSecond = 0 if self.messages == 0 else elapsed/self.messages
		recvPerSecond = 0 if self.recv == 0 else elapsed/self.recv
		self.logger.info("Messages published : %s, life: %.0fs, rate: 1/%.2fs" % (self.messages, elapsed, msgPerSecond))
		self.logger.info("Messages recieved  : %s, life: %.0fs, rate: 1/%.2fs" % (self.recv, elapsed, recvPerSecond))

		
	def on_log(self, mqttc, obj, level, string):
		self.logger.debug("%s" % (string))



	'''
	This is called when the client disconnects from the broker. The rc parameter indicates the status of the disconnection. 
	When 0 the disconnection was the result of disconnect() being called, when 1 the disconnection was unexpected.
	'''
	def on_disconnect(self, mosq, obj, rc):
		if rc == 1:
			self.logger.error("Unexpected disconnect from the IBM Internet of Things Foundation")
		
	'''
	This is called when a message from the client has been successfully sent to the broker. 
	The mid parameter gives the message id of the successfully published message.
	'''
	def on_publish(self, mosq, obj, mid):
		self.messages = self.messages + 1


'''
Generic Connection exception "Something went wrong"
'''
class ConnectionException(Exception):
	def __init__(self, reason):
		self.reason = reason
	
	def __str__(self):
		return self.reason

'''
Specific Connection exception where the configuration is invalid
'''
class ConfigurationException(ConnectionException):
	def __init__(self, reason):
		self.reason = reason
	
	def __str__(self):
		return self.reason


'''
Specific Connection exception where the authentication method specified is not supported
'''
class UnsupportedAuthenticationMethod(ConnectionException):
	def __init__(self, method):
		self.method = method
	
	def __str__(self):
		return "Unsupported authentication method %s" % self.method


'''
Specific exception where and Event object can not be constructed
'''
class InvalidEventException(Exception):
	def __init__(self, reason):
		self.reason = reason
	
	def __str__(self):
		return "Invalid Event %s" % self.reason


