import os
import pytest
import uuid

from testUtils import AbstractTest

from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.registry.devices import DeviceCreateRequest

import logging

logger = logging.getLogger()


@pytest.fixture(scope="module")
def testUtil(request):
    yield AbstractTest()


@pytest.fixture(scope="module")
def deviceType(request, testUtil):
    """
    You only get one device type created per test suite (per file/module)
    """
    typeId = "%s_%s" % ("iotpython", request.module.__name__)
    # Chop off some characters if module name is too long
    typeId = typeId[:32]
    try:
        deviceType = testUtil.appClient.registry.devicetypes[typeId]
        logger.debug("Device type %s already exists for test %s" % (typeId, request.module.__name__))
    except KeyError:
        logger.debug("Device type %s doesn't exist, creating now for test %s" % (typeId, request.module.__name__))
        try:
            deviceType = testUtil.appClient.registry.devicetypes.create({"id": typeId})
        except ApiException as ex:
            logging.exception(
                "Unable to register device type for test %s. API response: %s" % (request.module.__name__, ex.message)
            )

    yield deviceType
    # We don't delete the devicetype as we want to re-use it across threads in Travis
    # testUtil.appClient.registry.devicetypes.delete(typeId)


@pytest.fixture
def device(request, testUtil, deviceType, authToken):
    """
    One device will be created per testcase (per function)
    """
    # Max length is 36, chop off some characters if test name is too long
    deviceId = str(uuid.uuid4())
    deviceUid = "d:%s:%s:%s" % (testUtil.ORG_ID, deviceType.id, deviceId)

    # Cleanup any old devices to ensure auth token will be correct for test
    if deviceId in deviceType.devices:
        logger.debug("Deleting device %s to start fresh for test %s" % (deviceUid, request.function.__name__))
        testUtil.appClient.registry.devices.delete({"typeId": deviceType.id, "deviceId": deviceId})

    logger.debug("Creating device %s for test %s" % (deviceUid, request.function.__name__))
    try:
        deviceReq = DeviceCreateRequest(typeId=deviceType.id, deviceId=deviceId, authToken=authToken)
        deviceCreateResponse = testUtil.appClient.registry.devices.create(deviceReq)
        device = testUtil.appClient.registry.devices[deviceUid]
        device["authToken"] = deviceCreateResponse.authToken

    except ApiException as ex:
        logging.exception(
            "Unable to register device for test %s. API response: %s" % (request.function.__name__, ex.message)
        )

    yield device

    # Cleanup device after test is finished
    testUtil.appClient.registry.devices.delete({"typeId": deviceType.id, "deviceId": deviceId})


@pytest.fixture(scope="module")
def gatewayDeviceType(request, testUtil):
    """
    You only get one device type created per test suite (per file/module)
    """
    typeId = "%s_%s" % ("iotpython", request.module.__name__)
    # Chop off some characters if module name is too long
    typeId = typeId[:32]
    try:
        gatewayDeviceType = testUtil.appClient.registry.devicetypes[typeId]
        logger.debug("Device type %s already exists for test %s" % (typeId, request.module.__name__))
    except KeyError:
        logger.debug("Device type %s doesn't exist, creating now for test %s" % (typeId, request.module.__name__))
        try:
            gatewayDeviceType = testUtil.appClient.registry.devicetypes.create({"id": typeId, "classId": "Gateway"})
        except ApiException as ex:
            logging.exception(
                "Unable to register device type for test %s. API response: %s" % (request.module.__name__, ex.message)
            )

    yield gatewayDeviceType

    # We don't delete the devicetype as we want to re-use it across threads in Travis
    # testUtil.appClient.registry.devicetypes.delete(typeId)


@pytest.fixture
def gateway(request, testUtil, gatewayDeviceType, authToken):
    """
    One gateway will be created per testcase (per function)
    """
    # Max length is 36, chop off some characters if test name is too long
    gatewayId = str(uuid.uuid4())
    gatewayUid = "d:%s:%s:%s" % (testUtil.ORG_ID, gatewayDeviceType.id, gatewayId)

    # Cleanup any old devices to ensure auth token will be correct for test
    if gatewayId in gatewayDeviceType.devices:
        logger.debug("Deleting device %s to start fresh for test %s" % (gatewayUid, request.function.__name__))
        testUtil.appClient.registry.devices.delete({"typeId": gatewayDeviceType.id, "deviceId": gatewayId})

    logger.debug("Creating device %s for test %s" % (gatewayUid, request.function.__name__))
    try:
        deviceReq = DeviceCreateRequest(typeId=gatewayDeviceType.id, deviceId=gatewayId, authToken=authToken)
        gatewayCreateResponse = testUtil.appClient.registry.devices.create(deviceReq)
        gateway = testUtil.appClient.registry.devices[gatewayUid]
        gateway["authToken"] = gatewayCreateResponse.authToken
    except ApiException as ex:
        logging.exception(
            "Unable to register device for test %s. API response: %s" % (request.function.__name__, ex.message)
        )

    yield gateway

    # Cleanup device after test is finished
    testUtil.appClient.registry.devices.delete({"typeId": gateway.typeId, "deviceId": gateway.deviceId})


@pytest.fixture
def manageEnvVars(request):
    # Add placeholder environmental variables for testing
    os.environ["WIOTP_IDENTITY_ORGID"] = "myOrg"
    os.environ["WIOTP_IDENTITY_TYPEID"] = "myType"
    os.environ["WIOTP_IDENTITY_DEVICEID"] = "myDevice"
    os.environ["WIOTP_AUTH_TOKEN"] = "myToken"
    os.environ["WIOTP_OPTIONS_MQTT_PORT"] = "0"
    os.environ["WIOTP_OPTIONS_MQTT_SESSIONEXPIRY"] = "0"
    os.environ["WIOTP_OPTIONS_MQTT_KEEPALIVE"] = "0"
    os.environ["WIOTP_OPTIONS_LOGLEVEL"] = "info"
    yield manageEnvVars
    # Remove the placeholder variables so as not to intefere in other areas of the program
    try:
        del os.environ["WIOTP_IDENTITY_ORGID"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_IDENTITY_ORGID")
    try:
        del os.environ["WIOTP_IDENTITY_TYPEID"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_IDENTITY_TYPEID")
    try:
        del os.environ["WIOTP_IDENTITY_DEVICEID"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_IDENTITY_DEVICEID")
    try:
        del os.environ["WIOTP_AUTH_TOKEN"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_AUTH_TOKEN")
    try:
        del os.environ["WIOTP_MQTT_OPTIONS_PORT"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_PORT")
    try:
        del os.environ["WIOTP_OPTIONS_MQTT_SESSIONEXPIRY"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_OPTIONS_MQTT_SESSIONEXPIRY")
    try:
        del os.environ["WIOTP_OPTIONS_MQTT_KEEPALIVE"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_OPTIONS_MQTT_KEEPALIVE")
    try:
        del os.environ["WIOTP_OPTIONS_LOGLEVEL"]
    except KeyError:
        logging.exception("KeyError when deleting WIOTP_OPTIONS_LOGLEVEL")


@pytest.fixture
def authToken():
    logger.debug("Generating auth token for test...")
    yield str(uuid.uuid4())
