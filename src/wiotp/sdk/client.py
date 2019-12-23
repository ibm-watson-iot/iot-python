# *****************************************************************************
# Copyright (c) 2014, 2019 IBM Corporation and other Contributors.
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
import platform

from logging.handlers import RotatingFileHandler
from paho.mqtt import __version__ as pahoVersion
import paho.mqtt.client as paho
import threading
import pytz
from datetime import datetime

from wiotp.sdk import __version__ as wiotpVersion
from wiotp.sdk.exceptions import MissingMessageEncoderException, ConnectionException
from wiotp.sdk.messages import JsonCodec, RawCodec, Utf8Codec


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
    cleanStart (string): Defaults to `false`.  Although this is a true|false parameter
    sessionExpiry (string): Defaults to 3600 seconds.  Does nothing today (pending MQTT v5)
    transport (string): Defaults to `tcp`
    caFile (string): Defaults to None
    
    # Attributes
    client (paho.mqtt.client.Client): Built-in Paho MQTT client handling connectivity for the client.
    logger (logging.logger): Client logger.
    """

    def __init__(
        self,
        domain,
        organization,
        clientId,
        username,
        password,
        port=None,
        transport="tcp",
        cleanStart=False,
        sessionExpiry=3600,
        keepAlive=60,
        caFile=None,
        logLevel=logging.INFO,
        logHandlers=None,
    ):

        self.organization = organization
        self.username = username
        self.password = password
        self.address = organization + ".messaging." + domain
        self.port = port
        # This is for a future MQTT v5 feature once Paho library is updated
        self.sessionExpiry = sessionExpiry
        self.keepAlive = keepAlive

        self.connectEvent = threading.Event()

        # If we are disconnected we lose all our active subscriptions.  Keep
        # track of all subscriptions so that we can internally restore all
        # subscriptions on reconnect
        # Also, create a lock for gating access to the subscription dictionary
        # Finally, create an Event that allows us to track the first subscriptions being made
        self._subscriptions = {}
        self._subLock = threading.Lock()
        self.subscriptionsAcknowledged = threading.Event()

        # Create a map to contain mids for onPublish() callback handling.
        # and a lock to gate access to the dictionary
        self._onPublishCallbacks = {}
        self._messagesLock = threading.Lock()

        self.clientId = clientId

        # Configure logging
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.logger.setLevel(logLevel)

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
            # Generate a default stream handler
            fhFormatter = logging.Formatter("%(asctime)-25s %(name)-25s " + " %(levelname)-7s %(message)s")
            ch = logging.StreamHandler()
            ch.setFormatter(fhFormatter)

            self.logger.addHandler(ch)

        # This will be used as a MQTTv5 connect user property once v5 support is added.
        # For now it's just a useful debug message logged when we connect
        self.userAgent = "MQTT/3.1.1 (%s %s) Paho/%s (Python) WIoTP/%s (Python)" % (
            platform.system(),
            platform.release(),
            pahoVersion,
            wiotpVersion,
        )
        self.client = paho.Client(self.clientId, transport=transport, clean_session=(not cleanStart))

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
            self.logger.warning(
                "Unable to encrypt messages because client configuration has overridden port selection to an insecure port (%s)"
                % self.port
            )
        elif self.port in [443, 8883]:
            self.tlsVersion = ssl.PROTOCOL_TLSv1_2
            # We allow an exception to raise here if running in an environment where
            # TLS 1.2 is unavailable because the configuration explicitly requested
            # to use encrypted connection
        elif self.port is None:
            if self.organization == "quickstart":
                self.tlsVersion = None
                self.port = 1883
            else:
                try:
                    self.tlsVersion = ssl.PROTOCOL_TLSv1_2
                    self.port = 8883
                except:
                    self.tlsVersion = None
                    self.port = 1883
                    self.logger.warning(
                        "Unable to encrypt messages because TLSv1.2 is unavailable (MQTT over SSL requires at least Python v2.7.9 or 3.4 and openssl v1.0.1)"
                    )
        else:
            raise Exception("Unsupported value for port override: %s.  Supported values are 1883 & 8883." % self.port)

        # Configure authentication
        if self.username is not None:
            # In environments where either ssl is not available, or TLSv1.2 is not available we will fallback to MQTT over TCP
            if self.tlsVersion is not None:
                # Path to default CA certificate if none provided
                if caFile is None:
                    caFile = os.path.dirname(os.path.abspath(__file__)) + "/messaging.pem"

                self.client.tls_set(
                    ca_certs=caFile,
                    certfile=None,
                    keyfile=None,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2,
                )
            self.client.username_pw_set(self.username, self.password)

        # Attach MQTT callbacks
        self.client.on_log = self._onLog
        self.client.on_connect = self._onConnect
        self.client.on_disconnect = self._onDisconnect
        self.client.on_publish = self._onPublish
        self.client.on_subscribe = self._onSubscribe

        # User configurable callback methods
        self.subscriptionCallback = None

        # Initialize default message encoders and decoders.
        self._messageCodecs = {}

        self.setMessageCodec("json", JsonCodec)
        self.setMessageCodec("raw", RawCodec)
        self.setMessageCodec("utf8", Utf8Codec)

    def getMessageCodec(self, messageFormat):
        """
        Get the Python class that is currently defined as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retrieve the encoder for
        
        # Returns
        code (class): The python class, or `None` if there is no codec defined for the `messageFormat`
        """
        if messageFormat not in self._messageCodecs:
            return None
        return self._messageCodecs[messageFormat]

    def setMessageCodec(self, messageFormat, codec):
        """
        Set a Python class as the encoder/decoder for a specified message format.
        
        # Arguments
        messageFormat (string): The message format to retreive the encoder for
        codec (class): The Python class (subclass of `wiotp.common.MessageCodec` to set as the encoder/decoder for `messageFormat`
        """
        self._messageCodecs[messageFormat] = codec

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
        self.logger.debug(
            "Connecting... (address = %s, port = %s, clientId = %s, username = %s)"
            % (self.address, self.port, self.clientId, self.username)
        )
        try:
            self.connectEvent.clear()
            self.logger.debug(
                "Connecting with clientId %s to host %s on port %s with keepAlive set to %s"
                % (self.clientId, self.address, self.port, self.keepAlive)
            )
            self.logger.debug("User-Agent: %s" % self.userAgent)
            self.client.connect(self.address, port=self.port, keepalive=self.keepAlive)
            self.client.loop_start()
            if not self.connectEvent.wait(timeout=60):
                self.client.loop_stop()
                self._logAndRaiseException(
                    ConnectionException(
                        "Operation timed out connecting to IBM Watson IoT Platform: %s" % (self.address)
                    )
                )

        except socket.error as serr:
            self.client.loop_stop()
            self._logAndRaiseException(
                ConnectionException("Failed to connect to IBM Watson IoT Platform: %s - %s" % (self.address, str(serr)))
            )

    def disconnect(self):
        """
        Disconnect the client from IBM Watson IoT Platform
        """
        # self.logger.info("Closing connection to the IBM Watson IoT Platform")
        self.client.disconnect()
        # If we don't call loop_stop() it appears we end up with a zombie thread which continues to process
        # network traffic, preventing any subsequent attempt to reconnect using connect()
        self.client.loop_stop()
        self.logger.info("Closed connection to the IBM Watson IoT Platform")

    def isConnected(self):
        return self.connectEvent.isSet()

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

    def _onConnect(self, mqttc, userdata, flags, rc):
        """
        Called when the broker responds to our connection request.

        The value of rc determines success or not:
            0: Connection successful
            1: Connection refused - incorrect protocol version
            2: Connection refused - invalid client identifier
            3: Connection refused - server unavailable
            4: Connection refused - bad username or password
            5: Connection refused - not authorised
            6-255: Currently unused.
        """
        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s" % (self.clientId))

            # Restoring previous subscriptions
            with self._subLock:
                if len(self._subscriptions) > 0:
                    for subscription in self._subscriptions:
                        # We use the underlying mqttclient subscribe method rather than _subscribe because we are
                        # claiming a lock on the subscriptions list and do not want anything else to modify it,
                        # which that method does
                        (result, mid) = self.client.subscribe(subscription, qos=self._subscriptions[subscription])
                        if result != paho.MQTT_ERR_SUCCESS:
                            self._logAndRaiseException(ConnectionException("Unable to subscribe to %s" % subscription))
                    self.logger.debug("Restored %s previous subscriptions" % len(self._subscriptions))
        elif rc == 1:
            self._logAndRaiseException(ConnectionException("Incorrect protocol version"))
        elif rc == 2:
            self._logAndRaiseException(ConnectionException("Invalid client identifier"))
        elif rc == 3:
            self._logAndRaiseException(ConnectionException("Server unavailable"))
        elif rc == 4:
            self._logAndRaiseException(
                ConnectionException("Bad username or password: (%s, %s)" % (self.username, self.password))
            )
        elif rc == 5:
            self._logAndRaiseException(
                ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password))
            )
        else:
            self._logAndRaiseException(ConnectionException("Unexpected connection failure: %s" % (rc)))

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
        # Clear the event to indicate we're no longer connected
        self.connectEvent.clear()

        if rc != 0:
            self.logger.error("Unexpected disconnect from IBM Watson IoT Platform: %d" % (rc))
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

    def _onSubscribe(self, mqttc, userdata, mid, grantedQoS):
        self.subscriptionsAcknowledged.set()
        self.logger.debug("Subscribe callback: mid: %s qos: %s" % (mid, grantedQoS))
        if self.subscriptionCallback:
            self.subscriptionCallback(mid, grantedQoS)

    def _subscribe(self, topic, qos=1):
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to %s because client is in disconnected state" % (topic))
            return 0
        else:
            (result, mid) = self.client.subscribe(topic, qos=qos)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = qos
                return mid
            else:
                return 0

    def _publishEvent(self, topic, event, msgFormat, data, qos=0, onPublish=None):
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to send event %s because client is is disconnected state", event)
            return False
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                # The data object may not be serializable, e.g. if using a custom binary format
                try:
                    dataString = json.dumps(data)
                except:
                    dataString = str(data)
                self.logger.debug("Sending event %s with data %s" % (event, dataString))

            # Raise an exception if there is no codec for this msgFormat
            if self.getMessageCodec(msgFormat) is None:
                raise MissingMessageEncoderException(msgFormat)

            payload = self.getMessageCodec(msgFormat).encode(data, datetime.now(pytz.timezone("UTC")))

            result = self.client.publish(topic, payload=payload, qos=qos, retain=False)
            if result[0] == paho.MQTT_ERR_SUCCESS:
                # Because we are dealing with aync pub/sub model and callbacks it is possible that
                # the _onPublish() callback for this mid is called before we obtain the lock to place
                # the mid into the _onPublishCallbacks list.
                #
                # _onPublish knows how to handle a scenario where the mid is not present (no nothing)
                # in this scenario we will need to invoke the callback directly here, because at the time
                # the callback was invoked the mid was not yet in the list.
                with self._messagesLock:
                    if result[1] in self._onPublishCallbacks:
                        # Paho callback beat this thread so call callback inline now
                        del self._onPublishCallbacks[result[1]]
                        if onPublish is not None:
                            onPublish()
                    else:
                        # This thread beat paho callback so set up for call later
                        self._onPublishCallbacks[result[1]] = onPublish
                return True
            else:
                return False
