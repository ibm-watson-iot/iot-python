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
from wiotp.sdk.api.common import RestApiDictReadOnly
from wiotp.sdk.api.common import RestApiModifiableProperty
from wiotp.sdk.api.state.devices import Devices
from wiotp.sdk.api.state.logicalInterfaces import BaseLogicalInterface
from wiotp.sdk.api.state.physicalInterfaces import PhysicalInterface

# =========================================================================
# Physical Interface for the Device Type
# =========================================================================
class DraftPI(RestApiModifiableProperty):
    def __init__(self):
        super(DraftPI, self).__init__(PhysicalInterface)

    def getUrl(self, instance):
        return "api/v0002/draft/device/types/%s/physicalinterface" % instance.id

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
        return self["classId"]  #

    @property
    def deviceInfo(self):
        if "deviceInfo" in self:
            return self["deviceInfo"]
        else:
            return None

    @property
    def metadata(self):
        if "metadata" in self:
            return self["metadata"]
        else:
            return None

    @property
    def edgeConfiguration(self):
        if "edgeConfiguration" in self:
            return self["edgeConfiguration"]
        else:
            return None

    @property
    def logicalInterfaces(self):
        return self._logicalInterfaces

    @property
    def mappings(self):
        return self._mappings


class DeviceType(BaseDeviceType):
    physicalInterface = DraftPI()  # TBD need to provide access to active and draft.

    def __init__(self, apiClient, **kwargs):
        super(DeviceType, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/device/types/%s" % self.id
        self._draftUrl = "api/v0002/draft/device/types/%s" % self.id
        self._logicalInterfaces = DraftLogicalInterfaces(
            apiClient, self.id
        )  # TBD need to provide access to active and draft.
        self._mappings = ActiveMappings(apiClient, self.id)
        self._devices = Devices(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseDeviceType

    @property
    def devices(self):
        return self._devices

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code in (200, 202):
            return r.json()
        else:
            raise ApiException(r)

    def deactivate(self):
        return self.__callPatchOperation__({"operation": "deactivate-configuration"})

    def __callDraftPatchOperation__(self, body):
        r = self._apiClient.patch(self._draftUrl, body)
        if r.status_code in (200, 202):
            return r.json()
        else:
            raise ApiException(r)

    def activate(self):
        return self.__callDraftPatchOperation__({"operation": "activate-configuration"})

    def validate(self):
        return self.__callDraftPatchOperation__({"operation": "validate-configuration"})

    def differences(self):
        return self.__callDraftPatchOperation__({"operation": "list-differences"})


class IterableDeviceTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableDeviceTypeList, self).__init__(apiClient, DeviceType, url, filters=filters)


class DeviceTypes(RestApiDict):
    def __init__(self, apiClient):
        super(DeviceTypes, self).__init__(apiClient, DeviceType, IterableDeviceTypeList, "api/v0002/device/types")


# =========================================================================
# Logical Interfaces for the Device Type
# =========================================================================


class IterableLogicalInterfaceList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableLogicalInterfaceList, self).__init__(apiClient, BaseLogicalInterface, url)


class DraftLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/logicalinterfaces" % deviceTypeId
        super(DraftLogicalInterfaces, self).__init__(apiClient, BaseLogicalInterface, IterableLogicalInterfaceList, url)


class ActiveLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/device/types/%s/logicalinterfaces" % deviceTypeId
        super(ActiveLogicalInterfaces, self).__init__(
            apiClient, BaseLogicalInterface, IterableLogicalInterfaceList, url
        )


# =========================================================================
# Mappings for the Device Type
# =========================================================================

# define the common properties found on most Rest API Items
class DeviceTypeMapping(defaultdict):
    def __init__(self, **kwargs):
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
    def __init__(self, apiClient, url, filters=None, passApiClient=False):
        # This API does not support sorting
        super(IterableMappingList, self).__init__(apiClient, DeviceTypeMapping, url)


class DraftMappings(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/mappings" % deviceTypeId
        super(DraftMappings, self).__init__(apiClient, DeviceTypeMapping, IterableMappingList, url)


class ActiveMappings(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/draft/device/types/%s/mappings" % deviceTypeId
        super(ActiveMappings, self).__init__(apiClient, DeviceTypeMapping, IterableMappingList, url)
