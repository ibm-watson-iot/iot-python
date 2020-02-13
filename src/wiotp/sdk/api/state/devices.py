# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.common import IterableList
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.state.state import States

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002-beta/Device-mgr-beta.html


class Device(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        super(Device, self).__init__(apiClient, **kwargs)
        self._states = States(apiClient, self.typeId, self.deviceId)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def typeId(self):
        return self["typeId"]

    @property
    def deviceId(self):
        return self["deviceId"]

    @property
    def deviceInfo(self):
        return self["deviceInfo"]

    @property
    def metadata(self):
        return self["metadata"]

    @property
    def total_rows(self):
        return self["total_rows"]

    @property
    def registration(self):
        return self["registration"]

    @property
    def status(self):
        return self["status"]

    @property
    def states(self):
        return self._states


class IterableDeviceList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableDeviceList, self).__init__(apiClient, Device, url, filters=filters)


class Devices(RestApiDict):
    def __init__(self, apiClient, deviceTypeId):
        url = "api/v0002/device/types/%s/devices" % deviceTypeId
        super(Devices, self).__init__(apiClient, Device, IterableDeviceList, url)
