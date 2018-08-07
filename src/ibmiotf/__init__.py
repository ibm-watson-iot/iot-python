# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
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
import pytz
from datetime import datetime
from encodings.base64_codec import base64_encode

__version__ = "0.4.0"


class Message:
    """
    Represents an abstract message recieved over Mqtt.  All implementations of 
    a Codec must return an object of this type.
    
    # Attributes
    data (dict): The message payload
    timestamp (datetime): Timestamp intended to denote the time the message was sent, 
        or `None` if this information is not available. 
    
    """
    
    def __init__(self, data, timestamp=None):
        self.data = data
        self.timestamp = timestamp

class MessageCodec(object):
    @staticmethod
    def encode(data=None, timestamp=None):
        raise NotImplementedError()
    
    @staticmethod
    def decode(message):
        raise NotImplementedError()



class AbstractClient(object):
    """
    The underlying client object utilised for Platform connectivity over MQTT 
    in devices, gateways, and applications.
    
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
    def __init__(self, domain, organization, clientId, username, password, port=None, logHandlers=None, cleanSession="true", transport="tcp"):
        self.organization = organization
        self.username = username
        self.password = password
        self.address = organization + ".messaging." + domain
        self.port = port
        self.keepAlive = 60

        self.connectEvent = threading.Event()


        # If we are disconnected we lose all our active subscriptions.  Keep
        # track of all subscriptions so that we can internally restore all
        # subscriptions on reconnect
        # Also, create a lock for gating access to the subscription dictionary
        self._subscriptions = {}
        self._subLock = threading.Lock()

        # Create a map to contain mids for onPublish() callback handling.
        # and a lock to gate access to the dictionary
        self._onPublishCallbacks = {}
        self._messagesLock = threading.Lock()

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
        
        # Normal usage puts the client in an auto-detect mode, where it will try to use 
        # TLS, and fall back to unencrypted mode ONLY if TLS 1.2 is unavailable.
        # However, we now support explicit override of this by allowing the client to be 
        # configured to use a specific port.
        #
        # If there is no specific port set in the configuration then we will auto-negotiate TLS if possible
        # If the port has been configured to 80 or 1883 we should not try to auto-enable TLS configuration
        # if the port has been configured to 443 or 8883 we should not auto-fallback to no TLS on 1883
        if self.port in [80, 1883]:
            # Note: We don't seem to support port 80 fallback (anymore?)
            self.tlsVersion = None
            self.logger.warning("Unable to encrypt messages because client configuration has overridden port selection to an insecure port (%s)" % self.port)
        elif self.port in [443, 8883]:
            self.tlsVersion = ssl.PROTOCOL_TLSv1_2
            # We allow an exception to raise here if running in an environment where 
            # TLS 1.2 is unavailable because the configuration explicitly requested 
            # to use encrypted connection
        elif self.port is None:
            try:
                self.tlsVersion = ssl.PROTOCOL_TLSv1_2
                self.port = 8883
            except:
                self.tlsVersion = None
                self.port = 1883
                self.logger.warning("Unable to encrypt messages because TLSv1.2 is unavailable (MQTT over SSL requires at least Python v2.7.9 or 3.4 and openssl v1.0.1)")
        else:
            raise Exception("Unsupported value for port override: %s.  Supported values are 1883 & 8883." % self.port)
            
        # Configure authentication
        if self.username is not None:
            # In environments where either ssl is not available, or TLSv1.2 is not available we will fallback to MQTT over TCP
            if self.tlsVersion is not None:
                # Path to certificate
                caFile = os.path.dirname(os.path.abspath(__file__)) + "/messaging.pem"
                self.client.tls_set(ca_certs=caFile, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.client.username_pw_set(self.username, self.password)

        # Attach MQTT callbacks
        self.client.on_log = self._onLog
        self.client.on_disconnect = self._onDisconnect
        self.client.on_publish = self._onPublish

        # Initialize default message encoders and decoders.
        self._messageEncoderModules = {}


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


    def _logAndRaiseException(self, e):
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
                self._logAndRaiseException(ConnectionException("Operation timed out connecting to IBM Watson IoT Platform: %s" % (self.address)))

        except socket.error as serr:
            self.client.loop_stop()
            self._logAndRaiseException(ConnectionException("Failed to connect to IBM Watson IoT Platform: %s - %s" % (self.address, str(serr))))


    def disconnect(self):
        """
        Disconnect the client from IBM Watson IoT Platform
        """
        #self.logger.info("Closing connection to the IBM Watson IoT Platform")
        self.client.disconnect()
        # If we don't call loop_stop() it appears we end up with a zombie thread which continues to process
        # network traffic, preventing any subsequent attempt to reconnect using connect()
        self.client.loop_stop()
        self.logger.info("Closed connection to the IBM Watson IoT Platform")


    def _onLog(self, mqttc, obj, level, string):
        """
        Called when the client has log information.  
        
        See [paho.mqtt.python#on_log](https://github.com/eclipse/paho.mqtt.python#on_log) for more information
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        level (int): The severity of the message, will be one of `MQTT_LOG_INFO`, 
            `MQTT_LOG_NOTICE`, `MQTT_LOG_WARNING`, `MQTT_LOG_ERR`, and `MQTT_LOG_DEBUG`.
        string (string): The log message itself
        
        """
        self.logger.debug("%d %s" % (level, string))


    def _onDisconnect(self, mqttc, obj, rc):
        """
        Called when the client disconnects from IBM Watson IoT Platform.
        
        See [paho.mqtt.python#on_disconnect](https://github.com/eclipse/paho.mqtt.python#on_disconnect) for more information
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        rc (int): indicates the disconnection state.  If `MQTT_ERR_SUCCESS` (0), the callback was 
            called in response to a `disconnect()` call. If any other value the disconnection was 
            unexpected, such as might be caused by a network error.
        
        """
        if rc != 0:
            self.logger.error("Unexpected disconnect from the IBM Watson IoT Platform: %d" % (rc))
        else:
            self.logger.info("Disconnected from the IBM Watson IoT Platform")

    def _onPublish(self, mqttc, obj, mid):
        """
        Called when a message from the client has been successfully sent to IBM Watson IoT Platform.
        
        See [paho.mqtt.python#on_publish](https://github.com/eclipse/paho.mqtt.python#on_publish) for more information
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        obj (object): The private user data as set in Client() or user_data_set()
        mid (int): Gives the message id of the successfully published message.
        """
        with self._messagesLock:
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
    Generic Connection exception
    
    # Attributes
    reason (string): The reason why the connection exception occured
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class ConfigurationException(ConnectionException):
    """
    Specific Connection exception where the configuration is invalid
    
    # Attributes
    reason (string): The reason why the configuration is invalid
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class UnsupportedAuthenticationMethod(ConnectionException):
    """
    Specific Connection exception where the authentication method specified is not supported
    
    # Attributes
    method (string): The authentication method that is unsupported
    """
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "Unsupported authentication method: %s" % self.method


class InvalidEventException(Exception):
    """
    Specific exception where an Event object can not be constructed
    
    # Attributes
    reason (string): The reason why the event could not be constructed
    """
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Invalid Event: %s" % self.reason


class MissingMessageDecoderException(Exception):
    """
    Specific exception where there is no message decoder defined for the message format being processed
    
    # Attributes
    format (string): The message format for which no encoder could be found
    """
    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message decoder defined for message format: %s" % self.format


class MissingMessageEncoderException(Exception):
    """
    Specific exception where there is no message encoder defined for the message format being processed
    
    # Attributes
    format (string): The message format for which no encoder could be found
    """
    def __init__(self, format):
        self.format = format

    def __str__(self):
        return "No message encoder defined for message format: %s" % self.format


class APIException(Exception):
    """
    Exception raised when any API call fails
    
    # Attributes
    httpCode (int): The HTTP status code returned
    message (string): The exception message
    response (string): The reponse body that triggered the exception
    """
    def __init__(self, httpCode, message, response):
        self.httpCode = httpCode
        self.message = message
        self.response = response

    def __str__(self):
        return "[%s] %s" % (self.httpCode, self.message)


class HttpAbstractClient(object):
    """
    The underlying client object utilised for Platform connectivity 
    over HTPP in devices, gateways, and applications.
    
    Restricted to HTTP only.  Unless for some technical reason
    you are unable to use the full MQTT-enable client there really 
    is no need to use this alternative feature-limited client as 
    installing this library means you already have access to the 
    rich MQTT/HTTP client implementation.
    
    The HTTP client supports four content-types for posted events:
    
    - `application/xml`: for events/commands using message format `xml`
    - `text/plain; charset=utf-8`: for events/commands using message format `plain`
    - `application/octet-stream`: for events/commands using message format `bin`
    - `application/json`: the default for all other message formats.
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
        """
        Connect is a no-op with HTTP-only client, but the presence of this method makes it easy 
        to switch between using HTTP & MQTT client implementation
        """
        pass

    def disconnect(self):
        """
        Disconnect is a no-op with HTTP-only client, but the presence of this method makes it easy 
        to switch between using HTTP & MQTT client implementation
        """
        pass

    def getMessageEncoderModule(self, messageFormat):
        """
        Get the Python module that is currently defined as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retrieve the encoder for
        
        # Returns
        Boolean: The python module, or `None` if there is no codec defined for the `messageFormat`
        """
        return self._messageEncoderModules[messageFormat]

    def setMessageEncoderModule(self, messageFormat, module):
        """
        Set a Python module as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retreive the encoder for
        module (module): The Python module to set as the encoder/decoder for `messageFormat`
        """
        self._messageEncoderModules[messageFormat] = module

    def _logAndRaiseException(self, e):
        """
        Logs an exception at log level `critical` before raising it.
        
        # Arguments
        e (Exception): The exception to log/raise
        """
        self.logger.critical(str(e))
        raise e

    def _getContentType(self, dataFormat):
        """
        Determines the content type for the HTTP message
        """
        # Default content type is json
        contentType = "application/json"
        if dataFormat == "text":
            contentType = "text/plain; charset=utf-8"
        elif dataFormat == "xml":
            contentType = "application/xml"
        elif dataFormat == "bin":
            contentType = "application/octet-stream"
        
        # Return derived content type
        return contentType
