# *****************************************************************************
# Copyright (c) 2016, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
import re
import pytz
import uuid
import threading
import requests
import logging
import paho.mqtt.client as paho

from datetime import datetime

from ibmiotf import AbstractClient, InvalidEventException, UnsupportedAuthenticationMethod,ConfigurationException, ConnectionException, MissingMessageEncoderException,MissingMessageDecoderException
from ibmiotf.codecs import jsonCodec
from ibmiotf.device import DeviceClient
from ibmiotf.device.command import Command
from ibmiotf.gateway.config import GatewayClientConfig
from ibmiotf.gateway.messages import Notification
from ibmiotf import api

# Support Python 2.7 and 3.4 versions of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser



class GatewayClient(DeviceClient):

    def __init__(self, config, logHandlers=None):
        """
        Override the constructor
        """
        self._config = GatewayClientConfig(**config)

        AbstractClient.__init__(
            self,
            domain = self._config.domain,
            organization = self._config.orgId,
            clientId = self._config.clientId,
            username = self._config.username,
            password = self._config.password,
            logHandlers = logHandlers,
            cleanSession = self._config.cleanSession,
            port = self._config.port,
            transport = self._config.transport
        )

        self.COMMAND_TOPIC = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/cmd/+/fmt/+"

        # Add handler for subscriptions
        self.client.on_subscribe = self._onSubscribe

        gatewayCommandTopic = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/cmd/+/fmt/json"
        deviceCommandTopic = "iot-2/type/+/id/+/cmd/+/fmt/+"
        messageNotificationTopic = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/notify"
        
        self.client.message_callback_add(gatewayCommandTopic, self._onCommand)
        self.client.message_callback_add(deviceCommandTopic, self._onDeviceCommand)
        self.client.message_callback_add(messageNotificationTopic, self._onMessageNotification)

        # Initialize user supplied callback
        self.commandCallback = None
        self.deviceCommandCallback = None
        self.notificationCallback = None
        self.subscriptionCallback = None
        self.client.on_connect = self._onConnect
        self.client.on_disconnect = self._onDisconnect
        self.setMessageEncoderModule('json', jsonCodec)

        # Create api key for gateway authentication
        self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.api = api.ApiClient({"org": self._config.orgId,"auth-token": self._config.apiToken,"auth-key": self._config.apiKey}, self.logger)


    def _onConnect(self, client, userdata, flags, rc):
        '''
        Called when the broker responds to our connection request.

        The value of rc determines success or not:
            0: Connection successful
            1: Connection refused - incorrect protocol version
            2: Connection refused - invalid client identifier
            3: Connection refused - server unavailable
            4: Connection refused - bad username or password
            5: Connection refused - not authorised
            6-255: Currently unused.
        '''
        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s" % (self.clientId))

            # Restoring previous subscriptions
            with self._subLock:
                if len(self._subscriptions) > 0:
                    for subscription in self._subscriptions:
                        self.client.subscribe(subscription, qos=self._subscriptions[subscription])
                    self.logger.debug("Restored %s previous subscriptions" % len(self._subscriptions))
        elif rc == 1:
            self._logAndRaiseException(ConnectionException("Incorrect protocol version"))
        elif rc == 2:
            self._logAndRaiseException(ConnectionException("Invalid client identifier"))
        elif rc == 3:
            self._logAndRaiseException(ConnectionException("Server unavailable"))
        elif rc == 4:
            self._logAndRaiseException(ConnectionException("Bad username or password: (%s, %s)" % (self.username, self.password))            )
        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Unexpected connection failure: %s" % (rc)))


    def publishDeviceEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
        topic = 'iot-2/type/' + deviceType + '/id/' + deviceId +'/evt/'+event+'/fmt/' + msgFormat
        return self._publishEvent(topic, event, msgFormat, data, qos, on_publish)


    def publishEvent(self, event, msgFormat, data, qos=0, on_publish=None):
        topic = 'iot-2/type/' + self._config.typeId + '/id/' + self._config.deviceId +'/evt/' + event + '/fmt/' + msgFormat
        return self._publishEvent(topic, event, msgFormat, data, qos, on_publish)


    def subscribeToDeviceCommands(self, deviceType, deviceId, command='+', format='json', qos=1):
        topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
        return self._subscribe(topic, qos=1)


    def subscribeToCommands(self, command='+', format='json', qos=1):
        deviceType = self._config.typeId
        deviceId = self._config.deviceId
        topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
        return self._subscribe(topic, qos=1)


    def _subscribe(self, topic, qos=1):
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to %s because gateway is not currently connected" % (topic))
            return 0
        else:
            (result, mid) = self.client.subscribe(topic, qos=qos)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = qos
                return mid
            else:
                return 0


    def subscribeToNotifications(self):
        deviceType = self._config.typeId
        deviceId = self._config.deviceId
        topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/notify'

        return self._subscribe(topic, qos=0)


    def _onSubscribe(self, client, userdata, mid, grantedQoS):
        '''
        Internal callback for handling subscription acknowledgement
        '''
        self.logger.debug("Subscribe callback: mid: %s qos: %s" % (mid, grantedQoS))
        if self.subscriptionCallback: self.subscriptionCallback(mid, grantedQoS)


    def _onCommand(self, client, userdata, pahoMessage):
        '''
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        '''
        try:
            command = Command(pahoMessage, self._messageEncoderModules)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received device command '%s'" % (command.command))
            if self.commandCallback: self.commandCallback(command)


    def _onDeviceCommand(self, client, userdata, pahoMessage):
        '''
        Internal callback for gateway command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        '''
        try:
            command = Command(pahoMessage, self._messageEncoderModules)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received gateway command '%s'" % (command.command))
            if self.deviceCommandCallback: self.deviceCommandCallback(command)


    def _onMessageNotification(self, client, userdata, pahoMessage):
        '''
        Internal callback for gateway notification messages, parses source device from topic string and
        passes the information on to the registered device command callback
        '''
        try:
            note = Notification(pahoMessage, self._messageEncoderModules)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received Notification")
            if self.notificationCallback: self.notificationCallback(note)
