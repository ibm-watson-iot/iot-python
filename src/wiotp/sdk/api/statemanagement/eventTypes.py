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

from wiotp.sdk.api.Schemamanager.triggers import Triggers
from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.common import IterableList

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/Schema-mgr-beta.html


class Schema(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

        self.triggers=Triggers(
             apiClient=self._apiClient, 
             SchemaId=kwargs["id"]
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
    def SchemaType(self):
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

class IterableSchemaList(IterableList):
    def __init__(self, apiClient, filters=None):
        # This API does not support sorting
        super(IterableSchemaList, self).__init__(
            apiClient, Schema, "api/v0002/Schemas", sort=None, filters=filters, passApiClient=True
        )


class Schemas(defaultdict):

    allSchemasUrl = "api/v0002/Schemas"
    oneSchemaUrl = "api/v0002/Schemas/%s"

    def __init__(self, apiClient):
        self._apiClient = apiClient
        
    def __contains__(self, key):
        """
        Does an Schema exist?
        """
        url = Schemas.oneSchemaUrl % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        """
        Retrieve the Schema with the specified id.
        Parameters:
            - SchemaId (String), Schema Id which is a UUID
        Throws APIException on failure.

        """

        url = Schemas.oneSchemaUrl % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return Schema(apiClient=self._apiClient, **r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        """
        Register a new Schema - not currently supported via this interface, use: `Schemamanager.Schemas.create()`
        """
        raise Exception("Unable to register or update a Schema via this interface at the moment.")

    def __delitem__(self, key):
        """
        Delete an Schema
        """
        url = Schemas.oneSchemaUrl % (key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204:
            raise ApiException(r)

    def __missing__(self, key):
        """
        Schema does not exist
        """
        raise KeyError("Schema %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Schemas
        """
        return IterableSchemaList(self._apiClient)

    def find(self, nameFilter=None, typeFilter=None, enabledFilter=None, triggerLIId=None, triggerRuleId=None, triggerTypeId=None, triggerInstanceId=None):
        """
        Gets the list of Schemas, they are used to call specific business logic when data in Watson IoT Platform changes.
        
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

        return IterableSchemaList(self._apiClient, filters=queryParms)

    def create(self, name, type, description, configuration, enabled):
        """
        Create an Schema for the organization in the Watson IoT Platform. 
        The Schema must reference the target service that the Watson IoT Platform will store the IoT data in.
        Parameters:
            - name (string) - Name of the service
            - type - must be webhook
            - description (string) - description of the service
            - configuration - specifies the JSON Schema configuration required
            - enabled (boolean) - enabled
        Throws APIException on failure
        """

        Schema = {
            "name": name,
            "type": type,
            "description": description,
            "configuration": configuration,
            "enabled": enabled,
        }

        r = self._apiClient.post(Schemas.allSchemasUrl, data=Schema)
        if r.status_code == 201:
            return Schema(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def update(self, SchemaId, name, description, configuration, enabled):
        """
        Updates the Schema with the specified SchemaId.
        if description is empty, the existing description will be removed.
        Parameters:
            - SchemaId (String), Schema Id which is a UUID
            - name (string) - Name of the Schema
            - description (string) - description of the Schema
            - configuration (json object) - Describes the Schema configuration.
            - enabled (boolean) - enabled
        Throws APIException on failure.

        """

        url = Schemas.oneSchemaUrl % (SchemaId)

        SchemaBody = {}
        SchemaBody["name"] = name
        SchemaBody["description"] = description
        SchemaBody["configuration"] = configuration
        SchemaBody["enabled"] = enabled

        r = self._apiClient.put(url, data=SchemaBody)
        if r.status_code == 200:
            return Schema(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)
