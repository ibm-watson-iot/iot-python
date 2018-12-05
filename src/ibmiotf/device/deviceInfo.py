# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json

class DeviceInfo(object):
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

