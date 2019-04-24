# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from wiotp.sdk.api.actionmanager.actions import Actions
from wiotp.sdk.api.actionmanager.triggers import Triggers

"""
General overview of how Action Manager resources are related:

- 1. Set up one or more action (e.g. invoke a specific webhook)
- 2. Configure a trigger to invoke the action based on events in the IoT Platform (e.g. a specific rule is fired)

"""
class ActionManager:
    def __init__(self, apiClient):
        self._apiClient = apiClient

        self.actions = Actions(self._apiClient)
