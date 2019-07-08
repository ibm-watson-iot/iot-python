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
from wiotp.sdk.api.state.rules import DraftRulesPerLI
from wiotp.sdk.api.state.rules import ActiveRulesPerLI

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/state-mgmt.html#/Logical Interfaces


class BaseLogicalInterface(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def alias(self):
        return self["alias"]

    @property
    def schemaId(self):
        return self["schemaId"]

    @property
    def version(self):
        return self["version"]

    @property
    def rules(self):
        return self._rules


class DraftLogicalInterface(BaseLogicalInterface):
    def __init__(self, apiClient, **kwargs):
        super(DraftLogicalInterface, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/draft/logicalinterfaces/%s" % self.id
        self._rules = DraftRulesPerLI(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseLogicalInterface

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 202:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))

    def activate(self):
        return self.__callPatchOperation__({"operation": "activate-configuration"})

    def validate(self):
        return self.__callPatchOperation__({"operation": "validate-configuration"})

    def differences(self):
        return self.__callPatchOperation__({"operation": "list-differences"})


class ActiveLogicalInterface(BaseLogicalInterface):
    def __init__(self, apiClient, **kwargs):
        super(ActiveLogicalInterface, self).__init__(apiClient, **kwargs)
        self._url = "api/v0002/logicalinterfaces/%s" % self.id
        self._rules = ActiveRulesPerLI(apiClient, self.id)

    # Note - data accessor functions for common data items are defined in BaseLogicalInterface

    def __callPatchOperation__(self, body):
        r = self._apiClient.patch(self._url, body)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 202:
            return r.json()
        else:
            raise Exception("Unexpected response from API (%s) = %s %s" % (self._url, r.status_code, r.text))

    def deactivate(self):
        return self.__callPatchOperation__({"operation": "deactivate-configuration"})


class IterableDraftLogicalInterfaceList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableDraftLogicalInterfaceList, self).__init__(apiClient, DraftLogicalInterface, url, filters=filters)


class DraftLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient):
        super(DraftLogicalInterfaces, self).__init__(
            apiClient, DraftLogicalInterface, IterableDraftLogicalInterfaceList, "api/v0002/draft/logicalinterfaces"
        )


class IterableActiveLogicalInterfaceList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableActiveLogicalInterfaceList, self).__init__(
            apiClient, ActiveLogicalInterface, url, filters=filters
        )


class ActiveLogicalInterfaces(RestApiDict):
    def __init__(self, apiClient):
        super(ActiveLogicalInterfaces, self).__init__(
            apiClient, ActiveLogicalInterface, IterableActiveLogicalInterfaceList, "api/v0002/logicalinterfaces"
        )
