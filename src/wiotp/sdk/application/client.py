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

from wiotp.sdk import ConnectionException, MissingMessageEncoderException, AbstractClient, InvalidEventException
from wiotp.sdk.application.messages import Status, Command, Event, State, Error, ThingError, DeviceState
from wiotp.sdk.application.config import ApplicationClientConfig
from wiotp.sdk.api import ApiClient, Registry, Usage, ServiceStatus, DSC, LEC, Mgmt, ServiceBindings, Actions, StateMgr

import paho.mqtt.client as paho

import requests


class ApplicationClient(AbstractClient):
    """
    Extends #wiotp.AbstractClient to implement an application client supporting 
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
            domain=self._config.domain,
            organization=self._config.orgId,
            clientId=self._config.clientId,
            username=self._config.username,
            password=self._config.password,
            logHandlers=logHandlers,
            cleanStart=self._config.cleanStart,
            port=self._config.port,
            transport=self._config.transport,
            caFile=self._config.caFile,
        )

        # Add handlers for events and status
        self.client.message_callback_add("iot-2/type/+/id/+/evt/+/fmt/+", self._onDeviceEvent)
        self.client.message_callback_add("iot-2/type/+/id/+/mon", self._onDeviceStatus)
        self.client.message_callback_add("iot-2/app/+/mon", self._onAppStatus)
        self.client.message_callback_add("iot-2/type/+/id/+/intf/+/evt/state", self._onDeviceState)
        self.client.message_callback_add("iot-2/thing/type/+/id/+/intf/+/evt/state", self._onThingState)
        self.client.message_callback_add("iot-2/type/+/id/+/err/data", self._onErrorTopic)
        self.client.message_callback_add("iot-2/thing/type/+/id/+/err/data", self._onThingError)

        # Add handler for commands if not connected to QuickStart
        if not self._config.isQuickstart():
            self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self._onDeviceCommand)

        # Attach fallback handler
        self.client.on_message = self._onUnsupportedMessage

        # Initialize user supplied callbacks
        self.deviceEventCallback = None
        self.deviceCommandCallback = None
        self.deviceStateCallback = None
        self.deviceStatusCallback = None
        self.thingStateCallback = None
        self.errorTopicCallback = None
        self.appStatusCallback = None

        # Create an api client if not connected in QuickStart mode
        if not self._config.isQuickstart():
            apiClient = ApiClient(self._config, self.logger)
            self.registry = Registry(apiClient)
            self.usage = Usage(apiClient)
            self.dsc = DSC(apiClient)
            self.lec = LEC(apiClient)
            self.mgmt = Mgmt(apiClient)
            self.serviceBindings = ServiceBindings(apiClient)
            self.actions = Actions(apiClient)
            self.state = StateMgr(apiClient)

            # We directly expose the get() method via self.serviceStatus()
            self._serviceStatus = ServiceStatus(apiClient)

    def serviceStatus(self):
        if not self._config.isQuickstart():
            return self._serviceStatus.get()
        else:
            return None

    def subscribeToDeviceEvents(self, typeId="+", deviceId="+", eventId="+", msgFormat="+", qos=0):
        """
        Subscribe to device event messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        deviceId (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
        eventId (string): eventId for the subscription, optional.  Defaults to all events (MQTT `+` wildcard)
        msgFormat (string): msgFormat for the subscription, optional.  Defaults to all formats (MQTT `+` wildcard)
        qos (int): MQTT quality of service level to use (`0`, `1`, or `2`)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart() and deviceId == "+":
            self.logger.warning(
                "QuickStart applications do not support wildcard subscription to events from all devices"
            )
            return 0

        topic = "iot-2/type/%s/id/%s/evt/%s/fmt/%s" % (typeId, deviceId, eventId, msgFormat)
        return self._subscribe(topic, qos)

    def subscribeToDeviceStatus(self, typeId="+", deviceId="+"):
        """
        Subscribe to device status messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
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

        topic = "iot-2/type/%s/id/%s/mon" % (typeId, deviceId)
        return self._subscribe(topic, 0)

    def subscribeToErrorTopic(self, typeId="+", Id="+"):
        """
        Subscribe to device error messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        Id (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart() and Id == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to error topics")
            return 0

        topic = "iot-2/type/%s/id/%s/err/data" % (typeId, Id)
        return self._subscribe(topic, 0)

    def subscribeToThingErrors(self, typeId="+", Id="+"):
        """
        Subscribe to thingerror messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all thing types (MQTT `+` wildcard)
        Id (string): thingId for the subscription, optional.  Defaults to all things (MQTT `+` wildcard)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart() and Id == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to error topics")
            return 0

        topic = "iot-2/thing/type/%s/id/%s/err/data" % (typeId, Id)
        return self._subscribe(topic, 0)

    def subscribeToThingState(self, typeId="+", thingId="+", logicalInterfaceId="+"):
        """
        Subscribe to thing state messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all thing types (MQTT `+` wildcard)
        thingId (string): thingId for the subscription, optional.  Defaults to all things (MQTT `+` wildcard)
        logicalInterfaceId (string): logicalInterfaceId for the subscription, optional.  Defaults to all LIs (MQTT `+` wildcard)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart():
            self.logger.warning("QuickStart applications do not support thing state")
            return 0

        topic = "iot-2/thing/type/%s/id/%s/intf/%s/evt/state" % (typeId, thingId, logicalInterfaceId)
        return self._subscribe(topic, 0)

    def subscribeToDeviceState(self, typeId="+", deviceId="+", logicalInterfaceId="+"):
        """
        Subscribe to device state messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all thing types (MQTT `+` wildcard)
        deviceId (string): thingId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
        logicalInterfaceId (string): logicalInterfaceId for the subscription, optional.  Defaults to all LIs (MQTT `+` wildcard)

        # Returns
        int: If the subscription was successful then the return Message ID (mid) for the subscribe request
            will be returned. The mid value can be used to track the subscribe request by checking against
            the mid argument if you register a subscriptionCallback method.
            If the subscription fails then the return value will be `0`
        """
        if self._config.isQuickstart():
            self.logger.warning("QuickStart applications do not support device state")
            return 0

        topic = "iot-2/type/%s/id/%s/intf/%s/evt/state" % (typeId, deviceId, logicalInterfaceId)
        return self._subscribe(topic, 0)

    def subscribeToDeviceCommands(self, typeId="+", deviceId="+", commandId="+", msgFormat="+"):
        """
        Subscribe to device command messages

        # Parameters
        typeId (string): typeId for the subscription, optional.  Defaults to all device types (MQTT `+` wildcard)
        deviceId (string): deviceId for the subscription, optional.  Defaults to all devices (MQTT `+` wildcard)
        commandId (string): commandId for the subscription, optional.  Defaults to all commands (MQTT `+` wildcard)
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

        topic = "iot-2/type/%s/id/%s/cmd/%s/fmt/%s" % (typeId, deviceId, commandId, msgFormat)
        return self._subscribe(topic, 0)

    def publishEvent(self, typeId, deviceId, eventId, msgFormat, data, qos=0, onPublish=None):
        topic = "iot-2/type/%s/id/%s/evt/%s/fmt/%s" % (typeId, deviceId, eventId, msgFormat)
        return self._publishEvent(topic, eventId, msgFormat, data, qos, onPublish)

    def publishCommand(self, typeId, deviceId, commandId, msgFormat, data=None, qos=0, onPublish=None):
        """
        Publish a command to a device

        # Parameters
        typeId (string) : The type of the device this command is to be published to
        deviceId (string): The id of the device this command is to be published to
        command (string) : The name of the command
        msgFormat (string) : The format of the command payload
        data (dict) : The command data
        qos (int) : The equivalent MQTT semantics of quality of service using the same constants (optional, defaults to `0`)
        onPublish (function) : A function that will be called when receipt of the publication is confirmed.  This has
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
            topic = "iot-2/type/%s/id/%s/cmd/%s/fmt/%s" % (typeId, deviceId, commandId, msgFormat)

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
                        if onPublish is not None:
                            onPublish()
                    else:
                        # this thread beat paho callback so set up for call later
                        self._onPublishCallbacks[result[1]] = onPublish
                return True
            else:
                return False

    def _onUnsupportedMessage(self, client, userdata, message):
        """
        Internal callback for messages that have not been handled by any of the specific internal callbacks, these
        messages are not passed on to any user provided callback
        """
        self.logger.warning(
            "Received messaging on unsupported topic '%s' on topic '%s'" % (message.payload, message.topic)
        )

    def _onDeviceEvent(self, client, userdata, pahoMessage):
        """
        Internal callback for device event messages, parses source device from topic string and
        passes the information on to the registerd device event callback
        """
        try:
            event = Event(pahoMessage, self._messageCodecs)
            self.logger.debug("Received event '%s' from %s:%s" % (event.eventId, event.typeId, event.deviceId))
            if self.deviceEventCallback:
                self.deviceEventCallback(event)
        except InvalidEventException as e:
            self.logger.critical(str(e))

    def _onThingState(self, client, userdata, pahoMessage):
        """
        Internal callback for thing state messages, parses source thing from topic string and
        passes the information on to the registerd thing state callback
        """
        try:
            state = State(pahoMessage)
            self.logger.debug("Received state from %s:%s" % (state.typeId, state.thingId))
            if self.thingStateCallback:
                self.thingStateCallback(state)
        except InvalidEventException as e:
            self.logger.critical(str(e))

    def _onDeviceState(self, client, userdata, pahoMessage):
        """
        Internal callback for thing state messages, parses source thing from topic string and
        passes the information on to the registerd thing state callback
        """
        try:
            state = DeviceState(pahoMessage)
            self.logger.debug("Received state from %s:%s" % (state.typeId, state.deviceId))
            if self.deviceStateCallback:
                self.deviceStateCallback(state)
        except InvalidEventException as e:
            self.logger.critical(str(e))

    def _onErrorTopic(self, client, userdata, pahoMessage):
        """
        Internal callback for error messages, parses source thing/device from topic string and
        passes the information on to the registerd error callback
        """
        try:
            error = Error(pahoMessage)
            self.logger.debug("Received error from device %s:%s" % (error.typeId, error.id))
            if self.errorTopicCallback:
                self.errorTopicCallback(error)
        except InvalidEventException as e:
            self.logger.critical(str(e))

    def _onThingError(self, client, userdata, pahoMessage):
        """
        Internal callback for error messages, parses source thing/device from topic string and
        passes the information on to the registerd error callback
        """
        try:
            error = ThingError(pahoMessage)
            self.logger.debug("Received error from thing %s:%s" % (error.typeId, error.id))
            if self.errorTopicCallback:
                self.errorTopicCallback(error)
        except InvalidEventException as e:
            self.logger.critical(str(e))

    def _onDeviceCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registerd device command callback
        """
        try:
            command = Command(pahoMessage, self._messageCodecs)
            self.logger.debug(
                "Received command '%s' from %s:%s" % (command.commandId, command.typeId, command.deviceId)
            )
            if self.deviceCommandCallback:
                self.deviceCommandCallback(command)
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
            if self.deviceStatusCallback:
                self.deviceStatusCallback(status)
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
            if self.appStatusCallback:
                self.appStatusCallback(status)
        except InvalidEventException as e:
            self.logger.critical(str(e))
