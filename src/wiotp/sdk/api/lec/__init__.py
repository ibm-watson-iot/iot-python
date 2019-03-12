# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import iso8601
from collections import defaultdict
from wiotp.sdk.api.registry.devices import DeviceUid
from wiotp.sdk.exceptions import ApiException


class LastEvent(defaultdict):
    def __init__(self, **kwargs):
        if not set(["deviceId", "typeId", "eventId", "format", "timestamp", "payload"]).issubset(kwargs):
            raise Exception("Missing required attributes to construct a LastEvent object")
        dict.__init__(self, **kwargs)

    @property
    def typeId(self):
        return self["typeId"]

    @property
    def deviceId(self):
        return self["deviceId"]

    @property
    def eventId(self):
        return self["eventId"]

    @property
    def format(self):
        return self["format"]

    @property
    def timestamp(self):
        return iso8601.parse_date(self["timestamp"])

    @property
    def payload(self):
        return self["payload"]


class LEC:
    def __init__(self, apiClient):
        self._apiClient = apiClient

    def get(self, deviceUid, eventId):
        """
        Retrieves the last cached message for specified event from a specific device.
        """

        if not isinstance(deviceUid, DeviceUid) and isinstance(deviceUid, dict):
            deviceUid = DeviceUid(**deviceUid)

        url = "api/v0002/device/types/%s/devices/%s/events/%s" % (deviceUid.typeId, deviceUid.deviceId, eventId)
        r = self._apiClient.get(url)

        if r.status_code == 200:
            return LastEvent(**r.json())
        else:
            raise ApiException(r)

    def getAll(self, deviceUid):
        """
        Retrieves a list of the last cached message for all events from a specific device.
        """

        if not isinstance(deviceUid, DeviceUid) and isinstance(deviceUid, dict):
            deviceUid = DeviceUid(**deviceUid)

        url = "api/v0002/device/types/%s/devices/%s/events" % (deviceUid.typeId, deviceUid.deviceId)
        r = self._apiClient.get(url)

        if r.status_code == 200:
            events = []
            for event in r.json():
                events.append(LastEvent(**event))
            return events
        else:
            raise ApiException(r)
