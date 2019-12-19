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
from wiotp.sdk.api.common import IterableList, RestApiDict, RestApiItemBase

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/historian-connector.html


class ForwardingRule(RestApiItemBase):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def destinationName(self):
        return self["destinationName"]

    @property
    def ruleType(self):
        # Can be "event" or "state"
        return self["type"]

    @property
    def selector(self):
        return self["selector"]

    @property
    def enabled(self):
        return self["enabled"]

    # Event only configuration
    # I can't beleieve the API doesn't use the typeId naming convention consistent with everything else in the platform!
    # This client will mask that inconsistency for the sake of my sanity, if not the users.
    @property
    def typeId(self):
        if self["type"] == "event":
            return self["selector"]["deviceType"]
        else:
            return None

    @property
    def eventId(self):
        if self["type"] == "event":
            return self["selector"]["eventId"]
        else:
            return None

    # State only configuration
    @property
    def logicalInterfaceId(self):
        if self["type"] == "state":
            return self["selector"]["logicalInterfaceId"]
        else:
            return None

    # DB2/Postgres column mapping configuration
    @property
    def columnMappings(self):
        # this is an optional parameter so check if it exists
        if "configuration" in self and "columnMappings" in self["configuration"]:
            return self["configuration"]["columnMappings"]
        else:
            return None


class IterableForwardingRuleList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableForwardingRuleList, self).__init__(
            apiClient, ForwardingRule, url, sort=None, filters=filters, passApiClient=False
        )


class ForwardingRules(RestApiDict):
    def __init__(self, apiClient, connectorId):
        self.connectorId = connectorId
        self.allRulesUrl = "api/v0002/historianconnectors/%s/forwardingrules" % connectorId
        super(ForwardingRules, self).__init__(apiClient, ForwardingRule, IterableForwardingRuleList, self.allRulesUrl)

    def find(self, nameFilter=None, typeFilter=None, enabledFilter=None, destinationNameFilter=None):
        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter
        if typeFilter:
            queryParms["type"] = typeFilter
        if destinationNameFilter:
            queryParms["destinationName"] = destinationNameFilter
        if enabledFilter:
            queryParms["enabled"] = enabledFilter

        return IterableForwardingRuleList(self._apiClient, self.allRulesUrl, filters=queryParms)

    def createEventRule(self, name, destinationName, typeId, eventId, description=None, enabled=None):
        rule = {
            "name": name,
            "destinationName": destinationName,
            "type": "event",
            "selector": {"eventId": eventId, "deviceType": typeId},
        }
        if description != None:
            rule["description"] = description
        if enabled != None:
            rule["enabled"] = enabled

        return self._create(rule)

    def createStateRule(
        self, name, destinationName, logicalInterfaceId, description=None, enabled=None, configuration=None
    ):
        rule = {
            "name": name,
            "destinationName": destinationName,
            "type": "state",
            "selector": {"logicalInterfaceId": logicalInterfaceId},
        }
        if description != None:
            rule["description"] = description
        if enabled != None:
            rule["enabled"] = enabled
        if configuration != None:
            rule["configuration"] = configuration

        return self._create(rule)

    def _create(self, rule):
        url = "api/v0002/historianconnectors/%s/forwardingrules" % (self.connectorId)

        r = self._apiClient.post(url, data=rule)
        if r.status_code == 201:
            return ForwardingRule(**r.json())
        else:
            raise ApiException(r)

    def update(
        self, ruleId, ruleType, name, destinationName, selector, description=None, enabled=None, configuration=None
    ):
        url = "api/v0002/historianconnectors/%s/forwardingrules/%s" % (self.connectorId, ruleId)

        body = {}
        body["id"] = ruleId
        body["name"] = name
        body["type"] = ruleType
        body["destinationName"] = destinationName
        body["selector"] = selector
        if description != None:
            body["description"] = description
        if enabled != None:
            body["enabled"] = enabled
        if configuration != None:
            body["configuration"] = configuration

        r = self._apiClient.put(url, data=body)
        if r.status_code == 200:
            return ForwardingRule(**r.json())
        else:
            raise ApiException(r)
