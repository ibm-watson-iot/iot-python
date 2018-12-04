# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import os
import logging
import re
import uuid
import json
import yaml
import threading
from datetime import datetime

import pytz
import requests
import paho.mqtt.client as paho
from ibmiotf import (
    AbstractClient, HttpAbstractClient, InvalidEventException,
    UnsupportedAuthenticationMethod, ConfigurationException,
    ConnectionException, MissingMessageEncoderException,
    MissingMessageDecoderException)
from ibmiotf.codecs import jsonCodec


# Support Python 2.7 and 3.4 versions of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class Command:
    """
    Represents a command sent to a device.
    
    # Parameters
    pahoMessage (?): ?
    messageEncoderModules (dict): Dictionary of Python modules, keyed to the 
        message format the module should use. 
    
    # Attributes
    command (string): Identifies the command.
    format (string): The format can be any string, for example JSON.
    data (dict): The data for the payload. Maximum length is 131072 bytes.
    timestamp (datetime): The date and time of the event.

    # Raises
    InvalidEventException: If the command was recieved on a topic that does 
        not match the regular expression `iot-2/cmd/(.+)/fmt/(.+)`
    """
    
    _TOPIC_REGEX = re.compile("iot-2/cmd/(.+)/fmt/(.+)")

    def __init__(self, pahoMessage, messageEncoderModules):
        result = Command._TOPIC_REGEX.match(pahoMessage.topic)
        if result:
            self.command = result.group(1)
            self.format = result.group(2)

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))


class Client(AbstractClient):
    """
    Extends #ibmiotf.AbstractClient to implement a device client supporting 
    messaging over MQTT
    
    # Parameters
    options (dict): Configuration options for the client
    logHandlers (list<logging.Handler>): Log handlers to configure.  Defaults to `None`, 
        which will result in a default log handler being created.
        
    # Configuration Options
    The options parameter expects a Python dictionary containing the following keys:
    
    - `orgId` Your organization ID.
    - `type` The type of the device. Think of the device type is analagous to a model number.
    - `id` A unique ID to identify a device. Think of the device id as analagous to a serial number.
    - `auth-method` The method of authentication. The only method that is currently supported is `token`.
    - `auth-token` An authentication token to securely connect your device to Watson IoT Platform.
    - `clean-session` A boolean value indicating whether to use MQTT clean session.
    
    # Publishing events
    Events are the mechanism by which devices publish data to the Watson IoT Platform. The device 
    controls the content of the event and assigns a name for each event that it sends.

    When an event is received by Watson IoT Platform, the credentials of the received event identify 
    the sending device, which means that a device cannot impersonate another device.

    Events can be published with any of the three quality of service (QoS) levels that are defined 
    by the MQTT protocol. By default, events are published with a QoS level of 0.

    ```python
    client.connect()
    qos=0
    myData={'name' : 'foo', 'cpu' : 60, 'mem' : 50}
    client.publishEvent("status", "json", myData, qos)
    ```
    
    # Handling commands
    When the device client connects, it automatically subscribes to any command that is specified for 
    this device. To process specific commands, you need to register a command callback method. 
    
    The messages are returned as an instance of the #Command class

    ```python
    def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)
        if cmd.command == "setInterval":
            if 'interval' not in cmd.data:
                print("Error - command is missing required information: 'interval'")
            else:
                interval = cmd.data['interval']
        elif cmd.command == "print":
            if 'message' not in cmd.data:
                print("Error - command is missing required information: 'message'")
            else:
                print(cmd.data['message'])
    client.connect()
    client.commandCallback = myCommandCallback
    ```

    # Custom message format support
    By default, the message format is set to json, which means that the library supports the encoding 
    and decoding of Python dictionary objects in JSON format. To add support for your own custom message formats, 
    see the Custom Message Format sample.

    When you create a custom encoder module, you must register it in the device client:
    
    ```
    import myCustomCodec

    client.setMessageEncoderModule("custom", myCustomCodec)
    client.publishEvent("status", "custom", myData)
    ```
    
    If an event is sent in an unknown format or if a device does not recognize the format, the device 
    library raises #ibmiotf.MissingMessageDecoderException.
    """
    
    _COMMAND_TOPIC = "iot-2/cmd/+/fmt/+"

    def __init__(self, config, logHandlers=None):
        self._config = config

        self._validateOptions()

        AbstractClient.__init__(
            self,
            domain = self._config['options']['domain'],
            organization = self._config['identity']['orgId'],
            clientId = "d:" + self._config['identity']['orgId'] + ":" + self._config['identity']['typeId'] + ":" + self._config['identity']['deviceId'],
            username = "use-token-auth" if ('auth' in self._config) else None,
            password = self._config['auth']['token'] if ('auth' in self._config) else None,
            logHandlers = logHandlers,
            cleanSession = self._config['options']['cleanSession'],
            port = self._config['options']['port'],
            transport = self._config['options']['transport']
        )

        # Add handler for commands if not connected to QuickStart
        if self._config['org'] != "quickstart":
            self.client.message_callback_add("iot-2/cmd/+/fmt/+", self._onCommand)

        self.subscriptionsAcknowledged = threading.Event()

        # Initialize user supplied callback
        self.commandCallback = None

        self.client.on_connect = self._onConnect

        self.setMessageEncoderModule('json', jsonCodec)


    def _validateOptions(self):
        if 'identity' not in self._config:
            raise ConfigurationException("Missing identity from configuration")
        if 'orgId' not in self._config['identity'] or self._config['identity']['orgId'] is None:
            raise ConfigurationException("Missing identity.orgId from configuration")
        if 'typeId' not in self._config['identity'] or self._config['identity']['typeId'] is None:
            raise ConfigurationException("Missing identity.typeId from configuration")
        if 'deviceId' not in self._config['identity'] or self._config['identity']['deviceId'] is None:
            raise ConfigurationException("Missing identity.deviceId from configuration")
        
        # Authentication is not supported for quickstart
        if self._config['identity']['orgId'] is "quickstart":
            if 'auth' in self._config:
                raise ConfigurationException("Quickstart service does not support device authentication")
        else:
            if 'auth' not in self._config:
                raise ConfigurationException("Missing auth from configuration")
            if 'token' not in self._config['auth'] or self._config['auth']['token'] is None:
                raise ConfigurationException("Missing auth.token from configuration")
        
        if 'options' in self._config and 'port' in self._config['options'] and not isinstance(self._config['options']['port'], int):
            raise ConfigurationException("Optional setting options.port must be a number if provided")
        if 'options' in self._config and 'cleanSession' in self._config['options'] and not isinstance(self._config['options']['cleanSession'], bool):
            raise ConfigurationException("Optional setting options.cleanSession must be a boolean if provided")
        
        # Set defaults for optional configuration
        if 'options' not in self._config:
            self._config['options'] = {}
        
        if "domain" not in self._config['options']:
            self._config['options']['domain'] = "internetofthings.ibmcloud.com"
        
        if "clean-session" not in self._config['options']:
            self._config['options']['clean-session'] = True

        if "port" not in self._config['options']:
            # None allows the underlying MQTT client to auto-select the port
            self._config['options']['port'] = None
        
        if "transport" not in self._config['options']:
            self._config['options']['transport'] = 'tcp'



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
            if self._config['org'] != "quickstart":
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

            topic = "iot-2/evt/{event}/fmt/{msg_format}".format(event=event, msg_format=msgFormat)

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
        if self._config['org'] == "quickstart":
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


class DeviceInfo(object):
    def __init__(self):
        self.serialNumber = None
        self.manufacturer = None
        self.model = None
        self.deviceClass = None
        self.description = None
        self.fwVersion = None
        self.hwVersion = None
        self.descriptiveLocation = None

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)


class DeviceFirmware(object):
    def __init__(self, version=None, name=None, url=None, verifier=None,
                 state=None, updateStatus=None, updatedDateTime=None):
        self.version = version
        self.name = name
        self.url = url
        self.verifier = verifier
        self.state = state
        self.updateStatus = updateStatus
        self.updatedDateTime = updatedDateTime

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)


class ManagedClient(Client):

    # Publish MQTT topics
    MANAGE_TOPIC = 'iotdevice-1/mgmt/manage'
    UNMANAGE_TOPIC = 'iotdevice-1/mgmt/unmanage'
    UPDATE_LOCATION_TOPIC = 'iotdevice-1/device/update/location'
    ADD_ERROR_CODE_TOPIC = 'iotdevice-1/add/diag/errorCodes'
    CLEAR_ERROR_CODES_TOPIC = 'iotdevice-1/clear/diag/errorCodes'
    NOTIFY_TOPIC = 'iotdevice-1/notify'
    RESPONSE_TOPIC = 'iotdevice-1/response'
    ADD_LOG_TOPIC = 'iotdevice-1/add/diag/log'
    CLEAR_LOG_TOPIC = 'iotdevice-1/clear/diag/log'

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC = 'iotdm-1/response'
    DM_OBSERVE_TOPIC = 'iotdm-1/observe'
    DM_REBOOT_TOPIC = 'iotdm-1/mgmt/initiate/device/reboot'
    DM_FACTORY_REESET = 'iotdm-1/mgmt/initiate/device/factory_reset'
    DM_UPDATE_TOPIC = 'iotdm-1/device/update'
    DM_CANCEL_OBSERVE_TOPIC = 'iotdm-1/cancel'
    DM_FIRMWARE_DOWNLOAD_TOPIC = 'iotdm-1/mgmt/initiate/firmware/download'
    DM_FIRMWARE_UPDATE_TOPIC = 'iotdm-1/mgmt/initiate/firmware/update'
    DME_ACTION_TOPIC = 'iotdm-1/mgmt/custom/#'

    #ResponceCode
    RESPONSECODE_FUNCTION_NOT_SUPPORTED = 501
    RESPONSECODE_ACCEPTED = 202
    RESPONSECODE_INTERNAL_ERROR = 500
    RESPONSECODE_BAD_REQUEST = 400

    UPDATESTATE_IDLE = 0
    UPDATESTATE_DOWNLOADING = 1
    UPDATESTATE_DOWNLOADED = 2
    UPDATESTATE_SUCCESS = 0
    UPDATESTATE_IN_PROGRESS = 1
    UPDATESTATE_OUT_OF_MEMORY = 2
    UPDATESTATE_CONNECTION_LOST = 3
    UPDATESTATE_VERIFICATION_FAILED = 4
    UPDATESTATE_UNSUPPORTED_IMAGE = 5
    UPDATESTATE_INVALID_URI = 6


    def __init__(self, config, logHandlers=None, deviceInfo=None):
        if config['identity']['orgId'] == "quickstart":
            raise Exception("Unable to create ManagedClient instance.  QuickStart devices do not support device management")

        Client.__init__(self, config, logHandlers)

        # Initialize user supplied callback
        self.deviceActionCallback = None
        self.firmwereActionCallback = None
        self.dmeActionCallback = None

        messages_callbacks = (
            ("iotdm-1/#", self.__onDeviceMgmtResponse),
            (ManagedClient.DM_REBOOT_TOPIC, self.__onRebootRequest),
            (ManagedClient.DM_FACTORY_REESET, self.__onFactoryResetRequest),
            (ManagedClient.DM_FIRMWARE_UPDATE_TOPIC, self.__onFirmwereUpdate),
            (ManagedClient.DM_OBSERVE_TOPIC, self.__onFirmwereObserve),
            (ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC, self.__onFirmwereDownload),
            (ManagedClient.DM_UPDATE_TOPIC, self.__onUpdatedDevice),
            (ManagedClient.DM_CANCEL_OBSERVE_TOPIC, self.__onFirmwereCancel),
            (ManagedClient.DME_ACTION_TOPIC, self.__onDMEActionRequest),
        )

        # Add handler for supported device management commands
        for message, callback in messages_callbacks:
            self.client.message_callback_add(message, callback)

        self.client.on_subscribe = self.on_subscribe

        self.readyForDeviceMgmt = threading.Event()

        # List of DM requests that have not received a response yet
        self._deviceMgmtRequestsPendingLock = threading.Lock()
        self._deviceMgmtRequestsPending = {}

        # List of DM notify hook
        self._deviceMgmtObservationsLock = threading.Lock()
        self._deviceMgmtObservations = []

        # Initialize local device data model
        self.metadata = {}
        if deviceInfo is not None:
            self._deviceInfo = deviceInfo
        else:
            self._deviceInfo = DeviceInfo()

        self._location = None
        self._errorCode = None
        self.__firmwareUpdate = None

        self.manageTimer = None

    def setSerialNumber(self, serialNumber):
        self._deviceInfo.serialNumber = serialNumber
        return self.notifyFieldChange("deviceInfo.serialNumber", serialNumber)

    def setManufacturer(self, manufacturer):
        self._deviceInfo.serialNumber = manufacturer
        return self.notifyFieldChange("deviceInfo.manufacturer", manufacturer)

    def setModel(self, model):
        self._deviceInfo.serialNumber = model
        return self.notifyFieldChange("deviceInfo.model", model)

    def setdeviceClass(self, deviceClass):
        self._deviceInfo.deviceClass = deviceClass
        return self.notifyFieldChange("deviceInfo.deviceClass", deviceClass)

    def setDescription(self, description):
        self._deviceInfo.description = description
        return self.notifyFieldChange("deviceInfo.description", description)

    def setFwVersion(self, fwVersion):
        self._deviceInfo.fwVersion = fwVersion
        return self.notifyFieldChange("deviceInfo.fwVersion", fwVersion)

    def setHwVersion(self, hwVersion):
        self._deviceInfo.hwVersion = hwVersion
        return self.notifyFieldChange("deviceInfo.hwVersion", hwVersion)

    def setDescriptiveLocation(self, descriptiveLocation):
        self._deviceInfo.descriptiveLocation = descriptiveLocation
        return self.notifyFieldChange("deviceInfo.descriptiveLocation", descriptiveLocation)

    def notifyFieldChange(self, field, value):
        with self._deviceMgmtObservationsLock:
            if field in self._deviceMgmtObservations:
                if not self.readyForDeviceMgmt.wait(timeout=10):
                    self.logger.warning("Unable to notify service of field "
                                        "change because device is not ready "
                                        "for device management")
                    return threading.Event().set()

                reqId = str(uuid.uuid4())
                message = {
                    "d": {
                        "field": field,
                        "value": value
                    },
                    "reqId": reqId
                }

                resolvedEvent = threading.Event()
                self.client.publish(ManagedClient.NOTIFY_TOPIC, payload=json.dumps(message), qos=1, retain=False)
                with self._deviceMgmtRequestsPendingLock:
                    self._deviceMgmtRequestsPending[reqId] = {
                        "topic": ManagedClient.NOTIFY_TOPIC,
                        "message": message,
                        "event": resolvedEvent
                    }

                return resolvedEvent
            else:
                return threading.Event().set()
    '''
    This is called after the client has received a CONNACK message from the broker in response to calling connect().
    The parameter rc is an integer giving the return code:
    0: Success
    1: Refused - unacceptable protocol version
    2: Refused - identifier rejected
    3: Refused - server unavailable
    4: Refused - bad user name or password
    5: Refused - not authorised
    '''
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))
            if self._config['org'] != "quickstart":
                self.client.subscribe(
                    [
                        (ManagedClient.DM_RESPONSE_TOPIC, 1),
                        (ManagedClient.DM_OBSERVE_TOPIC, 1),
                        (ManagedClient.DM_REBOOT_TOPIC, 1),
                        (ManagedClient.DM_FACTORY_REESET, 1),
                        (ManagedClient.DM_UPDATE_TOPIC, 1),
                        (ManagedClient.DM_FIRMWARE_UPDATE_TOPIC, 1),
                        (ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC, 1),
                        (ManagedClient.DM_CANCEL_OBSERVE_TOPIC, 1),
                        (self._COMMAND_TOPIC, 1),
                        (ManagedClient.DME_ACTION_TOPIC, 1)
                    ]
                )
        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


    def on_subscribe(self, client, userdata, mid, granted_qos):
        # Once IoTF acknowledges the subscriptions we are able to process commands and responses from device management server
        self.subscriptionsAcknowledged.set()
        self.manage()


    def manage(self, lifetime=3600, supportDeviceActions=True, supportFirmwareActions=True,
               supportDeviceMgmtExtActions=False, bundleIds=[]):
        # TODO: throw an error, minimum lifetime this client will support is 1 hour, but for now set lifetime to infinite if it's invalid
        if lifetime < 3600:
            lifetime = 0

        if not self.subscriptionsAcknowledged.wait(timeout=10):
            self.logger.warning("Unable to send register for device "
                                "management because device subscriptions "
                                "are not in place")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            'd': {
                "lifetime": lifetime,
                "supports": {
                    "deviceActions": supportDeviceActions,
                    "firmwareActions": supportFirmwareActions,
                },
                "deviceInfo": self._deviceInfo.__dict__,
                "metadata": self.metadata
            },
            'reqId': reqId
        }
        if supportDeviceMgmtExtActions and len(bundleIds) > 0:
            for bundleId in bundleIds:
                message['d']['supports'][bundleId] = supportDeviceMgmtExtActions

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.MANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": ManagedClient.MANAGE_TOPIC, "message": message, "event": resolvedEvent}

        # Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
        if lifetime != 0:
            if self.manageTimer is not None:
                self.logger.debug("Cancelling existing manage timer")
                self.manageTimer.cancel()
            self.manageTimer = threading.Timer(
                lifetime - 120,
                self.manage,
                [
                    lifetime,
                    supportDeviceActions,
                    supportFirmwareActions,
                    supportDeviceMgmtExtActions,
                    bundleIds
                ]
            )
            self.manageTimer.start()

        return resolvedEvent

    def unmanage(self):
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to set device to unmanaged because "
                                "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            'reqId': reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.UNMANAGE_TOPIC,
                            payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.UNMANAGE_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def setLocation(self, longitude, latitude, elevation=None, accuracy=None):
        # TODO: Add validation (e.g. ensure numeric values)
        if self._location is None:
            self._location = {}

        self._location['longitude'] = longitude
        self._location['latitude'] = latitude
        if elevation:
            self._location['elevation'] = elevation

        self._location['measuredDateTime'] = datetime.now(pytz.timezone('UTC')).isoformat()

        if accuracy:
            self._location['accuracy'] = accuracy
        elif "accuracy" in self._location:
            del self._location["accuracy"]

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish device location because "
                                "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": self._location,
            "reqId": reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.UPDATE_LOCATION_TOPIC,
                            payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.UPDATE_LOCATION_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def setErrorCode(self, errorCode=0):
        if errorCode is None:
            errorCode = 0

        self._errorCode = errorCode

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because "
                                "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": {"errorCode": errorCode},
            "reqId": reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(
            ManagedClient.ADD_ERROR_CODE_TOPIC,
            payload=json.dumps(message),
            qos=1,
            retain=False
        )
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.ADD_ERROR_CODE_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def clearErrorCodes(self):
        self._errorCode = None

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear error codes because "
                                "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "reqId": reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.CLEAR_ERROR_CODES_TOPIC,
                            payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.CLEAR_ERROR_CODES_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def addLog(self, msg="", data="", sensitivity=0):
        timestamp = datetime.now().isoformat()
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because "
                                "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": {
                "message": msg,
                "timestamp": timestamp,
                "data": data,
                "severity": sensitivity
            },
            "reqId": reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.ADD_LOG_TOPIC,
                            payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.ADD_LOG_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def clearLog(self):

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear log because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "reqId": reqId
        }

        resolvedEvent = threading.Event()
        self.client.publish(ManagedClient.CLEAR_LOG_TOPIC,
                            payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedClient.CLEAR_LOG_TOPIC,
                "message": message,
                "event": resolvedEvent
            }

        return resolvedEvent

    def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):

        try:
            data = json.loads(pahoMessage.payload.decode("utf-8"))
            if 'rc' not in data:
                return True
            rc = data['rc']
            reqId = data['reqId']
        except ValueError as e:
            raise Exception(
                "Unable to parse JSON. payload=\"%s\" error=%s" % (
                    pahoMessage.payload,
                    str(e)
                )
            )
        else:
            request = None
            with self._deviceMgmtRequestsPendingLock:
                try:
                    request = self._deviceMgmtRequestsPending.pop(reqId)
                except KeyError:
                    self.logger.warning("Received unexpected response from "
                                        "device management: %s", reqId)
                else:
                    self.logger.debug("Remaining unprocessed device "
                                      "management requests: %s",
                                      len(self._deviceMgmtRequestsPending))


            if request is None:
                return False

            state = {
                ManagedClient.MANAGE_TOPIC: {
                    # rc, json.dumps(request['message'])
                    'msg_succ': "[%s] Manage action completed: %s",
                    'msg_fail': "[%s] Manage action failed: %s",
                },
                ManagedClient.UNMANAGE_TOPIC: {
                    'msg_succ': "[%s] Unmanage action completed: %s",
                    'msg_fail': "[%s] Unmanage action failed: %s"
                },
                ManagedClient.UPDATE_LOCATION_TOPIC: {
                    'msg_succ': "[%s] Location update action completed: %s",
                    'msg_fail': "[%s] Location update action failed: %s"
                },
                ManagedClient.ADD_ERROR_CODE_TOPIC: {
                    'msg_succ': "[%s] Add error code action completed: %s",
                    'msg_fail': "[%s] Add error code action failed: %s"
                },
                ManagedClient.CLEAR_ERROR_CODES_TOPIC: {
                    'msg_succ': "[%s] Clear error codes action completed: %s",
                    'msg_fail': "[%s] Clear error codes action failed: %s"
                },
                ManagedClient.ADD_LOG_TOPIC: {
                    'msg_succ': "[%s] Add log action completed: %s",
                    'msg_fail': "[%s] Add log action failed: %s"
                },
                ManagedClient.CLEAR_LOG_TOPIC: {
                    'msg_succ': "[%s] Clear log action completed: %s",
                    'msg_fail': "[%s] Clear log action failed: %s"
                }
            }

            try:
                msg_succ = state[request['topic']]['msg_succ']
                msg_fail = state[request['topic']]['msg_fail']
            except Exception as e:
                self.logger.warning("[%s] Unknown action response: %s",
                                    rc, json.dumps(request['message']))
            else:
                dump_str = json.dumps(request['message'])
                if rc == 200:
                    self.logger.info(msg_succ, rc, dump_str)
                else:
                    self.logger.critical(msg_fail, rc, dump_str)

                if request['topic'] == ManagedClient.MANAGE_TOPIC:
                    self.readyForDeviceMgmt.set()
                elif request['topic'] == ManagedClient.UNMANAGE_TOPIC:
                    self.readyForDeviceMgmt.clear()

            # Now clear the event, allowing anyone that was waiting on this to proceed
            request["event"].set()
            return True

    # Device Action Handlers
    def __onRebootRequest(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_REBOOT_TOPIC, paho_payload)
        try:
            data = json.loads(paho_payload)
            reqId = data['reqId']
            if self.deviceActionCallback:
                self.deviceActionCallback(reqId, "reboot")
        except ValueError as e:
            raise Exception("Unable to process Reboot request.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))

    def __onFactoryResetRequest(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_FACTORY_REESET,
                         paho_payload)
        try:
            data = json.loads(paho_payload)
            reqId = data['reqId']
            if self.deviceActionCallback:
                self.deviceActionCallback(reqId, "reset")
        except ValueError as e:
            raise Exception("Unable to process Factory Reset request.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))

    def respondDeviceAction(self, reqId, responseCode=202, message=""):
        response = {
            "rc": responseCode,
            "message": message,
            "reqId": reqId
        }
        payload = json.dumps(response)
        self.logger.info("Publishing Device Action response with payload :%s",
                         payload)
        self.client.publish('iotdevice-1/response', payload,
                            qos=1, retain=False)

    # Firmware Handlers
    def __onFirmwereDownload(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_FIRMWARE_DOWNLOAD_TOPIC,
                         paho_payload)

        data = json.loads(paho_payload)
        reqId = data['reqId']
        rc = ManagedClient.RESPONSECODE_ACCEPTED
        msg = ""

        if self.__firmwareUpdate.state != ManagedClient.UPDATESTATE_IDLE:
            rc = ManagedClient.RESPONSECODE_BAD_REQUEST
            msg = "Cannot download as the device is not in idle state"
        thread = threading.Thread(target=self.respondDeviceAction,
                                  args=(reqId, rc, msg),
                                  name='respondDeviceAction')
        thread.start()
        if self.firmwereActionCallback:
            self.firmwereActionCallback("download", self.__firmwareUpdate)


    def __onFirmwereCancel(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_CANCEL_OBSERVE_TOPIC,
                         paho_payload)
        data = json.loads(paho_payload)
        reqId = data['reqId']
        thread = threading.Thread(target=self.respondDeviceAction,
                                  args=(reqId, 200, ""),
                                  name='respondDeviceAction')
        thread.start()

    def __onFirmwereObserve(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_OBSERVE_TOPIC, paho_payload)
        data = json.loads(paho_payload)
        reqId = data['reqId']
        # TODO: Proprer validation for fields in payload
        thread = threading.Thread(target=self.respondDeviceAction,
                                  args=(reqId, 200, ""),
                                  name='respondDeviceAction')
        thread.start()

    def __onUpdatedDevice(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_UPDATE_TOPIC, paho_payload)

        data = json.loads(paho_payload)
        if 'reqId' in data:
            reqId = data['reqId']
            d = data['d']
            value = None
            for obj in d['fields']:
                if 'field' in obj:
                    if obj['field'] == "mgmt.firmware":
                        value = obj["value"]
            if value is not None:
                self.__firmwareUpdate = DeviceFirmware(
                    value['version'],
                    value['name'],
                    value['uri'],
                    value['verifier'],
                    value['state'],
                    value['updateStatus'],
                    value['updatedDateTime'])
            thread = threading.Thread(target=self.respondDeviceAction,
                                      args=(reqId, 204, ""),
                                      name='respondDeviceAction')
            thread.start()
        else:
            d = data['d']
            value = None
            for obj in d['fields']:
                if 'field' in obj:
                    if obj['field'] == "metadata":
                        value = obj["value"]
            if value is not None:
                self.metadata = value

    def setState(self, status):
        notify = {
            "d": {
                "fields": [
                    {
                        "field": "mgmt.firmware",
                        "value": {
                            "state": status
                        }
                    }
                ]
            }
        }
        if self.__firmwareUpdate is not None:
            self.__firmwareUpdate.state = status

        self.logger.info("Publishing state Update with payload :%s",
                         json.dumps(notify))
        thread = threading.Thread(
            target=self.client.publish,
            args=('iotdevice-1/notify', json.dumps(notify), 1, False),
            name='client.publish')
        thread.start()

    def setUpdateStatus(self, status):
        notify = {
            "d": {
                "fields": [
                    {
                        "field": "mgmt.firmware",
                        "value": {
                            "state": ManagedClient.UPDATESTATE_IDLE,
                            "updateStatus": status
                        }
                    }
                ]
            }
        }
        if self.__firmwareUpdate is not None:
            self.__firmwareUpdate.state = ManagedClient.UPDATESTATE_IDLE
            self.__firmwareUpdate.updateStatus = status

        self.logger.info("Publishing  Update Status  with payload :%s",
                         json.dumps(notify))
        thread = threading.Thread(
            target=self.client.publish,
            args=('iotdevice-1/notify', json.dumps(notify), 1, False),
            name='client.publish')
        thread.start()

    def __onFirmwereUpdate(self,client,userdata,pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DM_FIRMWARE_UPDATE_TOPIC, paho_payload)

        data = json.loads(paho_payload)
        reqId = data['reqId']
        rc = ManagedClient.RESPONSECODE_ACCEPTED
        msg = ""
        if self.__firmwareUpdate.state != ManagedClient.UPDATESTATE_DOWNLOADED:
            rc = ManagedClient.RESPONSECODE_BAD_REQUEST
            msg = "Firmware is still not successfully downloaded."
        thread = threading.Thread(
            target=self.respondDeviceAction,
            args=(reqId, rc, msg),
            name='respondDeviceAction')
        thread.start()
        if self.firmwereActionCallback:
            self.firmwereActionCallback("update", self.__firmwareUpdate)

    def __onDMEActionRequest(self, client, userdata, pahoMessage):
        data = json.loads(pahoMessage.payload.decode("utf-8"))
        self.logger.info("Message received on topic :%s with payload %s",
                         ManagedClient.DME_ACTION_TOPIC, data)

        reqId = data['reqId']
        if self.dmeActionCallback:
            if self.dmeActionCallback(pahoMessage.topic, data, reqId):
                msg = "DME Action successfully completed from Callback"
                thread = threading.Thread(
                    target=self.respondDeviceAction,
                    args=(reqId, 200, msg),
                    name='respondDeviceAction')
                thread.start()
            else:
                msg = "Unexpected device error"
                thread = threading.Thread(
                    target=self.respondDeviceAction,
                    args=(reqId, 500, msg),
                    name='respondDeviceAction')
                thread.start()

        else:
            thread = threading.Thread(
                target=self.respondDeviceAction,
                args=(reqId, 501, "Operation not implemented"),
                name='respondDeviceAction')
            thread.start()

def parseEnvVars():
    """
    Parse environment variables into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter

    **Identity**
    - `WIOTP_ORG_ID`
    - `WIOTP_TYPE_ID`
    - `WIOTP_DEVICE_ID`
    
    **Auth**
    - `WIOTP_AUTH_TOKEN`
    
    **Options**
    - `WIOTP_DOMAIN` (optional)
    - `WIOTP_PORT` (optional)
    - `WIOTP_TRANSPORT` (optional)
    - `WIOTP_CA_FILE` (optional)
    - `WIOTP_CLEAN_SESSION` (optional)


    ```python
    import ibmiotf.device
    
    try:
        options = ibmiotf.device.ParseEnvVars()
        client = ibmiotf.device.Client(options)
    except ibmiotf.ConnectionException  as e:
        pass
        
    ```
    """

    # Identify
    orgId     = os.getenv("WIOTP_ORG_ID", None)
    typeId    = os.getenv("WIOTP_TYPE_ID", None)
    deviceId  = os.getenv("WIOTP_DEVICE_ID", None)
    # Auth
    authToken = os.getenv("WIOTP_AUTH_TOKEN", None)
    # Options
    domain    = os.getenv("WIOTP_DOMAIN", None)
    port      = os.getenv("WIOTP_PORT", None)
    transport = os.getenv("WIOTP_TRANSPORT", None)
    caFile    = os.getenv("WIOTP_CA_FILE", None)
    cleanSession = os.getenv("WIOTP_CLEAN_SESSION", "True")
    
    if orgId is None:
        raise ConfigurationException("Missing WIOTP_ORG_ID environment variable")
    if typeId is None:
        raise ConfigurationException("Missing WIOTP_TYPE_ID environment variable")
    if deviceId is None:
        raise ConfigurationException("Missing WIOTP_DEVICE_ID environment variable")
    if orgId is not "quickstart" and authToken is None:
        raise ConfigurationException("Missing WIOTP_AUTH_TOKEN environment variable")
    if port is not None:
        try:
            port = int(port)
        except ValueError as e:
            raise ConfigurationException("Missing WIOTP_PORT must be a number")

    cfg = {
        'identity': {
            'orgId': orgId,
            'typeId': typeId,
            'deviceId': deviceId
        },
        'options': {
            'domain': domain,
            'port': port,
            'transport': transport,
            'caFile': caFile,
            'clean-session': cleanSession in ["True", "true", "1"]
        }
    }

    # Quickstart doesn't support auth, so ensure we only add this if it's defined
    if authToken is not None:
        cfg['auth'] = { 'token': authToken }
    
    return cfg


def ParseConfigFile(configFilePath):
    """
    Parse a yaml configuration file into a Python dictionary suitable for passing to the 
    device client constructor as the `options` parameter
    
    ```python
    import ibmiotf.device
    
    try:
        options = ibmiotf.device.ParseConfigFile(configFilePath)
        client = ibmiotf.device.Client(options)
    except ibmiotf.ConnectionException  as e:
        pass
        
    ```
    
    # Example Configuration File
    
    device.yaml
    ```
    identity:
      orgId: org1id
      typeId: raspberry-pi-3
      deviceId: 00ef08ac05
    auth:
      token: Ab$76s)asj8_s5
    options:
      domain: internetofthings.ibmcloud.com
      port: 8883
      transport: tcp
      caFile: /path/to/certificateAuthorityFile.pem
      cleanSession: true
    ```
    
    **Optional Settings**
    
    - `options.domain` Defaults to `internetofthings.ibmcloud.com`
    - `options.port` Defaults to `8883`    
    - `options.transport` Defaults to `tcp`    
    - `options.caFile` Defaults to `messaging.pem` inside this module    
    - `options.cleanSession` Defaults to `false`
    """
    
    try:
        with open(configFilePath) as f:
            data = yaml.load(f)
    except IOError as e:
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath, e[1])
        raise ConfigurationException(reason)

    return data
