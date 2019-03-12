# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import iso8601
import json
from datetime import datetime
from collections import defaultdict, MutableSequence
from wiotp.sdk.exceptions import ApiException


class DeviceErrorCode(defaultdict):
    def __init__(self, **kwargs):
        if not set(["errorCode", "timestamp"]).issubset(kwargs):
            raise Exception("Data passed to DeviceErrorCode is not correct: %s" % (",".join(sorted(kwargs.keys()))))

        if isinstance(kwargs["timestamp"], datetime):
            # Remove the microsecond, as WIoTP API's don't handle ISO8601 with microsecond
            kwargs["timestamp"] = kwargs["timestamp"].replace(microsecond=0)
        else:
            kwargs["timestamp"] = iso8601.parse_date(kwargs["timestamp"])

        dict.__init__(self, **kwargs)

    @property
    def errorCode(self):
        return self["errorCode"]

    @property
    def timestamp(self):
        return self["timestamp"]


class DeviceErrorCodes(MutableSequence):
    def __init__(self, apiClient, typeId, deviceId):
        self._apiClient = apiClient
        self.typeId = typeId
        self.deviceId = deviceId

    def __len__(self):
        # Get all, convert list to iterator
        logsUrl = "api/v0002/device/types/%s/devices/%s/diag/errorCodes" % (self.typeId, self.deviceId)

        r = self._apiClient.get(logsUrl)
        if r.status_code == 200:
            return len(r.json())
        else:
            raise ApiException(r)

    def __delitem__(self, index):
        raise Exception("Individual error codes can not be deleted use clear() method instead")

    def insert(self, index, value):
        raise Exception("only append() is supported for new error codes")

    def __setitem__(self, index, value):
        raise Exception("Reported error codes are immutable")

    def __getitem__(self, index):
        """
        Get a log entry
        """
        ecUrl = "api/v0002/device/types/%s/devices/%s/diag/errorCodes" % (self.typeId, self.deviceId)

        r = self._apiClient.get(ecUrl)
        if r.status_code == 200:
            if index > len(r.json()):
                self.__missing__(index)
            return DeviceErrorCode(**r.json()[index])
        else:
            raise ApiException(r)

    def append(self, item=None, **kwargs):
        # Get all, convert list to iterator
        ecUrl = "api/v0002/device/types/%s/devices/%s/diag/errorCodes" % (self.typeId, self.deviceId)

        if item is None:
            item = DeviceErrorCode(**kwargs)

        r = self._apiClient.post(ecUrl, item)
        if r.status_code == 201:
            return True
        else:
            raise ApiException(r)

    def __missing__(self, index):
        """
        Log does not exist
        """
        raise KeyError("Error Code at index %s does not exist" % (index))

    def clear(self):
        # Get all, convert list to iterator
        ecUrl = "api/v0002/device/types/%s/devices/%s/diag/errorCodes" % (self.typeId, self.deviceId)

        r = self._apiClient.delete(ecUrl)
        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)


class DeviceLog(defaultdict):
    def __init__(self, **kwargs):
        if not set(["message", "severity", "data", "timestamp"]).issubset(kwargs):
            raise Exception("Data passed to DeviceLog is not correct: %s" % (",".join(sorted(kwargs.keys()))))

        if isinstance(kwargs["timestamp"], datetime):
            # Remove the microsecond, as WIoTP API's don't handle ISO8601 with microsecond
            kwargs["timestamp"] = kwargs["timestamp"].replace(microsecond=0)
        else:
            kwargs["timestamp"] = iso8601.parse_date(kwargs["timestamp"])

        dict.__init__(self, **kwargs)

    @property
    def message(self):
        return self["message"]

    @property
    def severity(self):
        return self["severity"]

    @property
    def data(self):
        return self["data"]

    @property
    def timestamp(self):
        return self["timestamp"]

    # Following properties are not used when creating a new DeviceLog, but are present when reading one that has been persisted
    @property
    def id(self):
        return self.get("id", None)

    @property
    def typeId(self):
        return self.get("typeId", None)

    @property
    def deviceId(self):
        return self.get("deviceId", None)


class DeviceLogs(defaultdict):
    def __init__(self, apiClient, typeId, deviceId):
        self._apiClient = apiClient
        self.typeId = typeId
        self.deviceId = deviceId

    def __contains__(self, key):
        """
        Does a log exist?
        """
        logUrl = "api/v0002/device/types/%s/devices/%s/diag/logs/%s" % (self.typeId, self.deviceId, key)

        r = self._apiClient.get(logUrl)
        if r.status_code == 200:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise ApiException(r)

    def __getitem__(self, key):
        """
        Get a log entry
        """
        if isinstance(key, int):
            # Special case -- allow this to be used as a dict or a list
            # Get all, convert list to iterator
            logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

            r = self._apiClient.get(logsUrl)
            if r.status_code == 200:
                if key > len(r.json()):
                    self.__missing__(key)
                return DeviceLog(**r.json()[key])
            else:
                raise ApiException(r)
        else:
            logUrl = "api/v0002/device/types/%s/devices/%s/diag/logs/%s" % (self.typeId, self.deviceId, key)

            r = self._apiClient.get(logUrl)
            if r.status_code == 200:
                return DeviceLog(**r.json())
            elif r.status_code == 404:
                self.__missing__(key)
            else:
                raise ApiException(r)

    def __setitem__(self, key, value):
        """
        Logs are immutable
        """
        raise Exception("Log entries are immutable")

    def __delitem__(self, key):
        """
        Delete a log
        """
        if isinstance(key, int):
            # Special case -- allow this to be used as a dict or a list
            logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

            r = self._apiClient.get(logsUrl)
            if r.status_code == 200:
                if key > len(r.json()):
                    self.__missing__(key)
                key = r.json()[key]["id"]
            else:
                raise ApiException(r)

        logUrl = "api/v0002/device/types/%s/devices/%s/diag/logs/%s" % (self.typeId, self.deviceId, key)

        r = self._apiClient.delete(logUrl)
        if r.status_code == 404:
            self.__missing__(key)
        elif r.status_code != 204:
            raise ApiException(r)

    def __missing__(self, key):
        """
        Log does not exist
        """
        raise KeyError("Log Entry %s does not exist" % (key))

    def __iter__(self, *args, **kwargs):
        """
        Iterate through all devices
        """

        # Get all, convert list to iterator
        logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

        r = self._apiClient.get(logsUrl)
        if r.status_code == 200:
            logArray = []
            for logEntry in r.json():
                logArray.append(DeviceLog(**logEntry))
            return iter(logArray)
        else:
            raise ApiException(r)

    def __len__(self):
        # Get all, convert list to iterator
        logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

        r = self._apiClient.get(logsUrl)
        if r.status_code == 200:
            return len(r.json())
        else:
            raise ApiException(r)

    def append(self, item=None, **kwargs):
        # Get all, convert list to iterator
        logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

        if item is None:
            item = DeviceLog(**kwargs)
        r = self._apiClient.post(logsUrl, item)
        if r.status_code == 201:
            return True
        else:
            raise ApiException(r)

    def clear(self):
        # Get all, convert list to iterator
        logsUrl = "api/v0002/device/types/%s/devices/%s/diag/logs" % (self.typeId, self.deviceId)

        r = self._apiClient.delete(logsUrl)
        if r.status_code == 204:
            return True
        else:
            raise ApiException(r)
