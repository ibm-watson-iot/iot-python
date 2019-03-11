# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import json


class DeviceInfo(defaultdict):
    def __init__(self):
        dict.__init__(
            self,
            serialNumber=None,
            manufacturer=None,
            model=None,
            deviceClass=None,
            description=None,
            fwVersion=None,
            hwVersion=None,
            descriptiveLocation=None,
        )

    @property
    def serialNumber(self):
        return self["serialNumber"]

    @property
    def manufacturer(self):
        return self["manufacturer"]

    @property
    def model(self):
        return self["model"]

    @property
    def deviceClass(self):
        return self["deviceClass"]

    @property
    def description(self):
        return self["description"]

    @property
    def fwVersion(self):
        return self["fwVersion"]

    @property
    def hwVersion(self):
        return self["hwVersion"]

    @property
    def descriptiveLocation(self):
        return self["descriptiveLocation"]

    @serialNumber.setter
    def serialNumber(self, serialNumber):
        self["serialNumber"] = serialNumber

    @manufacturer.setter
    def manufacturer(self, value):
        self["manufacturer"] = value

    @model.setter
    def model(self, value):
        self["model"] = value

    @deviceClass.setter
    def deviceClass(self, value):
        self["deviceClass"] = value

    @description.setter
    def description(self, value):
        self["description"] = value

    @fwVersion.setter
    def fwVersion(self, fwVersion):
        self["fwVersion"] = fwVersion

    @hwVersion.setter
    def hwVersion(self, value):
        self["hwVersion"] = value

    @descriptiveLocation.setter
    def descriptiveLocation(self, value):
        self["descriptiveLocation"] = value

    def __str__(self):
        return json.dumps(self, sort_keys=True)


"""
    def __init__(self):
        self.serialNumber = None
        self.manufacturer = None
        self.model = None
        self.deviceClass = None
        self.description = None
        self.fwVersion = None
        self.hwVersion = None
        self.descriptiveLocation = None

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)
"""
