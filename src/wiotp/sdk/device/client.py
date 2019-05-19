# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import datetime
import json
import logging
import threading
import paho.mqtt.client as paho
import pytz
from wiotp.sdk import (
    AbstractClient,
    ConfigurationException,
    ConnectionException,
    MissingMessageEncoderException,
    InvalidEventException,
)
from wiotp.sdk.device.command import Command
from wiotp.sdk.device.config import DeviceClientConfig


class DeviceClient(AbstractClient):
    """
    Extends #wiotp.common.AbstractClient to implement a device client supporting 
    messaging over MQTT
    
    # Parameters
    options (dict): Configuration options for the client
    logHandlers (list<logging.Handler>): Log handlers to configure.  Defaults to `None`, 
        which will result in a default log handler being created.
    """

    _COMMAND_TOPIC = "iot-2/cmd/+/fmt/+"

    def __init__(self, config, logHandlers=None):
        self._config = DeviceClientConfig(**config)

        AbstractClient.__init__(
            self,
            domain=self._config.domain,
            organization=self._config.orgId,
            clientId=self._config.clientId,
            username=self._config.username,
            password=self._config.password,
            port=self._config.port,
            transport=self._config.transport,
            cleanStart=self._config.cleanStart,
            sessionExpiry=self._config.sessionExpiry,
            keepAlive=self._config.keepAlive,
            caFile=self._config.caFile,
            logLevel=self._config.logLevel,
            logHandlers=logHandlers,
        )

        # Add handler for commands if not connected to QuickStart
        if not self._config.isQuickstart():
            self.client.message_callback_add("iot-2/cmd/+/fmt/+", self._onCommand)

        # Initialize user supplied callback
        self.commandCallback = None

        # Register startup subscription list (only for non-Quickstart)
        if not self._config.isQuickstart():
            self._subscriptions[self._COMMAND_TOPIC] = 1

    def publishEvent(self, eventId, msgFormat, data, qos=0, onPublish=None):
        """
        Publish an event to Watson IoT Platform.

        # Parameters
        eventId (string): Name of this event
        msgFormat (string): Format of the data for this event
        data (dict): Data for this event
        qos (int): MQTT quality of service level to use (`0`, `1`, or `2`)
        onPublish(function): A function that will be called when receipt 
           of the publication is confirmed.  
        
        # Callback and QoS
        The use of the optional #onPublish function has different implications depending 
        on the level of qos used to publish the event: 
        
        - qos 0: the client has asynchronously begun to send the event
        - qos 1 and 2: the client has confirmation of delivery from the platform
        """
        topic = "iot-2/evt/{eventId}/fmt/{msgFormat}".format(eventId=eventId, msgFormat=msgFormat)
        return self._publishEvent(topic, eventId, msgFormat, data, qos, onPublish)

    def _onCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        """
        try:
            command = Command(pahoMessage, self._messageCodecs)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received command '%s'" % (command.commandId))
            if self.commandCallback:
                self.commandCallback(command)
