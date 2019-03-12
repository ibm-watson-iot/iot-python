# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict

from wiotp.sdk.exceptions import ApiException


class ServiceStatus(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def region(self):
        return next(iter(self))

    @property
    def messaging(self):
        return self[self.region]["messaging"]

    @property
    def dashboard(self):
        return self[self.region]["dashboard"]

    @property
    def thirdParty(self):
        return self[self.region]["thirdParty"]


class Status:
    def __init__(self, apiClient):
        self._apiClient = apiClient

    def serviceStatus(self):
        """
        Retrieve the organization-specific status of each of the services offered by the IBM Watson IoT Platform.
        In case of failure it throws APIException
        """

        r = self._apiClient.get("api/v0002/service-status")

        if r.status_code == 200:
            return ServiceStatus(**r.json())
        else:
            raise ApiException(r)
