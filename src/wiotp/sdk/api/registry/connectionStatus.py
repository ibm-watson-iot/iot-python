# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.exceptions import ApiException


class ClientStatus(defaultdict):
    def __init__(self, **kwargs):
        # if not set(["message", "timestamp"]).issubset(kwargs):
        #    raise Exception("message and timestamp are required properties for a LogEntry")

        # kwargs["timestamp"] = iso8601.parse_date(kwargs["timestamp"])
        dict.__init__(self, **kwargs)


#    @property
#    def message(self):
#        return self["message"]

#    @property
#    def timestamp(self):
#        return self["timestamp"]


class IterableClientStatusList(IterableList):
    def __init__(self, apiClient, filters=None):
        super(IterableClientStatusList, self).__init__(
            apiClient, ClientStatus, "api/v0002/clientconnectionstates", sort=None, filters=filters, passApiClient=False
        )


class ConnectionStatus(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

    def __contains__(self, key):
        url = "api/v0002/clientconnectionstates/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        url = "api/v0002/clientconnectionstates/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return ClientStatus(**r.json())
        if r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all Connectors
        """
        return IterableClientStatusList(self._apiClient, filters=None)

    def __missing__(self, key):
        """
        Device does not exist
        """
        raise KeyError("No status available for client %s" % (key))

    def __setitem__(self, key, value):
        raise Exception("Unsupported operation")

    def __delitem__(self, key):
        raise Exception("Unsupported operation")

    def find(self, typeId=None, deviceId=None, connectionStatus=None, connectedAfter=None):
        """
        Iterate through all Connectors
        """
        queryParms = {}
        if typeId:
            queryParms["deviceType"] = typeId
        if deviceId:
            queryParms["deviceId"] = deviceId
        if connectionStatus:
            queryParms["connectionStatus"] = connectionStatus
        if connectedAfter:
            queryParms["connectedAfter"] = connectedAfter

        return IterableClientStatusList(self._apiClient, filters=queryParms)
