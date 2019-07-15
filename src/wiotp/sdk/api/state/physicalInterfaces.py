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

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/state-mgmt.html#/Physical Interfaces


class PhysicalInterface(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

        # setup access to the event mappings, a separate REST API call.
        if self.version == "draft":
            self._events = DraftEventMappings(apiClient=self._apiClient, physicalInterfaceId=kwargs["id"])
        elif self.version == "active":
            self._events = ActiveEventMappings(apiClient=self._apiClient, physicalInterfaceId=kwargs["id"])

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def version(self):
        return self["version"]

    @property
    def events(self):
        return self._events


class IterablePhysicalInterfaceList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterablePhysicalInterfaceList, self).__init__(apiClient, PhysicalInterface, url, filters=filters)


class DraftPhysicalInterfaces(RestApiDict):
    def __init__(self, apiClient):
        super(DraftPhysicalInterfaces, self).__init__(
            apiClient, PhysicalInterface, IterablePhysicalInterfaceList, "api/v0002/draft/physicalinterfaces"
        )


class ActivePhysicalInterfaces(RestApiDict):
    def __init__(self, apiClient):
        super(ActivePhysicalInterfaces, self).__init__(
            apiClient, PhysicalInterface, IterablePhysicalInterfaceList, "api/v0002/physicalinterfaces"
        )


# =========================================================================
# Event Mappings for the Physical Interfaces
# =========================================================================


class EventMapping(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def eventId(self):
        return self["eventId"]

    @property
    def eventTypeId(self):
        return self["eventTypeId"]


class IterableEventMappingList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None, passApiClient=False):
        # This API does not support sorting
        super(IterableEventMappingList, self).__init__(apiClient, EventMapping, url)


class DraftEventMappings(RestApiDict):
    def __init__(self, apiClient, physicalInterfaceId):
        url = "api/v0002/draft/physicalinterfaces/%s/events" % physicalInterfaceId
        super(DraftEventMappings, self).__init__(apiClient, EventMapping, IterableEventMappingList, url)


class ActiveEventMappings(RestApiDict):
    def __init__(self, apiClient, physicalInterfaceId):
        url = "api/v0002/physicalinterfaces/%s/events" % physicalInterfaceId
        super(ActiveEventMappings, self).__init__(apiClient, EventMapping, IterableEventMappingList, url)
