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

from wiotp.sdk import (
    AbstractClient,
    InvalidEventException,
    UnsupportedAuthenticationMethod,
    ConfigurationException,
    ConnectionException,
    MissingMessageEncoderException,
    MissingMessageDecoderException,
)
from wiotp.sdk.device.managedClient import ManagedDeviceClient
from wiotp.sdk.device.deviceInfo import DeviceInfo
from wiotp.sdk.gateway.config import GatewayClientConfig
from wiotp.sdk.gateway.messages import Command, Notification


class ManagedGatewayClient(ManagedDeviceClient):

    MANAGE_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/mgmt/manage"
    UNMANAGE_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/mgmt/unmanage"
    UPDATE_LOCATION_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/device/update/location"
    ADD_ERROR_CODE_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/add/diag/errorCodes"
    CLEAR_ERROR_CODES_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/clear/diag/errorCodes"
    NOTIFY_TOPIC_TEMPLATE = "iotdevice-1/type/%s/id/%s/notify"

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC_TEMPLATE = "iotdm-1/type/%s/id/%s/response"
    DM_OBSERVE_TOPIC_TEMPLATE = "iotdm-1/type/%s/id/%s/observe"

    def __init__(self, config, logHandlers=None, deviceInfo=None):
        """
        Override the constructor
        """
        if config["identity"]["orgId"] == "quickstart":
            raise ConfigurationException("QuickStart does not support device management")

        self._config = GatewayClientConfig(**config)

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

        self.COMMAND_TOPIC = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/cmd/+/fmt/+"

        gatewayCommandTopic = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/cmd/+/fmt/json"
        deviceCommandTopic = "iot-2/type/+/id/+/cmd/+/fmt/+"
        messageNotificationTopic = "iot-2/type/" + self._config.typeId + "/id/" + self._config.deviceId + "/notify"

        self.client.message_callback_add(gatewayCommandTopic, self._onCommand)
        self.client.message_callback_add(deviceCommandTopic, self._onDeviceCommand)
        self.client.message_callback_add(messageNotificationTopic, self._onMessageNotification)

        # Initialize user supplied callback
        self.deviceCommandCallback = None
        self.notificationCallback = None

        # ---------------------------------------------------------------------
        # Device Management Specific code starts here
        # ---------------------------------------------------------------------
        self.readyForDeviceMgmt = threading.Event()

        # Add handler for supported device management commands
        self.client.message_callback_add("iotdm-1/#", self.__onDeviceMgmtResponse)

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

        # Initialize subscription list
        self._subscriptions[self.DM_RESPONSE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)] = 1
        self._subscriptions[self.DM_OBSERVE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)] = 1
        self._subscriptions[self.COMMAND_TOPIC] = 1

    def publishDeviceEvent(self, typeId, deviceId, eventId, msgFormat, data, qos=0, onPublish=None):
        topic = "iot-2/type/" + typeId + "/id/" + deviceId + "/evt/" + eventId + "/fmt/" + msgFormat
        return self._publishEvent(topic, eventId, msgFormat, data, qos, onPublish)

    def publishEvent(self, eventId, msgFormat, data, qos=0, onPublish=None):
        topic = (
            "iot-2/type/"
            + self._config.typeId
            + "/id/"
            + self._config.deviceId
            + "/evt/"
            + eventId
            + "/fmt/"
            + msgFormat
        )
        return self._publishEvent(topic, eventId, msgFormat, data, qos, onPublish)

    def subscribeToDeviceCommands(self, typeId, deviceId, commandId="+", format="json", qos=1):
        topic = "iot-2/type/" + typeId + "/id/" + deviceId + "/cmd/" + commandId + "/fmt/" + format
        return self._subscribe(topic, qos=1)

    def subscribeToCommands(self, commandId="+", format="json", qos=1):
        typeId = self._config.typeId
        deviceId = self._config.deviceId
        topic = "iot-2/type/" + typeId + "/id/" + deviceId + "/cmd/" + commandId + "/fmt/" + format
        return self._subscribe(topic, qos=1)

    def subscribeToNotifications(self):
        typeId = self._config.typeId
        deviceId = self._config.deviceId
        topic = "iot-2/type/" + typeId + "/id/" + deviceId + "/notify"

        return self._subscribe(topic, qos=0)

    def _onDeviceCommand(self, client, userdata, pahoMessage):
        """
        Internal callback for gateway command messages, parses source device from topic string and
        passes the information on to the registered device command callback
        """
        try:
            command = Command(pahoMessage, self._messageCodecs)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received gateway command '%s'" % (command.command))
            if self.deviceCommandCallback:
                self.deviceCommandCallback(command)

    def _onMessageNotification(self, client, userdata, pahoMessage):
        """
        Internal callback for gateway notification messages, parses source device from topic string and
        passes the information on to the registered device command callback
        """
        try:
            note = Notification(pahoMessage, self._messageCodecs)
        except InvalidEventException as e:
            self.logger.critical(str(e))
        else:
            self.logger.debug("Received Notification")
            if self.notificationCallback:
                self.notificationCallback(note)

    def setProperty(self, name, value):
        if name not in [
            "serialNumber",
            "manufacturer",
            "model",
            "deviceClass",
            "description",
            "fwVersion",
            "hwVersion",
            "descriptiveLocation",
        ]:
            raise Exception("Unsupported property name: %s" % name)

        self._deviceInfo[name] = value
        return self.notifyFieldChange("deviceInfo.%s" % name, value)

    def notifyFieldChange(self, field, value):
        with self._deviceMgmtObservationsLock:
            if field in self._deviceMgmtObservations:
                if not self.readyForDeviceMgmt.wait(timeout=10):
                    self.logger.warning(
                        "Unable to notify service of field change because gateway is not ready for gateway management"
                    )
                    return threading.Event().set()

                reqId = str(uuid.uuid4())
                message = {"d": {"field": field, "value": value}, "reqId": reqId}

                notify_topic = ManagedGatewayClient.NOTIFY_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
                resolvedEvent = threading.Event()

                self.client.publish(notify_topic, payload=json.dumps(message), qos=1, retain=False)
                with self._deviceMgmtRequestsPendingLock:
                    self._deviceMgmtRequestsPending[reqId] = {
                        "topic": notify_topic,
                        "message": message,
                        "event": resolvedEvent,
                    }

                return resolvedEvent
            else:
                return threading.Event().set()

    def manage(self, lifetime=3600, supportDeviceActions=False, supportFirmwareActions=False):
        # TODO: throw an error, minimum lifetime this client will support is 1 hour, but for now set lifetime to infinite if it's invalid
        if lifetime < 3600:
            lifetime = 0

        if not self.subscriptionsAcknowledged.wait(timeout=10):
            self.logger.warning(
                "Unable to send register for device management because device subscriptions are not in place"
            )
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {
            "d": {
                "lifetime": lifetime,
                "supports": {"deviceActions": supportDeviceActions, "firmwareActions": supportFirmwareActions},
                "deviceInfo": self._deviceInfo.__dict__,
                "metadata": self.metadata,
            },
            "reqId": reqId,
        }

        manage_topic = ManagedGatewayClient.MANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
        resolvedEvent = threading.Event()

        self.client.publish(manage_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {"topic": manage_topic, "message": message, "event": resolvedEvent}

        # Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
        if lifetime != 0:
            threading.Timer(
                lifetime - 120, self.manage, [lifetime, supportDeviceActions, supportFirmwareActions]
            ).start()

        return resolvedEvent

    def unmanage(self):
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to set device to unmanaged because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"reqId": reqId}

        unmanage_topic = ManagedGatewayClient.UNMANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
        resolvedEvent = threading.Event()

        self.client.publish(unmanage_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": unmanage_topic,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def setLocation(self, longitude, latitude, elevation=None, accuracy=None):
        # TODO: Add validation (e.g. ensure numeric values)
        if self._location is None:
            self._location = {}

        self._location["longitude"] = longitude
        self._location["latitude"] = latitude
        if elevation:
            self._location["elevation"] = elevation

        self._location["measuredDateTime"] = datetime.now(pytz.timezone("UTC")).isoformat()

        if accuracy:
            self._location["accuracy"] = accuracy
        elif "accuracy" in self._location:
            del self._location["accuracy"]

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish device location because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"d": self._location, "reqId": reqId}

        update_location_topic = ManagedGatewayClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (
            self.config.typeId,
            self._config.deviceId,
        )
        resolvedEvent = threading.Event()

        self.client.publish(update_location_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": update_location_topic,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def setErrorCode(self, errorCode=0):
        if errorCode is None:
            errorCode = 0

        self._errorCode = errorCode

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"d": {"errorCode": errorCode}, "reqId": reqId}

        add_error_code_topic = ManagedGatewayClient.ADD_ERROR_CODE_TOPIC_TEMPLATE % (
            self._config.typeId,
            self._config.deviceId,
        )
        resolvedEvent = threading.Event()

        self.client.publish(add_error_code_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": add_error_code_topic,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def clearErrorCodes(self):
        self._errorCode = None

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear error codes because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"reqId": reqId}

        clear_error_codes_topic = ManagedGatewayClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE % (
            self._config.typeId,
            self._config.deviceId,
        )
        resolvedEvent = threading.Event()

        self.client.publish(clear_error_codes_topic, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": clear_error_codes_topic,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):
        try:
            data = json.loads(pahoMessage.payload.decode("utf-8"))

            rc = data["rc"]
            reqId = data["reqId"]
        except ValueError as e:
            raise Exception('Unable to parse JSON.  payload="%s" error=%s' % (pahoMessage.payload, str(e)))
        else:
            request = None
            with self._deviceMgmtRequestsPendingLock:
                try:
                    request = self._deviceMgmtRequestsPending.pop(reqId)
                except KeyError:
                    self.logger.warning("Received unexpected response from device management: %s" % (reqId))
                else:
                    self.logger.debug(
                        "Remaining unprocessed device management requests: %s" % (len(self._deviceMgmtRequestsPending))
                    )

            if request is None:
                return False

            manage_topic = ManagedGatewayClient.MANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            unmanage_topic = ManagedGatewayClient.UNMANAGE_TOPIC_TEMPLATE % (self._config.typeId, self._config.deviceId)
            update_location_topic = ManagedGatewayClient.UPDATE_LOCATION_TOPIC_TEMPLATE % (
                self._config.typeId,
                self._config.deviceId,
            )
            add_error_code_topic = ManagedGatewayClient.ADD_ERROR_CODE_TOPIC_TEMPLATE % (
                self._config.typeId,
                self._config.deviceId,
            )
            clear_error_codes_topic = ManagedGatewayClient.CLEAR_ERROR_CODES_TOPIC_TEMPLATE % (
                self._config.typeId,
                self._config.deviceId,
            )

            if request["topic"] == manage_topic:
                if rc == 200:
                    self.logger.info("[%s] Manage action completed: %s" % (rc, json.dumps(request["message"])))
                    self.readyForDeviceMgmt.set()
                else:
                    self.logger.critical("[%s] Manage action failed: %s" % (rc, json.dumps(request["message"])))

            elif request["topic"] == unmanage_topic:
                if rc == 200:
                    self.logger.info("[%s] Unmanage action completed: %s" % (rc, json.dumps(request["message"])))
                    self.readyForDeviceMgmt.clear()
                else:
                    self.logger.critical("[%s] Unmanage action failed: %s" % (rc, json.dumps(request["message"])))

            elif request["topic"] == update_location_topic:
                if rc == 200:
                    self.logger.info("[%s] Location update action completed: %s" % (rc, json.dumps(request["message"])))
                else:
                    self.logger.critical(
                        "[%s] Location update action failed: %s" % (rc, json.dumps(request["message"]))
                    )

            elif request["topic"] == add_error_code_topic:
                if rc == 200:
                    self.logger.info("[%s] Add error code action completed: %s" % (rc, json.dumps(request["message"])))
                else:
                    self.logger.critical("[%s] Add error code action failed: %s" % (rc, json.dumps(request["message"])))

            elif request["topic"] == clear_error_codes_topic:
                if rc == 200:
                    self.logger.info(
                        "[%s] Clear error codes action completed: %s" % (rc, json.dumps(request["message"]))
                    )
                else:
                    self.logger.critical(
                        "[%s] Clear error codes action failed: %s" % (rc, json.dumps(request["message"]))
                    )

            else:
                self.logger.warning("[%s] Unknown action response: %s" % (rc, json.dumps(request["message"])))

            # Now clear the event, allowing anyone that was waiting on this to proceed
            request["event"].set()
            return True
