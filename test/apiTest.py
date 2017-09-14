# *****************************************************************************
# Copyright (c) 2016 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Lokesh Haralakatta  - Initial Contribution
#   Prasanna A Mathada  - Initial Contribution
# *****************************************************************************

from __future__ import print_function
from ibmiotf import *
from nose.tools import *
from nose import SkipTest
from requests_toolbelt.multipart.encoder import MultipartEncoder
import ibmiotf.api
import ibmiotf.application
import ibmiotf.gateway
import ibmiotf.device
import logging
import requests
logging.basicConfig(level=logging.DEBUG)
import json
import time

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Variable
deviceType=None
draftSchemaId=None
draftEventId=None
draftEventTypeId=None
draftPhysicalInterfaceId=None
draftLogicalInterfaceId=None
ids = {}
schemaId=None
eventId=None
eventTypeId=None
nonExistentEventTypeId=None
physicalInterfaceId=None
physicalInterfaceName=None
nonExistentPhysicalInterfaceId='59b247df5222ff002c3bfe71'
logicalInterfaceId=None
nonExistentLogicalInterfaceId='59b247df52ffff002c3bfe71'
schemaIdForPhysicalInterface=None
schemaIdForLogicalInterface=None
nonExistentSchemaIdForPhysicalInterface='59b57b0aaaaaff002cfe1fbf'
nonExistentSchemaIdForLogicalInterface='59b57b04ffffff002d0c6889'
schemaNamePI = 'event1 schema'
schemaFileNamePI = 'event1.json'
schemaNameLI = 'k64fappinterface'
schemaFileNameLI = 'appinterface1.json'
outputValue=None


class TestApi:
    logger=None
    org=None
    deviceType=None
    deviceId=None
    authToken=None
    authKey=None
    invalidAuthKey=None

    @classmethod
    def setup_class(self):
        global deviceType
        global eventId
        global eventTypeId
        global schemaId
        global schemaIdForPhysicalInterface
        global schemaIdForLogicalInterface
        global schemaNamePI
        global schemaFileNamePI
        global schemaNameLI
        global schemaFileNameLI
        global nonExistentSchemaIdForPhysicalInterface
        global nonExistentSchemaIdForLogicalInterface
        global nonExistentEventTypeId
        global nonExistentPhysicalInterfaceId
        global nonExistentLogicalInterfaceId
        global outputValue

        self.nonExistentSchemaIdForPhysicalInterface='59b57b0aaaaaff002cfe1fbf'
        self.nonExistentSchemaIdForLogicalInterface='59b57b04ffffff002d0c6889'
        nonExistentEventTypeId='59b5847252faff000000dea6'
        
        self.logger = logging.getLogger(self.__module__+".TestApi")
        self.logger.setLevel(logging.INFO)

        appConfFile="application.conf"
        options = ibmiotf.application.ParseConfigFile(appConfFile)

        gwayConfFile="gateway.conf"
        gwayOptions = ibmiotf.gateway.ParseConfigFile(gwayConfFile)

        self.org = options['auth-key'][2:8]
        self.deviceType = options['type']
        self.gatewayType = gwayOptions['type']
        self.deviceId = options['id']
        self.authToken = options['auth-token']
        self.authKey = options['auth-key']
        self.deviceGateway = gwayOptions['id']
        self.newDeviceId = "python-api-test-device"
        self.newDeviceType = "python-api-add-type"
        self.invalidAuthKey = self.authKey[0:9]+"xxxxxxxxxx"
        deviceType = options['type']
        
        if schemaIdForPhysicalInterface is None:
            print ('Create a schema for Physical Interface ..')
            try:
                infile = open(schemaFileNamePI)
                schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
                infile.close()
                apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                ids["event1 schema"], output = apiClient.createSchema(schemaNamePI, schemaFileNamePI, schemaFileContents)
                print("Schema ID for Physical Interface is", ids["event1 schema"])
                schemaIdForPhysicalInterface = output['id']
            except Exception as e:
                print ('----- exception -------'+ str(e))

        if schemaIdForLogicalInterface is None:
            print ('Create a schema for Logical Interface ..')
            try:
                infile = open(schemaFileNameLI)
                schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
                infile.close()
                apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                ids["k64f app interface schema"], output = apiClient.createSchema(schemaNameLI, 'k64fappinterface.json', schemaFileContents)
                print("Schema ID for Logical Interface is", ids["k64f app interface schema"])
                schemaIdForLogicalInterface = output['id']
            except Exception as e:
                print ('----- exception -------'+ str(e))

    @classmethod
    def teardown_class(self):
        self.logger=None

    @raises(Exception)
    def testMissingOptions(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.api.ApiClient({},self.logger)
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-key')

    @raises(Exception)
    def testMissingAuthKey(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.api.ApiClient({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                        "auth-method": "token" , "auth-token": self.authToken },self.logger)
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-key')

    @raises(Exception)
    def testAuthKeyNone(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.api.ApiClient({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                        "auth-method": "token", "auth-token": self.authToken, "auth-key":None},self.logger)
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-key')

    @raises(Exception)
    def testMissingAuthToken(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.api.ApiClient({"org": self.org, "type": self.deviceType, "id": self.deviceId,
                                   "auth-key": self.authKey },self.logger)
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-token')

    @raises(Exception)
    def testAuthTokenNone(self):
        with assert_raises(ConfigurationException) as e:
            ibmiotf.api.ApiClient({"org":self.org, "type": self.deviceType, "id": self.deviceId,
                                   "auth-token": None, "auth-key":self.authKey},self.logger)
        assert_equal(e.exception.msg, 'Missing required property for API key based authentication: auth-token')

    def testGetOrganizationDetails(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        orgDetails = apiClient.getOrganizationDetails()
        assert_is_instance(orgDetails,dict)
        assert_equal(orgDetails['name'],"Testing Devices Org")

    @raises(Exception)
    def testGetOrganizationDetailsInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "invalid-token", "auth-key": self.authKey},self.logger)
            apiClient.getOrganizationDetails()
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testGetOrganizationDetailsApiKeyNotExist(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getOrganizationDetails()
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDevicesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDevices(parameters=self.deviceId)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetDevicesInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "invalid-token", "auth-key": self.authKey},self.logger)
            apiClient.getDevices()
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testGetDevicesInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDevices()
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')


    def testGetDevices(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        devicesDetails = apiClient.getDevices()
        assert_is_instance(devicesDetails,dict)
        deviceIds = list()
        for item in devicesDetails['results']:
            deviceIds.append(item['deviceId'])

        assert_equal(deviceIds.count(self.deviceId),1)
        assert_equal(deviceIds.count(self.deviceGateway),1)

    @raises(Exception)
    def testRegisterDevicesInvalidRequestException(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            devicesList = ["device-1","device-2","device-3"]
            apiClient.registerDevices(devicesList)
        assert_equal(e.exception.msg, 'Invalid request (No body, invalid JSON, unexpected key, bad value)')

    @SkipTest
    def testRegisterDevicesEmptyDeviceId(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        devicesList = [{'typeId' : "Python-Api-Test"}]
        registerResult = apiClient.registerDevices(devicesList)
        assert_false(registerResult[0]['success'])

    @raises(Exception)
    def testRegisterDevicesMaxLimitException(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            devicesList = list()
            for x in range(30):
                item = {'typeId': 'Python-Api-Test-'+str(x)}
                devicesList.append(item)

            apiClient.registerDevices(devicesList)
        assert_equal(e.exception.msg, 'Maximum number of devices exceeded')

    @raises(Exception)
    def testRegisterDevicesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.registerDevices(None)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testRegisterDeviceDuplicate(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.registerDevice(self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The device already exists')

    @raises(Exception)
    def testRegisterDeviceInvalidRequest(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.registerDevice("invalid-type","invalid-device")
        assert_equal(e.exception.msg, 'Invalid request (No body, invalid JSON, unexpected key, bad value)')

    @raises(Exception)
    def testRegisterDeviceInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.registerDevice(self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testRegisterDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.registerDevice(self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    def testRegisterGetUpdateRemoveDevice(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        location = {"longitude" : "12.78", "latitude" : "45.90", "elevation" : "2000", "accuracy" : "0",
                    "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
        deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
        metadata = {"customField1": "customValue3", "customField2": "customValue4"}

        #Register new device and validate
        registerResult = apiClient.registerDevice(self.deviceType, self.newDeviceId, self.authToken,deviceInfo, location,metadata)
        assert_equal(registerResult['typeId'],self.deviceType)
        assert_equal(registerResult['deviceId'],self.newDeviceId)

        #Get newly registered device
        getResult = apiClient.getDevice(self.deviceType, self.newDeviceId)
        assert_equal(getResult['typeId'],self.deviceType)
        assert_equal(getResult['deviceId'],self.newDeviceId)

        #Update device info for newly registered device
        updDeviceInfo = {"serialNumber": "001", "manufacturer": "Blackberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "ISL Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
        updResult = apiClient.updateDevice(self.deviceType, self.newDeviceId,metadata,updDeviceInfo)
        assert_equal(updResult['typeId'],self.deviceType)
        assert_equal(updResult['deviceId'],self.newDeviceId)
        assert_equal(updResult['deviceInfo']['manufacturer'],"Blackberry")
        assert_equal(updResult['deviceInfo']['descriptiveLocation'],"ISL Bangalore")

        #Remove the newly registered device
        assert_true(apiClient.removeDevice(self.deviceType, self.newDeviceId))

    @raises(Exception)
    def testGetDeviceInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.getDevice(self.deviceType,self.newDeviceId)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testGetDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDevice(self.deviceType,self.newDeviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceNotExists(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDevice(self.deviceType,"Device-Not-Exists")
        assert_equal(e.exception.msg, 'The device does not exist')

    @raises(Exception)
    def testUpdateDeviceInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            metadata = {"customField1": "customValue3", "customField2": "customValue4"}
            apiClient.updateDevice(self.deviceType,self.newDeviceId,metadata)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testUpdateDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            metadata = {"customField1": "customValue3", "customField2": "customValue4"}
            apiClient.updateDevice(self.deviceType,self.newDeviceId,metadata)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testUpdateDeviceNotExists(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            metadata = {"customField1": "customValue3", "customField2": "customValue4"}
            apiClient.updateDevice(self.deviceType,"Device-Not-Exists",metadata)
        assert_equal(e.exception.msg, 'The device does not exist')

    @raises(Exception)
    def testUpdateDeviceUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            deviceInfo = {"serialNumber": "001", "manufacturer": "Blackberry"}
            apiClient.updateDevice(self.deviceType,self.newDeviceId,self.authToken,deviceInfo)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testRemoveDeviceInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.removeDevice(self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testRemoveDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.removeDevice(self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testRemoveDeviceNotExists(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.removeDevice(self.deviceType,"Device-Not-Exists")
        assert_equal(e.exception.msg, 'The device does not exist')

    @raises(Exception)
    def testGetDeviceTypesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceTypes(self.gatewayType)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetDeviceTypesInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.getDeviceTypes()
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testGetDeviceTypesInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceTypes()
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    def testGetDeviceTypes(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        typesDetails = apiClient.getDeviceTypes()
        assert_is_instance(typesDetails,dict)
        typesIds = list()
        for item in typesDetails['results']:
            typesIds.append(item['id'])

        assert_equal(typesIds.count(self.deviceType),1)
        assert_equal(typesIds.count(self.gatewayType),1)

    def testAddGetUpdateDeleteDeviceType(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
        metadata = {"customField1": "customValue3", "customField2": "customValue4"}

        #Add new device type
        addResult = apiClient.addDeviceType(self.newDeviceType,"Added by apiClient.addDeviceType Method",deviceInfo,metadata)
        assert_equal(addResult['id'],self.newDeviceType)

        #Get newly added device type
        getResult = apiClient.getDeviceType(self.newDeviceType)
        assert_equal(getResult['id'],self.newDeviceType)

        #Update newly added device type
        upd_deviceInfo = {"serialNumber": "001", "manufacturer": "Blackberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
        updResult=apiClient.updateDeviceType(self.newDeviceType, "Added by apiClient.addDeviceType Method",upd_deviceInfo, metadata)
        assert_equal(updResult['deviceInfo']['manufacturer'],"Blackberry")

        #Remove newly added device type
        assert_true(apiClient.deleteDeviceType(self.newDeviceType))

    @raises(Exception)
    def testAddDeviceTypeDuplicate(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.addDeviceType(self.deviceType)
        assert_equal(e.exception.msg, 'The device type already exists')

    @raises(Exception)
    def testAddDeviceTypeInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.addDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testAddDeviceTypeInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.addDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testAddDeviceTypeInvalidRequest(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.addDeviceType(self.newDeviceType,{'description':'newDescription'})
        assert_equal(e.exception.msg, 'Invalid request (No body, invalid JSON, unexpected key, bad value)')

    @raises(Exception)
    def testGetDeviceTypeNotExists(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceType(None)
        assert_equal(e.exception.msg, 'The device type does not exist')

    @raises(Exception)
    def testGetDeviceTypeInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.getDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testGetDeviceTypeInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testUpdateDeviceTypeNotExists(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
            apiClient.updateDeviceType("type-not-exists","no-decription",deviceInfo)
        assert_equal(e.exception.msg, 'The device type does not exist')

    @raises(Exception)
    def testUpdateDeviceTypeInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
            apiClient.updateDeviceType(self.newDeviceType,"no-description",deviceInfo)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testUpdateDeviceTypeInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
            apiClient.updateDeviceType(self.newDeviceType,"no-description",deviceInfo)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testDeleteDeviceTypeInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.deleteDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testDeleteDeviceTypeInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.deleteDeviceType(self.newDeviceType)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testDeleteDeviceInvalidAuthToken(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": "x9lB6C9QOb9Hkp0xS", "auth-key": self.authKey},self.logger)
            apiClient.deleteDevice(self.deviceType,self.newDeviceId)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testDeleteDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.deleteDevice(self.deviceType,self.newDeviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testDeleteDeviceUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.deleteDevice(self.deviceId,self.deviceType)
        assert_equal(e.exception.msg, 'Unexpected error')

    def testDeleteMulitpleDevices(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)

        assert_true(apiClient.deleteMultipleDevices([{}])[0]['success'])

    @raises(Exception)
    def testDeleteMultipleDevicesInvalidBody(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.deleteMultipleDevices(self.deviceType)
        assert_equal(e.exception.msg, 'Invalid request (No body, invalid JSON, unexpected key, bad value)')

    @raises(Exception)
    def testDeleteMultipleDevicesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.deleteMultipleDevices(None)
        assert_equal(e.exception.msg, 'Unexpected error')

    @SkipTest
    def testGetLastEvents(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)

        events = apiClient.getLastEvents(self.deviceType,self.deviceId)
        eventId = events[0]['eventId']
        event = apiClient.getLastEvent(self.deviceType,self.deviceId,eventId)
        assert_equal(event['eventId'],eventId)

    @raises(Exception)
    def testGetLastEventUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getLastEvent({"typeId":self.deviceType}, {"deviceId":self.deviceId}, "eventId")
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetLastEventsUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getLastEvent({"typeId":self.deviceType}, {"deviceId":self.deviceId})
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetLastEventNotFoundError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getLastEvent(self.deviceType, self.deviceId, "eventId")
        assert_equal(e.exception.msg, 'Event not found')

    def testDeviceModelMethods(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        location = {"longitude" : 12.78, "latitude" : 45.90, "elevation" : 2000, "accuracy" : 0,
                    "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
        deviceInfo = {"serialNumber": "001", "manufacturer": "Blueberry", "model": "e2", "deviceClass": "A",
                      "descriptiveLocation" : "Bangalore", "fwVersion" : "1.0.1", "hwVersion" : "12.01"}
        metadata = {"customField1": "customValue3", "customField2": "customValue4"}

        #Register new device and validate
        registerResult = apiClient.registerDevice(self.deviceType, self.newDeviceId, self.authToken,deviceInfo, location,metadata)
        assert_equal(registerResult['typeId'],self.deviceType)
        assert_equal(registerResult['deviceId'],self.newDeviceId)

        #Get Device location and validtae the results returned
        locationResult = apiClient.getDeviceLocation(self.deviceType,self.newDeviceId)
        assert_true(locationResult['longitude'] == location['longitude'])
        assert_true(locationResult['latitude'] == location['latitude'])
        assert_true(locationResult['elevation'] == location['elevation'])
        assert_true(locationResult['accuracy'] == location['accuracy'])

        #Update Device Location Information
        location = {"longitude" : 13, "latitude" : 46, "elevation" : 3000, "accuracy" : 100,
                    "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
        updateResult = apiClient.updateDeviceLocation(self.deviceType,self.newDeviceId,location)
        assert_true(updateResult['longitude'] == location['longitude'])
        assert_true(updateResult['latitude'] == location['latitude'])
        assert_true(updateResult['elevation'] == location['elevation'])
        assert_true(updateResult['accuracy'] == location['accuracy'])

        #Remove added device using deleteDevice Method
        assert_true(apiClient.deleteDevice(self.deviceType, self.newDeviceId))

    @raises(Exception)
    def testGetDeviceLocationNotFoundError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceLocation(self.deviceId,self.deviceType)
        assert_equal(e.exception.msg, 'Device location information not found')

    @raises(Exception)
    def testGetDeviceLocationUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceLocation({"typeId":self.deviceId},self.deviceType)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testUpdateDeviceLocationNotFoundError(self):
        location = {"longitude" : "13", "latitude" : "46", "elevation" : "3000", "accuracy" : "100",
                    "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.updateDeviceLocation(self.deviceType,"device-not-exists",location)
        assert_equal(e.exception.msg, 'Device location information not found')

    @raises(Exception)
    def testUpdateDeviceLocationUnexpectedError(self):
        location = {"longitude" : "13", "latitude" : "46", "elevation" : "3000", "accuracy" : "100",
                    "measuredDateTime" : "2015-10-28T08:45:11.662Z"}
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.updateDeviceLocation({"typeId":self.deviceType},self.deviceId,location)
        assert_equal(e.exception.msg, 'Unexpected error')

    @SkipTest
    def testGetDeviceManagementInformation(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        apiClient.getDeviceManagementInformation(self.deviceType, self.deviceId)

    @raises(Exception)
    def testGetDeviceManagementInformationInvalidAuth(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementInformation(self.deviceType, self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceManagementInformationUnexepctedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementInformation({"typeId":self.deviceType}, self.deviceId)
        assert_equal(e.exception.msg, 'Unexpected error')

    def testGetConnectionLogs(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        apiClient.getConnectionLogs({"typeId":self.deviceType, "deviceId":self.deviceId})

    @raises(Exception)
    def testGetConnectionLogsUnexepctedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getConnectionLogs(self.deviceType)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetConnectionLogsInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getConnectionLogs({"typeId":self.deviceType, "deviceId":self.deviceId})
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    def testDeviceDiagnosticsLogs(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        logData = { "message": "sample log entry for python-ut-device","severity": 0,"data": "Diagnostic log entry","timestamp": "2016-05-16T08:44:23.909Z"}

        #Clear all diagnostic logs for the device
        assert_true(apiClient.clearAllDiagnosticLogs(self.deviceType, self.deviceId))

        #Add one diagnostic log
        assert_true(apiClient.addDiagnosticLog(self.deviceType, self.deviceId, logData))

        #Get all diagnostic logs
        logsData = apiClient.getAllDiagnosticLogs(self.deviceType, self.deviceId)
        assert_equal(logsData[0]['data'],"Diagnostic log entry")

    @raises(Exception)
    def testGetAllDiagnosticLogsDeviceNotFoundError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticLogs(self.deviceType,"device-not-exists")
        assert_equal(e.exception.msg, 'Device not found')

    @raises(Exception)
    def testGetAllDiagnosticLogs500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticLogs("device-not-exists",self.deviceType)
        assert_equal(e.exception.msg, '[500] Unexpected error')

    @raises(Exception)
    def testGetAllDiagnosticLogsUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticLogs({"typeId":self.deviceType},{"deviceId":self.deviceId})
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testClearAllDiagnosticLogsDeviceNotFoundError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.clearAllDiagnosticLogs(self.deviceType,"device-not-exists")
        assert_equal(e.exception.msg, 'Device not found')

    @raises(Exception)
    def testClearAllDiagnosticLogs500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.clearAllDiagnosticLogs("device-not-exists",self.deviceType)
        assert_equal(e.exception.msg, '[500] Unexpected error')

    @raises(Exception)
    def testClearAllDiagnosticLogsUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.clearAllDiagnosticLogs({"typeId":self.deviceType},{"deviceId":self.deviceId})
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testClearAllDiagnosticLogsInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.clearAllDiagnosticLogs(self.deviceType, self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testAddDiagnosticLogDeviceNotFoundError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            logData = { "message": "sample log entry for python-ut-device","severity": 0,"data": "Diagnostic log entry","timestamp": "2016-05-16T08:44:23.909Z"}
            apiClient.addDiagnosticLog(self.deviceType,"device-not-exists",logData)
        assert_equal(e.exception.msg, 'Device not found')

    @raises(Exception)
    def testAddDiagnosticLog500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            logData = { "message": "sample log entry for python-ut-device","severity": 0,"data": "Diagnostic log entry","timestamp": "2016-05-16T08:44:23.909Z"}
            apiClient.addDiagnosticLog("device-not-exists",self.deviceType,logData)
        assert_equal(e.exception.msg, '[500] Unexpected error')

    @raises(Exception)
    def testAddDiagnosticLogUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            logData = { "message": "sample log entry for python-ut-device","severity": 0,"data": "Diagnostic log entry","timestamp": "2016-05-16T08:44:23.909Z"}
            apiClient.addDiagnosticLog({"typeId":self.deviceType},{"deviceId":self.deviceId},logData)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testAddDiagnosticLogInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            logData = { "message": "sample log entry for python-ut-device","severity": 0,"data": "Diagnostic log entry","timestamp": "2016-05-16T08:44:23.909Z"}
            apiClient.addDiagnosticLog(self.deviceType, self.deviceId,logData)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    def testDeviceDiagnosticsErrorCodes(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        errorData = { "errorCode": 0,"timestamp": "2016-05-17T07:16:42.312Z"}

        #Clear all error codes for the device
        assert_true(apiClient.clearAllErrorCodes(self.deviceType, self.deviceId))

        #Add one error code
        assert_true(apiClient.addErrorCode(self.deviceType, self.deviceId, errorData))

        #Get all error codes
        assert_equal(apiClient.getAllDiagnosticErrorCodes(self.deviceType, self.deviceId)[0]['errorCode'],errorData['errorCode'])

    @raises(Exception)
    def testAddErrorCodeInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            errorData = { "errorCode": 0,"timestamp": "2016-05-17T07:16:42.312Z"}
            apiClient.addErrorCode(self.deviceType, self.deviceId, errorData)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testAddErrorCode500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.addErrorCode(self.deviceType,self.deviceId,None)
        assert_equal(e.exception.msg, '[500] Unexpected error')

    @raises(Exception)
    def testAddErrorCodeUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            errorData = { "errorCode": "","timestamp": "2016-05-17T07:16:42.312Z"}
            apiClient.addErrorCode(self.deviceType,self.deviceId,errorData)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testAddErrorCodeNotFound(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            errorData = { "errorCode": 0,"timestamp": "2016-05-17T07:16:42.312Z"}
            apiClient.addErrorCode(self.deviceType,None,errorData)
        assert_equal(e.exception.msg, 'Error Code not found')

    @raises(Exception)
    def testGetAllDiagnosticErrorCodesInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getAllDiagnosticErrorCodes(self.deviceType, self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetAllDiagnosticErrorCodes500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticErrorCodes(None,None)
        assert_equal(e.exception.msg, '[500] Unexpected error')

    @raises(Exception)
    def testGetAllDiagnosticErrorCodesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticErrorCodes({"typeId":self.deviceType},self.deviceId)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testGetAllDiagnosticErrorCodesNotFound(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getAllDiagnosticErrorCodes(self.deviceType,None)
        assert_equal(e.exception.msg, 'Error Code not found')

    @raises(Exception)
    def testClearAllErrorCodesInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.clearAllErrorCodes(self.deviceType, self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testClearAllErrorCodesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.clearAllErrorCodes({"typeId":self.deviceType},self.deviceId)
        assert_equal(e.exception.msg, 'Unexpected error')

    @raises(Exception)
    def testClearAllErrorCodesNotFound(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.clearAllErrorCodes(self.deviceType,None)
        assert_equal(e.exception.msg, 'Error Code not found')

    def testGetServiceStatus(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)

        statusData = apiClient.getServiceStatus()

    @raises(Exception)
    def testGetServiceStatusUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getServiceStatus()
        assert_equal(e.exception.msg, 'Unexpected Error')

    @raises(Exception)
    def testGetActiveDevicesBadRequest(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getActiveDevices({"dummy":"value"})
        assert_equal(e.exception.msg, 'Bad Request')

    @raises(Exception)
    def testGetActiveDevicesUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getActiveDevices({'start':'2015','end':'2016'})
        assert_equal(e.exception.msg, 'Unexpected Error')

    @SkipTest
    def testGetActiveDevices(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        apiClient.getActiveDevices({'start':'2015-01-01','end':'2016-01-01'})

    def testGetDataTraffic(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        apiClient.getDataTraffic({'start':'2016-01-01','end':'2016-05-01'})

    @raises(Exception)
    def testGetDataTrafficBadRequest(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDataTraffic({'start':'2017-01-01','end':'2016-05-01'})
        assert_equal(e.exception.msg, 'Bad Request')

    def testDeviceManagementAPIs(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        mgmtRequest = {"action": "device/reboot", "parameters": [{"name": "action","value": "reboot" }],
                       "devices": [{ "typeId": self.deviceType, "deviceId": self.deviceId }]}

        #Instantiate required device managed client
        deviceConfFile="device.conf"
        deviceOptions = ibmiotf.device.ParseConfigFile(deviceConfFile)
        deviceInfoObj = ibmiotf.device.DeviceInfo()
        managedClient = ibmiotf.device.ManagedClient(deviceOptions,deviceInfo=deviceInfoObj)
        managedClient.connect()

        #Initialize device management request
        initResult = apiClient.initiateDeviceManagementRequest(mgmtRequest)
        reqId = initResult['reqId']

        #Get device management request using request id
        getResult = apiClient.getDeviceManagementRequest(reqId)
        assert_true(getResult['action'],mgmtRequest['action'])

        #Get device management request status using request id
        getStatusResult = apiClient.getDeviceManagementRequestStatus(reqId)
        results = getStatusResult['results']
        assert_true(results[0]['typeId'],self.deviceType)
        assert_true(results[0]['deviceId'],self.deviceId)

        #Get device management request status using typeId and deviceId
        getStatusResult = apiClient.getDeviceManagementRequestStatusByDevice(reqId,self.deviceType,self.deviceId)
        assert_true(getStatusResult['status'] == 1)
        assert_false(getStatusResult['complete'])

        #Get all management requests
        getResult = apiClient.getAllDeviceManagementRequests()
        results = getResult['results']
        assert_true(results[0]['action'],mgmtRequest['action'])

        #Delete initiated device management request
        assert_true(apiClient.deleteDeviceManagementRequest(reqId))

        #Disconnect managed client
        managedClient.disconnect()

    @raises(Exception)
    def testInitiateDeviceManagementRequestUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.initiateDeviceManagementRequest({'typeId':'Python'})
        assert_equal(e.exception.msg, 'Unexpected Error')

    @raises(Exception)
    def testInitiateDeviceManagementRequest500UnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.initiateDeviceManagementRequest(None)
        assert_equal(e.exception.msg, '500 Unexpected Error')

    @raises(Exception)
    def testDeleteDeviceManagementRequestUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.deleteDeviceManagementRequest({'typeId':'Python'})
        assert_equal(e.exception.msg, 'Unexpected Error')

    @raises(Exception)
    def testDeleteDeviceManagementRequestBadRequestID(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.deleteDeviceManagementRequest('not-exists')
        assert_equal(e.exception.msg, 'Request Id not found')

    @raises(Exception)
    def testDeleteDeviceManagementRequestInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.deleteDeviceManagementRequest('requestId')
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceManagementRequestUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequest({'typeId':'Python'})
        assert_equal(e.exception.msg, 'Unexpected Error')

    @raises(Exception)
    def testGetDeviceManagementRequestBadRequestID(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequest('not-exists')
        assert_equal(e.exception.msg, 'Request Id not found')

    @raises(Exception)
    def testGetDeviceManagementRequestInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceManagementRequest('requestId')
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequestStatus({'typeId':'Python'})
        assert_equal(e.exception.msg, 'Unexpected Error')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusBadRequestID(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequestStatus('not-exists')
        assert_equal(e.exception.msg, 'Request Id not found')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceManagementRequestStatus('requestId')
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusByDeviceInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceManagementRequestStatusByDevice('requestId',self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusByDeviceBadRequestID(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequestStatusByDevice('id-not-exists',self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'Request status not found')

    @raises(Exception)
    def testGetDeviceManagementRequestStatusByDeviceUnexpectedError(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDeviceManagementRequestStatusByDevice({'reqId':'req-id'},self.deviceType,self.deviceId)
        assert_equal(e.exception.msg, 'Unexpected Error')

    def testGatewayAPISupport(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        gwTypeId = "add-gw-device-type-test"
        devId = "reg-dev-undr-gw-test"

        #Add new gateway device type
        addResult = apiClient.addGatewayDeviceType(gwTypeId)
        assert_equal(addResult['id'],gwTypeId)

        #Get devices under above added gateway device type
        getResult = apiClient.getDevicesConnectedThroughGateway(gwTypeId)
        assert_equal(getResult['results'],[])

        #Add new device through above added gateway
        addResult = apiClient.registerDeviceUnderGateway(gwTypeId,devId)
        assert_equal(addResult['typeId'],gwTypeId)
        assert_equal(addResult['deviceId'],devId)

        #Get devices under above added gateway device type
        getResult = apiClient.getDevicesConnectedThroughGateway(gwTypeId)
        assert_equal(getResult['results'][0]['typeId'],gwTypeId)
        assert_equal(getResult['results'][0]['deviceId'],devId)

        getResult = apiClient.getDevicesConnectedThroughGateway(gwTypeId,devId)
        assert_equal(getResult['typeId'],gwTypeId)
        assert_equal(getResult['deviceId'],devId)

        #Remove the added device followed by the removal of gateway device type
        assert_true(apiClient.deleteDevice(gwTypeId, devId))
        assert_true(apiClient.deleteDeviceType(gwTypeId))

    @raises(Exception)
    def testgetDevicesConnectedThroughGatewayInvalidAuthKey(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDevicesConnectedThroughGateway(self.gatewayType)
        assert_equal(e.exception.msg, 'The authentication method is invalid or the api key used does not exist')

    @raises(Exception)
    def testgetDevicesConnectedThroughGatewayAuthTokenEmpty(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken[0:-1], "auth-key": self.authKey},self.logger)
            apiClient.getDevicesConnectedThroughGateway(self.gatewayType)
        assert_equal(e.exception.msg, 'The authentication token is empty or invalid')

    @raises(Exception)
    def testgetDevicesConnectedThroughGatewayNotExistingDevice(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            apiClient.getDevicesConnectedThroughGateway(self.gatewayType,"device-not-exists")
        assert_equal(e.exception.msg, 'The device does not exist')

    def testDeviceManagementExtensionMethods(self):
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token",
           "auth-token": self.authToken, "auth-key": self.authKey})

        dmeData = {"bundleId": "example-dme-actions-v1",
                   "displayName": {"en_US": "example-dme Actions v1"},
                   "version": "1.0","actions": {"installPlugin": {
                   "actionDisplayName": { "en_US": "Install Plug-in"},
                   "parameters": [ { "name": "pluginURI",
                                     "value": "http://example.dme.com",
                                    "required": "true" } ] } } }
        addResult = apiClient.createDeviceManagementExtensionPkg(dmeData)
        assert_equal(addResult['bundleId'],'example-dme-actions-v1')

        getResult = apiClient.getAllDeviceManagementExtensionPkgs();
        assert_equal(getResult['results'][0]['bundleId'],'edgeanalytics')

        getResult = apiClient.getDeviceManagementExtensionPkg('example-dme-actions-v1')
        assert_equal(getResult['bundleId'],'example-dme-actions-v1')

        updData = {"displayName": {"en_US": "example-dme Actions v1"},
                   "version": "1.1","actions": {"installPlugin": {
                   "actionDisplayName": { "en_US": "Install Plug-in"},
                   "parameters": [ { "name": "pluginURI",
                                     "value": "http://example.dme.com",
                                    "required": "true" } ] } } }
        updResult = apiClient.updateDeviceManagementExtensionPkg('example-dme-actions-v1',updData)
        assert_equal(updResult['bundleId'],'example-dme-actions-v1')
        assert_equal(updResult['version'],'1.1')

        assert_true(apiClient.deleteDeviceManagementExtensionPkg('example-dme-actions-v1'))

    @raises(Exception)
    def testgetAllDeviceManagementExtensionPkgsException(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getAllDeviceManagementExtensionPkgs()
        assert_equal(e.exception.msg, 'HTTP Error in getAllDeviceManagementExtensionPkgs')

    @raises(Exception)
    def testcreateDeviceManagementExtensionPkg(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.invalidAuthKey},self.logger)
            apiClient.createDeviceManagementExtensionPkg(None)
        assert_equal(e.exception.msg, 'HTTP Error in createDeviceManagementExtensionPkg')

    @raises(Exception)
    def testdeleteDeviceManagementExtensionPkg(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.invalidAuthKey},self.logger)
            apiClient.deleteDeviceManagementExtensionPkg(None)
        assert_equal(e.exception.msg, 'HTTP Error in deleteDeviceManagementExtensionPkg')

    @raises(Exception)
    def testgetDeviceManagementExtensionPkg(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.invalidAuthKey},self.logger)
            apiClient.getDeviceManagementExtensionPkg(None)
        assert_equal(e.exception.msg, 'HTTP Error in getDeviceManagementExtensionPkg')

    @raises(Exception)
    def testupdateDeviceManagementExtensionPkg(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.invalidAuthKey})
            apiClient.updateDeviceManagementExtensionPkg(None,None)
        assert_equal(e.exception.msg, 'HTTP Error in updateDeviceManagementExtensionPkg')
    
##########################################################################
#                   Information Management Schema APIs
##########################################################################

    @raises(Exception)
    def test001TestCreateSchema(self):
        global schemaIdForPhysicalInterface
        with assert_raises(APIException) as e:
            if schemaIdForPhysicalInterface is None:
                global ids
                print ('----- About to create a schema -------')
                schemaName = 'event1 schema'
                schemaFileName = 'event1.json'
                try:
                    infile = open(schemaFileName)
                    schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
                    infile.close()
                    apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                    ids["event1 schema"], output = apiClient.createSchema(schemaName, schemaFileName, schemaFileContents, description=None)
                    schemaIdForPhysicalInterface = output['id']
                    print ('Successfully created the Schema: ' + schemaIdForPhysicalInterface)
                except Exception as e:
                    print ('----- exception -------'+ str(e))
                assert_equal(e.exception.msg, 'Exception in creating a Schema')
            else:
                assert_true(schemaIdForPhysicalInterface)
                print ('Successfully created the Schema: ' + schemaIdForPhysicalInterface)

    @raises(Exception)
    def test002TestCreateSchemaErr(self):
        with assert_raises(APIException) as e:
            global schemaId
            global ids
            print ('----- About to create a schema -------')
            schemaName = 'event1 schema'
            schemaFileName = 'event2.json'
            try:
                infile = open(schemaFileName)
                schemaFileContents = ''.join([x.strip() for x in infile.readlines()])
                infile.close()
                apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                ids["event1 schema"], output = apiClient.createSchema(schemaName, schemaFileName, schemaFileContents, description=None)
                schemaId = output['id']
                print ('Successfully created the Schema: ' + schemaId)
            except Exception as e:
                print ('HTTP error creating a schema')
        assert_equal(e.exception.msg, "'No such file or directory: 'event2.json'")
		
    def test003TestGetSchema(self):
        global schemaIdForPhysicalInterface
        if schemaIdForPhysicalInterface is not None:
            print ('Fetch a schema whose Schema ID is :' + schemaIdForPhysicalInterface)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            output = apiClient.getSchema(schemaIdForPhysicalInterface, draft=True)
            print (output)
            assert_equal(output['id'] , schemaIdForPhysicalInterface)
            print ('One schema retrieved')

    @raises(Exception)
    def test004TestGetSchemaErr(self):
        with assert_raises(APIException) as e:
            try:
                global nonExistentSchemaIdForPhysicalInterface
                if nonExistentSchemaIdForPhysicalInterface is not None:
                    print ('Fetch a schema whose Schema ID is :' + nonExistentSchemaIdForPhysicalInterface)
                    apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                    output = apiClient.getSchema(nonExistentSchemaIdForPhysicalInterface, draft=True)
            except Exception as e:
                print('HTTP error in get a schema for Schema ID '+nonExistentSchemaIdForPhysicalInterface)
            
    def test005TestGetSchemas(self):
        print ('----- Fetch all schemas -------')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getSchemas(self)
        print (output)
        assert_true(output)
        print ('All schemas retrieved')
        
    def test006TestGetSchemaContent(self):
        global schemaIdForPhysicalInterface
        global ids
        print ('Fetching the schema content for ID: ' + schemaIdForPhysicalInterface)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getSchemaContent(schemaIdForPhysicalInterface, draft=True)
        print (output)
        assert_true(output)
        print ('Schema content retrieved')

    @raises(Exception)
    def test007TestGetSchemaContentErr(self):
        with assert_raises(APIException) as e:
            try:
                global nonExistentSchemaIdForPhysicalInterface
                global ids
                print ('Fetching the schema content for ID: ' + nonExistentSchemaIdForPhysicalInterface)
                apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
                output = apiClient.getSchemaContent(nonExistentSchemaIdForPhysicalInterface, draft=True)
                print (output)
            except Exception as e:
                print ('HTTP Error fetching the Schema Content for ID '+nonExistentSchemaIdForPhysicalInterface)
        
##########################################################################
#                 Information Management event type APIs
##########################################################################

    def test008TestCreateEventType(self):
        global schemaIdForPhysicalInterface
        global eventTypeId
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        ids["k64feventtype"], output = apiClient.createEventType("K64F event", schemaIdForPhysicalInterface, "K64F event")
        eventTypeId = output['id']
        print ('event type created')
        print ('EventTypeId is '+eventTypeId)
        assert_true(eventTypeId)

    def test009TestCreateEventTypeErr(self):
        try:
            global schemaIdForPhysicalInterface
            global EventTypeId
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
            ids["nonExistentk64feventtype"], output = apiClient.createEventType("K64F event", nonExistentSchemaIdForPhysicalInterface, "K64F event")
            EventTypeId = output['id']
            assert_true(output)
        except Exception as e:
            print('HTTP error creating event type')
		
    def test010TestGetEventTypeErr(self):
        try:
            global nonExistentEventTypeId
            print ('Fetching Event Type Id: ' + nonExistentEventTypeId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_false(apiClient.getEventType(nonExistentEventTypeId))
        except Exception as e:
            print ('[404] HTTP error getting an event type')
		
    @raises(Exception)
    def test011TestGetEventTypes(self):
        print ('----- Fetch all event types -------')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getEventTypes(draft=True)
        print (output)
        assert_equal(e.exception.msg, 'All event types retrieved')
        print ('All event types retrieved')
		
    def test012TestGetEventType(self):
        global eventTypeId
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getEventType(EventTypeId, draft=True)
        print (output)
        assert_true(output)

##########################################################################
#             Information Management Physical Interface APIs
##########################################################################

    def test013TestCreatePhysicalInterface(self):
        global physicalInterfaceId
        global physicalInterfaceName
        print ('About to create physical interface')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken, "auth-key": self.authKey},self.logger)
        ids["physicalinterface"], output = apiClient.createPhysicalInterface("K64F", "The physical interface for K64F example")
        #print (output)
        physicalInterfaceId = output['id']
        physicalInterfaceName = output['name']
        print ('physicalInterfaceId value is '+physicalInterfaceId)
        assert_true(physicalInterfaceId)
        print ('physical interface created')

    def test061TestUpdatePhysicalInterface(self):
        global physicalInterfaceId
        global schemaIdForPhysicalInterface
        global physicalInterfaceName
        print ('About to Update physical interface')
        print ('Updating physical interface: ' + physicalInterfaceId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.updatePhysicalInterface(physicalInterfaceId,physicalInterfaceName,schemaIdForPhysicalInterface,description='Test PI Update')
        print(output['description'])
        assert_equal('Test PI Update', output['description'])
        print ('physical interface Updated')

    def test014TestGetPhysicalInterfaceErr(self):
        try:
            global physicalInterfaceId
            global nonExistentPhysicalInterfaceId
            print ('Fetching physical interface: ' + nonExistentPhysicalInterfaceId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_equal(msg, apiClient.getPhysicalInterface(nonExistentPhysicalInterfaceId))
        except Exception as e:
            print ('[404] HTTP error getting a physical interface')

    def test015TestGetPhysicalInterface(self):
        global physicalInterfaceId
        global outputValue
        print ('Fetching physical interface ')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getPhysicalInterface(physicalInterfaceId, draft=True)
        print (output)
        outputValue = output
        assert_equal(output['id'], physicalInterfaceId)
		
    def test016TestGetPhysicalInterfaces(self):
        print ('----- Fetch all physical interfaces -------')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getPhysicalInterfaces(self)
        print (output)
        print ('All physical interfaces retrieved')


##########################################################################
#             Information Management Event Mapping APIs
##########################################################################

    def test019TestCreateEvent(self):
        global eventTypeId
        global physicalInterfaceId
        global schemaIdForPhysicalInterface
        print ('----- Create an event mapping for a physical interface -------')
        eventId = "status"
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        ids["k64feventtype"], output = apiClient.createEventType("K64F event", schemaIdForPhysicalInterface, "K64F event")
        EventTypeId = output['id']
        output = apiClient.createEvent(ids["physicalinterface"], ids["k64feventtype"], "status")
        print (output)
        assert_true(output, 'Event mapping created')
        print ('Event mapping created')
			
    @raises(Exception)
    def test020TestCreateEventErr(self):
        try:
            global eventTypeId
            global physicalInterfaceId
            global eventId
            physicalInterfaceId = None
            eventTypeId = '59b2428a52faff002c3bffff'
            print ('----- Create an event mapping for a physical interface -------')
            eventId = None
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            apiClient.createEvent(physicalInterfaceId, eventTypeId, eventId)
        except Exception as e:
            assert_equal(e.exception.msg, '[400] HTTP error creating event mapping')
            print ('[400] HTTP error creating event mapping')

    def test021TestGetEventsErr(self):
        print ('----- Fetch all event types -------')
        try:
            global nonExistentPhysicalInterfaceId
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            apiClient.getEvents(nonExistentPhysicalInterfaceId)
            assert_equal(e.exception.msg, 'HTTP error getting event mappings')
        except Exception as e:
            print ('HTTP error getting event mappings')

    def test022TestGetEvents(self):
        print ('----- Fetch all event types -------')
        global physicalInterfaceId
        print (physicalInterfaceId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getEvents(physicalInterfaceId, draft=True)
        print (output)
        assert_true(output)
        print ('All event mappings retrieved')
			
##########################################################################
#             Information Management Logical Interface APIs
##########################################################################

    def test023TestCreateLogicalInterface(self):
        global schemaIdForLogicalInterface
        global logicalInterfaceId
        global ids
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        ids["k64f app interface"], output = apiClient.createLogicalInterface("K64F logical interface", ids["k64f app interface schema"])
        assert_not_equal(None, output['id'])
        logicalInterfaceId = output['id']
        print ('Logical interface created')
        print ('value of logicalInterfaceId is :' + logicalInterfaceId)

    def test024TestCreateLogicalInterfaceErr(self):
        global nonExistentschemaIdForLogicalInterface
        name = 'Non Existent'
        global ids
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        try:
            ids["k64f app interface"], output = apiClient.createLogicalInterface(name, self.nonExistentschemaIdForLogicalInterface, description=None)
            assert_not_equal(None, output['id'])
            logicalInterfaceId = output['id']
            print ('value of logicalInterfaceId is :' + logicalInterfaceId)
        except Exception as exc:
            print('HTTP error creating logical interface')
            
    def test025TestUpdateLogicalInterface(self):
        global schemaIdForLogicalInterface
        global logicalInterfaceId
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.updateLogicalInterface(logicalInterfaceId, "K64F logical interface", schemaIdForLogicalInterface, description='Test LI Update')
        print(output['description'])
        assert_equal('Test LI Update', output['description'])
        print ('Logical interface updated')

    def test025TestUpdateLogicalInterfaceErr(self):
        try:
            global schemaIdForLogicalInterface
            global nonExistentLogicalInterfaceId
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            output = apiClient.updateLogicalInterface(nonExistentLogicalInterfaceId, "K64F logical interface", schemaIdForLogicalInterface, description='Test LI Update')
            print(output['description'])
            assert_equal('Test LI Update', output['description'])
            print ('Logical interface updated')
        except Exception as e:
            print ('HTTP error updating logical interface')

    def test026TestGetLogicalInterfaces(self):
        print ('----- Fetch all Logical Interfaces -------')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getLogicalInterfaces()
        print (output)
        assert_true(output)
        print ('All logical interfaces retrieved')
        
    @raises(Exception)
    def test027TestGetLogicalInterfacesErr(self):
        with assert_raises(APIException) as e:
            global nonExistentLogicalInterfaceId
            print ('----- Fetch all Logical Interfaces -------')
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_true(apiClient.getLogicalInterfaces(nonExistentLogicalInterfaceId))
            print ('HTTP error getting all logical interfaces')

    def test028TestGetLogicalInterface(self):
        global logicalInterfaceId
        print ('Fetching Logical Interface: '+logicalInterfaceId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        output = apiClient.getLogicalInterface(logicalInterfaceId, draft=True)
        print (output)
        assert_true(output)

    def test029TestGetLogicalInterfaceErr(self):
        try:
            global nonExistentLogicalInterfaceId
            print ('Fetching Logical Interface: '+nonExistentLogicalInterfaceId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_false(apiClient.getLogicalInterface(nonExistentLogicalInterfaceId, draft=True))
        except Exception as e:
            print ('[404] HTTP error getting an logical interface')

##########################################################################
#               Information Management Device Type APIs
##########################################################################

    def test031TestAddPhysicalInterfaceToDeviceType(self):
        global physicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (physicalInterfaceId)
        print (deviceType)
        print ('Add a physical interface to a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.addPhysicalInterfaceToDeviceType(deviceType, physicalInterfaceId)
        print ('Physical interface added to a device type')
        assert_true(result)
    
    def test033TestAddLogicalInterfaceToDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (logicalInterfaceId)
        print (deviceType)
        print ('Add a logical interface to a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.addLogicalInterfaceToDeviceType(deviceType, logicalInterfaceId)
        print ('Logical interface added to a device type')
        assert_true(result)

    def test035TestGetLogicalInterfacesOnDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Get all logical interfaces for a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.getLogicalInterfacesOnDeviceType(deviceType, draft=True)
        print (result)
        assert_true(result)

    def test036TestGetMappingsOnDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Get all the mappings for a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.getMappingsOnDeviceType(deviceType, draft=True)
        print (result)
        assert_true(result)
        print('All device type mappings retrieved')

    def test037TestAddMappingsToDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (logicalInterfaceId)
        print (deviceType)
        infile = open("event1appint1mappings.json")
        mappingsObject = json.loads(''.join([x.strip() for x in infile.readlines()]))
        infile.close()
        notificationStrategy = 'on-state-change'
        print ('Add mappings for a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.addMappingsToDeviceType(deviceType, ids["k64f app interface"], mappingsObject, notificationStrategy)
        print ('Device type mappings created for logical interface')
        assert_true(result)

    def test038TestUpdateMappingsOnDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (logicalInterfaceId)
        print (deviceType)
        infile = open("event1appint1mappings.json")
        mappingsObject = json.loads(''.join([x.strip() for x in infile.readlines()]))
        infile.close()
        notificationStrategy = 'on-state-change'
        print ('Update mappings for a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.updateMappingsOnDeviceType(deviceType, logicalInterfaceId, mappingsObject, notificationStrategy)
        print ('Device type mappings updated for logical interface')
        assert_true(result)

##    @raises(Exception)
    def test039TestGetMappingsOnDeviceTypeForLogicalInterface(self):
        try:
            global logicalInterfaceId
            global outputValue
            deviceType = self.deviceType
            print (logicalInterfaceId)
            print (deviceType)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            print ('Get mappings for a logical interface from a device type')
            result = apiClient.getMappingsOnDeviceTypeForLogicalInterface(deviceType, logicalInterfaceId, draft=True)
            print (result)
            print ('Mappings retrieved from the device type')
            assert_true(result)
        except Exception as e:
            print(str(e.httpCode))
            print(str(e.message))
            print ('Error while mapping')


##########################################################################
#               Information Management Device APIs
##########################################################################

    def test041TestValidateDeviceTypeConfiguration(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Validate the device type configuration')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.validateDeviceTypeConfiguration(deviceType)
        print (result)
        assert_true(result)
        print('Validation for device type configuration succeeded')

    def test042TestValidateLogicalInterfaceConfiguration(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        self.test023TestCreateLogicalInterface()
        print (logicalInterfaceId)
        print ('Validate the logical interface configuration')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.validateLogicalInterfaceConfiguration(logicalInterfaceId)
        print (result)
        assert_true(result)
        print('Validation for logical interface configuration succeeded')

    
    def test043TestActivateDeviceTypeConfiguration(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Activate the device type configuration')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        print ('Initiating activation')
        result = apiClient.activateDeviceTypeConfiguration(deviceType)
        print (result)
        assert_true(result)
        print('Activation for device type configuration succeeded')

    def test044TestActivateLogicalInterfaceConfiguration(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Activate the logical interface configuration')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        print ('Initiating activation')
        result = apiClient.activateLogicalInterfaceConfiguration(logicalInterfaceId)
        print (result)
        assert_true(result)
        print('Activation for logical interface configuration succeeded')

    def test047TestGetDeviceStateForLogicalInterface(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        deviceId = self.deviceId
        print (deviceType)
        print (deviceId)
        print (logicalInterfaceId)
        print ('Gets the state for an logical interface for a device')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.getDeviceStateForLogicalInterface(deviceType, deviceId, logicalInterfaceId)
        print (result)
        assert_true(result)
        print('State retrieved from the device type for an logical interface')

##########################################################################
#       Information Management Delete / Deactivate Statements
##########################################################################

    def test048TestDeactivateLogicalInterfaceConfiguration(self):
        try:
            global logicalInterfaceId
            global outputValue
            deviceType = self.deviceType
            print (deviceType)
            print ('Deactivate the logical interface configuration')
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            print ('Initiating Deactivation')
            time.sleep(60)
            result = apiClient.deactivateLogicalInterfaceConfiguration(logicalInterfaceId, draft=False)
            print (result)
            assert_true(result)
            print('Deactivate for logical interface configuration succeeded')
        except Exception as e:
            print ('CUDIM0208E: The deactivate-configuration operation is not permitted on a draft Logical Interface resource.')

    def test049TestDeactivateDeviceTypeConfiguration(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (deviceType)
        print ('Deactivate the device type configuration')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        print ('Initiating Deactivation')
        time.sleep(60)
        result = apiClient.deactivateDeviceTypeConfiguration(deviceType)
        print (result)
        assert_true(result)
        print('Deactivation for device type configuration succeeded')

    def test050TestDeleteMappingsFromDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        print (logicalInterfaceId)
        print (deviceType)
        print ('About to Delete mapping for an Logical interface from a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deleteMappingsFromDeviceType(deviceType, logicalInterfaceId))
        print ('Mappings deleted from the device type')

    def test051TestRemoveLogicalInterfaceFromDeviceType(self):
        global logicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        self.test023TestCreateLogicalInterface()
        print (logicalInterfaceId)
        print (deviceType)
        print ('Add a logical interface to a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.addLogicalInterfaceToDeviceType(deviceType, logicalInterfaceId)
        print ('Logical interface added to a device type')
        print ('About to Remove the Logical Interface from Device Type')
        assert_true(apiClient.removeLogicalInterfaceFromDeviceType(deviceType, logicalInterfaceId))
        print ('Logical interface removed from a device type')

    @raises(Exception)
    def test052TestRemovePhysicalInterfaceFromDeviceType(self):
        global physicalInterfaceId
        global outputValue
        deviceType = self.deviceType
        self.test013TestCreatePhysicalInterface()
        print (physicalInterfaceId)
        print (deviceType)
        print ('Add a physical interface to a device type')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        result = apiClient.addPhysicalInterfaceToDeviceType(deviceType, physicalInterfaceId)
        print ('Physical interface added to a device type')
        print ('About to Remove the Physical Interface from Device Type')
        output = apiClient.removePhysicalInterfaceFromDeviceType(deviceType)
        assert_equal('204',output)
        print ('Physical interface removed from a device type')

    def test053TestDeleteLogicalInterface(self):
        global logicalInterfaceId
        print ('About to Delete Logical Interface: '+logicalInterfaceId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deleteLogicalInterface(logicalInterfaceId))
        print ('logical interface deleted')

    def test054TestDeleteLogicalInterfaceErr(self):
        try:
            global nonExistentLogicalInterfaceId
            print ('About to Delete Logical Interface: '+nonExistentLogicalInterfaceId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_true(apiClient.deleteLogicalInterface(nonExistentLogicalInterfaceId))
            print ('logical interface deleted')
        except Exception as e:
            print ('HTTP error deleting an logical interface')

    def test055TestDeleteEvent(self):
        global physicalInterfaceId
        global eventId
        eventId = "status"
        print (physicalInterfaceId)
        print (eventId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deleteEvent(physicalInterfaceId, eventId))
        print ('Event mapping deleted')

    def test056TestDeletePhysicalInterface(self):
        global physicalInterfaceId
        print ('About to Delete physical interface: ' + physicalInterfaceId)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deletePhysicalInterface(physicalInterfaceId))
        print ('physical interface deleted')

    def test057TestDeletePhysicalInterfaceErr(self):
        try:
            global nonExistentPhysicalInterfaceId
            print ('About to Delete physical interface: ' + nonExistentPhysicalInterfaceId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            apiClient.deletePhysicalInterface(nonExistentPhysicalInterfaceId)
        except Exception as e:
            print ('HTTP error deleting a physical interface')

    def test058TestDeleteEventTypeErr(self):
        try:
            global eventTypeId
            eventTypeId = '59b247df52faff002c3bfe71'
            print ('About to Delete Event Type Id: ' + eventTypeId)
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
            assert_true(apiClient.deleteEventType('59b0f0eb52faff002c3bfe3d'))
        except Exception as e:
            print ('[409] HTTP error deleting an event type')

    def test059TestDeleteEventType(self):
        global eventTypeId
        print ('About to Delete Event Type Id')
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deleteEventType(eventTypeId))
        print ('event type deleted')

    def test060TestDeleteSchema(self):
        global schemaIdForPhysicalInterface
        print ('About to Delete Schema: ' + schemaIdForPhysicalInterface)
        apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,"auth-key": self.authKey},self.logger)
        assert_true(apiClient.deleteSchema(schemaIdForPhysicalInterface))
        print ('Schema deleted')
