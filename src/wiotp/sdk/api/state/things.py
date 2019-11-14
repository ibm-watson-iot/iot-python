# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.state.thingState import ThingStates


class Thing(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        super(Thing, self).__init__(apiClient, **kwargs)
        self._states = ThingStates(apiClient, self.thingTypeId, self.thingId)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def thingTypeId(self):
        return self["thingTypeId"]

    @property
    def thingId(self):
        return self["thingId"]

    @property
    def description(self):
        if "description" in self:
            return self["description"]
        else:
            return None

    @property
    def aggregatedObjects(self):
        return self["aggregatedObjects"]

    @property
    def metadata(self):
        if "metadata" in self:
            return self["metadata"]
        else:
            return None

    @property
    def states(self):
        return self._states


class IterableThingList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableThingList, self).__init__(apiClient, Thing, url, filters=filters)


class Things(RestApiDict):
    def __init__(self, apiClient, thingTypeId):
        url = "api/v0002/thing/types/%s/things" % thingTypeId
        super(Things, self).__init__(apiClient, Thing, IterableThingList, url)
