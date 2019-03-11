# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.exceptions import ApiException


class MgmtExtensions:
    def __init__(self, apiClient):
        """
        Device Management Extension API
        - List all device management extension packages
        - Create a new device management extension package
        - Delete a device management extension package
        - Get a specific device management extension package
        - Update a device management extension package
        """
        self._apiClient = apiClient

    def list(self):
        """
        List all device management extension packages
        """
        url = "api/v0002/mgmt/custom/bundle"
        r = self._apiClient.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)

    def create(self, dmeData):
        """
        Create a new device management extension package
        In case of failure it throws APIException
        """
        url = "api/v0002/mgmt/custom/bundle"
        r = self._apiClient.post(url, dmeData)

        if r.status_code == 201:
            return r.json()
        else:
            raise ApiException(r)

    def delete(self, bundleId):
        """
        Delete a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        url = "api/v0002/mgmt/custom/bundle/%s" % (bundleId)
        r = self._apiClient.delete(url)

        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)

    def get(self, bundleId):
        """
        Get a specific device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        url = "api/v0002/mgmt/custom/bundle/%s" % (bundleId)
        r = self._apiClient.get(url)

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)

    def update(self, bundleId, dmeData):
        """
        Update a device management extension package
        It accepts bundleId (string) as parameters
        In case of failure it throws APIException
        """
        url = "api/v0002/mgmt/custom/bundle/%s" % (bundleId)
        r = self._apiClient.put(url, dmeData)

        if r.status_code == 200:
            return r.json()
        else:
            raise ApiException(r)
