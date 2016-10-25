# *****************************************************************************
# Copyright (c) 2014 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   David Parker
#   Paul Slater
#   Ben Bakowski
#   Amit M Mangalvedkar
# *****************************************************************************

import sys
import os
import time
import json
import socket
import ssl
import logging
from logging.handlers import RotatingFileHandler
import paho.mqtt.client as paho
import threading
import iso8601
import pytz
from datetime import datetime
from pkg_resources import get_distribution
from encodings.base64_codec import base64_encode

__version__ = "0.2.6"

class Message:
	def __init__(self, data, timestamp=None):
		self.data = data
		self.timestamp = timestamp

class AbstractClient:
	def __init__(self, domain, organization, clientId, username, password, port=8883,
										logHandlers=None, cleanSession="true"):
		self.organization = organization
		self.username = username
		self.password = password
		self.address = organization + ".messaging." + domain
		self.port = port
		self.keepAlive = 60

		self.connectEvent = threading.Event()

		self._recvLock = threading.Lock()
		self._messagesLock = threading.Lock()

		self.messages = 0
		self.recv = 0

		self.clientId = clientId

		# Configure logging
		self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
		self.logger.setLevel(logging.INFO)

		# Remove any existing log handlers we may have picked up from getLogger()
		self.logger.handlers = []

		if logHandlers:
			if isinstance(logHandlers, list):
				# Add all supplied log handlers
				for handler in logHandlers:
					self.logger.addHandler(handler)
			else:
				# Add the supplied log handler
				self.logger.addHandler(logHandlers)
		else:
			# Generate a default rotating file log handler and stream handler
			logFileName = '%s.log' % (clientId.replace(":", "_"))
			fhFormatter = logging.Formatter('%(asctime)-25s %(name)-25s ' + ' %(levelname)-7s %(message)s')
			rfh = RotatingFileHandler(logFileName, mode='a', maxBytes=1024000 , backupCount=0, encoding=None, delay=True)
			rfh.setFormatter(fhFormatter)

			ch = logging.StreamHandler()
			ch.setFormatter(fhFormatter)
			ch.setLevel(logging.DEBUG)

			self.logger.addHandler(rfh)
			self.logger.addHandler(ch)

		self.client = paho.Client(self.clientId, clean_session=False if cleanSession == "false" else True)

		try:
			self.tlsVersion = ssl.PROTOCOL_TLSv1_2
		except:
			self.tlsVersion = None

		# Configure authentication
		if self.username is not None:
			# In environments where either ssl is not available, or TLSv1.2 is not available we will fallback to MQTT over TCP
			if self.tlsVersion is not None:
				# Path to certificate
				caFile = os.path.dirname(os.path.abspath(__file__)) + "/messaging.pem"
				self.client.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
				# Pre Python 3.2 the Paho MQTT client will use a bespoke hostname check which does not support wildcard certificates
				# Fix is included in 1.1 - https://bugs.eclipse.org/bugs/show_bug.cgi?id=440547
				if float(get_distribution('paho-mqtt').version) < 1.1 and (sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2)):
					self.logger.warning("Disabling TLS certificate hostname checking - Versions of the Paho MQTT client pre 1.1 do not support TLS wildcarded certificates on Python 3.2 or earlier: https://bugs.eclipse.org/bugs/show_bug.cgi?id=440547")
					self.client.tls_insecure_set(True)
			else:
				self.port = 1883
				self.logger.warning("Unable to encrypt messages because TLSv1.2 is unavailable (MQTT over SSL requires at least Python v2.7.9 or 3.4 and openssl v1.0.1)")
			self.client.username_pw_set(self.username, self.password)

		# Attach MQTT callbacks
		self.client.on_log = self.on_log
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		self.client.on_publish = self.on_publish

		# Initialize default message encoders and decoders.
		self._messageEncoderModules = {}

		self.start = time.time()

		# initialize callbacks
		self._onPublishCallbacks = {}


	def getMessageEncoderModule(self, messageFormat):
		return self._messageEncoderModules[messageFormat]

	def setMessageEncoderModule(self, messageFormat, module):
		self._messageEncoderModules[messageFormat] = module

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
		#self.logger.info("Closing connection to the IBM Watson IoT Platform")
		self.client.disconnect()
		# If we don't call loop_stop() it appears we end up with a zombie thread which continues to process
		# network traffic, preventing any subsequent attempt to reconnect using connect()
		self.client.loop_stop()
		#self.stats()
		self.logger.info("Closed connection to the IBM Watson IoT Platform")

	def stats(self):
		elapsed = ((time.time()) - self.start)

		msgPerSecond = 0 if self.messages == 0 else elapsed/self.messages
		recvPerSecond = 0 if self.recv == 0 else elapsed/self.recv
		self.logger.debug("Messages published : %s, life: %.0fs, rate: 1/%.2fs" % (self.messages, elapsed, msgPerSecond))
		self.logger.debug("Messages received  : %s, life: %.0fs, rate: 1/%.2fs" % (self.recv, elapsed, recvPerSecond))


	def on_log(self, mqttc, obj, level, string):
		self.logger.debug("%s" % (string))



	'''
	This is called when the client disconnects from the broker. The rc parameter indicates the status of the disconnection.
	When 0 the disconnection was the result of disconnect() being called, when 1 the disconnection was unexpected.
	'''
	def on_disconnect(self, mosq, obj, rc):
		if rc == 1:
			self.logger.error("Unexpected disconnect from the IBM Watson IoT Platform")
		else:
			self.logger.info("Disconnected from the IBM Watson IoT Platform")
		self.stats()

	'''
	This is called when a message from the client has been successfully sent to the broker.
	The mid parameter gives the message id of the successfully published message.
	'''
	def on_publish(self, mosq, obj, mid):
		with self._messagesLock:
			self.messages = self.messages + 1
			if mid in self._onPublishCallbacks:
				midOnPublish = self._onPublishCallbacks.get(mid)
				del self._onPublishCallbacks[mid]
				midOnPublish()

	'''
	Setter and Getter methods to set and get user defined keepAlive Interval  value to
	override the MQTT default value of 60
	'''
	def setKeepAliveInterval(self, newKeepAliveInterval):
		self.keepAlive = newKeepAliveInterval

	def getKeepAliveInterval(self):
		return(self.keepAlive)



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
		return "Unsupported authentication method: %s" % self.method


'''
Specific exception where and Event object can not be constructed
'''
class InvalidEventException(Exception):
	def __init__(self, reason):
		self.reason = reason

	def __str__(self):
		return "Invalid Event: %s" % self.reason


'''
Specific exception where and Event object can not be constructed
'''
class MissingMessageDecoderException(Exception):
	def __init__(self, format):
		self.format = format

	def __str__(self):
		return "No message decoder defined for message format: %s" % self.format


class MissingMessageEncoderException(Exception):
	def __init__(self, format):
		self.format = format

	def __str__(self):
		return "No message encoder defined for message format: %s" % self.format


'''
This exception has been added in V2 and provides the following
1) The exact HTTP Status Code
2) The error thrown
3) The JSON message returned
'''
class APIException(Exception):
	def __init__(self, httpCode, message, response):
		self.httpCode = httpCode
		self.message = message
		self.response = response

	def __str__(self):
		return "[%s] %s" % (self.httpCode, self.message)

class HttpAbstractClient:
	def __init__(self, clientId, logHandlers=None):
		# Configure logging
		self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
		self.logger.setLevel(logging.INFO)

		# Remove any existing log handlers we may have picked up from getLogger()
		self.logger.handlers = []

		if logHandlers:
			if isinstance(logHandlers, list):
				# Add all supplied log handlers
				for handler in logHandlers:
					self.logger.addHandler(handler)
			else:
				# Add the supplied log handler
				self.logger.addHandler(logHandlers)
		else:
			# Generate a default rotating file log handler and stream handler
			logFileName = '%s.log' % (clientId.replace(":", "_"))
			fhFormatter = logging.Formatter('%(asctime)-25s %(name)-25s ' + ' %(levelname)-7s %(message)s')
			rfh = RotatingFileHandler(logFileName, mode='a', maxBytes=1024000 , backupCount=0, encoding=None, delay=True)
			rfh.setFormatter(fhFormatter)

			ch = logging.StreamHandler()
			ch.setFormatter(fhFormatter)
			ch.setLevel(logging.DEBUG)

			self.logger.addHandler(rfh)
			self.logger.addHandler(ch)

	   	# Initialize default message encoders and decoders.
		self._messageEncoderModules = {}

	def getMessageEncoderModule(self, messageFormat):
		return self._messageEncoderModules[messageFormat]

	def setMessageEncoderModule(self, messageFormat, module):
		self._messageEncoderModules[messageFormat] = module

	def logAndRaiseException(self, e):
		self.logger.critical(str(e))
		raise e
