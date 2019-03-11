# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import json


class DeviceFirmware(object):
    def __init__(
        self, version=None, name=None, url=None, verifier=None, state=None, updateStatus=None, updatedDateTime=None
    ):
        self.version = version
        self.name = name
        self.url = url
        self.verifier = verifier
        self.state = state
        self.updateStatus = updateStatus
        self.updatedDateTime = updatedDateTime

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)
