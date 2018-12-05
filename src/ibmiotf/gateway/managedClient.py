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
from ibmiotf.device.managedClient import ManagedDeviceClient
from ibmiotf.device.deviceInfo import DeviceInfo
from ibmiotf.gateway.config import GatewayClientConfig
from ibmiotf.gateway.messages import Command, Notification

from ibmiotf import api


class ManagedGatewayClient(ManagedDeviceClient):

    MANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/manage'
    UNMANAGE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/mgmt/unmanage'
    UPDATE_LOCATION_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/device/update/location'
    ADD_ERROR_CODE_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/add/diag/errorCodes'
    CLEAR_ERROR_CODES_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/clear/diag/errorCodes'
    NOTIFY_TOPIC_TEMPLATE = 'iotdevice-1/type/%s/id/%s/notify'

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/response'
    DM_OBSERVE_TOPIC_TEMPLATE = 'iotdm-1/type/%s/id/%s/observe'


    def __init__(self, config, logHandlers=None, deviceInfo=None):
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

        # ---------------------------------------------------------------------
        # Device Management Specific code starts here
        # ---------------------------------------------------------------------
        self.subscriptionsAcknowledged = threading.Event()

        # Add handler for supported device management commands
        self.client.message_callback_add("iotdm-1/#", self.__onDeviceMgmtResponse)

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
    

    def _onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connectEvent.set()
            self.logger.info("Connected successfully: %s, Port: %s" % (self.clientId,self.port))

            dm_response_topic = ManagedGatewayClient.DM_RESPONSE_TOPIC_TEMPLATE %  (self._config.typeId, self._config.deviceId)
            dm_observe_topic = ManagedGatewayClient.DM_OBSERVE_TOPIC_TEMPLATE %  (self._config.typeId, self._config.deviceId)
            (self.dmSubscriptionResult, self.dmSubscriptionMid) = self.client.subscribe( [(dm_response_topic, 1), (dm_observe_topic, 1), (self.COMMAND_TOPIC, 1)] )

            if self.dmSubscriptionResult != paho.MQTT_ERR_SUCCESS:
                self._logAndRaiseException(ConnectionException("Unable to subscribe to device management topics"))

        elif rc == 5:
            self._logAndRaiseException(ConnectionException("Not authorized: s (%s, %s, %s)" % (self.clientId, self.username, self.password)))
        else:
            self._logAndRaiseException(ConnectionException("Connection failed: RC= %s" % (rc)))


    def _onSubscribe(self, client, userdata, mid, grantedQoS):
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


    def setProperty(self, name, value):
        if name not in ["serialNumber", "manufacturer", "model", "deviceClass", "description", "fwVersion", "hwVersion", "descriptiveLocation"]:
            raise Exception("Unsupported property name: %s" % name)

        self._deviceInfo[name] = value
        return self.notifyFieldChange("deviceInfo.%s" % name, value)


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

                notify_topic = ManagedGatewayClient.NOTIFY_TOPIC_TEMPLATE %  (self._config.typeId,self._config.deviceId)
                resolvedEvent = threading.Event()

                self.client.publish(notify_topic, payload=json.dumps(message), qos=1, retain=False)
                with self._deviceMgmtRequestsPendingLock:
                    self._deviceMgmtRequestsPending[reqId] = {"topic": notify_topic, "message": message, "event": resolvedEvent}

                return resolvedEvent
            else:
                return threading.Event().set()


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

        manage_topic = ManagedGatewayClient.MANAGE_TOPIC_TEMPLATE % (self._config.typeId,self._config.deviceId)
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

        unmanage_topic = ManagedGatewayClient.UNMANAGE_TOPIC_TEMPLATE % (self._config.typeId,self._config.deviceId)
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

        update_location_topic = ManagedGatewayClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (self.config.typeId,self._config.deviceId)
        resolvedEvent = threading.Event()

        self.client.publish(update_location_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": update_location_topic, "message": message, "event": resolvedEvent}

        return resolvedEvent


    def setErrorCode(self, errorCode=0):
        if errorCode is None:
            errorCode = 0

        self._errorCode = errorCode

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": { "errorCode": errorCode },
            "reqId": reqId
        }

        add_error_code_topic = ManagedGatewayClient.ADD_ERROR_CODE_TOPIC_TEMPLATE %  (self._config.typeId,self._config.deviceId)
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

        clear_error_codes_topic = ManagedGatewayClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._config.typeId, self._config.deviceId)
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

            manage_topic = ManagedGatewayClient.MANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            unmanage_topic = ManagedGatewayClient.UNMANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            update_location_topic = ManagedGatewayClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            add_error_code_topic = ManagedGatewayClient.ADD_ERROR_CODE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            clear_error_codes_topic = ManagedGatewayClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE %  (self._config.typeId, self._config.deviceId)

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
