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

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/State-mgr-beta.html


class ThingState(defaultdict):
    def __init__(self, apiClient, url, **kwargs):
        self._apiClient = apiClient
        self._url = url
        dict.__init__(self, **kwargs)

    @property
    def state(self):
        return self["state"]

    @property
    def timestamp(self):
        return iso8601.parse_date(self["timestamp"])

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))

    def reset(self):
        return self.__callPatchOperation__({"operation": "reset-state"})


class ThingStates(RestApiDictReadOnly):
    def __init__(self, apiClient, thingTypeId, thingId):
        url = "api/v0002/thing/types/%s/things/%s/state" % (thingTypeId, thingId)
        super(ThingStates, self).__init__(apiClient, ThingState, None, url)

    def __getitem__(self, key):
        url = self._singleItemUrl % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return self._castToClass(apiClient=self._apiClient, url=url, **r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    # override the standard iterator as there is no api to get all state itetrating over LIs
    def __iter__(self, *args, **kwargs):
        raise Exception("Unable to iterate through thing state. Retrieve it for a specific LI.")

    def find(self, query_params={}):
        raise Exception("Unable to find thing state. Retrieve it for a specific LI.")
