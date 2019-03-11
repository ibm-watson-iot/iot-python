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


class Destination(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def name(self):
        # Unlike most other resources name == the UUID, there is no seperate id property
        return self["name"]

    @property
    def destinationType(self):
        return self["type"]

    @property
    def configuration(self):
        return self["configuration"]

    # EventStreams only configuration
    @property
    def partitions(self):
        if self["type"] == "eventstreams":
            return self["configuration"]["partitions"]
        else:
            return None

    # Cloudant only configuration
    @property
    def bucketInterval(self):
        if self["type"] == "cloudant":
            return self["configuration"]["bucketInterval"]
        else:
            return None


class IterableDestinationList(IterableList):
    def __init__(self, apiClient, connectorId, filters=None):
        self.connectorId = connectorId
        # This API does not support sorting
        super(IterableDestinationList, self).__init__(
            apiClient,
            Destination,
            "api/v0002/historianconnectors/%s/destinations" % (connectorId),
            sort=None,
            filters=filters,
            passApiClient=False,
        )


class Destinations(defaultdict):
    def __init__(self, apiClient, connectorId, connectorType):
        self._apiClient = apiClient
        self.connectorId = connectorId
        self.connectorType = connectorType

    def __contains__(self, key):
        url = "api/v0002/historianconnectors/%s/destinations/%s" % (self.connectorId, key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        url = "api/v0002/historianconnectors/%s/destinations/%s" % (self.connectorId, key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return Destination(**r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        raise Exception("Unable to register or update a destination via this interface at the moment.")

    def __delitem__(self, key):
        url = "api/v0002/historianconnectors/%s/destinations/%s" % (self.connectorId, key)

        r = self._apiClient.delete(url)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 200:
            # Unlike most DELETE requests, this API is expected to return 200 with a message body containing the message:
            # "Successfully deleted Cloudant configuration, the Cloudant database must be manually deleted"
            raise ApiException(r)

    def __missing__(self, key):
        raise KeyError("Destination %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Destinations
        """
        return IterableDestinationList(self._apiClient, self.connectorId)

    def find(self, nameFilter=None):
        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter

        return IterableDestinationList(self._apiClient, self.connectorId, filters=queryParms)

    def create(self, name, **kwargs):
        if self.connectorType == "cloudant":
            if ["bucketInterval"] != kwargs.keys():
                raise Exception("You must specify bucketInterval parameter on create for a Cloudant destination")
        if self.connectorType == "eventstreams":
            if ["partitions"] != kwargs.keys():
                raise Exception("You must specify partitions parameter on create for an EventStreams destination")

        destination = {"name": name, "type": self.connectorType, "configuration": kwargs}

        url = "api/v0002/historianconnectors/%s/destinations" % (self.connectorId)

        r = self._apiClient.post(url, data=destination)
        if r.status_code == 201:
            return Destination(**r.json())
        else:
            raise ApiException(r)
