# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.exceptions import ApiException


class MgmtRequests:
    # Device Management URLs
    mgmtRequests = "api/v0002/mgmt/requests"
    mgmtSingleRequest = "api/v0002/mgmt/requests/%s"
    mgmtRequestStatus = "api/v0002/mgmt/requests/%s/deviceStatus"
    mgmtRequestSingleDeviceStatus = "api/v0002/mgmt/requests/%s/deviceStatus/%s/%s"

    def __init__(self, apiClient):
        """
        Device Management API
        - Get all requests
        - Initiate new request
        - Delete request
        - Get request
        - Get request status
        - Get request status for specific device
        """
        self._apiClient = apiClient

    def list(self):
        """
        Gets a list of device management requests, which can be in progress or recently completed.
        In case of failure it throws APIException
        """
        url = MgmtRequests.mgmtRequests
        r = self._apiClient.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)

    def initiate(self, request):
        """
        Initiates a device management request, such as reboot.
        In case of failure it throws APIException
        """
        url = MgmtRequests.mgmtRequests
        r = self._apiClient.post(url, request)

        if r.status_code == 202:
            return r.json()
        else:
            raise ApiException(r)

    def delete(self, requestId):
        """
        Clears the status of a device management request.
        You can use this operation to clear the status for a completed request, or for an in-progress request which may never complete due to a problem.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        url = MgmtRequests.mgmtSingleRequest % (requestId)
        r = self._apiClient.delete(url)

        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)

    def get(self, requestId):
        """
        Gets details of a device management request.
        It accepts requestId (string) as parameters
        In case of failure it throws APIException
        """
        url = MgmtRequests.mgmtSingleRequest % (requestId)
        r = self._apiClient.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)

    def getStatus(self, requestId, typeId=None, deviceId=None):
        """
        Get a list of device management request device statuses.
        Get an individual device mangaement request device status.
        """
        if typeId is None or deviceId is None:
            url = MgmtRequests.mgmtRequestStatus % (requestId)
            r = self._apiClient.get(url)

            if r.status_code == 200:
                return r.json()
            else:
                raise ApiException(r)
        else:
            url = MgmtRequests.mgmtRequestSingleDeviceStatus % (requestId, typeId, deviceId)
            r = self._apiClient.get(url)

            if r.status_code == 200:
                return r.json()
            else:
                raise ApiException(r)
