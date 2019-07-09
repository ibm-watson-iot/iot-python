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

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/action-mgr-beta.html


class Trigger(RestApiItemBase):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def triggerType(self):
        return self["type"]

    @property
    def enabled(self):
        return self["enabled"]

    @property
    def configuration(self):
        return self["configuration"]

    @property
    def variableMappings(self):
        return self["variableMappings"]


class IterableTriggerList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableTriggerList, self).__init__(apiClient, Trigger, url, filters=filters, passApiClient=False)


class Triggers(RestApiDict):
    def __init__(self, apiClient, actionId):
        url = "api/v0002/actions/%s/triggers" % actionId
        super(Triggers, self).__init__(apiClient, Trigger, IterableTriggerList, url, passApiClient=False)
