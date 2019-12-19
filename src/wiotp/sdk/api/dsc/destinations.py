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
from wiotp.sdk.api.common import IterableList, RestApiDict

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

    # Cloudant only configuration
    @property
    def retentionDays(self):
        # this is an optional parameter so check if it exists
        if "configuration" in self and "retentionDays" in self["configuration"]:
            return self["configuration"]["retentionDays"]
        else:
            return None

    # DB2/Postgres only configuration
    @property
    def columns(self):
        # this is an optional parameter so check if it exists
        if "configuration" in self and "columns" in self["configuration"]:
            return self["configuration"]["columns"]
        else:
            return None


class IterableDestinationList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableDestinationList, self).__init__(
            apiClient, Destination, url, sort=None, filters=filters, passApiClient=False
        )


class Destinations(RestApiDict):
    def __init__(self, apiClient, connectorId, connectorType):
        super(Destinations, self).__init__(
            apiClient,
            Destination,
            IterableDestinationList,
            "api/v0002/historianconnectors/%s/destinations" % connectorId,
        )
        self.connectorId = connectorId
        self.connectorType = connectorType
        self.allDestinationsUrl = "api/v0002/historianconnectors/%s/destinations" % connectorId

    def find(self, nameFilter=None):
        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter

        return IterableDestinationList(self._apiClient, self.allDestinationsUrl, filters=queryParms)

    def create(self, name, **kwargs):
        if self.connectorType == "cloudant":
            if "bucketInterval" not in kwargs.keys():
                raise Exception("You must specify bucketInterval parameter on create for a Cloudant destination")
        if self.connectorType == "eventstreams":
            if "partitions" not in kwargs.keys():
                raise Exception("You must specify partitions parameter on create for an EventStreams destination")
        if self.connectorType == "db2" or self.connectorType == "postgres":
            if "columns" not in kwargs.keys():
                raise Exception("You must specify a columns parameter on create for a DB2 or Postgres destination")

        destination = {"name": name, "type": self.connectorType, "configuration": kwargs}

        r = self._apiClient.post(self.allDestinationsUrl, data=destination)
        if r.status_code == 201:
            return Destination(**r.json())
        else:
            raise ApiException(r)

    def update(self, key, item):
        """
        Create an Item - not supported for CTIVE item
        """
        raise Exception("The API doesn't support updating a destination.")
