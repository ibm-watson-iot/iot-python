# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import iso8601

from wiotp.sdk.api.actions.triggers import Triggers
from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiItemBase

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/action-mgr-beta.html


class Action(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):

        self._apiClient = apiClient

        self.triggers = Triggers(apiClient=self._apiClient, actionId=kwargs["id"])
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def actionType(self):
        return self["type"]

    @property
    def enabled(self):
        return self["enabled"]

    @property
    def configuration(self):
        return self["configuration"]


class IterableActionList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableActionList, self).__init__(apiClient, Action, url, filters=filters)


class Actions(RestApiDict):
    def __init__(self, apiClient):
        super(Actions, self).__init__(apiClient, Action, IterableActionList, "api/v0002/actions")
