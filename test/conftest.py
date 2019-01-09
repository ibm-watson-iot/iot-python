import os
import pytest
import uuid

from testUtils import AbstractTest

from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.registry.devices import DeviceCreateRequest

import logging
logger = logging.getLogger()

@pytest.fixture
def testUtil(scope="module"):
    yield AbstractTest()

@pytest.fixture
def deviceType(request, testUtil):
    typeId = "%s_%s" % ("iotpython", request.module.__name__)
    # Chop off some characters if module name is too long
    typeId = typeId[:32]
    try:
        deviceType = testUtil.appClient.registry.devicetypes[typeId]
        logger.debug("Device type %s already exists for test %s" % (typeId, request.function.__name__))
    except KeyError:
        logger.debug("Device type %s doesn't exist, creating now for test %s" % (typeId, request.function.__name__))
        try:
            deviceType = testUtil.appClient.registry.devicetypes.create({"id": typeId})
        except ApiException as ex:
            logging.exception("Unable to register device type for test %s. API response: %s" % (request.function.__name__, ex.message))
    
    yield deviceType

    # Cleanup fails because the device fixture cleanup is executed after the deviceType fixture
    # It's only possible to delete a device type if there are no devices associated with it
    # testUtil.appClient.registry.devicetypes.delete(typeId)

@pytest.fixture
def device(request, testUtil, deviceType, authToken):
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
        testUtil.appClient.registry.devices.create(deviceReq)
        device = testUtil.appClient.registry.devices[deviceUid]
    except ApiException as ex:
        logging.exception("Unable to register device for test %s. API response: %s" % (request.function.__name__, ex.message))

    yield device

    # Cleanup device after test is finished
    testUtil.appClient.registry.devices.delete({"typeId": deviceType.id, "deviceId": deviceId})

@pytest.fixture
def authToken():
    logger.debug("Generating auth token for test...")
    yield str(uuid.uuid4())