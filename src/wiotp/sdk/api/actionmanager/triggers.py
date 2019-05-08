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
from wiotp.sdk.api.common import  RestApiDict

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
        # This API does not support sorting
        super(IterableTriggerList, actionId, self).__init__(
            apiClient,
            Trigger,
            "api/v0002/actions/%s/triggers" % (actionId),
            sort=None,
            filters=filters,
            passApiClient=False,
        )


class Triggers(RestApiDict):

    def __init__(self, apiClient, actionId):
        super(Triggers, self).__init__(
            apiClient, Trigger, IterableTriggerList(apiClient, actionId), "api/v0002/actions/%s/triggers" % actionId
        )

    def create(self, name, type, description, configuration, variable_mappings, enabled):
        trigger = {
            "name": name, 
            "type": type,
            "description": description,
            "configuration": configuration,
            "variableMappings": variable_mappings,
            "enabled": enabled,
        }
        
        return super(Triggers, self).create(trigger)
