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

from ibmiotf import ConnectionException, MissingMessageEncoderException
from ibmiotf.codecs import jsonCodec
from ibmiotf.application.messages import Status, Command, Event
import ibmiotf.api
import paho.mqtt.client as paho

import requests


class Client(ibmiotf.AbstractClient):
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

    def __init__(self, options, logHandlers=None):
        self._options = options

        username = None
        password = None

        ### DEFAULTS ###
        if "domain" not in self._options:
            # Default to the domain for the public cloud offering
            self._options['domain'] = "internetofthings.ibmcloud.com"
            
        if "clean-session" not in self._options:
            self._options['clean-session'] = "true"
            
        ### REQUIRED ###
        if 'auth-key' not in self._options or self._options['auth-key'] is None:
            # Configure for Quickstart
            self._options['org'] = "quickstart"
            self._options['port'] = 1883
        else:
            # Get the orgId from the apikey (format: a-orgid-randomness)
            self._options['org'] = self._options['auth-key'].split("-")[1]

            if 'auth-token' not in self._options or self._options['auth-token'] == None:
                raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

            username = self._options['auth-key']
            password = self._options['auth-token']

        # Generate an application ID if one is not supplied
        if 'id' not in self._options or self._options['id'] == None:
            self._options['id'] = str(uuid.uuid4())

        clientIdPrefix = "a" if ('type' not in self._options or self._options['type'] == 'standalone') else "A"

        # Call parent constructor
        ibmiotf.AbstractClient.__init__(
            self,
            domain = self._options['domain'],
            organization = self._options['org'],
            clientId = clientIdPrefix + ":" + self._options['org'] + ":" + self._options['id'],
            username = username,
            password = password,
            logHandlers = logHandlers,
            cleanSession = self._options['clean-session'],
            port = self._options.get('port', None),
            transport = self._options.get('transport', 'tcp')
        )

        # Add handler for subscriptions
        self.client.on_subscribe = self.__onSubscribe

        # Add handlers for events and status
        self.client.message_callback_add("iot-2/type/+/id/+/evt/+/fmt/+", self.__onDeviceEvent)
        self.client.message_callback_add("iot-2/type/+/id/+/mon", self.__onDeviceStatus)
        self.client.message_callback_add("iot-2/app/+/mon", self.__onAppStatus)

        # Add handler for commands if not connected to QuickStart
        if self._options['org'] != "quickstart":
            self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self.__onDeviceCommand)

        # Attach fallback handler
        self.client.on_message = self.__onUnsupportedMessage

        # Initialize user supplied callbacks (devices)
        self.deviceEventCallback = None
        self.deviceCommandCallback = None
        self.deviceStatusCallback = None
        self.subscriptionCallback = None

        # Initialize user supplied callbacks (applcations)
        self.appStatusCallback = None

        self.client.on_connect = self._onConnect

        self.setMessageEncoderModule('json', jsonCodec)

        # Create an api client if not connected in QuickStart mode
        if self._options['org'] != "quickstart":
            self.api = ibmiotf.api.ApiClient(self._options, self.logger)

        self.orgId = self._options['org']
        self.appId = self._options['id']


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
        if self._options['org'] == "quickstart" and deviceId == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to events from all devices")
            return 0

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to events (%s, %s, %s) because application is not currently connected" % (deviceType, deviceId, event))
            return 0
        else:
            topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)
            (result, mid) = self.client.subscribe(topic, qos=qos)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = qos
                return mid
            else:
                return 0


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
        
        if self._options['org'] == "quickstart" and deviceId == "+":
            self.logger.warning("QuickStart applications do not support wildcard subscription to device status")
            return 0

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to device status (%s, %s) because application is not currently connected" % (deviceType, deviceId))
            return 0
        else:
            topic = 'iot-2/type/%s/id/%s/mon' % (deviceType, deviceId)
            (result, mid) = self.client.subscribe(topic, qos=0)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = 0
                return mid
            else:
                return 0


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
        
        if self._options['org'] == "quickstart":
            self.logger.warning("QuickStart applications do not support commands")
            return 0

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to commands (%s, %s, %s) because application is not currently connected" % (deviceType, deviceId, command))
            return 0
        else:
            topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)
            (result, mid) = self.client.subscribe(topic, qos=1)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = 1
                return mid
            else:
                return 0


    def publishEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
        """
        Publish an event on behalf of a device.

        # Parameters
        deviceType (string): The typeId of the device this event is to be published from
        deviceId (string): The deviceId of the device this event is to be published from
        event (string): The name of this event
        msgFormat (string): The format of the data for this event
        data (dict) : The data for this event
        qos (int) : The equivalent MQTT semantics of quality of service using the same constants (optional, defaults to `0`)
        on_publish (function) : A function that will be called when receipt of the publication is confirmed.  This
            has different implications depending on the qos:
            - qos 0 : the client has asynchronously begun to send the event
            - qos 1 and 2 : the client has confirmation of delivery from IoTF
        """
        
        if not self.connectEvent.wait(timeout=10):
            return False
        else:
            topic = 'iot-2/type/%s/id/%s/evt/%s/fmt/%s' % (deviceType, deviceId, event, msgFormat)

            if msgFormat in self._messageEncoderModules:
                payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now())
                result = self.client.publish(topic, payload=payload, qos=qos, retain=False)
                if result[0] == paho.MQTT_ERR_SUCCESS:
                    # Because we are dealing with aync pub/sub model and callbacks it is possible that 
                    # the _onPublish() callback for this mid is called before we obtain the lock to place
                    # the mid into the _onPublishCallbacks list.
                    #
                    # _onPublish knows how to handle a scenario where the mid is not present (do nothing)
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
            else:
                raise MissingMessageEncoderException(msgFormat)


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
        if self._options['org'] == "quickstart":
            self.logger.warning("QuickStart applications do not support sending commands")
            return False
        if not self.connectEvent.wait(timeout=10):
            return False
        else:
            topic = 'iot-2/type/%s/id/%s/cmd/%s/fmt/%s' % (deviceType, deviceId, command, msgFormat)

            if msgFormat in self._messageEncoderModules:
                payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now())
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
            else:
                raise MissingMessageEncoderException(msgFormat)


    def _onConnect(self, mqttc, userdata, flags, rc):
        """
        This is called after the client has received a `CONNACK` message 
        from the broker in response to calling connect().
        
        See [paho.mqtt.python#on_connect](https://github.com/eclipse/paho.mqtt.python#on_connect) for more information
        
        # Parameters
        mqttc (paho.mqtt.client.Client): The client instance for this callback
        userdata: The private user data as set in `Client()` or `user_data_set()`
        flags: response flags sent by the broker
        rc (int): the connection result.
        
        The value of `rc` indicates success or not

        - `0` Success
        - `1` Refused - incorrect protocol version
        - `2` Refused - invalid client identifier
        - `3` Refused - server unavailable
        - `4` Refused - bad user name or password
        - `5` Refused - not authorised
        """

        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s" % (self.clientId))

            # Restoring previous subscriptions
            with self._subLock:
                if len(self._subscriptions) > 0:
                    for subscription in self._subscriptions:
                        self.client.subscribe(subscription, qos=self._subscriptions[subscription])
                    self.logger.debug("Restored %s previous subscriptions" % len(self._subscriptions))

        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


    def __onSubscribe(self, client, userdata, mid, grantedQoS):
        """
        Internal callback for handling subscription acknowledgement
        """
        self.logger.debug("Subscribe callback: mid: %s qos: %s" % (mid, grantedQoS))
        if self.subscriptionCallback: self.subscriptionCallback(mid, grantedQoS)


    def __onUnsupportedMessage(self, client, userdata, message):
        """
        Internal callback for messages that have not been handled by any of the specific internal callbacks, these
        messages are not passed on to any user provided callback
        """
        self.logger.warning("Received messaging on unsupported topic '%s' on topic '%s'" % (message.payload, message.topic))


    def __onDeviceEvent(self, client, userdata, pahoMessage):
        """
        Internal callback for device event messages, parses source device from topic string and
        passes the information on to the registerd device event callback
        """
        try:
            event = Event(pahoMessage, self._messageEncoderModules)
            self.logger.debug("Received event '%s' from %s:%s" % (event.event, event.deviceType, event.deviceId))
            if self.deviceEventCallback: self.deviceEventCallback(event)
        except ibmiotf.InvalidEventException as e:
            self.logger.critical(str(e))


    def __onDeviceCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registerd device command callback
        """
        try:
            command = Command(pahoMessage, self._messageEncoderModules)
            self.logger.debug("Received command '%s' from %s:%s" % (command.command, command.deviceType, command.deviceId))
            if self.deviceCommandCallback: self.deviceCommandCallback(command)
        except ibmiotf.InvalidEventException as e:
            self.logger.critical(str(e))


    def __onDeviceStatus(self, client, userdata, pahoMessage):
        """
        Internal callback for device status messages, parses source device from topic string and
        passes the information on to the registerd device status callback
        """

        try:
            status = Status(pahoMessage)
            self.logger.debug("Received %s action from %s:%s" % (status.action, status.deviceType, status.deviceId))
            if self.deviceStatusCallback: self.deviceStatusCallback(status)
        except ibmiotf.InvalidEventException as e:
            self.logger.critical(str(e))


    def __onAppStatus(self, client, userdata, message):
        """
        Internal callback for application command messages, parses source application from topic string and
        passes the information on to the registerd applicaion status callback
        """

        statusMatchResult = self.__appStatusPattern.match(message.topic)
        if statusMatchResult:
            self.logger.debug("Received application status '%s' on topic '%s'" % (message.payload, message.topic))
            status = json.loads(str(message.payload))
            if self.appStatusCallback: self.appStatusCallback(statusMatchResult.group(1), status)
        else:
            self.logger.warning("Received application status on invalid topic: %s" % (message.topic))
