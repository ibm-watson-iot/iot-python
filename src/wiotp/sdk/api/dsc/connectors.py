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

from wiotp.sdk.api.dsc.destinations import Destinations
from wiotp.sdk.api.dsc.forwarding import ForwardingRules
from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.common import IterableList

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/historian-connector.html


class Connector(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

        self.destinations = Destinations(
            apiClient=self._apiClient, connectorId=kwargs["id"], connectorType=kwargs["type"]
        )
        self.rules = ForwardingRules(apiClient=self._apiClient, connectorId=kwargs["id"])
        dict.__init__(self, **kwargs)

    @property
    def created(self):
        return iso8601.parse_date(self["created"])

    @property
    def description(self):
        return self["description"]

    @property
    def serviceId(self):
        return self["serviceId"]

    @property
    def connectorType(self):
        return self["type"]

    @property
    def configuration(self):
        if "configuration" in self:
            return self["configuration"]
        else:
            return None

    @property
    def updated(self):
        return iso8601.parse_date(self["updated"])

    @property
    def name(self):
        return self["name"]

    @property
    def adminDisabled(self):
        return self["adminDisabled"]

    @property
    def enabled(self):
        return self["enabled"]

    @property
    def updatedBy(self):
        return self["updatedBy"]

    @property
    def createdBy(self):
        return self["createdBy"]

    @property
    def id(self):
        return self["id"]

    @property
    def timezone(self):
        return self["timezone"]


class IterableConnectorList(IterableList):
    def __init__(self, apiClient, filters=None):
        # This API does not support sorting
        super(IterableConnectorList, self).__init__(
            apiClient, Connector, "api/v0002/historianconnectors", sort=None, filters=filters, passApiClient=True
        )


class Connectors(defaultdict):

    allHistorianConnectorsUrl = "api/v0002/historianconnectors"
    oneHistorianConnectorUrl = "api/v0002/historianconnectors/%s"

    def __init__(self, apiClient):
        self._apiClient = apiClient

    def __contains__(self, key):
        """
        Does a connector exist?
        """
        url = "api/v0002/historianconnectors/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        """
        Retrieve the connector with the specified id.
        Parameters:
            - connectorId (String), Connector Id which is a UUID
        Throws APIException on failure.

        """

        url = "api/v0002/historianconnectors/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return Connector(apiClient=self._apiClient, **r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        """
        Register a new device - not currently supported via this interface, use: `registry.devices.create()`
        """
        raise Exception("Unable to register or update a connector via this interface at the moment.")

    def __delitem__(self, key):
        """
        Delete a connector
        """
        url = "api/v0002/historianconnectors/%s" % (key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204:
            raise ApiException(r)

    def __missing__(self, key):
        """
        Device does not exist
        """
        raise KeyError("Connector %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Connectors
        """
        return IterableConnectorList(self._apiClient)

    def find(self, nameFilter=None, typeFilter=None, enabledFilter=None, serviceId=None):
        """
        Gets the list of Historian connectors, they are used to configure the Watson IoT Platform to store IoT data in compatible services.
        
        Parameters:
        
            - nameFilter(string) -      Filter the results by the specified name
            - typeFilter(string) -      Filter the results by the specified type, Available values : cloudant, eventstreams
            - enabledFilter(boolean) -  Filter the results by the enabled flag 
            - serviceId(string) -       Filter the results by the service id
            - limit(number) -           Max number of results returned, defaults 25
            - bookmark(string) -        used for paging through results
        
        Throws APIException on failure.
        """

        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter
        if typeFilter:
            queryParms["type"] = typeFilter
        if enabledFilter:
            queryParms["enabled"] = enabledFilter
        if serviceId:
            queryParms["serviceId"] = serviceId

        return IterableConnectorList(self._apiClient, filters=queryParms)

    def create(self, name, type, serviceId, timezone, description, enabled, configuration=None):
        """
        Create a connector for the organization in the Watson IoT Platform. 
        The connector must reference the target service that the Watson IoT Platform will store the IoT data in.
        Parameters:
            - name (string) - Name of the service
            - serviceId (string) - must be either eventstreams or cloudant
            - timezone (string) - 
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure
        """

        connector = {
            "name": name,
            "type": type,
            "description": description,
            "serviceId": serviceId,
            "timezone": timezone,
            "enabled": enabled,
        }

        url = "api/v0002/historianconnectors"

        r = self._apiClient.post(url, data=connector)
        if r.status_code == 201:
            return Connector(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def update(self, connectorId, name, description, timezone, enabled, configuration=None):
        """
        Updates the connector with the specified uuid.
        if description is empty, the existing description will be removed.
        Parameters:
            - connector (String), Connnector Id which is a UUID
            - name (string) - Name of the service
            - timezone (json object) - Should have a valid structure for the service type.
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure.

        """

        url = "api/v0002/historianconnectors/%s" % (connectorId)

        connectorBody = {}
        connectorBody["name"] = name
        connectorBody["description"] = description
        connectorBody["timezone"] = timezone
        connectorBody["enabled"] = enabled
        if configuration != None:
            connectorBody["configuration"] = configuration

        r = self._apiClient.put(url, data=connectorBody)
        if r.status_code == 200:
            return Connector(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)
