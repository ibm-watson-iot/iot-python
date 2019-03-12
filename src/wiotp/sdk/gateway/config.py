# *****************************************************************************
# Copyright (c) 2014, 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import os
import yaml

from wiotp.sdk import ConfigurationException
from wiotp.sdk.device.config import DeviceClientConfig


class GatewayClientConfig(DeviceClientConfig):
    def __init__(self, **kwargs):
        DeviceClientConfig.__init__(self, **kwargs)

    @property
    def clientId(self):
        """
        We need to override the clientId method as a gateway's clientId is prefixed with "g"
        """
        return "g:%s:%s:%s" % (self["identity"]["orgId"], self["identity"]["typeId"], self["identity"]["deviceId"])

    @property
    def apiKey(self):
        return "g/%s/%s/%s" % (self["identity"]["orgId"], self["identity"]["typeId"], self["identity"]["deviceId"])

    @property
    def apiToken(self):
        return self["auth"]["token"] if ("auth" in self) else None
