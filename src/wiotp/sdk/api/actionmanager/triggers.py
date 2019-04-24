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

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/action-mgr-beta.html


class Trigger(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def name(self):
        # Unlike most other resources name == the UUID, there is no seperate id property
        return self["name"]

    @property
    def triggerType(self):
        return self["type"]

    @property
    def enabled(self):
        return self["enabled"]
    
    @property
    def configurationLiId(self):
        return self["configuration"]["logicalInterfaceId"]

    @property
    def configurationRuleId(self):
        return self["configuration"]["ruleId"]
    
    @property
    def configurationTypeId(self):
        return self["configuration"]["typeId"]
    
    # TBD Should I model Configuration and variable mapping subcomponents?
        
    @property
    def configuration(self):
        return self["configuration"]["instanceId"]
    
    @property
    def variableMappings(self):
        return self["variableMappings"]

class IterableTriggerList(IterableList):
    def __init__(self, apiClient, actionId, filters=None):
        self.actionId = actionId
        # This API does not support sorting
        super(IterableTriggerList, self).__init__(
            apiClient,
            Trigger,
            "api/v0002/actions/%s/triggers" % (actionId),
            sort=None,
            filters=filters,
            passApiClient=False,
        )


class Triggers(defaultdict):
    
    allTriggersUrl = "api/v0002/actions/%s/triggers"
    oneTriggerUrl = "api/v0002/actions/%s/triggers/%s"

    def __init__(self, apiClient, actionId, triggerType):
        self._apiClient = apiClient
        self.actionId = actionId

    def __contains__(self, key):
        url = self.oneTriggerUrl % (self.actionId, key)

        r = Triggers._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        url = Triggers.oneTriggerUrl % (self.actionId, key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return Trigger(**r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        raise Exception("Unable to register or update a trigger via this interface at the moment.")

    def __delitem__(self, key):
        url = Triggers.oneTriggerUrl % (self.actionId, key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 200:
            # Unlike most DELETE requests, this API is expected to return 200 with a message body containing the message:
            # "Successfully deleted Cloudant configuration, the Cloudant database must be manually deleted"
            raise ApiException(r)

    def __missing__(self, key):
        raise KeyError("Trigger %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Triggers
        """
        return IterableTriggerList(self._apiClient, self.actionId)

    def find(self, nameFilter=None):
        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter

        return IterableTriggerList(self._apiClient, self.actionId, filters=queryParms)

    def create(self, name, type, description, configuration, variable_mappings, enabled):
        trigger = {
            "name": name, 
            "type": type,
            "description": description,
            "configuration": configuration,
            "vafriableMappings": variable_mappings,
            "enabled": enabled,
        }
        
        url = Triggers.allTriggersUrl % (self.actionId)

        r = self._apiClient.post(url, data=trigger)
        if r.status_code == 201:
            return Trigger(**r.json())
        else:
            raise ApiException(r)
