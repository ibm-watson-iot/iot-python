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

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/historian-connector.html


class ForwardingRule(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def id(self):
        return self["id"]

    @property
    def name(self):
        return self["name"]

    @property
    def description(self):
        return self["description"]

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

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def updatedBy(self):
        return self["updatedBy"]

    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def createdBy(self):
        return self["createdBy"]

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


class IterableForwardingRuleList(IterableList):
    def __init__(self, apiClient, connectorId, filters=None):
        self.connectorId = connectorId
        # This API does not support sorting
        super(IterableForwardingRuleList, self).__init__(
            apiClient,
            ForwardingRule,
            "api/v0002/historianconnectors/%s/forwardingrules" % (connectorId),
            sort=None,
            filters=filters,
            passApiClient=False,
        )


class ForwardingRules(defaultdict):
    def __init__(self, apiClient, connectorId):
        self._apiClient = apiClient
        self.connectorId = connectorId

    def __contains__(self, key):
        url = "api/v0002/historianconnectors/%s/forwardingrules/%s" % (self.connectorId, key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        url = "api/v0002/historianconnectors/%s/forwardingrules/%s" % (self.connectorId, key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return ForwardingRule(**r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        raise Exception("Unable to register or update a forwarding rule via this interface at the moment.")

    def __delitem__(self, key):
        url = "api/v0002/historianconnectors/%s/forwardingrules/%s" % (self.connectorId, key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204:
            raise ApiException(r)

    def __missing__(self, key):
        raise KeyError("Forwarding Rule %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Forwarding Rules
        """
        return IterableForwardingRuleList(self._apiClient, self.connectorId)

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

        return IterableForwardingRuleList(self._apiClient, self.connectorId, filters=queryParms)

    def createEventRule(self, name, destinationName, description, enabled, typeId, eventId):
        rule = {
            "name": name,
            "destinationName": destinationName,
            "type": "event",
            "selector": {"eventId": eventId, "deviceType": typeId},
            "description": description,
            "enabled": enabled,
        }

        return self._create(rule)

    def createStateRule(self, name, destinationName, description, enabled, logicalInterfaceId):
        rule = {
            "name": name,
            "destinationName": destinationName,
            "type": "state",
            "selector": {"logicalInterfaceId": logicalInterfaceId},
            "description": description,
            "enabled": enabled,
        }

        return self._create(rule)

    def _create(self, rule):
        url = "api/v0002/historianconnectors/%s/forwardingrules" % (self.connectorId)

        r = self._apiClient.post(url, data=rule)
        if r.status_code == 201:
            return ForwardingRule(**r.json())
        else:
            raise ApiException(r)

    def update(self, ruleId, name, description, destinationName, selector, enabled):
        url = "api/v0002/historianconnectors/%s/forwardingrules/%s" % (self.connectorId, ruleId)

        body = {}
        body["name"] = name
        body["description"] = description
        body["destinationName"] = destinationName
        body["enabled"] = enabled
        body["selector"] = selector

        r = self._apiClient.put(url, data=body)
        if r.status_code == 200:
            return ForwardingRule(**r.json())
        else:
            raise ApiException(r)
