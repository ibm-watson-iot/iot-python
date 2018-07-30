# *****************************************************************************
# Copyright (c) 2018 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from ibmiotf.api.common import ApiClient 
from ibmiotf.api.registry.devices import Devices 
from ibmiotf.api.registry.types import DeviceTypes 

class Registry():

    def __init__(self, apiClient):
        self._apiClient = apiClient
        
        self.devices = Devices(self._apiClient)
        self.devicetypes = DeviceTypes(self._apiClient)
    
