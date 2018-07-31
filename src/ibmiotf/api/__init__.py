# *****************************************************************************
# Copyright (c) 2015, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import ibmiotf
import json
import requests
import base64
import json
from datetime import datetime

import logging
from symbol import parameters
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ibmiotf.api.registry import Registry
from ibmiotf.api.usage import Usage
from ibmiotf.api.status import Status
from ibmiotf.api.lec import LEC
from ibmiotf.api.common import ApiClient as NewApiClient


class ApiClient():
    #Organization URL
    organizationUrl = 'https://%s/api/v0002/'

    #Bulk Operations URL
    bulkRetrieve = 'https://%s/api/v0002/bulk/devices'
    bulkAddUrl = 'https://%s/api/v0002/bulk/devices/add'
    bulkRemoveUrl = 'https://%s/api/v0002/bulk/devices/remove'

    #Device Types URL
    deviceTypesUrl = 'https://%s/api/v0002/device/types'
    deviceTypeUrl = 'https://%s/api/v0002/device/types/%s'

    #Device URL
    devicesUrl = 'https://%s/api/v0002/device/types/%s/devices'
    deviceUrl = 'https://%s/api/v0002/device/types/%s/devices/%s'
    deviceUrlLocation = 'https://%s/api/v0002/device/types/%s/devices/%s/location'
    deviceUrlMgmt = 'https://%s/api/v0002/device/types/%s/devices/%s/mgmt'

    #Device Event Cache URLs
    deviceEventListCacheUrl = 'https://%s/api/v0002/device/types/%s/devices/%s/events'
    deviceEventCacheUrl = 'https://%s/api/v0002/device/types/%s/devices/%s/events/%s'

    #Log Events URL
    deviceLogs = 'https://%s/api/v0002/logs/connection'

    #Diagnostics URL
    deviceDiagLogs = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs'
    deviceDiagLogsLogId = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/logs/%s'
    deviceDiagErrorCodes = 'https://%s/api/v0002/device/types/%s/devices/%s/diag/errorCodes'

    #Usage Management URL
    usageMgmt = 'https://%s/api/v0002/usage'

    #Service Status URL
    serviceStatus = 'https://%s/api/v0002/service-status'

    #Device Management URL
    mgmtRequests = 'https://%s/api/v0002/mgmt/requests'
    mgmtSingleRequest = 'https://%s/api/v0002/mgmt/requests/%s'
    mgmtRequestStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus'
    mgmtRequestSingleDeviceStatus = 'https://%s/api/v0002/mgmt/requests/%s/deviceStatus/%s/%s'

    #Device Management Extensions (dme) URL
    dmeRequests = 'https://%s/api/v0002/mgmt/custom/bundle'
    dmeSingleRequest = 'https://%s/api/v0002/mgmt/custom/bundle/%s'

    # Information management URLs

    # Draft Device type URLs
    draftDeviceTypeUrl = 'https://%s/api/v0002/draft/device/types/%s'

    # Schema URLs
    allSchemasUrl = "https://%s/api/v0002%s/schemas"
    oneSchemaUrl  = "https://%s/api/v0002%s/schemas/%s"
    oneSchemaContentUrl  = "https://%s/api/v0002%s/schemas/%s/content"

    # Event type URLs
    allEventTypesUrl = "https://%s/api/v0002%s/event/types"
    oneEventTypeUrl  = "https://%s/api/v0002%s/event/types/%s"

    # Physical Interface URLs
    allPhysicalInterfacesUrl = "https://%s/api/v0002%s/physicalinterfaces"
    onePhysicalInterfaceUrl  = "https://%s/api/v0002%s/physicalinterfaces/%s"
    oneDeviceTypePhysicalInterfaceUrl = 'https://%s/api/v0002%s/device/types/%s/physicalinterface'

    # Event URLs
    allEventsUrl = "https://%s/api/v0002%s/physicalinterfaces/%s/events"
    oneEventUrl  = "https://%s/api/v0002%s/physicalinterfaces/%s/events/%s"

    # Logical Interface URLs
    allLogicalInterfacesUrl = "https://%s/api/v0002%s/logicalinterfaces"
    oneLogicalInterfaceUrl  = "https://%s/api/v0002%s/logicalinterfaces/%s"
    allDeviceTypeLogicalInterfacesUrl = "https://%s/api/v0002%s/device/types/%s/logicalinterfaces"
    oneDeviceTypeLogicalInterfaceUrl = "https://%s/api/v0002/draft/device/types/%s/logicalinterfaces/%s"

    # Rules
    allRulesForLogicalInterfaceUrl = "https://%s/api/v0002%s/logicalinterfaces/%s/rules"
    oneRuleForLogicalInterfaceUrl  = "https://%s/api/v0002%s/logicalinterfaces/%s/rules/%s"

    # Mappings
    allDeviceTypeMappingsUrl = "https://%s/api/v0002%s/device/types/%s/mappings"
    oneDeviceTypeMappingUrl = "https://%s/api/v0002%s/device/types/%s/mappings/%s"

    # Device state
    deviceStateUrl = "https://%s/api/v0002/device/types/%s/devices/%s/state/%s"
    
    # Thing Types URLs
    thingTypesUrl   = "https://%s/api/v0002/thing/types"
    thingTypeUrl    = "https://%s/api/v0002/thing/types/%s"
    
    # Thing URLs
    thingsUrl   = "https://%s/api/v0002/thing/types/%s/things"
    thingUrl    = "https://%s/api/v0002/thing/types/%s/things/%s"
    
    # Draft Thing type URLs
    draftThingTypesUrl  = 'https://%s/api/v0002/draft/thing/types'
    draftThingTypeUrl   = 'https://%s/api/v0002/draft/thing/types/%s'
    
    # Thing types logical interface URLs
    allThingTypeLogicalInterfacesUrl = "https://%s/api/v0002%s/thing/types/%s/logicalinterfaces"
    oneThingTypeLogicalInterfaceUrl = "https://%s/api/v0002/draft/thing/types/%s/logicalinterfaces/%s"
    
    # Thing Mappings
    allThingTypeMappingsUrl = "https://%s/api/v0002%s/thing/types/%s/mappings"
    oneThingTypeMappingUrl = "https://%s/api/v0002%s/thing/types/%s/mappings/%s"
    
    # Thing state
    thingStateUrl = "https://%s/api/v0002/thing/types/%s/things/%s/state/%s"

    
    def __init__(self, options, logger=None):
        self.__options = options

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.__module__+"."+self.__class__.__name__)
            logger.setLevel(logging.INFO)

        self.logger = logger
        if 'auth-key' not in self.__options or self.__options['auth-key'] is None:
            raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-key")
        if 'auth-token' not in self.__options or self.__options['auth-token'] is None:
            raise ibmiotf.ConfigurationException("Missing required property for API key based authentication: auth-token")

        # Get the orgId from the apikey
        self.__options['org'] = self.__options['auth-key'][2:8]

        if "domain" not in self.__options:
            # Default to the domain for the public cloud offering
            self.__options['domain'] = "internetofthings.ibmcloud.com"

        if "host" in self.__options.keys():
            self.host = self.__options['host']
        else:
            self.host = self.__options['org'] + "." + self.__options['domain']
            
        self.credentials = (self.__options['auth-key'], self.__options['auth-token'])

        # To support development systems this can be overridden to False
        self.verify = False
        if not self.verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        self.newApiClient = NewApiClient(options, self.logger)
        self.registry = Registry(self.newApiClient)
        self.status = Status(self.newApiClient)
        self.usage = Usage(self.newApiClient)
        self.lec = LEC(self.newApiClient)



    #This method returns the organization
    def getOrganizationDetails(self):
        """
        Get details about an organization
        It does not need any parameter to be passed
        In case of failure it throws APIException
        """
        if self.__options['org'] is None:
            raise ibmiotf.ConfigurationException("Missing required property: org")
        else:
            url = ApiClient.organizationUrl % (self.host)
        r = requests.get(url, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Organization retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The organization does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)


    # =============================================================================================
    # Start of methods that are moving in to api.registry
    #
    # All migrated
    # =============================================================================================
    def deleteDevice(self, typeId, deviceId):
        """
        Delete an existing device.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use 'del api.registry.devicetypes[deviceId].devices[deviceId]'")
        deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

        r = requests.delete(deviceUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device was successfully removed")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(status, "Unexpected error", None)
    
    def getDevices(self, parameters = None):
        """
        Retrieve bulk devices
        It accepts accepts a list of parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'for device in api.registry.devices'")

        bulkRetrieve = ApiClient.bulkRetrieve % (self.host )
        r = requests.get(bulkRetrieve, auth = self.credentials, params = parameters, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Bulk retrieval successful")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the API key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The organization or device type does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def registerDevices(self, listOfDevices):
        """
        Register multiple new devices, each request can contain a maximum of 512KB.
        The response body will contain the generated authentication tokens for all devices.
        You must make sure to record these tokens when processing the response.
        We are not able to retrieve lost authentication tokens
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """
        
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devices.create(listOfDevices)'")
        
        bulkAdd = ApiClient.bulkAddUrl % (self.host )
        r = requests.post(bulkAdd, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code

        if status == 201:
            self.logger.debug("Bulk registration successful")
            return r.json()
        elif status == 202:
            raise ibmiotf.APIException(202, "Partial Success. Some devices registered successfully", r.json())
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 403:
            raise ibmiotf.APIException(403, "Maximum number of devices exceeded", r.json())
        elif status == 413:
            raise ibmiotf.APIException(413, "Request content exceeds 512KB", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def deleteMultipleDevices(self, listOfDevices):
        """
        Delete multiple devices, each request can contain a maximum of 512Kb
        It accepts accepts a list of devices (List of Dictionary of Devices)
        In case of failure it throws APIException
        """

        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devices.delete(listOfDevices)'")
        
        bulkRemove = ApiClient.bulkRemoveUrl % (self.host )
        r = requests.post(bulkRemove, auth = self.credentials, data = json.dumps(listOfDevices), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 202:
            self.logger.debug("Some devices deleted successfully")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 413:
            raise ibmiotf.APIException(413, "Request content exceeds 512KB", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceTypes(self, parameters = None):
        """
        Retrieves all existing device types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'for devicetype in api.registry.devicetypes'")

        deviceTypeUrl = ApiClient.deviceTypesUrl % (self.host)
        r = requests.get(deviceTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device types successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def addDeviceType(self, typeId, description = None, deviceInfo = None, metadata = None, classId = "Device"):
        """
        Creates a device type.
        It accepts typeId (string), description (string), deviceInfo(dict) and metadata(dict) as parameter
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devicetypes.create()'")

        deviceTypesUrl = ApiClient.deviceTypesUrl % (self.host)
        payload = {'id' : typeId, 'description' : description, 'deviceInfo' : deviceInfo, 'metadata': metadata,'classId': classId}

        r = requests.post(deviceTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("Device Type Created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The device type already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def deleteDeviceType(self, typeId):
        """
        Deletes a device type.
        It accepts typeId (string) as the parameter
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'del api.registry.devicetypes[deviceId]'")
        
        deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)

        r = requests.delete(deviceTypeUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device type was successfully deleted")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceType(self, typeId):
        """
        Gets device type details.
        It accepts typeId (string) as the parameter
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devicetypes[typeId]'")
        
        deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)
        r = requests.get(deviceTypeUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device type was successfully retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The device type does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def updateDeviceType(self, typeId, description, deviceInfo, metadata = None):
        """
        Updates a device type.
        It accepts typeId (string), description (string), deviceInfo (JSON) and metadata(JSON) as the parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devicetypes[typeId].update()'")

        deviceTypeUrl = ApiClient.deviceTypeUrl % (self.host, typeId)
        deviceTypeUpdate = {'description' : description, 'deviceInfo' : deviceInfo, 'metadata' : metadata}
        r = requests.put(deviceTypeUrl, auth=self.credentials, data=json.dumps(deviceTypeUpdate), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device type was successfully modified")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The device type does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def registerDevice(self, typeId, deviceId, authToken = None, deviceInfo = None, location = None, metadata=None):
        """
        Registers a new device.
        It accepts typeId (string), deviceId (string), authToken (string), location (JSON) and metadata (JSON) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devices.create()'")


        devicesUrl = ApiClient.devicesUrl % (self.host, typeId)
        payload = {'deviceId' : deviceId, 'authToken' : authToken, 'deviceInfo' : deviceInfo, 'location' : location, 'metadata': metadata}

        r = requests.post(devicesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("Device Instance Created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The device already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDevice(self, typeId, deviceId, expand = None):
        """
        Gets device details.
        It accepts typeId (string), deviceId (string) and expand (JSON) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devicetypes[typeId].devices[deviceId]'")

        deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

        r = requests.get(deviceUrl, auth=self.credentials, params = expand, verify=self.verify)
        status = r.status_code

        if status == 200:
            self.logger.debug("Device was successfully retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The device does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDevicesForType(self, typeId, parameters = None):
        """
        Gets details for multiple devices of a type
        It accepts typeId (string), deviceId (string) and expand (JSON) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'for device in api.registry.devicetypes[typeId].devices'")
        
        deviceUrl = ApiClient.devicesUrl % (self.host, typeId)

        r = requests.get(deviceUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device was successfully retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The device does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def removeDevice(self, typeId, deviceId):
        """
        Delete an existing device.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'del api.registry.devicetypes[typeId].devices[deviceId]'")
        
        deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

        r = requests.delete(deviceUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device was successfully removed")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def updateDevice(self, typeId, deviceId, metadata, deviceInfo = None, status = None):
        """
        Updates a device.
        It accepts typeId (string), deviceId (string), metadata (JSON), deviceInfo (JSON) and status(JSON) as parameters
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.registry.devicetypes[typeId].devices[deviceId].update()'")
        
        deviceUrl = ApiClient.deviceUrl % (self.host, typeId, deviceId)

        payload = {'status' : status, 'deviceInfo' : deviceInfo, 'metadata': metadata}
        r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 200:
            self.logger.debug("Device was successfully modified")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The organization, device type or device does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
    
    # =============================================================================================
    # End of methods that are moving in to api.registry
    # =============================================================================================
    
    
    # =============================================================================================
    # Start of methods that are moving in to api.lec
    #
    # All migrated
    # =============================================================================================
    def getLastEvent(self, typeId, deviceId, eventId):
        """
        Retrieves Last Cached Event.
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.lec.get(DeviceUid, eventId)'")

        events = ApiClient.deviceEventCacheUrl % (self.host, typeId, deviceId, eventId)
        r = requests.get(events, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 200:
            response = r.json()
            if response["format"] == "json":
                # Convert from base64 to byte to string to dictionary
                jsonPayload = json.loads(base64.b64decode(response["payload"]))
                response["data"] = jsonPayload
            return response

        elif status == 404:
            raise ibmiotf.APIException(404, "Event not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getLastEvents(self, typeId, deviceId):
        """
        Retrieves all last cached events
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.lec.getAll(DeviceUid)'")
        
        events = ApiClient.deviceEventListCacheUrl % (self.host, typeId, deviceId)
        r = requests.get(events, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 200:
            response = r.json()
            for event in response:
                if event["format"] == "json":
                    # Convert from base64 to byte to string to dictionary
                    jsonPayload = json.loads(base64.b64decode(event["payload"]))
                    event["data"] = jsonPayload
            return response

        elif status == 404:
            raise ibmiotf.APIException(404, "Event not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    # =============================================================================================
    # End of methods that are moving in to api.lec
    # =============================================================================================
    

    """
    ===========================================================================
    Extended Device Model Methods
     - get location for device
     - update location for device
     - get device management information
    ===========================================================================
    """

    def getDeviceLocation(self, typeId, deviceId):
        """
        Retrieve Device Location.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceUrl = ApiClient.deviceUrlLocation % (self.host, typeId, deviceId)

        r = requests.get(deviceUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Location was successfully obtained")
            return r.json()
        elif status == 404:
            raise ibmiotf.APIException(404, "Device location information not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def updateDeviceLocation(self, typeId, deviceId, deviceLocation):
        """
        Updates the location information for a device. If no date is supplied, the entry is added with the current date and time.
        It accepts typeId (string), deviceId (string) and deviceLocation (JSON) as parameters
        In case of failure it throws APIException
        """
        deviceUrl = ApiClient.deviceUrlLocation % (self.host, typeId, deviceId)

        r = requests.put(deviceUrl, auth=self.credentials, data=json.dumps(deviceLocation), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Location was successfully modified")
            return r.json()
        elif status == 404:
            raise ibmiotf.APIException(404, "Device location information not found", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementInformation(self, typeId, deviceId):
        """
        Gets device management information for a device.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceUrl = ApiClient.deviceUrlMgmt % (self.host, typeId, deviceId)
        r = requests.get(deviceUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Management Information was successfully obtained")
            return r.json()
        #This also throws a 403, which has not been documented
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getConnectionLogs(self, parameters):
        """
        List connection log events for a device to aid in diagnosing connectivity problems.
        The entries record successful connection, unsuccessful connection attempts, intentional disconnection and server-initiated disconnection.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        logs = ApiClient.deviceLogs % (self.host)
        r = requests.get(logs, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Connection Logs were successfully obtained")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    """
    ===========================================================================
    Device Diagnostics - Logs
     - get logs
     - clear logs
     - add log
     - get log
    ===========================================================================
    """

    def getAllDiagnosticLogs(self, typeId, deviceId):
        """
        Retrieves All Device Diagnostic Logs.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
        r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("All Diagnostic logs successfully retrieved")
            return r.json()
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def clearAllDiagnosticLogs(self, typeId, deviceId):
        """
        Deletes All Device Diagnostic Logs.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
        r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("All Diagnostic logs successfully cleared")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def addDiagnosticLog(self, typeId, deviceId, logs):
        """
        Add Device Diagnostic Logs.
        It accepts typeId (string), deviceId (string) and logs (JSON) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagLogs % (self.host, typeId, deviceId)
        r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(logs), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 201:
            self.logger.debug("Diagnostic entry was successfully added")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDiagnosticLog(self, typeId, deviceId, logId):
        """
        Retrieves Device Diagnostic Logs.
        It accepts typeId (string), deviceId (string) and logId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, typeId, deviceId, logId)
        r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Diagnostic log successfully retrieved")
            return r.json()
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def clearDiagnosticLog(self, typeId, deviceId, logId):
        """
        Delete Device Diagnostic Logs.
        It accepts typeId (string), deviceId (string) and logId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagLogsLogId % (self.host, typeId, deviceId, logId)
        r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Diagnostic log successfully cleared")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Device not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)


    """
    ===========================================================================
    Device Diagnostics - Error Codes
     - add error code
     - get all error codes
     - clear all error codes
    ===========================================================================
    """

    def addErrorCode(self, typeId, deviceId, errorCode):
        """
        Adds an error code to the list of error codes for the device. The list may be pruned as the new entry is added.
        It accepts typeId (string), deviceId (string) and errorCode (JSON) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
        r = requests.post(deviceDiagnostics, auth=self.credentials, data = json.dumps(errorCode), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 201:
            self.logger.debug("Error code was successfully added")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error Code not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getAllDiagnosticErrorCodes(self, typeId, deviceId):
        """
        Gets diagnostic error codes for a device.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
        r = requests.get(deviceDiagnostics, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 200:
            self.logger.debug("Error codes were successfully retrieved")
            return r.json()
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error Code not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def clearAllErrorCodes(self, typeId, deviceId):
        """
        Clears the list of error codes for the device. The list is replaced with a single error code of zero.
        It accepts typeId (string) and deviceId (string) as parameters
        In case of failure it throws APIException
        """
        deviceDiagnostics = ApiClient.deviceDiagErrorCodes % (self.host, typeId, deviceId)
        r = requests.delete(deviceDiagnostics, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 204:
            self.logger.debug("Error codes successfully cleared")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Error Code not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)


    # =============================================================================================
    # Start of methods that are moving in to api.status
    #
    # All migrated
    # =============================================================================================
    def getServiceStatus(self):
        """
        Retrieve the organization-specific status of each of the services offered by the IBM Watson IoT Platform.
        In case of failure it throws APIException
        """
        
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.status.serviceStatus()'")

        serviceStatus = ApiClient.serviceStatus % (self.host)
        r = requests.get(serviceStatus, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Service status successfully retrieved")
            return r.json()
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    # =============================================================================================
    # End of methods that are moving in to api.status
    # =============================================================================================
    
    
    # =============================================================================================
    # Start of methods that are moving in to api.usage
    #
    # All migrated
    # =============================================================================================
    def getDataTraffic(self, options):
        """
        Retrieve the amount of data used.
        In case of failure it throws APIException
        """
        self.logger.warning("DEPRECATION NOTICE: In the 1.0.0 release this method will be removed.  Use: 'api.usage.dataTransfer(start=datetime.date, end=datetime.date, detail=boolean)'")
        dataTraffic = (ApiClient.usageMgmt + '/data-traffic') % (self.host)
        r = requests.get(dataTraffic, auth=self.credentials, params=options, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Data Traffic = ", r.json() )
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Bad Request", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    # =============================================================================================
    # End of methods that are moving in to api.usage
    # =============================================================================================
    
    

    """
    ===========================================================================
    Device Management API
    - Get all requests
    - Initiate new request
    - Delete request
    - Get request
    - Get request status
    - Get request status for specific device
    ===========================================================================
    """

    def getAllDeviceManagementRequests(self):
        """
        Gets a list of device management requests, which can be in progress or recently completed.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequests % (self.host)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved all device management requests")
            return r.json()
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def initiateDeviceManagementRequest(self, deviceManagementRequest):
        """
        Initiates a device management request, such as reboot.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequests % (self.host)
        r = requests.post(mgmtRequests, auth=self.credentials, data=json.dumps(deviceManagementRequest), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 202:
            self.logger.debug("The request has been accepted for processing")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(500, "Devices don't support the requested operation", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def deleteDeviceManagementRequest(self, requestId):
        """
        Clears the status of a device management request.
        You can use this operation to clear the status for a completed request, or for an in-progress request which may never complete due to a problem.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
        r = requests.delete(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code
        if status == 204:
            self.logger.debug("Request status cleared")
            return True
        #403 and 404 error code needs to be added in Swagger documentation
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request Id not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequest(self, requestId):
        """
        Gets details of a device management request.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtSingleRequest % (self.host, requestId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieving single management request")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request Id not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequestStatus(self, requestId):
        """
        Get a list of device management request device statuses.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequestStatus % (self.host, requestId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved all device management request statuses")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request status not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getDeviceManagementRequestStatusByDevice(self, requestId, typeId, deviceId):
        """
        Get an individual device mangaement request device status.
        In case of failure it throws APIException
        """
        mgmtRequests = ApiClient.mgmtRequestSingleDeviceStatus % (self.host, requestId, typeId, deviceId)
        r = requests.get(mgmtRequests, auth=self.credentials, verify=self.verify)

        status = r.status_code

        if status == 200:
            self.logger.debug("Retrieved device management request status of single device")
            return r.json()
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "Request status not found", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    """
    ===========================================================================
    Device Management Extension API
        - List all device management extension packages
        - Create a new device management extension package
        - Delete a device management extension package
        - Get a specific device management extension package
        - Update a device management extension package
    ===========================================================================
    """

    def getAllDeviceManagementExtensionPkgs(self):
        """
        List all device management extension packages
        """
        dmeReq = ApiClient.dmeRequests % (self.host)
        r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Retrieved all Device Management Extension Packages")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in getAllDeviceManagementExtensionPkgs", r)

    def createDeviceManagementExtensionPkg(self, dmeData):
        """
        Create a new device management extension package
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeRequests % (self.host)
        r = requests.post(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
                      headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("The DME package request has been accepted for processing")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in createDeviceManagementExtensionPkg", r)

    def deleteDeviceManagementExtensionPkg(self, bundleId):
        """
        Delete a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.delete(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device Management Extension Package removed")
            return True
        else:
            raise ibmiotf.APIException(status,"HTTP Error in deleteDeviceManagementExtensionPkg", r)

    def getDeviceManagementExtensionPkg(self, bundleId):
        """
        Get a specific device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.get(dmeReq, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Management Extension Package retrieved")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in getDeviceManagementExtensionPkg", r)

    def updateDeviceManagementExtensionPkg(self, bundleId, dmeData):
        """
        Update a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        dmeReq = ApiClient.dmeSingleRequest % (self.host, bundleId)
        r = requests.put(dmeReq, auth=self.credentials, data=json.dumps(dmeData),
                      headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Device Management Extension Package updated")
            return r.json()
        else:
            raise ibmiotf.APIException(status,"HTTP Error in updateDeviceManagementExtensionPkg", r)



    """
    Thing API methods
     - register a new thing
     - get a single thing
     - get all thing instances for a type
     - remove thing
     - update thing
    """
    
    def registerThing(self, thingTypeId, thingId, name = None, description = None, aggregatedObjects = None, metadata=None):
        """
        Registers a new thing.
        It accepts thingTypeId (string), thingId (string), name (string), description (string), aggregatedObjects (JSON) and metadata (JSON) as parameters
        In case of failure it throws APIException
        """
        thingsUrl = ApiClient.thingsUrl % (self.host, thingTypeId)
        payload = {'thingId' : thingId, 'name' : name, 'description' : description, 'aggregatedObjects' : aggregatedObjects, 'metadata': metadata}

        r = requests.post(thingsUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("Thing Instance Created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the API key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The thing type with specified id does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "A thing instance with the specified id already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getThing(self, thingTypeId, thingId):
        """
        Gets thing details.
        It accepts thingTypeId (string), thingId (string)
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        r = requests.get(thingUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code

        if status == 200:
            self.logger.debug("Thing instance was successfully retrieved")
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id, or a thing with the specified id, does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def getThingsForType(self, thingTypeId, parameters = None):
        """
        Gets details for multiple things of a type
        It accepts thingTypeId (string) and parameters
        In case of failure it throws APIException
        """
        thingsUrl = ApiClient.thingsUrl % (self.host, thingTypeId)

        r = requests.get(thingsUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("List of things was successfully retrieved")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The thing type does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def removeThing(self, thingTypeId, thingId):
        """
        Delete an existing thing.
        It accepts thingTypeId (string) and thingId (string) as parameters
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        r = requests.delete(thingUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Thing was successfully removed")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type or thing instance with the specified id does not exist.", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The thing instance is aggregated into another thing instance.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)

    def updateThing(self, thingTypeId, thingId, name, description, aggregatedObjects, metadata = None):
        """
        Updates a thing.
        It accepts thingTypeId (string), thingId (string), name (string), description (string), aggregatedObjects(JSON), metadata (JSON) as parameters
        In case of failure it throws APIException
        """
        thingUrl = ApiClient.thingUrl % (self.host, thingTypeId, thingId)

        payload = {'name' : name, 'description' : description, 'aggregatedObjects' : aggregatedObjects, 'metadata': metadata}
        r = requests.put(thingUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)

        status = r.status_code
        if status == 200:
            self.logger.debug("The thing with the specified id was successfully updated.")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id, or a thing with the specified id, does not exist.", None)
        elif status == 412:
            raise ibmiotf.APIException(412, "The state of the thing has been modified since the client retrieved its representation (response to a conditional PUT).", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    
    
    """
    Thing Types API methods
     - Add thing type
     - Get thing types
     - Get thing type
     - update thing type
     - remove thing type
    """
    
    def addDraftThingType(self, thingTypeId, name = None, description = None, schemaId = None, metadata = None):
        """
        Creates a thing type.
        It accepts thingTypeId (string), name (string), description (string), schemaId(string) and metadata(dict) as parameter
        In case of failure it throws APIException
        """
        draftThingTypesUrl = ApiClient.draftThingTypesUrl % (self.host)
        payload = {'id' : thingTypeId, 'name' : name, 'description' : description, 'schemaId' : schemaId, 'metadata': metadata}

        r = requests.post(draftThingTypesUrl, auth=self.credentials, data=json.dumps(payload), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 201:
            self.logger.debug("The draft thing Type is created")
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (No body, invalid JSON, unexpected key, bad value)", r.json())
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The draft thing type already exists", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def updateDraftThingType(self, thingTypeId, name, description, schemaId, metadata = None):
        """
        Updates a thing type.
        It accepts thingTypeId (string), name (string), description (string), schemaId (string) and metadata(JSON) as the parameters
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        draftThingTypeUpdate = {'name' : name, 'description' : description, 'schemaId' : schemaId, 'metadata' : metadata}
        r = requests.put(draftThingTypeUrl, auth=self.credentials, data=json.dumps(draftThingTypeUpdate), headers = {'content-type': 'application/json'}, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Thing type was successfully modified")
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "The Thing type does not exist", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The update could not be completed due to a conflict", r.json())
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
    
    def getDraftThingTypes(self, parameters = None):
        """
        Retrieves all existing draft thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        draftThingTypesUrl = ApiClient.draftThingTypesUrl % (self.host)
        r = requests.get(draftThingTypesUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Draft thing types successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
    
    def getDraftThingType(self, thingTypeId, parameters = None):
        """
        Retrieves all existing draft thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        r = requests.get(draftThingTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Draft thing type successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing type has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A draft thing type with the specified id does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
            
    def deleteDraftThingType(self, thingTypeId):
        """
        Deletes a Thing type.
        It accepts thingTypeId (string) as the parameter
        In case of failure it throws APIException
        """
        draftThingTypeUrl = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)

        r = requests.delete(draftThingTypeUrl, auth=self.credentials, verify=self.verify)
        status = r.status_code
        if status == 204:
            self.logger.debug("Device type was successfully deleted")
            return True
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A thing type with the specified id does not exist.", None)
        elif status == 409:
            raise ibmiotf.APIException(409, "The draft thing type with the specified id is currently being referenced by another object.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getActiveThingTypes(self, parameters = None):
        """
        Retrieves all existing active thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        thingTypesUrl = ApiClient.thingTypesUrl % (self.host)
        r = requests.get(thingTypesUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Active thing types successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 400:
            raise ibmiotf.APIException(400, "Invalid request (invalid or missing query parameter, invalid query parameter value)", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)
        
    def getActiveThingType(self, thingTypeId, parameters = None):
        """
        Retrieves all existing Active thing types.
        It accepts accepts an optional query parameters (Dictionary)
        In case of failure it throws APIException
        """
        thingTypeUrl = ApiClient.thingTypeUrl % (self.host, thingTypeId)
        r = requests.get(thingTypeUrl, auth=self.credentials, params = parameters, verify=self.verify)
        status = r.status_code
        if status == 200:
            self.logger.debug("Acvtive thing type successfully retrieved")
            self.logger.debug(json.dumps(r.json()))
            return r.json()
        elif status == 304:
            raise ibmiotf.APIException(304, "The state of the thing type has not been modified (response to a conditional GET).", None)
        elif status == 401:
            raise ibmiotf.APIException(401, "The authentication token is empty or invalid", None)
        elif status == 403:
            raise ibmiotf.APIException(403, "The authentication method is invalid or the api key used does not exist", None)
        elif status == 404:
            raise ibmiotf.APIException(404, "A active thing type with the specified id does not exist.", None)
        elif status == 500:
            raise ibmiotf.APIException(500, "Unexpected error", None)
        else:
            raise ibmiotf.APIException(None, "Unexpected error", None)


    """
    ===========================================================================
    Information Management Schema APIs
    ===========================================================================
    """

    def getSchemas(self, draft=False, name=None, schemaType=None):
        """
        Get all schemas for the org.  In case of failure it throws APIException
        """
        if draft:
            req = ApiClient.allSchemasUrl % (self.host, "/draft")
        else:
            req = ApiClient.allSchemasUrl % (self.host, "")

        if name or schemaType:
            req += "?"
            if name:
                req += "name="+name
            if schemaType:
                if name:
                    req += "&"
                req += "schemaType="+schemaType

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All schemas retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all schemas", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def getSchema(self, schemaId, draft=False):
        """
        Get a single schema.  Throws APIException on failure
        """
        if draft:
            req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        else:
            req = ApiClient.oneSchemaUrl % (self.host, "", schemaId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("One schema retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error in get a schema", resp)
        return resp.json()

    def createSchema(self, schemaName, schemaFileName, schemaContents, description=None):
        """
        Create a schema for the org.
        Returns: schemaId (string), response (object).
        Throws APIException on failure
        """
        req = ApiClient.allSchemasUrl % (self.host, "/draft")
        fields={
        'schemaFile': (schemaFileName, schemaContents, 'application/json'),
            'schemaType': 'json-schema',
            'name': schemaName,
        }
        if description:
            fields["description"] = description

        multipart_data = MultipartEncoder(fields=fields)
        resp = requests.post(req, auth=self.credentials, data=multipart_data,
                            headers={'Content-Type': multipart_data.content_type}, verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Schema created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating a schema", resp)
        return resp.json()["id"], resp.json()

    def deleteSchema(self, schemaId):
        """
        Delete a schema.  Parameter: schemaId (string). Throws APIException on failure.
        """
        req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Schema deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting schema", resp)
        return resp

    def updateSchema(self, schemaId, schemaDefinition):
        """
        Update a schema. Throws APIException on failure.
        """
        req = ApiClient.oneSchemaUrl % (self.host, "/draft", schemaId)
        body = {"schemaDefinition": schemaDefinition}
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                           data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating schema", resp)
        return resp.json()

    def getSchemaContent(self, schemaId, draft=False):
        """
        Get the content for a schema.  Parameters: schemaId (string), draft (boolean). Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneSchemaContentUrl % (self.host, "/draft", schemaId)
        else:
            req = ApiClient.oneSchemaContentUrl % (self.host, "", schemaId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema content retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting schema content", resp)
        return resp.json()

    def updateSchemaContent(self, schemaId, schemaFile):
        """
        Updates the content for a schema.  Parameters: schemaId (string). Throws APIException on failure.
        """
        req = ApiClient.oneSchemaContentUrl % (self.host, "/draft", schemaId)
        body = {"schemaFile": schemaFile}
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                           data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Schema content updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating schema content", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management event type APIs
    ===========================================================================
    """

    def getEventTypes(self, draft=False, name=None, schemaId=None):
        """
        Get all event types for an org.  Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allEventTypesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allEventTypesUrl % (self.host, "")

        if name or schemaId:
            req += "?"
            if name:
                req += "name="+name
            if schemaId:
                if name:
                    req += "&"
                req += "schemaId="+schemaId

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All event types retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all event types", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createEventType(self, name, schemaId, description=None):
        """
        Creates an event type.
        Parameters: name (string), schemaId (string), description (string, optional).
        Returns: event type id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allEventTypesUrl % (self.host, "/draft")
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("event type created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating event type", resp)
        return resp.json()["id"], resp.json()

    def updateEventType(self, eventTypeId, name, schemaId, description=None):
        """
        Updates an event type.
        Parameters: eventTypeId (string), name (string), schemaId (string), description (string, optional).
        Throws APIException on failure.
        """
        req = ApiClient.oneEventTypesUrl % (self.host, "/draft", eventTypeId)
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("event type updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating event type", resp)
        return resp.json()

    def deleteEventType(self, eventTypeId):
        """
        Deletes an event type.  Parameters: eventTypeId (string). Throws APIException on failure.
        """
        req = ApiClient.oneEventTypeUrl % (self.host, "/draft", eventTypeId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("event type deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting an event type", resp)
        return resp

    def getEventType(self, eventTypeId, draft=False):
        """
        Gets an event type.  Parameters: eventTypeId (string), draft (boolean).  Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneEventTypeUrl % (self.host, "/draft", eventTypeId)
        else:
            req = ApiClient.oneEventTypeUrl % (self.host, "", eventTypeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("event type retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting an event type", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management Physical Interface APIs
    ===========================================================================
    """

    def getPhysicalInterfaces(self, draft=False, name=None):
        """
        Get all physical interfaces for an org.
        Parameters: draft (boolean).
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allPhysicalInterfacesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allPhysicalInterfacesUrl % (self.host, "")

        if name:
            req += "?name="+name

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All physical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all physical interfaces", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createPhysicalInterface(self, name, description=None):
        """
        Create a physical interface.
        Parameters:
          - name (string)
          - description (string, optional)
        Returns: physical interface id, response.
        Throws APIException on failure.
        """
        req = ApiClient.allPhysicalInterfacesUrl % (self.host, "/draft")
        body = {"name" : name}
        if description:
            body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("physical interface created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating physical interface", resp)
        return resp.json()["id"], resp.json()

    def updatePhysicalInterface(self, physicalInterfaceId, name, schemaId, description=None):
        """
        Update a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - name (string)
          - schemaId (string)
          - description (string, optional)
        Throws APIException on failure.
        """
        req = ApiClient.onePhysicalInterfacesUrl % (self.host, "/draft", physicalInterfaceId)
        body = {"name" : name, "schemaId" : schemaId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("physical interface updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating physical interface", resp)
        return resp.json()

    def deletePhysicalInterface(self, physicalInterfaceId):
        """
        Delete a physical interface.
        Parameters: physicalInterfaceId (string).
        Throws APIException on failure.
        """
        req = ApiClient.onePhysicalInterfaceUrl % (self.host, "/draft", physicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("physical interface deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting a physical interface", resp)
        return resp

    def getPhysicalInterface(self, physicalInterfaceId, draft=False):
        """
        Get a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.onePhysicalInterfaceUrl % (self.host, "/draft", physicalInterfaceId)
        else:
            req = ApiClient.onePhysicalInterfaceUrl % (self.host, "", physicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("physical interface retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting a physical interface", resp)
        return resp.json()


    """
    ===========================================================================
    Information Management Event Mapping APIs
    ===========================================================================
    """

    def getEvents(self, physicalInterfaceId, draft=False):
        """
        Get the event mappings for a physical interface.
        Parameters:
          - physicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allEventsUrl % (self.host, "/draft", physicalInterfaceId)
        else:
            req = ApiClient.allEventsUrl % (self.host, "", physicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All event mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting event mappings", resp)
        return resp.json()

    def createEvent(self, physicalInterfaceId, eventTypeId, eventId):
        """
        Create an event mapping for a physical interface.
        Parameters:
          physicalInterfaceId (string) - value returned by the platform when creating the physical interface
          eventTypeId (string) - value returned by the platform when creating the event type
          eventId (string) - matches the event id used by the device in the MQTT topic
        Throws APIException on failure.
        """
        req = ApiClient.allEventsUrl % (self.host, "/draft", physicalInterfaceId)
        body = {"eventId" : eventId, "eventTypeId" : eventTypeId}
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                       verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Event mapping created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating event mapping", resp)
        return resp.json()

    def deleteEvent(self, physicalInterfaceId, eventId):
        """
        Delete an event mapping from a physical interface.
        Parameters: physicalInterfaceId (string), eventId (string).
        Throws APIException on failure.
        """
        req = ApiClient.oneEventUrl % (self.host, "/draft", physicalInterfaceId, eventId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Event mapping deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting event mapping", resp)
        return resp


    """
    ===========================================================================
    Information Management Logical Interface APIs
    ===========================================================================
    """

    def getLogicalInterfaces(self, draft=False, name=None, schemaId=None):
        """
        Get all logical interfaces for an org.
        Parameters: draft (boolean).
        Returns:
            - list of ids
            - response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allLogicalInterfacesUrl % (self.host, "/draft")
        else:
            req = ApiClient.allLogicalInterfacesUrl % (self.host, "")

        if name or schemaId:
            req += "?"
            if name:
                req += "name="+name
            if schemaId:
                if name:
                    req += "&"
                req += "schemaId="+schemaId

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all logical interfaces", resp)
        return [x["id"] for x in resp.json()["results"]], resp.json()

    def createLogicalInterface(self, name, schemaId, description=None, alias=None):
        """
        Creates a logical interface..
        Parameters: name (string), schemaId (string), description (string, optional), alias (string, optional).
        Returns: logical interface id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allLogicalInterfacesUrl % (self.host, "/draft")
        body = {"name" : name, "schemaId" : schemaId}
        if description:
          body["description"] = description
        if alias:
          body["alias"] = alias
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating logical interface", resp)
        return resp.json()["id"], resp.json()

    def updateLogicalInterface(self, logicalInterfaceId, name, schemaId, description=None):
        """
        Updates a logical interface.
        Parameters: logicalInterfaceId (string), name (string), schemaId (string), description (string, optional).
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"name" : name, "schemaId" : schemaId, "id" : logicalInterfaceId}
        if description:
            body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body),  verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Logical interface updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating logical interface", resp)
        return resp.json()

    def deleteLogicalInterface(self, logicalInterfaceId):
        """
        Deletes a logical interface.
        Parameters: logicalInterfaceId (string).
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("logical interface deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting a logical interface", resp)
        return resp

    def getLogicalInterface(self, logicalInterfaceId, draft=False):
        """
        Gets a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        else:
            req = ApiClient.oneLogicalInterfaceUrl % (self.host, "", logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting a logical interface", resp)
        return resp.json()

    def getRulesForLogicalInterface(self, logicalInterfaceId, draft=False):
        """
        Gets rules for a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        else:
            req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "", logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface rules retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting logical interface rules", resp)
        return resp.json()

    def getRuleForLogicalInterface(self, logicalInterfaceId, ruleId, draft=False):
        """
        Gets a rule for a logical interface.
        Parameters:
          - logicalInterfaceId (string)
          - ruleId (string)
          - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        else:
            req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "", logicalInterfaceId, ruleId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("logical interface rule retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting logical interface rule", resp)
        return resp.json()

    def addRuleToLogicalInterface(self, logicalInterfaceId, name, condition, description=None, alias=None):
        """
        Adds a rule to a logical interface.
        Parameters: 
          - logicalInterfaceId (string)
          - name (string)
          - condition (string)
          - (description (string, optional)
        Returns: rule id (string), response (object).
        Throws APIException on failure.
        """
        req = ApiClient.allRulesForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"name" : name, "condition" : condition}
        if description:
          body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface rule created")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating logical interface rule", resp)
        return resp.json()["id"], resp.json()

    def updateRuleOnLogicalInterface(self, logicalInterfaceId, ruleId, name, condition, description=None):
        """
        Updates a rule on a logical interface..
        Parameters: 
          - logicalInterfaceId (string),
          - ruleId (string)
          - name (string)
          - condition (string)
          - description (string, optional)
        Returns: response (object).
        Throws APIException on failure.
        """
        req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        body = {"logicalInterfaceId" : logicalInterfaceId, "id" : ruleId, "name" : name, "condition" : condition}
        if description:
          body["description"] = description
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                            data=json.dumps(body), verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Logical interface rule updated")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating logical interface rule", resp)
        return resp.json()

    def deleteRuleOnLogicalInterface(self, logicalInterfaceId, ruleId):
        """
        Deletes a rule from a logical interface
        Parameters: 
          - logicalInterfaceId (string),
          - ruleId (string)
        Returns: response (object)
        Throws APIException on failure
        """
        req = ApiClient.oneRuleForLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId, ruleId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface rule deleted")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting logical interface rule", resp)
        return resp


    """
    ===========================================================================
    Information Management Device Type APIs
    ===========================================================================
    """

    def addPhysicalInterfaceToDeviceType(self, typeId, physicalInterfaceId):
        """
        Adds a physical interface to a device type.
        Parameters:
            - typeId (string) - the device type
            - physicalInterfaceId (string) - the id returned by the platform on creation of the physical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        body = {"id" : physicalInterfaceId}
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                       verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Physical interface added to a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding physical interface to a device type", resp)
        return resp.json()

    def getPhysicalInterfaceOnDeviceType(self, typeId, draft=False):
        """
        Gets the physical interface associated with a device type.
        Parameters:
            - typeId (string) - the device type
            - draft (boolean)
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "", typeId)
        resp = requests.get(req, auth=self.credentials, headers={"Content-Type":"application/json"},
                       verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Physical interface retrieved from a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting physical interface on a device type", resp)
        return resp.json()["id"], resp.json()

    def removePhysicalInterfaceFromDeviceType(self, typeId):
        """
        Removes the physical interface from a device type.  Only one can be associated with a device type,
          so the physical interface id is not necessary as a parameter.
        Parameters:
                    - typeId (string) - the device type
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypePhysicalInterfaceUrl % (self.host, "/draft", typeId)
        body = {}
        resp = requests.delete(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
           verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Physical interface removed")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing a physical interface from a device type", resp)
        return resp

    def getLogicalInterfacesOnDeviceType(self, typeId, draft=False):
        """
        Get all logical interfaces for a device type.
        Parameters:
          - typeId (string)
          - draft (boolean)
        Returns:
            - list of logical interface ids
            - HTTP response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "", typeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All device type logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all device type logical interfaces", resp)
        return [appintf["id"] for appintf in resp.json()], resp.json()

    def addLogicalInterfaceToDeviceType(self, typeId, logicalInterfaceId):
        """
        Adds a logical interface to a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
            - description (string) - optional (not used)
        Throws APIException on failure.
        """
        req = ApiClient.allDeviceTypeLogicalInterfacesUrl % (self.host, "/draft", typeId)
        body = {"id" : logicalInterfaceId}
#       body = {"name" : "required but not used!!!", "id" : logicalInterfaceId, "schemaId" : schemaId}
#       if description:
#           body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                        verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Logical interface added to a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding logical interface to a device type", resp)
        return resp.json()

    def removeLogicalInterfaceFromDeviceType(self, typeId, logicalInterfaceId):
        """
        Removes a logical interface from a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeLogicalInterfaceUrl % (self.host, typeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface removed from a device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing logical interface from a device type", resp)
        return resp

    def getMappingsOnDeviceType(self, typeId, draft=False):
        """
        Get all the mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - draft (boolean) - draft or active
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "/draft", typeId)
        else:
            req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "", typeId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All device type mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all device type mappings", resp)
        return resp.json()

    def addMappingsToDeviceType(self, typeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalinterface (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
        }

        Throws APIException on failure.
        """
        req = ApiClient.allDeviceTypeMappingsUrl % (self.host, "/draft", typeId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Device type mappings created for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating device type mappings for logical interface", resp)
        return resp.json()

    def deleteMappingsFromDeviceType(self, typeId, logicalInterfaceId):
        """
        Deletes mappings for an application interface from a device type.
        Parameters:
            - typeId (string) - the device type
          - logicalInterfaceId (string) - the platform returned id of the application interface
        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Mappings deleted from the device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting mappings for a logical interface from a device type", resp)
        return resp

    def getMappingsOnDeviceTypeForLogicalInterface(self, typeId, logicalInterfaceId, draft=False):
        """
        Gets the mappings for a logical interface from a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        else:
            req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "", typeId, logicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Mappings retrieved from the device type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting mappings for a logical interface from a device type", resp)
        return resp.json()

    def updateMappingsOnDeviceType(self, typeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a device type.
        Parameters:
            - typeId (string) - the device type
            - logicalInterfaceId (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
      }

        Throws APIException on failure.
        """
        req = ApiClient.oneDeviceTypeMappingUrl % (self.host, "/draft", typeId, logicalInterfaceId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Device type mappings updated for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating device type mappings for logical interface", resp)
        return resp.json()

    """
    ===========================================================================
    Information Management Device APIs
    ===========================================================================
    # """

    def validateDeviceTypeConfiguration(self, typeId):
        """
        Validate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.draftDeviceTypeUrl % (self.host, typeId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for device type configuration failed", resp)
        return resp.json()

    def activateDeviceTypeConfiguration(self, typeId):
        """
        Activate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.draftDeviceTypeUrl % (self.host, typeId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for device type configuration failed", resp)
        return resp.json()

    def deactivateDeviceTypeConfiguration(self, typeId):
        """
        Deactivate the device type configuration.
        Parameters:
            - typeId (string) - the platform device type
        Throws APIException on failure.
        """
        req = ApiClient.deviceTypeUrl % (self.host, typeId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivation for device type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivation for device type configuration failed", resp)
        return resp.json()

    def validateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Validate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for logical interface configuration failed", resp)
        return resp.json()

    def activateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Activate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for logical interface configuration failed", resp)
        return resp.json()

    def deactivateLogicalInterfaceConfiguration(self, logicalInterfaceId):
        """
        Deactivate the logical interface configuration.
        Parameters:
            - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.oneLogicalInterfaceUrl % (self.host, "/draft", logicalInterfaceId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivate for logical interface configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivate for logical interface configuration failed", resp)
        return resp.json()

    def getDeviceStateForLogicalInterface(self, typeId, deviceId, logicalInterfaceId):
        """
        Gets the state for a logical interface for a device.
        Parameters:
            - typeId (string) - the platform device type
            - deviceId (string) - the platform device id
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.deviceStateUrl % (self.host, typeId, deviceId, logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("State retrieved from the device type for a logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting state for a logical interface from a device type", resp)
        return resp.json()
    
    """
    ===========================================================================
    Information Management Things APIs
    ===========================================================================
    """
    
    def validateThingTypeConfiguration(self, thingTypeId):
        """
        Validate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "validate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Validation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Validation for thing type configuration failed", resp)
        return resp.json()

    def activateThingTypeConfiguration(self, thingTypeId):
        """
        Activate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.draftThingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "activate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 202):
            self.logger.debug("Activation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Activation for thing type configuration failed", resp)
        return resp.json()

    def deactivateDeviceTypeConfiguration(self, thingTypeId):
        """
        Deactivate the thing type configuration.
        Parameters:
            - thingTypeId (string) - the platform thing type
        Throws APIException on failure.
        """
        req = ApiClient.thingTypeUrl % (self.host, thingTypeId)
        body = {"operation" : "deactivate-configuration"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if resp.status_code == 202:
            self.logger.debug("Deactivation for thing type configuration succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, "Deactivation for thing type configuration failed", resp)
        return resp.json()
    
    def getThingStateForLogicalInterface(self, thingTypeId, thingId, logicalInterfaceId):
        """
        Gets the state for a logical interface for a thing.
        Parameters:
            - thingTypeId (string) - the platform thing type
            - thingId (string) - the platform thing id
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.thingStateUrl % (self.host, thingTypeId, thingId, logicalInterfaceId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("State retrieved from the thing type for a logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting state for a logical interface from a thing type", resp)
        return resp.json()

    def resetThingStateForLogicalInterface(self, thingTypeId, thingId , logicalInterfaceId):
        """
        Perform an operation against the thing state for a logical interface
        Parameters:
           - thingTypeId (string)
           - thingId (string)
           - logicalInterfaceId (string)
        Throws APIException on failure.
        """
        req = ApiClient.thingStateUrl % (self.host, "", thingTypeId,thingId , logicalInterfaceId)
        body = {"operation" : "reset-state"}
        resp = requests.patch(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
               verify=self.verify)
        if (resp.status_code == 200):
            self.logger.debug("Reset ThingState For LogicalInterface succeeded")
        else:
            raise ibmiotf.APIException(resp.status_code, " HTTP error on reset ThingState For LogicalInterface ", resp)
        return resp.json()


    """
    ===========================================================================
    Information Management Things type APIs
    ===========================================================================
    """
    
    def getLogicalInterfacesOnThingType(self, thingTypeId, draft=False):
        """
        Get all logical interfaces for a thing type.
        Parameters:
          - thingTypeId (string)
          - draft (boolean)
        Returns:
            - list of logical interface ids
            - HTTP response object
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "/draft", thingTypeId)
        else:
            req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "", thingTypeId)
        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All thing type logical interfaces retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all thing type logical interfaces", resp)
        return [appintf["id"] for appintf in resp.json()], resp.json()

    def addLogicalInterfaceToThingType(self, thingTypeId, logicalInterfaceId, schemaId = None, name = None):
        """
        Adds a logical interface to a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.allThingTypeLogicalInterfacesUrl % (self.host, "/draft", thingTypeId)
        body = {"id" : logicalInterfaceId}
#        body = {"name" : name, "id" : logicalInterfaceId, "schemaId" : schemaId}
#       if description:
#           body["description"] = description
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=json.dumps(body),
                        verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("The draft logical interface was successfully associated with the thing type.")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error adding logical interface to a thing type", resp)
        return resp.json()

    def removeLogicalInterfaceFromThingType(self, thingTypeId, logicalInterfaceId):
        """
        Removes a logical interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id returned by the platform on creation of the logical interface
        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeLogicalInterfaceUrl % (self.host, thingTypeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Logical interface removed from a thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error removing logical interface from a thing type", resp)
        return resp
    
    def getMappingsOnThingType(self, thingTypeId, draft=False):
        """
        Get all the mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - draft (boolean) - draft or active
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.allThingTypeMappingsUrl % (self.host, "/draft", thingTypeId)
        else:
            req = ApiClient.allThingTypeMappingsUrl % (self.host, "", thingTypeId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("All thing type mappings retrieved")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting all thing type mappings", resp)
        return resp.json()

    def addMappingsToThingType(self, thingTypeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalinterface (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
        }

        Throws APIException on failure.
        """
        req = ApiClient.allThingTypeMappingsUrl % (self.host, "/draft", thingTypeId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.post(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 201:
            self.logger.debug("Thing type mappings created for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error creating Thing type mappings for logical interface", resp)
        return resp.json()

    def deleteMappingsFromThingType(self, thingTypeId, logicalInterfaceId):
        """
        Deletes mappings for an application interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the platform returned id of the application interface
        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        resp = requests.delete(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 204:
            self.logger.debug("Mappings deleted from the thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error deleting mappings for a logical interface from a thing type", resp)
        return resp

    def getMappingsOnThingTypeForLogicalInterface(self, thingTypeId, logicalInterfaceId, draft=False):
        """
        Gets the mappings for a logical interface from a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the platform returned id of the logical interface
        Throws APIException on failure.
        """
        if draft:
            req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        else:
            req = ApiClient.oneThingTypeMappingUrl % (self.host, "", thingTypeId, logicalInterfaceId)

        resp = requests.get(req, auth=self.credentials, verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Mappings retrieved from the thing type")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error getting mappings for a logical interface from a thing type", resp)
        return resp.json()

    def updateMappingsOnDeviceType(self, thingTypeId, logicalInterfaceId, mappingsObject, notificationStrategy = "never"):
        """
        Add mappings for a thing type.
        Parameters:
            - thingTypeId (string) - the thing type
            - logicalInterfaceId (string) - the id of the application interface these mappings are for
            - notificationStrategy (string) - the notification strategy to use for these mappings
            - mappingsObject (Python dictionary corresponding to JSON object) example:

            { # eventid -> { property -> eventid property expression }
         "status" :  {
                "eventCount" : "($state.eventCount == -1) ? $event.d.count : ($state.eventCount+1)",
           }
      }

        Throws APIException on failure.
        """
        req = ApiClient.oneThingTypeMappingUrl % (self.host, "/draft", thingTypeId, logicalInterfaceId)
        try:
            mappings = json.dumps({
                "logicalInterfaceId" : logicalInterfaceId,
                "notificationStrategy" : notificationStrategy,
                "propertyMappings" : mappingsObject
            })
        except Exception as exc:
            raise ibmiotf.APIException(-1, "Exception formatting mappings object to JSON", exc)
        resp = requests.put(req, auth=self.credentials, headers={"Content-Type":"application/json"}, data=mappings,
               verify=self.verify)
        if resp.status_code == 200:
            self.logger.debug("Thing type mappings updated for logical interface")
        else:
            raise ibmiotf.APIException(resp.status_code, "HTTP error updating thing type mappings for logical interface", resp)
        return resp.json()

