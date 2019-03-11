# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json
from collections import defaultdict

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.registry.devices import Devices, DeviceInfo
from wiotp.sdk.exceptions import ApiException
      
class ClientConnectivityStatus(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient
    
    def getClientConnectionStates(self):
        """
        get the connection states for all clients, max 25 at once
        """
        url = 'api/v0002/clientconnectionstates'

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)
        
    def getConnectedClientConnectionStates(self):
        """
        get the connection states for all connected clients, max 25 at once
        """
        url = 'api/v0002/clientconnectionstates?connectionStatus=connected'

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)
    
    def getClientConnectionState(self, id):
        """
        get the connection states for a single client
        """
        url = 'api/v0002/clientconnectionstates/%s' % (id)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return r.json()
        else:
            raise ApiException(r)
        
    def getRecentClientConnectionStates(self, iso8601Date):
        """
        get the connection states for clients that connected since previous date
        """
        url = 'api/v0002/clientconnectionstates?connectedAfter=%s' % (iso8601Date)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)