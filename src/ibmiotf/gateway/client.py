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
from ibmiotf.device import DeviceClient
from ibmiotf.device.command import Command
from ibmiotf.gateway.config import GatewayClientConfig
from ibmiotf.gateway.messages import Notification


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
        self.client.on_connect = self._onConnect
        self.client.on_disconnect = self._onDisconnect

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


    def subscribeToNotifications(self):
        deviceType = self._config.typeId
        deviceId = self._config.deviceId
        topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/notify'

        return self._subscribe(topic, qos=0)


    def _onCommand(self, client, userdata, pahoMessage):
        '''
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        '''
        try:
            command = Command(pahoMessage, self._messageCodecs)
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
            command = Command(pahoMessage, self._messageCodecs)
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
            note = Notification(pahoMessage, self._messageCodecs)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received Notification")
            if self.notificationCallback: self.notificationCallback(note)
