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
from wiotp.sdk.api.state.things import Things
from wiotp.sdk.api.state.logicalInterfaces import BaseLogicalInterface


# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/state-mgmt.html#/Logical Interfaces
class BaseThingType(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def name(self):
        return self["name"]

    @property
    def schemaId(self):
        return self["schemaId"]

    @property
    def description(self):
        if "description" in self:
            return self["description"]
        else:
            return None

    @property
    def metadata(self):
        if "metadata" in self:
            return self["metadata"]
        else:
            return None

    @property
    def schema(self):
        return self._schema

    @property
    def logicalInterfaces(self):
        return self._logicalInterfaces

    @property
    def mappings(self):
        return self._mappings


class DraftThingType(BaseThingType):
    def __init__(self, apiClient, **kwargs):
        super(DraftThingType, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/draft/thing/types/%s" % self.id
        self._logicalInterfaces = DraftLogicalInterfaces(
            apiClient, self.id
        )  # TBD need to provide access to active and draft.
        self._mappings = DraftMappings(apiClient, self.id)
        self._things = Things(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseDeviceType

    @property
    def things(self):
        return self._things

    def __callDraftPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
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


class ActiveThingType(BaseThingType):
    def __init__(self, apiClient, **kwargs):
        super(ActiveThingType, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/thing/types/%s" % self.id
        self._logicalInterfaces = ActiveLogicalInterfaces(
            apiClient, self.id
        )  # TBD need to provide access to active and draft.
        self._mappings = ActiveMappings(apiClient, self.id)
        self._things = Things(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseThingType

    @property
    def things(self):
        return self._things

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code in (200, 202):
            return r.json()
        else:
            raise ApiException(r)

    def deactivate(self):
        return self.__callPatchOperation__({"operation": "deactivate-configuration"})


class DraftIterableThingTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(DraftIterableThingTypeList, self).__init__(apiClient, DraftThingType, url, filters=filters)


class ActiveIterableThingTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(ActiveIterableThingTypeList, self).__init__(apiClient, ActiveThingType, url, filters=filters)


class DraftThingTypes(RestApiDict):
    def __init__(self, apiClient):
        super(DraftThingTypes, self).__init__(
            apiClient, DraftThingType, DraftIterableThingTypeList, "api/v0002/draft/thing/types"
        )


class ActiveThingTypes(RestApiDictReadOnly):
    def __init__(self, apiClient):
        super(ActiveThingTypes, self).__init__(
            apiClient, ActiveThingType, ActiveIterableThingTypeList, "api/v0002/thing/types"
        )


# =========================================================================
# Logical Interfaces for the Thing Type
# =========================================================================


class IterableLogicalInterfaceList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableLogicalInterfaceList, self).__init__(apiClient, BaseLogicalInterface, url)


class DraftLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, thingTypeId):
        url = "api/v0002/draft/thing/types/%s/logicalinterfaces" % thingTypeId
        super(DraftLogicalInterfaces, self).__init__(apiClient, BaseLogicalInterface, IterableLogicalInterfaceList, url)


class ActiveLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient, thingTypeId):
        url = "api/v0002/thing/types/%s/logicalinterfaces" % thingTypeId
        super(ActiveLogicalInterfaces, self).__init__(
            apiClient, BaseLogicalInterface, IterableLogicalInterfaceList, url
        )


# =========================================================================
# Mappings for the Thing Type
# =========================================================================

# define the common properties found on most Rest API Items
class ThingTypeMapping(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def logicalInterfaceId(self):
        return self["logicalInterfaceId"]

    @property
    def notificationStrategy(self):
        return self["notificationStrategy"]

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
        super(IterableMappingList, self).__init__(apiClient, ThingTypeMapping, url)


class DraftMappings(RestApiDict):
    def __init__(self, apiClient, thingTypeId):
        url = "api/v0002/draft/thing/types/%s/mappings" % thingTypeId
        super(DraftMappings, self).__init__(apiClient, ThingTypeMapping, IterableMappingList, url)


class ActiveMappings(RestApiDict):
    def __init__(self, apiClient, thingTypeId):
        url = "api/v0002/draft/thing/types/%s/mappings" % thingTypeId
        super(ActiveMappings, self).__init__(apiClient, ThingTypeMapping, IterableMappingList, url)
