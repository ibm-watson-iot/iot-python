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


class IterableDeviceTypeList(IterableList):
    def __init__(self, apiClient):
        super(IterableDeviceTypeList, self).__init__(apiClient, DeviceType, "api/v0002/device/types")


class DeviceType(defaultdict):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

        # {"classId": "Device", "createdDateTime": "2016-01-23T16:34:46+00:00", "description":
        # "Extended color light", "deviceInfo": {"description": "Extended color light", "manufacturer": "Philips", "model": "LCT003"},
        # "id": "LCT003", "refs": {"logicalInterfaces": "api/v0002/device/types/LCT003/logicalinterfaces", "mappings":
        # "api/v0002/device/types/LCT003/mappings", "physicalInterface": "api/v0002/device/types/LCT003/physicalinterface"},
        # "updatedDateTime": "2017-02-27T10:27:04.221Z"}

        self.devices = Devices(apiClient, kwargs["id"])

        dict.__init__(self, **kwargs)

    @property
    def id(self):
        return self["id"]

    @property
    def description(self):
        if "description" in self:
            return self["description"]
        else:
            return None

    @property
    def metadata(self):
        if "metadata" in self:
            return self["metadata"]
        else:
            return None

    @property
    def deviceInfo(self):
        # Unpack the deviceInfo dictionary into keyword arguments so that we
        # can return a DeviceIngo object instead of a plain dictionary
        if "deviceInfo" in self:
            return DeviceInfo(**self["deviceInfo"])
        else:
            return DeviceInfo()

    @property
    def classId(self):
        return self["classId"]

    def __str__(self):
        return "[%s] %s" % (self.id, self.deviceInfo.description or self.description or "<No description>")

    def __repr__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    def json(self):
        return dict(self)


class DeviceTypes(defaultdict):
    def __init__(self, apiClient):
        self._apiClient = apiClient

    def __contains__(self, key):
        """
        get a device type from the registry
        """

        url = "api/v0002/device/types/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        """
        get a device type from the registry
        """
        url = "api/v0002/device/types/%s" % (key)

        r = self._apiClient.get(url)
        if r.status_code == 200:
            return DeviceType(apiClient=self._apiClient, **r.json())
        elif r.status_code == 404:
            self.__missing__(key)
        else:
            raise ApiException(r)

    def __setitem__(self, key, value):
        """
        register a new device
        """
        raise Exception("Unable to register or update a device via this interface at the moment.")

    def __delitem__(self, key):
        """
        delete a device type
        """
        url = "api/v0002/device/types/%s" % (key)

        r = self._apiClient.delete(url)
        if r.status_code != 204:
            raise ApiException(r)

    def __missing__(self, key):
        """
        device type does not exist
        """
        raise KeyError("Device type %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        iterate through all devices
        """
        return IterableDeviceTypeList(self._apiClient)

    def create(self, deviceType):
        """
        Register one or more new device types, each request can contain a maximum of 512KB.
        """

        r = self._apiClient.post("api/v0002/device/types", deviceType)

        if r.status_code == 201:
            return DeviceType(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def update(self, typeId, description=None, deviceInfo=None, metadata=None):
        devicetypeUrl = "api/v0002/device/types/%s" % (typeId)

        data = {"description": description, "deviceInfo": deviceInfo, "metadata": metadata}

        r = self._apiClient.put(devicetypeUrl, data)
        if r.status_code == 200:
            return DeviceType(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def delete(self, typeId):
        del self[typeId]
