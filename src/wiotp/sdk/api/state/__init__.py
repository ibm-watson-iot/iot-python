# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.state.schemas import DraftSchemas
from wiotp.sdk.api.state.schemas import ActiveSchemas
from wiotp.sdk.api.state.eventTypes import DraftEventTypes
from wiotp.sdk.api.state.eventTypes import ActiveEventTypes
from wiotp.sdk.api.state.physicalInterfaces import DraftPhysicalInterfaces
from wiotp.sdk.api.state.physicalInterfaces import ActivePhysicalInterfaces
from wiotp.sdk.api.state.logicalInterfaces import DraftLogicalInterfaces
from wiotp.sdk.api.state.logicalInterfaces import ActiveLogicalInterfaces
from wiotp.sdk.api.state.deviceTypes import DeviceTypes
from wiotp.sdk.api.state.thingTypes import DraftThingTypes
from wiotp.sdk.api.state.thingTypes import ActiveThingTypes
from wiotp.sdk.api.state.rules import DraftRules
from wiotp.sdk.api.state.rules import ActiveRules


class DraftStateMgr:
    def __init__(self, apiClient):
        self.schemas = DraftSchemas(apiClient)
        self.eventTypes = DraftEventTypes(apiClient)
        self.physicalInterfaces = DraftPhysicalInterfaces(apiClient)
        self.logicalInterfaces = DraftLogicalInterfaces(apiClient)
        self.deviceTypes = DeviceTypes(apiClient)
        self.thingTypes = DraftThingTypes(apiClient)
        self.rules = DraftRules(apiClient)


class ActiveStateMgr:
    def __init__(self, apiClient):
        self.schemas = ActiveSchemas(apiClient)
        self.eventTypes = ActiveEventTypes(apiClient)
        self.physicalInterfaces = ActivePhysicalInterfaces(apiClient)
        self.logicalInterfaces = ActiveLogicalInterfaces(apiClient)
        self.deviceTypes = DeviceTypes(apiClient)
        self.thingTypes = ActiveThingTypes(apiClient)
        self.rules = ActiveRules(apiClient)


class StateMgr:
    def __init__(self, apiClient):
        self.draft = DraftStateMgr(apiClient)
        self.active = ActiveStateMgr(apiClient)
