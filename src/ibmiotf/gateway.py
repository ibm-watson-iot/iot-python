# *****************************************************************************
# Copyright (c) 2016, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Amit M Mangalvedkar
#   Lokesh K Haralakatta
#   Ian Craggs - fix for #99
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
from ibmiotf import api

# Support Python 2.7 and 3.4 versions of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

COMMAND_RE = re.compile("iot-2/type/(.+)/id/(.+)/cmd/(.+)/fmt/(.+)")

class Command:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = COMMAND_RE.match(pahoMessage.topic)
        if result:
            self.type = result.group(1)
            self.id = result.group(2)
            self.command = result.group(3)
            self.format = result.group(4)

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received command on invalid topic: %s" % (pahoMessage.topic))

NOTIFY_RE = re.compile("iot-2/type/(.+)/id/(.+)/notify")

class Notification:
    def __init__(self, pahoMessage, messageEncoderModules):
        result = NOTIFY_RE.match(pahoMessage.topic)
        if result:
            self.type = result.group(1)
            self.id = result.group(2)
            self.format = 'json'

            if self.format in messageEncoderModules:
                message = messageEncoderModules[self.format].decode(pahoMessage)
                self.timestamp = message.timestamp
                self.data = message.data
            else:
                raise MissingMessageDecoderException(self.format)
        else:
            raise InvalidEventException("Received notification on invalid topic: %s" % (pahoMessage.topic))

class Client(AbstractClient):

    def __init__(self, options, logHandlers=None):
        self._options = options

        #Defaults
        if "domain" not in self._options:
            # Default to the domain for the public cloud offering
            self._options['domain'] = "internetofthings.ibmcloud.com"

        if "org" not in self._options:
            # Default to the quickstart ode
            self._options['org'] = "quickstart"

        if "clean-session" not in self._options:
            self._options['clean-session'] = "true"

        if self._options["org"] == "quickstart":
            self._options["port"] = 1883;

        #Check for any missing required properties
        if self._options['org'] == None:
            raise ConfigurationException("Missing required property: org")
        if self._options['type'] == None:
            raise ConfigurationException("Missing required property: type")
        if self._options['id'] == None:
            raise ConfigurationException("Missing required property: id")

        if self._options['org'] != "quickstart":
            if self._options['auth-method'] == None:
                raise ConfigurationException("Missing required property: auth-method")

            if (self._options['auth-method'] == "token"):
                if self._options['auth-token'] == None:
                    raise ConfigurationException("Missing required property for token based authentication: auth-token")
            else:
                raise UnsupportedAuthenticationMethod(options['authMethod'])


        self.COMMAND_TOPIC = "iot-2/type/" + self._options['type'] + "/id/" + self._options['id'] + "/cmd/+/fmt/+"

        AbstractClient.__init__(
            self,
            domain = self._options['domain'],
            organization = self._options['org'],
            clientId = "g:" + self._options['org'] + ":" + self._options['type'] + ":" + self._options['id'],
            username = "use-token-auth" if (self._options['auth-method'] == "token") else None,
            password = self._options['auth-token'],
            logHandlers = logHandlers,
            port = self._options.get('port', None),
            transport = self._options.get('transport', 'tcp')
        )

        # Add handler for subscriptions
        self.client.on_subscribe = self.__onSubscribe

        # Add handler for commands if not connected to QuickStart
        if self._options['org'] != "quickstart":
            gatewayCommandTopic = "iot-2/type/" + options['type'] + "/id/" + options['id'] + "/cmd/+/fmt/json"
            messageNotificationTopic = "iot-2/type/" + options['type'] + "/id/" + options['id'] + "/notify"
            #localTopic = "iot-2/type/iotsample-raspberrypi2/id/89898889/cmd/greeting/fmt/json"
            self.client.message_callback_add(gatewayCommandTopic, self.__onCommand)
            self.client.message_callback_add("iot-2/type/+/id/+/cmd/+/fmt/+", self.__onDeviceCommand)
            self.client.message_callback_add(messageNotificationTopic, self.__onMessageNotification)


        self.subscriptionsAcknowledged = threading.Event()

        # Initialize user supplied callback
        self.commandCallback = None
        self.deviceCommandCallback = None
        self.notificationCallback = None
        self.subscriptionCallback = None
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self._onDisconnect
        self.setMessageEncoderModule('json', jsonCodec)

        # Create api key for gateway authentication
        self.gatewayApiKey = "g/" + self._options['org'] + '/' + self._options['type'] + '/' + self._options['id']
        self.logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.api = api.ApiClient({"org": self._options['org'], "auth-token": self._options['auth-token'], "auth-key": self.gatewayApiKey }, self.logger)

    '''
    Called when the broker responds to our connection request.

        flags is a dict that contains response flags from the broker:

        flags['session present']    This flag is useful for clients that
                                    are using clean session set to 0 only.
                                    If a client with clean session=0, that
                                    reconnects to a broker that it has
                                    previously connected to, this flag
                                    indicates whether the broker still has
                                    the session information for the client.
                                    If 1, the session still exists.

    The value of rc determines success or not:
        0: Connection successful
        1: Connection refused - incorrect protocol version
        2: Connection refused - invalid client identifier
        3: Connection refused - server unavailable
        4: Connection refused - bad username or password
        5: Connection refused - not authorised
        6-255: Currently unused.
    '''
    def on_connect(self, client, userdata, flags, rc):
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


    '''
    Called when the client disconnects from the broker.  The rc parameter indicates the disconnection state.  If
    MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call. If any other value the
    disconnection was unexpected, such as might be caused by a network error.
    '''
    def _onDisconnect(self, client, userdata, rc):
        super(Client, self)._onDisconnect(client, userdata, rc)

        # Clear the event to indicate we're no longer connected
        self.connectEvent.clear()

        if rc == 0:
            self.logger.info("Disonnected successfully: %s" % (self.clientId))
        else:
            self.logger.warning("Unexpected disconnection: %s (%s)" % (self.clientId, rc))


    '''
    Publish an event in Watson IoT.
    Parameters:
        event - the name of this event
        msgFormat - the format of the data for this event
        data - the data for this event
        deviceType - the device type of the device on the behalf of which the gateway is publishing the event

    Optional paramters:
        qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
        on_publish - a function that will be called when receipt of the publication is confirmed.  This
                     has different implications depending on the qos:
                     qos 0 - the client has asynchronously begun to send the event
                     qos 1 and 2 - the client has confirmation of delivery from Watson IoT
    '''
    def publishDeviceEvent(self, deviceType, deviceId, event, msgFormat, data, qos=0, on_publish=None):
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to send event %s because gateway as a device is not currently connected")
            return False
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                # The data object may not be serializable, e.g. if using a custom binary format
                try: 
                    dataString = json.dumps(data)
                except:
                    dataString = str(data)
                self.logger.debug("Sending event %s with data %s" % (event, dataString))
                
            topic = 'iot-2/type/' + deviceType + '/id/' + deviceId +'/evt/'+event+'/fmt/' + msgFormat

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
                            # this thread beat paho callback so set up for call later
                            self._onPublishCallbacks[result[1]] = on_publish
                    return True
                else:
                    return False
            else:
                raise MissingMessageEncoderException(msgFormat)


    '''
    Publish an event in Watson IoT as a device.
    Parameters:
        event - the name of this event
        msgFormat - the format of the data for this event
        data - the data for this event
    Optional paramters:
        qos - the equivalent MQTT semantics of quality of service using the same constants (0, 1 and 2)
        on_publish - a function that will be called when receipt of the publication is confirmed.  This
                     has different implications depending on the qos:
                     qos 0 - the client has asynchronously begun to send the event
                     qos 1 and 2 - the client has confirmation of delivery from Watson IoT
    '''
    def publishGatewayEvent(self, event, msgFormat, data, qos=0, on_publish=None):
        gatewayType = self._options['type']
        gatewayId = self._options['id']

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to send event %s because gateway as a device is not currently connected")
            return False
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                # The data object may not be serializable, e.g. if using a custom binary format
                try: 
                    dataString = json.dumps(data)
                except:
                    dataString = str(data)
                self.logger.debug("Sending event %s with data %s" % (event, dataString))
                
            topic = 'iot-2/type/' + gatewayType + '/id/' + gatewayId +'/evt/'+event+'/fmt/' + msgFormat

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
                            # paho callback beat this thread so call callback inline now
                            if on_publish is not None:
                              on_publish()
                            del self._onPublishCallbacks[result[1]]
                        else:
                            # this thread beat paho callback so set up for call later
                            self._onPublishCallbacks[result[1]] = on_publish
                    return True
                else:
                    return False
            else:
                raise MissingMessageEncoderException(msgFormat)


    def subscribeToDeviceCommands(self, deviceType, deviceId, command='+', format='json', qos=1):
        if self._options['org'] == "quickstart":
            self.logger.warning("QuickStart not supported in Gateways")
            return 0

        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to device commands because gateway is not currently connected")
            return 0
        else:
            topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
            (result, mid) = self.client.subscribe(topic, qos=qos)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = qos
                return mid
            else:
                return 0



    def subscribeToGatewayCommands(self, command='+', format='json', qos=1):
        deviceType = self._options['type']
        deviceId = self._options['id']
        if self._options['org'] == "quickstart":
            self.logger.warning("QuickStart not supported in Gateways")
            return 0
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to gateway commands because gateway is not currently connected")
            return 0
        else:
            topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/cmd/' + command + '/fmt/' + format
            (result, mid) = self.client.subscribe(topic, qos=qos)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = qos
                return mid
            else:
                return 0


    def subscribeToGatewayNotifications(self):
        deviceType = self._options['type']
        deviceId = self._options['id']
        if self._options['org'] == "quickstart":
            self.logger.warning("QuickStart not supported in Gateways")
            return 0
        if not self.connectEvent.wait(timeout=10):
            self.logger.warning("Unable to subscribe to notifications because gateway is not currently connected")
            return 0
        else:
            topic = 'iot-2/type/' + deviceType + '/id/' + deviceId + '/notify'
            (result, mid) = self.client.subscribe(topic, qos=0)
            if result == paho.MQTT_ERR_SUCCESS:
                with self._subLock:
                    self._subscriptions[topic] = 0
                return mid
            else:
                return 0

    def __onSubscribe(self, client, userdata, mid, grantedQoS):
        '''
        Internal callback for handling subscription acknowledgement
        '''
        self.logger.debug("Subscribe callback: mid: %s qos: %s" % (mid, grantedQoS))
        if self.subscriptionCallback: self.subscriptionCallback(mid, grantedQoS)

    def __onCommand(self, client, userdata, pahoMessage):
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

    def __onDeviceCommand(self, client, userdata, pahoMessage):
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

    '''
    Internal callback for gateway notification messages, parses source device from topic string and
    passes the information on to the registered device command callback
    '''
    def __onMessageNotification(self, client, userdata, pahoMessage):
        try:
            note = Notification(pahoMessage, self._messageEncoderModules)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received Notification")
            if self.notificationCallback: self.notificationCallback(note)



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


class ManagedClient(Client):

    # Publish MQTT topics
    '''
    MANAGE_TOPIC = 'iotdevice-1/mgmt/manage'
    UNMANAGE_TOPIC = 'iotdevice-1/mgmt/unmanage'
    UPDATE_LOCATION_TOPIC = 'iotdevice-1/device/update/location'
    ADD_ERROR_CODE_TOPIC = 'iotdevice-1/add/diag/errorCodes'
    CLEAR_ERROR_CODES_TOPIC = 'iotdevice-1/clear/diag/errorCodes'
    NOTIFY_TOPIC = 'iotdevice-1/notify'

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC = 'iotdm-1/response'
    DM_OBSERVE_TOPIC = 'iotdm-1/observe'
    '''

    MANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/manage'
    UNMANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/unmanage'
    UPDATE_LOCATION_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/device/update/location'
    ADD_ERROR_CODE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/add/diag/errorCodes'
    CLEAR_ERROR_CODES_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/clear/diag/errorCodes'
    NOTIFY_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/notify'

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/response'
    DM_OBSERVE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/observe'

    def __init__(self, options, logHandlers=None, deviceInfo=None):
        if options['org'] == "quickstart":
            raise Exception("Unable to create ManagedClient instance.  QuickStart devices do not support device management")

        Client.__init__(self, options, logHandlers)
        # TODO: Raise fatal exception if tries to create managed device client for QuickStart

        # Add handler for supported device management commands
        self.client.message_callback_add("iotdm-1/#", self.__onDeviceMgmtResponse)
        self.client.on_subscribe = self.__onSubscribe

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

        self._gatewayType = self._options['type']
        self._gatewayId = self._options['id']


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
                    self.logger.warning("Unable to notify service of field change because gateway is not ready for gateway management")
                    return threading.Event().set()

                reqId = str(uuid.uuid4())
                message = {
                    "d": {
                        "field": field,
                        "value": value
                    },
                    "reqId": reqId
                }

                notify_topic = ManagedClient.NOTIFY_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
                resolvedEvent = threading.Event()

                self.client.publish(notify_topic, payload=json.dumps(message), qos=1, retain=False)
                with self._deviceMgmtRequestsPendingLock:
                    self._deviceMgmtRequestsPending[reqId] = {"topic": notify_topic, "message": message, "event": resolvedEvent}

                return resolvedEvent
            else:
                return threading.Event().set()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))
            if self._options['org'] != "quickstart":
                dm_response_topic = ManagedClient.DM_RESPONSE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
                dm_observe_topic = ManagedClient.DM_OBSERVE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
                (self.dmSubscriptionResult, self.dmSubscriptionMid) = self.client.subscribe( [(dm_response_topic, 1), (dm_observe_topic, 1), (self.COMMAND_TOPIC, 1)] )

                if self.dmSubscriptionResult != paho.MQTT_ERR_SUCCESS:
                    self._logAndRaiseException(ConnectionException("Unable to subscribe to device management topics"))

        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))

    def __onSubscribe(self, client, userdata, mid, grantedQoS):
        '''
        Internal callback for handling subscription acknowledgement
        '''
        if mid == self.dmSubscriptionMid:
            # Once Watson IoT acknowledges the DM subscriptions we are able to
            # process commands and responses from device management server
            self.subscriptionsAcknowledged.set()
            self.manage()
        else:
            self.logger.debug("Subscribe callback: mid: %s qos: %s" % (mid, grantedQoS))
            if self.subscriptionCallback: self.subscriptionCallback(mid, grantedQoS)


    def manage(self, lifetime=3600, supportDeviceActions=False, supportFirmwareActions=False):
        # TODO: throw an error, minimum lifetime this client will support is 1 hour, but for now set lifetime to infinite if it's invalid
        if lifetime < 3600:
            lifetime = 0

        if not self.subscriptionsAcknowledged.wait(timeout=10):
            self.logger.warning("Unable to send register for device management because device subscriptions are not in place")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            'd': {
                "lifetime": lifetime,
                "supports": {
                    "deviceActions": supportDeviceActions,
                    "firmwareActions": supportFirmwareActions
                },
                "deviceInfo" : self._deviceInfo.__dict__,
                "metadata" : self.metadata
            },
            'reqId': reqId
        }

        manage_topic = ManagedClient.MANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
        resolvedEvent = threading.Event()

        self.client.publish(manage_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": manage_topic, "message": message, "event": resolvedEvent}

        # Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
        if lifetime != 0:
            threading.Timer(lifetime-120, self.manage, [lifetime, supportDeviceActions, supportFirmwareActions]).start()

        return resolvedEvent


    def unmanage(self):
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to set device to unmanaged because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            'reqId': reqId
        }

        unmanage_topic = ManagedClient.UNMANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
        resolvedEvent = threading.Event()

        self.client.publish(unmanage_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": unmanage_topic, "message": message, "event": resolvedEvent}

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
            self.logger.warning("Unable to publish device location because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": self._location,
            "reqId": reqId
        }

        update_location_topic = ManagedClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
        resolvedEvent = threading.Event()

        self.client.publish(update_location_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": update_location_topic, "message": message, "event": resolvedEvent}

        return resolvedEvent


    def setErrorCode(self, errorCode=0):
        if errorCode is None:
            errorCode = 0;

        self._errorCode = errorCode

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": { "errorCode": errorCode },
            "reqId": reqId
        }

        add_error_code_topic = ManagedClient.ADD_ERROR_CODE_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
        resolvedEvent = threading.Event()

        self.client.publish(add_error_code_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": add_error_code_topic, "message": message, "event": resolvedEvent}

        return resolvedEvent

    def clearErrorCodes(self):
        self._errorCode = None

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear error codes because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "reqId": reqId
        }

        clear_error_codes_topic = ManagedClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)
        resolvedEvent = threading.Event()

        self.client.publish(clear_error_codes_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": clear_error_codes_topic, "message": message, "event": resolvedEvent}

        return resolvedEvent


    def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):
        try:
            data = json.loads(pahoMessage.payload.decode("utf-8"))

            rc = data['rc']
            reqId = data['reqId']
        except ValueError as e:
            raise Exception("Unable to parse JSON.  payload=\"%s\" error=%s" % (pahoMessage.payload, str(e)))
        else:
            request = None
            with self._deviceMgmtRequestsPendingLock:
                try:
                    request = self._deviceMgmtRequestsPending.pop(reqId)
                except KeyError:
                    self.logger.warning("Received unexpected response from device management: %s" % (reqId))
                else:
                    self.logger.debug("Remaining unprocessed device management requests: %s" % (len(self._deviceMgmtRequestsPending)))


            if request is None:
                return False

            manage_topic = ManagedClient.MANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
            unmanage_topic = ManagedClient.UNMANAGE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
            update_location_topic = ManagedClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
            add_error_code_topic = ManagedClient.ADD_ERROR_CODE_TOPIC_TEMPLATE % (self._gatewayType,self._gatewayId)
            clear_error_codes_topic = ManagedClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._gatewayType,self._gatewayId)

            if request['topic'] == manage_topic:
                if rc == 200:
                    self.logger.info("[%s] Manage action completed: %s" % (rc, json.dumps(request['message'])))
                    self.readyForDeviceMgmt.set()
                else:
                    self.logger.critical("[%s] Manage action failed: %s" % (rc, json.dumps(request['message'])))

            elif request['topic'] == unmanage_topic:
                if rc == 200:
                    self.logger.info("[%s] Unmanage action completed: %s" % (rc, json.dumps(request['message'])))
                    self.readyForDeviceMgmt.clear()
                else:
                    self.logger.critical("[%s] Unmanage action failed: %s" % (rc, json.dumps(request['message'])))

            elif request['topic'] == update_location_topic:
                if rc == 200:
                    self.logger.info("[%s] Location update action completed: %s" % (rc, json.dumps(request['message'])))
                else:
                    self.logger.critical("[%s] Location update action failed: %s" % (rc, json.dumps(request['message'])))

            elif request['topic'] == add_error_code_topic:
                if rc == 200:
                    self.logger.info("[%s] Add error code action completed: %s" % (rc, json.dumps(request['message'])))
                else:
                    self.logger.critical("[%s] Add error code action failed: %s" % (rc, json.dumps(request['message'])))

            elif request['topic'] == clear_error_codes_topic:
                if rc == 200:
                    self.logger.info("[%s] Clear error codes action completed: %s" % (rc, json.dumps(request['message'])))
                else:
                    self.logger.critical("[%s] Clear error codes action failed: %s" % (rc, json.dumps(request['message'])))

            else:
                self.logger.warning("[%s] Unknown action response: %s" % (rc, json.dumps(request['message'])))

            # Now clear the event, allowing anyone that was waiting on this to proceed
            request["event"].set()
            return True



def ParseConfigFile(configFilePath):
    parms = configparser.ConfigParser({
        "domain": "internetofthings.ibmcloud.com",
        "port": "8883", # Even though this is a string here, the parms.getint method will ensure it's assigned as an int
        "clean-session": "true"
    })
    sectionHeader = "device"

    try:
        with open(configFilePath) as f:
            try:
                parms.read_file(f)
            except AttributeError:
                # Python 2.7 support
                # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_file
                parms.readfp(f)

        domain = parms.get(sectionHeader, "domain")
        organization = parms.get(sectionHeader, "org")
        deviceType = parms.get(sectionHeader, "type")
        deviceId = parms.get(sectionHeader, "id")

        authMethod = parms.get(sectionHeader, "auth-method")
        authToken = parms.get(sectionHeader, "auth-token")
        cleanSession = parms.get(sectionHeader, "clean-session")
        port = parms.getint(sectionHeader, "port")

    except IOError as e:
        reason = "Error reading device configuration file '%s' (%s)" % (configFilePath,e[1])
        raise ConfigurationException(reason)

    return {'domain': domain, 'org': organization, 'type': deviceType, 'id': deviceId, 'auth-method': authMethod, 'auth-token': authToken, 'clean-session': cleanSession, 'port': int(port)}
