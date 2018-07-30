# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from ibmiotf.api.common import ApiClient, ApiException


class Status():

    def __init__(self, apiClient):
        self._apiClient = apiClient
        
    
    def serviceStatus(self):
        """
        Retrieve the organization-specific status of each of the services offered by the IBM Watson IoT Platform.
        In case of failure it throws APIException
        """
        
        r = self._apiClient.get('api/v0002/service-status')

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)
