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
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDictReadOnly

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/EventType-mgr-beta.html


class EventType(RestApiItemBase):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def schemaId(self):
        return self["schemaId"]

    @property
    def version(self):
        return self["version"]


class IterableEventTypeList(IterableList):
    def __init__(self, apiClient, url, filters=None, passApiClient=False):
        # This API does not support sorting
        super(IterableEventTypeList, self).__init__(apiClient, EventType, url, filters=filters)


class ActiveEventTypes(RestApiDictReadOnly):
    def __init__(self, apiClient):
        super(ActiveEventTypes, self).__init__(apiClient, EventType, IterableEventTypeList, "api/v0002/event/types")


class DraftEventTypes(RestApiDict):
    def __init__(self, apiClient):
        super(DraftEventTypes, self).__init__(
            apiClient, EventType, IterableEventTypeList, "api/v0002/draft/event/types"
        )
