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
# *****************************************************************************

import ibmiotf.api
import ibmiotf.application
import ibmiotf.gateway
import ibmiotf.device
from ibmiotf import *
from nose.tools import *
from nose import SkipTest


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
    def testGetSchemas(self):
        with assert_raises(APIException) as e:
            apiClient = ibmiotf.api.ApiClient({"auth-method": "token","auth-token": self.authToken,
                                               "auth-key": self.authKey},self.logger)
            apiClient.getSchemas(self, draft=False, name=None, schemaType=None)
        assert_equal(e.exception.msg, 'All schemas retrieved')
