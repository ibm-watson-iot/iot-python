# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.statemanagement.schemas import DraftSchemas
from wiotp.sdk.api.statemanagement.schemas import ActiveSchemas
from wiotp.sdk.api.statemanagement.eventTypes import DraftEventTypes
from wiotp.sdk.api.statemanagement.eventTypes import ActiveEventTypes
from wiotp.sdk.api.statemanagement.physicalInterfaces import DraftPhysicalInterfaces
from wiotp.sdk.api.statemanagement.physicalInterfaces import ActivePhysicalInterfaces
from wiotp.sdk.api.statemanagement.logicalInterfaces import DraftLogicalInterfaces
from wiotp.sdk.api.statemanagement.logicalInterfaces import ActiveLogicalInterfaces

"""
General overview of how Action Manager resources are related:

- 1. Set up one or more action (e.g. invoke a specific webhook)
- 2. Configure a trigger to invoke the action based on events in the IoT Platform (e.g. a specific rule is fired)

"""
class StateManagement:
    def __init__(self, apiClient):
        self._apiClient = apiClient

        self.draftSchemas = DraftSchemas(self._apiClient)
        self.activeSchemas = ActiveSchemas(self._apiClient)
        self.draftEventTypes = DraftEventTypes(self._apiClient)
        self.activeEventTypes = ActiveEventTypes(self._apiClient)
        self.draftPhysicalInterfaces = DraftPhysicalInterfaces(self._apiClient)
        self.activePhysicalInterfaces = ActivePhysicalInterfaces(self._apiClient)
        self.draftLogicalInterfaces = DraftLogicalInterfaces(self._apiClient)
        self.activeLogicalInterfaces = ActiveLogicalInterfaces(self._apiClient)
