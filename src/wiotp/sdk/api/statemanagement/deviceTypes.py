# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import iso8601

from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import IterableSimpleList
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDictActive
from wiotp.sdk.api.common import RestApiModifiableProperty
from wiotp.sdk.api.statemanagement.logicalInterfaces import BaseLogicalInterface
from wiotp.sdk.api.statemanagement.physicalInterfaces import PhysicalInterface
        
# =========================================================================
# Physical Interface for the Device Type
# =========================================================================
class DraftPI(RestApiModifiableProperty):
    
    def __init__(self):
        super(DraftPI, self).__init__(PhysicalInterface)
    
    def getUrl(self, instance):
        return ("api/v0002/draft/device/types/%s/physicalinterface" % instance.id)  

    def getApiClient(self, instance):
        return instance._apiClient

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/state-mgmt.html#/Logical Interfaces        
class BaseDeviceType(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase
    
    @property
    def classId(self):
        """
        Class Id is 'Device' or 'Gateway'
        """
        return self["classId"]    # 
    
    # TBD can we subtype these to describe all the sub fields?
    @property
    def deviceInfo(self):
        return self["deviceInfo"]

    @property
    def metadata(self):
        return self["schemaId"]
        
    @property
    def version(self):
        return self["version"]   
 
    @property 
    def logicalInterfaces(self):
        return self._logicalInterfaces

    @property 
    def mappings(self):
        return self._mappings   
    
class DraftDeviceType(BaseDeviceType):
    physicalInterface = DraftPI()

    def __init__(self, apiClient, **kwargs):
        super(DraftDeviceType, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/draft/device/types/%s" % self.id
        #ßself.physicalInterface = RestApiModifiableProperty(apiClient, self._url + "/physicalinterface")
        self._logicalInterfaces = DraftLogicalInterfaces(apiClient, self.id)
        self._mappings = DraftMappings(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseDeviceType    
    
    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code == 200:
            print ("returning patch response response: %s " % r.json())
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))
        
    def activate(self):
        print ("Activating Device Type: %s " % self.id)
        return self.__callPatchOperation__({"operation": "activate-configuration"})
 
    def validate(self):
        print ("Validating Device Type: %s " % self.id)
        return self.__callPatchOperation__({"operation": "validate-configuration"})
 
    def differences(self):
        print ("List differences for Device Type: %s " % self.id)
        return self.__callPatchOperation__({"operation": "list-differences"})

 
class ActiveDeviceType(BaseDeviceType):
    physicalInterface = DraftPI()
    def __init__(self, apiClient, **kwargs):
        super(ActiveDeviceType, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/device/types/%s" % self.id
        self._draftUrl = "api/v0002/draft/device/types/%s" % self.id
        self._logicalInterfaces = ActiveLogicalInterfaces(apiClient, self.id)
        self._mappings = ActiveMappings(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseDeviceType

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code == 200:
            print ("returning patch response response: %s " % r.json())
            return r.json()
        if r.status_code == 202:
            print ("returning delayed patch response response: %s " % r.json())
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))
        
    def deactivate(self):
        print ("Deactivating Device Type: %s " % self.id)
        return self.__callPatchOperation__({"operation": "deactivate-configuration"})
    
    def __callDraftPatchOperation__(self, body):
        r = self._apiClient.patch(self._draftUrl, body)
        if r.status_code == 200:
            print ("returning patch response response: %s " % r.json())
            return r.json()
        if r.status_code == 202:
            print ("returning delayed patch response response: %s " % r.json())
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))
             
    def activate(self):
        print ("Activating Device Type: %s " % self.id)
        return self.__callDraftPatchOperation__({"operation": "activate-configuration"})
 
    def validate(self):
        print ("Validating Device Type: %s " % self.id)
        return self.__callDraftPatchOperation__({"operation": "validate-configuration"})
 
    def differences(self):
        print ("List differences for Device Type: %s " % self.id)
        return self.__callDraftPatchOperation__({"operation": "list-differences"})
    #def physicalInterface(self):
    #    r = self._apiClient.get(self._url + "/physicalinterface")
    #    if r.status_code == 200:
    #        # TBD print ("returning schema content: %s " % r.json())
    #        return r.json()
    #    else:
    #        raise Exception("Unexpected response from API (%s) = %s %s" % (self.contentUrl, r.status_code, r.text))

    
class IterableDraftDeviceTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableDraftDeviceTypeList, self).__init__(
            apiClient, DraftDeviceType, url, filters=filters
        )

class DraftDeviceTypes(RestApiDict):

    def __init__(self, apiClient):
        super(DraftDeviceTypes, self).__init__(
            apiClient, DraftDeviceType, IterableDraftDeviceTypeList, "api/v0002/draft/device/types"
        )
            
class IterableActiveDeviceTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableActiveDeviceTypeList, self).__init__(
            apiClient, ActiveDeviceType, url, filters=filters
        )

class ActiveDeviceTypes(RestApiDict):

    def __init__(self, apiClient):
        super(ActiveDeviceTypes, self).__init__(
            apiClient, ActiveDeviceType, IterableActiveDeviceTypeList, "api/v0002/device/types"
        )      


# =========================================================================
# Logical Interfaces for the Device Type
# =========================================================================
        
class IterableLogicalInterfaceList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableLogicalInterfaceList, self).__init__(
            apiClient, BaseLogicalInterface, url
        )

class DraftLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/logicalinterfaces" % deviceTypeId
        super(DraftLogicalInterfaces, self).__init__(
            apiClient, 
            BaseLogicalInterface, 
            IterableLogicalInterfaceList, 
            url
        )
        
class ActiveLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/logicalinterfaces" % deviceTypeId
        super(ActiveLogicalInterfaces, self).__init__(
            apiClient, 
            BaseLogicalInterface, 
            IterableLogicalInterfaceList,
            url
        )        
                
# =========================================================================
# Mappings for the Device Type
# =========================================================================
        
# define the common properties found on most Rest API Items
class DeviceTypeMapping(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)
        
    @property
    def logicalInterfaceId(self):
        return self["logicalInterfaceId"]   
        
    @property
    def notificationStrategy(self):
        return self["notificationStrategy"]   
        
    # TBD define the substructure?
    @property
    def propertyMappings(self):
        return self["propertyMappings"]   
            
    @property
    def version(self):
        return self["version"]   
        
    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def createdBy(self):
        return self["createdBy"]

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def updatedBy(self):
        return self["updatedBy"]
    
class IterableMappingList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableMappingList, self).__init__(
            apiClient, DeviceTypeMapping, url
        )

class DraftMappings(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/mappings" % deviceTypeId
        super(DraftMappings, self).__init__(
            apiClient, 
            DeviceTypeMapping, 
            IterableMappingList, 
            url
        )
        
class ActiveMappings(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/mappings" % deviceTypeId
        super(ActiveMappings, self).__init__(
            apiClient, 
            DeviceTypeMapping, 
            IterableMappingList,
            url
        )                        