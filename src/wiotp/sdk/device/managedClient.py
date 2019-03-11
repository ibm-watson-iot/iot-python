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
import pytz
import uuid

from wiotp.sdk import ConnectionException, ConfigurationException
from wiotp.sdk.device.client import DeviceClient
from wiotp.sdk.device.deviceInfo import DeviceInfo
from wiotp.sdk.device.deviceFirmware import DeviceFirmware


class ManagedDeviceClient(DeviceClient):

    # Publish MQTT topics
    MANAGE_TOPIC = "iotdevice-1/mgmt/manage"
    UNMANAGE_TOPIC = "iotdevice-1/mgmt/unmanage"
    UPDATE_LOCATION_TOPIC = "iotdevice-1/device/update/location"
    ADD_ERROR_CODE_TOPIC = "iotdevice-1/add/diag/errorCodes"
    CLEAR_ERROR_CODES_TOPIC = "iotdevice-1/clear/diag/errorCodes"
    NOTIFY_TOPIC = "iotdevice-1/notify"
    RESPONSE_TOPIC = "iotdevice-1/response"
    ADD_LOG_TOPIC = "iotdevice-1/add/diag/log"
    CLEAR_LOG_TOPIC = "iotdevice-1/clear/diag/log"

    # Subscribe MQTT topics
    DM_RESPONSE_TOPIC = "iotdm-1/response"
    DM_OBSERVE_TOPIC = "iotdm-1/observe"
    DM_REBOOT_TOPIC = "iotdm-1/mgmt/initiate/device/reboot"
    DM_FACTORY_REESET = "iotdm-1/mgmt/initiate/device/factory_reset"
    DM_UPDATE_TOPIC = "iotdm-1/device/update"
    DM_CANCEL_OBSERVE_TOPIC = "iotdm-1/cancel"
    DM_FIRMWARE_DOWNLOAD_TOPIC = "iotdm-1/mgmt/initiate/firmware/download"
    DM_FIRMWARE_UPDATE_TOPIC = "iotdm-1/mgmt/initiate/firmware/update"
    DME_ACTION_TOPIC = "iotdm-1/mgmt/custom/#"

    # ResponceCode
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
        if config["identity"]["orgId"] == "quickstart":
            raise ConfigurationException("QuickStart does not support device management")

        DeviceClient.__init__(self, config, logHandlers)

        # Initialize user supplied callback
        self.deviceActionCallback = None
        self.firmwereActionCallback = None
        self.dmeActionCallback = None

        messages_callbacks = (
            ("iotdm-1/#", self.__onDeviceMgmtResponse),
            (ManagedDeviceClient.DM_REBOOT_TOPIC, self.__onRebootRequest),
            (ManagedDeviceClient.DM_FACTORY_REESET, self.__onFactoryResetRequest),
            (ManagedDeviceClient.DM_FIRMWARE_UPDATE_TOPIC, self.__onFirmwereUpdate),
            (ManagedDeviceClient.DM_OBSERVE_TOPIC, self.__onFirmwereObserve),
            (ManagedDeviceClient.DM_FIRMWARE_DOWNLOAD_TOPIC, self.__onFirmwereDownload),
            (ManagedDeviceClient.DM_UPDATE_TOPIC, self.__onUpdatedDevice),
            (ManagedDeviceClient.DM_CANCEL_OBSERVE_TOPIC, self.__onFirmwereCancel),
            (ManagedDeviceClient.DME_ACTION_TOPIC, self.__onDMEActionRequest),
        )

        # Add handler for supported device management commands
        for message, callback in messages_callbacks:
            self.client.message_callback_add(message, callback)

        # Initialize user supplied callback
        self.client.on_subscribe = self._onSubscribe
        self.client.on_disconnect = self._onDisconnect

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

        # Register startup subscription list
        self._subscriptions[self.DM_RESPONSE_TOPIC] = 1
        self._subscriptions[self.DM_OBSERVE_TOPIC] = 1
        self._subscriptions[self.DM_REBOOT_TOPIC] = 1
        self._subscriptions[self.DM_FACTORY_REESET] = 1
        self._subscriptions[self.DM_UPDATE_TOPIC] = 1
        self._subscriptions[self.DM_FIRMWARE_UPDATE_TOPIC] = 1
        self._subscriptions[self.DM_FIRMWARE_DOWNLOAD_TOPIC] = 1
        self._subscriptions[self.DM_CANCEL_OBSERVE_TOPIC] = 1
        self._subscriptions[self._COMMAND_TOPIC] = 1
        self._subscriptions[self.DME_ACTION_TOPIC] = 1

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
                        "Unable to notify service of field "
                        "change because device is not ready "
                        "for device management"
                    )
                    return threading.Event().set()

                reqId = str(uuid.uuid4())
                message = {"d": {"field": field, "value": value}, "reqId": reqId}

                resolvedEvent = threading.Event()
                self.client.publish(ManagedDeviceClient.NOTIFY_TOPIC, payload=json.dumps(message), qos=1, retain=False)
                with self._deviceMgmtRequestsPendingLock:
                    self._deviceMgmtRequestsPending[reqId] = {
                        "topic": ManagedDeviceClient.NOTIFY_TOPIC,
                        "message": message,
                        "event": resolvedEvent,
                    }

                return resolvedEvent
            else:
                return threading.Event().set()

    def _onSubscribe(self, mqttc, userdata, mid, granted_qos):
        super(ManagedDeviceClient, self)._onSubscribe(mqttc, userdata, mid, granted_qos)
        # Once IoTF acknowledges the subscriptions we are able to process commands and responses from device management server
        self.manage()

    def manage(
        self,
        lifetime=3600,
        supportDeviceActions=True,
        supportFirmwareActions=True,
        supportDeviceMgmtExtActions=False,
        bundleIds=[],
    ):
        # TODO: throw an error, minimum lifetime this client will support is 1 hour, but for now set lifetime to infinite if it's invalid
        if lifetime < 3600:
            lifetime = 0

        if not self.subscriptionsAcknowledged.wait(timeout=10):
            self.logger.warning(
                "Unable to send register for device " "management because device subscriptions " "are not in place"
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
        if supportDeviceMgmtExtActions and len(bundleIds) > 0:
            for bundleId in bundleIds:
                message["d"]["supports"][bundleId] = supportDeviceMgmtExtActions

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.MANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.MANAGE_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        # Register the future call back to Watson IoT Platform 2 minutes before the device lifetime expiry
        if lifetime != 0:
            if self.manageTimer is not None:
                self.logger.debug("Cancelling existing manage timer")
                self.manageTimer.cancel()
            self.manageTimer = threading.Timer(
                lifetime - 120,
                self.manage,
                [lifetime, supportDeviceActions, supportFirmwareActions, supportDeviceMgmtExtActions, bundleIds],
            )
            self.manageTimer.start()

        return resolvedEvent

    def unmanage(self):
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning(
                "Unable to set device to unmanaged because " "device is not ready for device management"
            )
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.UNMANAGE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.UNMANAGE_TOPIC,
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
            self.logger.warning(
                "Unable to publish device location because " "device is not ready for device management"
            )
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"d": self._location, "reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.UPDATE_LOCATION_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.UPDATE_LOCATION_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def setErrorCode(self, errorCode=0):
        if errorCode is None:
            errorCode = 0

        self._errorCode = errorCode

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because " "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"d": {"errorCode": errorCode}, "reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.ADD_ERROR_CODE_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.ADD_ERROR_CODE_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def clearErrorCodes(self):
        self._errorCode = None

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear error codes because " "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(
            ManagedDeviceClient.CLEAR_ERROR_CODES_TOPIC, payload=json.dumps(message), qos=1, retain=False
        )
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.CLEAR_ERROR_CODES_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def addLog(self, msg="", data="", sensitivity=0):
        timestamp = datetime.now().isoformat()
        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to publish error code because " "device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"d": {"message": msg, "timestamp": timestamp, "data": data, "severity": sensitivity}, "reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.ADD_LOG_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.ADD_LOG_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def clearLog(self):

        if not self.readyForDeviceMgmt.wait(timeout=10):
            self.logger.warning("Unable to clear log because device is not ready for device management")
            return threading.Event().set()

        reqId = str(uuid.uuid4())
        message = {"reqId": reqId}

        resolvedEvent = threading.Event()
        self.client.publish(ManagedDeviceClient.CLEAR_LOG_TOPIC, payload=json.dumps(message), qos=1, retain=False)
        with self._deviceMgmtRequestsPendingLock:
            self._deviceMgmtRequestsPending[reqId] = {
                "topic": ManagedDeviceClient.CLEAR_LOG_TOPIC,
                "message": message,
                "event": resolvedEvent,
            }

        return resolvedEvent

    def __onDeviceMgmtResponse(self, client, userdata, pahoMessage):

        try:
            data = json.loads(pahoMessage.payload.decode("utf-8"))
            if "rc" not in data:
                return True
            rc = data["rc"]
            reqId = data["reqId"]
        except ValueError as e:
            raise Exception('Unable to parse JSON. payload="%s" error=%s' % (pahoMessage.payload, str(e)))
        else:
            request = None
            with self._deviceMgmtRequestsPendingLock:
                try:
                    request = self._deviceMgmtRequestsPending.pop(reqId)
                except KeyError:
                    self.logger.warning("Received unexpected response from " "device management: %s", reqId)
                else:
                    self.logger.debug(
                        "Remaining unprocessed device " "management requests: %s", len(self._deviceMgmtRequestsPending)
                    )

            if request is None:
                return False

            state = {
                ManagedDeviceClient.MANAGE_TOPIC: {
                    # rc, json.dumps(request['message'])
                    "msg_succ": "[%s] Manage action completed: %s",
                    "msg_fail": "[%s] Manage action failed: %s",
                },
                ManagedDeviceClient.UNMANAGE_TOPIC: {
                    "msg_succ": "[%s] Unmanage action completed: %s",
                    "msg_fail": "[%s] Unmanage action failed: %s",
                },
                ManagedDeviceClient.UPDATE_LOCATION_TOPIC: {
                    "msg_succ": "[%s] Location update action completed: %s",
                    "msg_fail": "[%s] Location update action failed: %s",
                },
                ManagedDeviceClient.ADD_ERROR_CODE_TOPIC: {
                    "msg_succ": "[%s] Add error code action completed: %s",
                    "msg_fail": "[%s] Add error code action failed: %s",
                },
                ManagedDeviceClient.CLEAR_ERROR_CODES_TOPIC: {
                    "msg_succ": "[%s] Clear error codes action completed: %s",
                    "msg_fail": "[%s] Clear error codes action failed: %s",
                },
                ManagedDeviceClient.ADD_LOG_TOPIC: {
                    "msg_succ": "[%s] Add log action completed: %s",
                    "msg_fail": "[%s] Add log action failed: %s",
                },
                ManagedDeviceClient.CLEAR_LOG_TOPIC: {
                    "msg_succ": "[%s] Clear log action completed: %s",
                    "msg_fail": "[%s] Clear log action failed: %s",
                },
            }

            try:
                msg_succ = state[request["topic"]]["msg_succ"]
                msg_fail = state[request["topic"]]["msg_fail"]
            except Exception as e:
                self.logger.warning("[%s] Unknown action response: %s", rc, json.dumps(request["message"]))
            else:
                dump_str = json.dumps(request["message"])
                if rc == 200:
                    self.logger.info(msg_succ, rc, dump_str)
                else:
                    self.logger.critical(msg_fail, rc, dump_str)

                if request["topic"] == ManagedDeviceClient.MANAGE_TOPIC:
                    self.readyForDeviceMgmt.set()
                elif request["topic"] == ManagedDeviceClient.UNMANAGE_TOPIC:
                    self.readyForDeviceMgmt.clear()

            # Now clear the event, allowing anyone that was waiting on this to proceed
            request["event"].set()
            return True

    # Device Action Handlers
    def __onRebootRequest(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_REBOOT_TOPIC, paho_payload
        )
        try:
            data = json.loads(paho_payload)
            reqId = data["reqId"]
            if self.deviceActionCallback:
                self.deviceActionCallback(reqId, "reboot")
        except ValueError as e:
            raise Exception('Unable to process Reboot request.  payload="%s" error=%s' % (pahoMessage.payload, str(e)))

    def __onFactoryResetRequest(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_FACTORY_REESET, paho_payload
        )
        try:
            data = json.loads(paho_payload)
            reqId = data["reqId"]
            if self.deviceActionCallback:
                self.deviceActionCallback(reqId, "reset")
        except ValueError as e:
            raise Exception(
                'Unable to process Factory Reset request.  payload="%s" error=%s' % (pahoMessage.payload, str(e))
            )

    def respondDeviceAction(self, reqId, responseCode=202, message=""):
        response = {"rc": responseCode, "message": message, "reqId": reqId}
        payload = json.dumps(response)
        self.logger.info("Publishing Device Action response with payload :%s", payload)
        self.client.publish("iotdevice-1/response", payload, qos=1, retain=False)

    # Firmware Handlers
    def __onFirmwereDownload(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s",
            ManagedDeviceClient.DM_FIRMWARE_DOWNLOAD_TOPIC,
            paho_payload,
        )

        data = json.loads(paho_payload)
        reqId = data["reqId"]
        rc = ManagedDeviceClient.RESPONSECODE_ACCEPTED
        msg = ""

        if self.__firmwareUpdate.state != ManagedDeviceClient.UPDATESTATE_IDLE:
            rc = ManagedDeviceClient.RESPONSECODE_BAD_REQUEST
            msg = "Cannot download as the device is not in idle state"
        thread = threading.Thread(target=self.respondDeviceAction, args=(reqId, rc, msg), name="respondDeviceAction")
        thread.start()
        if self.firmwereActionCallback:
            self.firmwereActionCallback("download", self.__firmwareUpdate)

    def __onFirmwereCancel(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_CANCEL_OBSERVE_TOPIC, paho_payload
        )
        data = json.loads(paho_payload)
        reqId = data["reqId"]
        thread = threading.Thread(target=self.respondDeviceAction, args=(reqId, 200, ""), name="respondDeviceAction")
        thread.start()

    def __onFirmwereObserve(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_OBSERVE_TOPIC, paho_payload
        )
        data = json.loads(paho_payload)
        reqId = data["reqId"]
        # TODO: Proprer validation for fields in payload
        thread = threading.Thread(target=self.respondDeviceAction, args=(reqId, 200, ""), name="respondDeviceAction")
        thread.start()

    def __onUpdatedDevice(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_UPDATE_TOPIC, paho_payload
        )

        data = json.loads(paho_payload)
        if "reqId" in data:
            reqId = data["reqId"]
            d = data["d"]
            value = None
            for obj in d["fields"]:
                if "field" in obj:
                    if obj["field"] == "mgmt.firmware":
                        value = obj["value"]
            if value is not None:
                self.__firmwareUpdate = DeviceFirmware(
                    value["version"],
                    value["name"],
                    value["uri"],
                    value["verifier"],
                    value["state"],
                    value["updateStatus"],
                    value["updatedDateTime"],
                )
            thread = threading.Thread(
                target=self.respondDeviceAction, args=(reqId, 204, ""), name="respondDeviceAction"
            )
            thread.start()
        else:
            d = data["d"]
            value = None
            for obj in d["fields"]:
                if "field" in obj:
                    if obj["field"] == "metadata":
                        value = obj["value"]
            if value is not None:
                self.metadata = value

    def setState(self, status):
        notify = {"d": {"fields": [{"field": "mgmt.firmware", "value": {"state": status}}]}}
        if self.__firmwareUpdate is not None:
            self.__firmwareUpdate.state = status

        self.logger.info("Publishing state Update with payload :%s", json.dumps(notify))
        thread = threading.Thread(
            target=self.client.publish, args=("iotdevice-1/notify", json.dumps(notify), 1, False), name="client.publish"
        )
        thread.start()

    def setUpdateStatus(self, status):
        notify = {
            "d": {
                "fields": [
                    {
                        "field": "mgmt.firmware",
                        "value": {"state": ManagedDeviceClient.UPDATESTATE_IDLE, "updateStatus": status},
                    }
                ]
            }
        }
        if self.__firmwareUpdate is not None:
            self.__firmwareUpdate.state = ManagedDeviceClient.UPDATESTATE_IDLE
            self.__firmwareUpdate.updateStatus = status

        self.logger.info("Publishing  Update Status  with payload :%s", json.dumps(notify))
        thread = threading.Thread(
            target=self.client.publish, args=("iotdevice-1/notify", json.dumps(notify), 1, False), name="client.publish"
        )
        thread.start()

    def __onFirmwereUpdate(self, client, userdata, pahoMessage):
        paho_payload = pahoMessage.payload.decode("utf-8")
        self.logger.info(
            "Message received on topic :%s with payload %s", ManagedDeviceClient.DM_FIRMWARE_UPDATE_TOPIC, paho_payload
        )

        data = json.loads(paho_payload)
        reqId = data["reqId"]
        rc = ManagedDeviceClient.RESPONSECODE_ACCEPTED
        msg = ""
        if self.__firmwareUpdate.state != ManagedDeviceClient.UPDATESTATE_DOWNLOADED:
            rc = ManagedDeviceClient.RESPONSECODE_BAD_REQUEST
            msg = "Firmware is still not successfully downloaded."
        thread = threading.Thread(target=self.respondDeviceAction, args=(reqId, rc, msg), name="respondDeviceAction")
        thread.start()
        if self.firmwereActionCallback:
            self.firmwereActionCallback("update", self.__firmwareUpdate)

    def __onDMEActionRequest(self, client, userdata, pahoMessage):
        data = json.loads(pahoMessage.payload.decode("utf-8"))
        self.logger.info("Message received on topic :%s with payload %s", ManagedDeviceClient.DME_ACTION_TOPIC, data)

        reqId = data["reqId"]
        if self.dmeActionCallback:
            if self.dmeActionCallback(pahoMessage.topic, data, reqId):
                msg = "DME Action successfully completed from Callback"
                thread = threading.Thread(
                    target=self.respondDeviceAction, args=(reqId, 200, msg), name="respondDeviceAction"
                )
                thread.start()
            else:
                msg = "Unexpected device error"
                thread = threading.Thread(
                    target=self.respondDeviceAction, args=(reqId, 500, msg), name="respondDeviceAction"
                )
                thread.start()

        else:
            thread = threading.Thread(
                target=self.respondDeviceAction,
                args=(reqId, 501, "Operation not implemented"),
                name="respondDeviceAction",
            )
            thread.start()
