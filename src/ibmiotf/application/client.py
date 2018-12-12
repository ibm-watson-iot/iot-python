# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import os
import re
import json
import iso8601
import uuid
from datetime import datetime

from ibmiotf import ConnectionException, MissingMessageEncoderException, AbstractClient, InvalidEventException
from ibmiotf.application.messages import Status, Command, Event
from ibmiotf.application.config import ApplicationClientConfig
from ibmiotf.api import ApiClient, Registry, Usage, Status, LEC, Mgmt

import paho.mqtt.client as paho

import requests


class Client(AbstractClient):
    """
    Extends #ibmiotf.AbstractClient to implement an application client supporting 
    messaging over MQTT
        
    # Parameters
    options (dict): Configuration options for the client
    logHandlers (list<logging.Handler>): Log handlers to configure.  Defaults to `None`, 
        which will result in a default log handler being created.
    
    # Configuration Options
    The options parameter expects a Python dictionary containing the following keys:
    
    - `auth-key` The API key to to securely connect your application to Watson IoT Platform.
    - `auth-token` An authentication token to securely connect your application to Watson IoT Platform.
    - `clean-session` A boolean value indicating whether to use MQTT clean session.
    """

    def __init__(self, config, logHandlers=None):
        self._config = ApplicationClientConfig(**config)
        # Call parent constructor
        AbstractClient.__init__(
            self,
            domain = self._config.domain,
            organization = self._config.orgId,
            clientId = self._config.clientId,
            username = self._config.username,
            password = self._config.password,
            logHandlers = logHandlers,
            cleanStart = self._config.cleanStart,
            port = self._config.port,
            transport = self._config.transport
        )

        # Add handlers for events and status
        self.client.message_callback_add("iot-2/type/+/id/+/evt/+/fmt/+", self._onDeviceEvent)
        self.client.message_callback_add("iot-2/type/+/id/+/mon", self._onDeviceStatus)
        self.client.message_callback_add("iot-2/app/+/mon", self._onAppStatus)

        # Add handler for commands if not connected to QuickStart
        if not self._config.isQuickstart():
            self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self._onDeviceCommand)

        # Attach fallback handler
        self.client.on_message = self._onUnsupportedMessage

        # Initialize user supplied callbacks
        self.deviceEventCallback = None
        self.deviceCommandCallback = None
        self.deviceStatusCallback = None
        self.appStatusCallback = None

        # Create an api client if not connected in QuickStart mode
        if not self._config.isQuickstart():
            apiClient = ApiClient(self._config, self.logger)
            self.registry  = Registry(apiClient)
            self.status    = Status(apiClient)
            self.usage     = Usage(apiClient)
            self.lec       = LEC(apiClient)
            self.mgmt      = Mgmt(apiClient)


    def subscribeToDeviceEvents(self, deviceType="+", deviceId="+", event="+", msgFormat="+", qos=0):
        """
        Subscribe to device event messages

        # Parameters
        deviceType (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        deviceId (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
        event (string): eventId for the subscription, optional.  Defaults to all events (MQTT `+` wildcard)
        msgFormat (string): msgFormat for the subscription, optional.  Defaults to all formats (MQTT `+` wildcard)
        qos (int): MQTT quality of service level to use (`0`, `1`, or `2`)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart() and deviceId == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to events from all devices")
            return 0

        topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)
        return self._subscribe(topic, qos)


    def subscribeToDeviceStatus(self, deviceType="+", deviceId="+"):
        """
        Subscribe to device status messages

        # Parameters
        deviceType (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        deviceId (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart() and deviceId == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to device status")
            return 0
        
        topic = 'iot-2/type/%s/id/%s/mon' % (deviceType, deviceId)
        return self._subscribe(topic, 0)


    def subscribeToDeviceCommands(self, deviceType="+", deviceId="+", command="+", msgFormat="+"):
        """
        Subscribe to device command messages

        # Parameters
        deviceType (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        deviceId (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
        command (string): commandId for the subscription, optional.  Defaults to all commands (MQTT `+` wildcard)
        msgFormat (string): msgFormat for the subscription, optional.  Defaults to all formats (MQTT `+` wildcard)
        qos (int): MQTT quality of service level to use (`0`, `1`, or `2`)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart():
            self.logger.warning("QuickStart applications do not support commands")
            return 0

        topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)
        return self._subscribe(topic, 0)


    def publishEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
        topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)
        return self._publishEvent(topic, event, msgFormat, data, qos, on_publish)


    def publishCommand(self, deviceType, deviceId, command, msgFormat, data=None, qos=0, on_publish=None):
        """
        Publish a command to a device

        # Parameters
        deviceType (string) : The type of the device this command is to be published to
        deviceId (string): The id of the device this command is to be published to
        command (string) : The name of the command
        msgFormat (string) : The format of the command payload
        data (dict) : The command data
        qos (int) : The equivalent MQTT semantics of quality of service using the same constants (optional, defaults to `0`)
        on_publish (function) : A function that will be called when receipt of the publication is confirmed.  This has
            different implications depending on the qos:
            - qos 0 : the client has asynchronously begun to send the event
            - qos 1 and 2 : the client has confirmation of delivery from WIoTP
        """
        if self._config.isQuickstart():
            self.logger.warning("QuickStart applications do not support sending commands")
            return False
        if not self.connectEvent.wait(timeout=10):
            return False
        else:
            topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)

            # Raise an exception if there is no codec for this msgFormat
            if self.getMessageCodec(msgFormat) is None:
                raise MissingMessageEncoderException(msgFormat)

            payload = self.getMessageCodec(msgFormat).encode(data, datetime.now())
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
                        # paho callback beat this thread so call callback inline now
                        del self._onPublishCallbacks[result[1]]
                        if on_publish is not None:
                            on_publish()
                    else:
                        # this thread beat paho callback so set up for call later
                        self._onPublishCallbacks[result[1]] = on_publish
                return True
            else:
                return False

    def _onUnsupportedMessage(self, client, userdata, message):
        """
        Internal callback for messages that have not been handled by any of the specific internal callbacks, these
        messages are not passed on to any user provided callback
        """
        self.logger.warning("Received messaging on unsupported topic '%s' on topic '%s'" % (message.payload, message.topic))


    def _onDeviceEvent(self, client, userdata, pahoMessage):
        """
        Internal callback for device event messages, parses source device from topic string and
        passes the information on to the registerd device event callback
        """
        try:
            event = Event(pahoMessage, self._messageCodecs)
            self.logger.debug("Received event '%s' from %s:%s" % (event.event, event.deviceType, event.deviceId))
            if self.deviceEventCallback: self.deviceEventCallback(event)
        except InvalidEventException as e:
            self.logger.critical(str(e))


    def _onDeviceCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registerd device command callback
        """
        try:
            command = Command(pahoMessage, self._messageCodecs)
            self.logger.debug("Received command '%s' from %s:%s" % (command.command, command.deviceType, command.deviceId))
            if self.deviceCommandCallback: self.deviceCommandCallback(command)
        except InvalidEventException as e:
            self.logger.critical(str(e))


    def _onDeviceStatus(self, client, userdata, pahoMessage):
        """
        Internal callback for device status messages, parses source device from topic string and
        passes the information on to the registerd device status callback
        """
        try:
            status = Status(pahoMessage)
            self.logger.debug("Received %s action from %s" % (status.action, status.clientId))
            if self.deviceStatusCallback: self.deviceStatusCallback(status)
        except InvalidEventException as e:
            self.logger.critical(str(e))


    def _onAppStatus(self, client, userdata, pahoMessage):
        """
        Internal callback for application command messages, parses source application from topic string and
        passes the information on to the registerd applicaion status callback
        """
        try:
            status = Status(pahoMessage)
            self.logger.debug("Received %s action from %s" % (status.action, status.clientId))
            if self.appStatusCallback: self.appStatusCallback(status)
        except InvalidEventException as e:
            self.logger.critical(str(e))
