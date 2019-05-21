# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import datetime
from collections import defaultdict
from wiotp.sdk.exceptions import ApiException


class DataTransferSummary(defaultdict):
    def __init__(self, **kwargs):
        daysAsObj = []
        if "days" in kwargs and kwargs["days"] is not None:
            for day in kwargs["days"]:
                daysAsObj.append(DayDataTransfer(**day))
        del kwargs["days"]
        dict.__init__(self, days=daysAsObj, **kwargs)

    @property
    def start(self):
        return datetime.strptime(self["start"], "%Y-%m-%d").date()

    @property
    def end(self):
        return datetime.strptime(self["end"], "%Y-%m-%d").date()

    @property
    def average(self):
        return self["average"]

    @property
    def total(self):
        return self["total"]

    @property
    def days(self):
        return self["days"]


class DayDataTransfer(defaultdict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @property
    def date(self):
        return datetime.strptime(self["date"], "%Y-%m-%d").date()

    @property
    def total(self):
        return self["total"]


class Usage:
    def __init__(self, apiClient):
        self._apiClient = apiClient

    def dataTransfer(self, start, end, detail=False):
        """
        Retrieve the organization-specific status of each of the services offered by the IBM Watson IoT Platform.
        In case of failure it throws APIException
        """

        r = self._apiClient.get(
            "api/v0002/usage/data-traffic?start=%s&end=%s&detail=%s"
            % (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), detail)
        )

        if r.status_code == 200:
            return DataTransferSummary(**r.json())
        else:
            raise ApiException(r)
