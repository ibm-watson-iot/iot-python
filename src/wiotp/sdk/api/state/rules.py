# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import IterableSimpleList
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDictReadOnly

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/state-mgmt.html#/Rules


class Rule(RestApiItemBase):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def logicalInterfaceId(self):
        return self["logicalInterfaceId"]

    @property
    def condition(self):
        return self["condition"]

    @property
    def notificationStrategy(self):
        return self["notificationStrategy"]

    @property
    def version(self):
        return self["version"]


class IterableRuleList(IterableList):
    def __init__(self, apiClient, url, filters=None, passApiClient=False):
        # This API does not support sorting
        super(IterableRuleList, self).__init__(apiClient, Rule, url, filters=filters)


class DraftRules(RestApiDict):
    def __init__(self, apiClient):
        super(DraftRules, self).__init__(apiClient, Rule, IterableRuleList, "api/v0002/draft/rules")


class ActiveRules(RestApiDictReadOnly):
    def __init__(self, apiClient):
        super(ActiveRules, self).__init__(apiClient, Rule, IterableRuleList, "api/v0002/rules")


class IterableSimpleRuleList(IterableSimpleList):
    def __init__(self, apiClient, url, filters=None, passApiClient=False):
        # This API does not support sorting
        super(IterableSimpleRuleList, self).__init__(apiClient, Rule, url, filters=filters)


class DraftRulesPerLI(RestApiDict):
    def __init__(self, apiClient, logicalInterfaceId):
        url = "api/v0002/draft/logicalinterfaces/%s/rules" % logicalInterfaceId
        super(DraftRulesPerLI, self).__init__(apiClient, Rule, IterableSimpleRuleList, url)


class ActiveRulesPerLI(RestApiDictReadOnly):
    def __init__(self, apiClient, logicalInterfaceId):
        url = "api/v0002/logicalinterfaces/%s/rules" % logicalInterfaceId
        super(ActiveRulesPerLI, self).__init__(apiClient, Rule, IterableSimpleRuleList, url)
