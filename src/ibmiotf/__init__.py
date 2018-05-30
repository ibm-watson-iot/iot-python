# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
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
#   Lokesh Haralakatta
#   Ian Craggs - fix for #99
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
from encodings.base64_codec import base64_encode

__version__ = "0.3.5"


class Message:
    """
    Represents an abstract message recieved over Mqtt.  All implementations of a Codec must return an object of this type.
    
    # Parameters
    data (dict): The message payload
    timestamp (datetime): Timestamp intended to denote the time the message was sent, 
        or `None` if this information is not available. 
    
    """
    
    def __init__(self, data, timestamp=None):
        self.data = data
        self.timestamp = timestamp


class AbstractClient(object):
    """
    Represents an abstract message recieved over Mqtt.  All implementations of a Codec must return an object of this type.
    
    # Parameters
    domain (string): Domain denoting the instance of IBM Watson IoT Platform to connect to
    organization (string): IBM Watson IoT Platform organization ID to connect to
    clientId (string): MQTT clientId for the underlying Paho client
    username (string): MQTT username for the underlying Paho client
    password (string): MQTT password for the underlying Paho client
    port (int): MQTT port for the underlying Paho client to connect using.  Defaults to `8883`
    logHandlers (list<logging.Handler>): Log handlers to configure.  Defaults to `None`, 
        which will result in a default log handler being created.
    cleanSession (string): Defaults to `true`.  Although this is a true|false parameter, 
        it is being handled as a string for some reason
    transport (string): Defaults to `tcp`
    
    # Attributes
    client (paho.mqtt.client.Client): Built-in Paho MQTT client handling connectivity for the client.
    logger (logging.logger): Client logger.
    """
    def __init__(self, domain, organization, clientId, username, password, port=8883, logHandlers=None, cleanSession="true", transport="tcp"):
        self.organization = organization
        self.username = username
        self.password = password
        self.address = organization + ".messaging." + domain
        self.port = port
        self.keepAlive = 60

        self.connectEvent = threading.Event()

        self._recvLock = threading.Lock()
        self._messagesLock = threading.Lock()

        # If we are disconnected we lose all our active subscriptions.  Keep
        # track of all subscriptions so that we can internally restore all
        # subscriptions on reconnect
        self._subscriptions = {}

        # Create a lock for the subscription dictionary
        self._subLock = threading.Lock()

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

        self.client = paho.Client(self.clientId, transport=transport, clean_session=False if cleanSession == "false" else True)

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
        """
        Get the Python module that is currently defined as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retrieve the encoder for
        
        # Returns
        Boolean: The python module, or `None` if there is no codec defined for the `messageFormat`
        """
        if messageFormat not in self._messageEncoderModules:
            return None
        return self._messageEncoderModules[messageFormat]


    def setMessageEncoderModule(self, messageFormat, module):
        """
        Set a Python module as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retreive the encoder for
        module (module): The Python module to set as the encoder/decoder for `messageFormat`
        """
        self._messageEncoderModules[messageFormat] = module


    def logAndRaiseException(self, e):
        """
        Logs an exception at log level `critical` before raising it.
        
        # Arguments
        e (Exception): The exception to log/raise
        """
        self.logger.critical(str(e))
        raise e


    def connect(self):
        """
        Connect the client to IBM Watson IoT Platform using the underlying Paho MQTT client
        
        # Raises
        ConnectionException: If there is a problem establishing the connection.
        """
        self.logger.debug("Connecting... (address = %s, port = %s, clientId = %s, username = %s)" % (self.address, self.port, self.clientId, self.username))
        try:
            self.connectEvent.clear()
            self.client.connect(self.address, port=self.port, keepalive=self.keepAlive)
            self.client.loop_start()
            if not self.connectEvent.wait(timeout=30):
                self.client.loop_stop()
                self.logAndRaiseException(ConnectionException("Operation timed out connecting to IBM Watson IoT Platform: %s" % (self.address)))

        except socket.error as serr:
            self.client.loop_stop()
            self.logAndRaiseException(ConnectionException("Failed to connect to IBM Watson IoT Platform: %s - %s" % (self.address, str(serr))))


    def disconnect(self):
        """
        Disconnect the client from IBM Watson IoT Platform
        """
        #self.logger.info("Closing connection to the IBM Watson IoT Platform")
        self.client.disconnect()
        # If we don't call loop_stop() it appears we end up with a zombie thread which continues to process
        # network traffic, preventing any subsequent attempt to reconnect using connect()
        self.client.loop_stop()
        #self.stats()
        self.logger.info("Closed connection to the IBM Watson IoT Platform")


    def stats(self):
        """
        I think we killed the use of this and this is dead code
        
        TODO: clean all this up .. should we really be tracking these stats within the client itself in the first place?
        """
        elapsed = ((time.time()) - self.start)

        msgPerSecond = 0 if self.messages == 0 else elapsed/self.messages
        recvPerSecond = 0 if self.recv == 0 else elapsed/self.recv
        self.logger.debug("Messages published : %s, life: %.0fs, rate: 1/%.2fs" % (self.messages, elapsed, msgPerSecond))
        self.logger.debug("Messages received  : %s, life: %.0fs, rate: 1/%.2fs" % (self.recv, elapsed, recvPerSecond))


    def on_log(self, mqttc, obj, level, string):
        """
        Called when the client has log information.  
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        level (int): The severity of the message, will be one of `MQTT_LOG_INFO`, 
            `MQTT_LOG_NOTICE`, `MQTT_LOG_WARNING`, `MQTT_LOG_ERR`, and `MQTT_LOG_DEBUG`.
        string (string): The log message itself
        
        See https://github.com/eclipse/paho.mqtt.python#on_log for more information
        """
        self.logger.debug("%d %s" % (level, string))


    def on_disconnect(self, mqttc, obj, rc):
        """
        Called when the client disconnects from IBM Watson IoT Platform.  
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        rc (int): indicates the disconnection state.  If `MQTT_ERR_SUCCESS` (0), the callback was 
            called in response to a `disconnect()` call. If any other value the disconnection was 
            unexpected, such as might be caused by a network error.
        
        See https://github.com/eclipse/paho.mqtt.python#on_disconnect for more information
        """
        if rc != 0:
            self.logger.error("Unexpected disconnect from the IBM Watson IoT Platform: %d" % (rc))
        else:
            self.logger.info("Disconnected from the IBM Watson IoT Platform")
        self.stats()

    def on_publish(self, mqttc, obj, mid):
        """
        Called when a message from the client has been successfully sent to IBM Watson IoT Platform.
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        mid (int): Gives the message id of the successfully published message.
        """
        with self._messagesLock:
            self.messages = self.messages + 1
            if mid in self._onPublishCallbacks:
                midOnPublish = self._onPublishCallbacks.get(mid)
                del self._onPublishCallbacks[mid]
                if midOnPublish != None:
                    midOnPublish()
            else:
                # record the fact that paho callback has already come through so it can be called inline
                # with the publish.
                self._onPublishCallbacks[mid] = None

    def setKeepAliveInterval(self, newKeepAliveInterval):
        """
        Reconfigure the keepalive value for any subsequent MQTT connection made 
        by the client.  This does not affect the keep alive setting of any 
        existing connection.  Traffic generated by keep alive is minimal, but 
        also billable as part of your data transfer to/from the Platform. 
        
        # Properties
        newKeepAliveInterval (int): Number of seconds for the new keepalive interval
        """
        self.keepAlive = newKeepAliveInterval

    def getKeepAliveInterval(self):
        """
        Get the current setting for keepalive.  Note: This is not necessarily the 
        value used by the current active connection, as any changes to this value
        are only applied when a new connection to the Platfrom is established 
        
        # Returns
        int: Number of seconds the keepalive interval is set to 
        """
        return(self.keepAlive)


class ConnectionException(Exception):
    """
    Generic Connection exception "Something went wrong"
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class ConfigurationException(ConnectionException):
    """
    Specific Connection exception where the configuration is invalid
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class UnsupportedAuthenticationMethod(ConnectionException):
    """
    Specific Connection exception where the authentication method specified is not supported
    """
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "Unsupported authentication method: %s" % self.method


class InvalidEventException(Exception):
    """
    Specific exception where and Event object can not be constructed
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Invalid Event: %s" % self.reason


class MissingMessageDecoderException(Exception):
    """
    Specific exception where there is no message decoder defined for the message format being processed
    """
    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message decoder defined for message format: %s" % self.format


class MissingMessageEncoderException(Exception):
    """
    Specific exception where there is no message encoder defined for the message format being processed
    """
    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message encoder defined for message format: %s" % self.format


class APIException(Exception):
    """
    Exception raised when any API call fails
    1 The exact HTTP Status Code
    2 The error thrown
    3 The JSON message returned
    """
    def __init__(self, httpCode, message, response):
        self.httpCode = httpCode
        self.message = message
        self.response = response

    def __str__(self):
        return "[%s] %s" % (self.httpCode, self.message)


class HttpAbstractClient(object):
    """
    Base client class restricted to HTTP only.  Unless for some technical reason
    you are unable to use the full MQTT-enable client there really is no need to
    use this alternative feature-limited client.
    """
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

    def connect(self):
        # No-op with HTTP client (but makes it easy to switch between using http & mqtt clients in your code)
        pass

    def disconnect(self):
        # No-op with HTTP client (but makes it easy to switch between using http & mqtt clients in your code)
        pass

    def getMessageEncoderModule(self, messageFormat):
        return self._messageEncoderModules[messageFormat]

    def setMessageEncoderModule(self, messageFormat, module):
        self._messageEncoderModules[messageFormat] = module

    def logAndRaiseException(self, e):
        self.logger.critical(str(e))
        raise e

    def getContentType(self,dataFormat):
        '''
           Method to detect content type using given data format
        '''
        # Default content type is json
        contentType = "application/json"
        if dataFormat == "text":
            contentType = "text/plain; charset=utf-8"
        elif dataFormat == "xml":
            contentType = "application/xml"
        elif dataFormat == "bin":
            contentType = "application/octet-stream"
        else:
            contentType = "application/json"
        # Return derived content type
        return contentType
