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

from wiotp.sdk.api.actionmanager.triggers import Triggers
from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import  RestApiDict

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/action-mgr-beta.html

class Action(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

        self.triggers=Triggers(
             apiClient=self._apiClient, 
             actionId=kwargs["id"]
        ) 
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
    def actionType(self):
        return self["type"]

    @property
    def enabled(self):
        return self["enabled"]

    # TBD Configuration subcomponents?
    
    @property
    def configuration(self):
        return self["configuration"]
    
    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def createdBy(self):
        return self["createdBy"]

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def updatedBy(self):
        return self["updatedBy"]

class IterableActionList(IterableList):
    def __init__(self, apiClient, filters=None):
        # This API does not support sorting
        super(IterableActionList, self).__init__(
            apiClient, Action, "api/v0002/actions", sort=None, filters=filters, passApiClient=True
        )


class Actions(RestApiDict):

    def __init__(self, apiClient):
        super(Actions, self).__init__(
            apiClient, Action, IterableActionList, "api/v0002/actions"
        )

    def find(self, nameFilter=None, typeFilter=None, enabledFilter=None, triggerLIId=None, triggerRuleId=None, triggerTypeId=None, triggerInstanceId=None):
        """
        Gets the list of Actions, they are used to call specific business logic when data in Watson IoT Platform changes.
        
        Parameters:
        
            - name(string) -              Filter the results by the specified name
            - type(string) -              Filter the results by the specified type, Available values : webhook
            - triggerLIId(string) -       Filter the results by the logical interface id defined in a trigger sub-resource
            - triggerRuleId(string) -     Filter the results by the service id
            - triggerTypeId(string) -     Filter the results by the type id defined in a trigger sub-resource
            - triggerInstanceId(string) - Filter the results by the instance id defined in a trigger sub-resource
            - enabled(boolean) -          Filter the results by the enabled flag 
            - limit(number) -             Max number of results returned, defaults 25
            - bookmark(string) -          used for paging through results
        
        Throws APIException on failure.
        """

        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter
        if typeFilter:
            queryParms["type"] = typeFilter
        if enabledFilter:
            queryParms["enabled"] = enabledFilter
        if triggerLIId:
            queryParms["triggerLIId"] = triggerLIId
        if triggerRuleId:
            queryParms["triggerRuleId"] = triggerRuleId
        if triggerTypeId:
            queryParms["triggerTypeId"] = triggerTypeId
        if triggerInstanceId:
            queryParms["triggerInstanceId"] = triggerInstanceId

        # print ("finding actions, queryParams: %s" % queryParms)
        return super(Actions, self).find(queryParms)

    def create(self, name, type, description, configuration, enabled):
        """
        Create an action for the organization in the Watson IoT Platform. 
        The action must reference the target service that the Watson IoT Platform will store the IoT data in.
        Parameters:
            - name (string) - Name of the service
            - type - must be webhook
            - description (string) - description of the service
            - configuration - specifies the JSON action configuration required
            - enabled (boolean) - enabled
        Throws APIException on failure
        """

        action = {
            "name": name,
            "type": type,
            "description": description,
            "configuration": configuration,
            "enabled": enabled,
        }

        return super(Actions, self).create(action)


    def update(self, actionId, name, type, description, configuration, enabled):
        """
        Updates the action with the specified actionId.
        if description is empty, the existing description will be removed.
        Parameters:
            - actionId (String), Action Id which is a UUID
            - name (string) - Name of the action
            - description (string) - description of the action
            - configuration (json object) - Describes the action configuration.
            - enabled (boolean) - enabled
        Throws APIException on failure.

        """

        action = {
            "id" : actionId,
            "name": name,
            "type": type,
            "description": description,
            "configuration": configuration,
            "enabled": enabled,
        }
        
        return super(Actions, self).update(actionId, action)
