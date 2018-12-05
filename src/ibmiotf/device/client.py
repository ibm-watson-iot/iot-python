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
from ibmiotf import AbstractClient, ConfigurationException, ConnectionException, MissingMessageEncoderException, InvalidEventException
from ibmiotf.codecs import jsonCodec
from ibmiotf.device.command import Command
from ibmiotf.device.config import DeviceClientConfig


class DeviceClient(AbstractClient):
    """
    Extends #ibmiotf.AbstractClient to implement a device client supporting 
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

        # Add handler for commands if not connected to QuickStart
        if not self._config.isQuickstart():
            self.client.message_callback_add("iot-2/cmd/+/fmt/+", self._onCommand)

        # Initialize user supplied callback
        self.commandCallback = None

        self.client.on_connect = self._onConnect

        self.setMessageEncoderModule('json', jsonCodec)


    def _onConnect(self, mqttc, userdata, flags, rc):
        """
        This is called after the client has received a CONNACK message 
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
            if not self._config.isQuickstart():
                self._subscribeToCommands()
        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


    def publishEvent(self, event, msgFormat, data, qos=0, on_publish=None):
        """
        Publish an event to Watson IoT Platform.

        # Parameters
        event (string): Name of this event
        msgFormat (string): Format of the data for this event
        data (dict): Data for this event
        qos (int): MQTT quality of service level to use (`0`, `1`, or `2`)
        on_publish(function): A function that will be called when receipt 
           of the publication is confirmed.  
        
        # Callback and QoS
        The use of the optional #on_publish function has different implications depending 
        on the level of qos used to publish the event: 
        
        - qos 0: the client has asynchronously begun to send the event
        - qos 1 and 2: the client has confirmation of delivery from the platform
        """
        topic = "iot-2/evt/{event}/fmt/{msg_format}".format(event=event, msg_format=msgFormat)
        return self._publishEvent(topic, event, msgFormat, data, qos, on_publish)

    def _publishEvent(self, topic, event, msgFormat, data, qos=0, on_publish=None):
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to send event %s because device is not currently connected", event)
            return False
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                # The data object may not be serializable, e.g. if using a custom binary format
                try: 
                    dataString = json.dumps(data)
                except:
                    dataString = str(data)
                self.logger.debug("Sending event %s with data %s" % (event, dataString))

            if msgFormat in self._messageEncoderModules:
                payload = self._messageEncoderModules[msgFormat].encode(data, datetime.now(pytz.timezone('UTC')))

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
                            if on_publish is not None:
                                on_publish()
                        else:
                            # This thread beat paho callback so set up for call later
                            self._onPublishCallbacks[result[1]] = on_publish
                    return True
                else:
                    return False
            else:
                raise MissingMessageEncoderException(msgFormat)


    def _subscribeToCommands(self):
        """
        Subscribe to commands sent to this device.
        """
        if self._config.isQuickstart():
            self.logger.warning("QuickStart applications do not support commands")
            return False

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to commands because device is not currently connected")
            return False
        else:
            self.client.subscribe(self._COMMAND_TOPIC, qos=1)
            return True


    def _onCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for device command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        """
        try:
            command = Command(pahoMessage, self._messageEncoderModules)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received command '%s'" % (command.command))
            if self.commandCallback:
                self.commandCallback(command)
