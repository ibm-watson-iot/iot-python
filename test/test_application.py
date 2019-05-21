# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import uuid
import os
import testUtils
import wiotp.sdk.application

class TestApplication(testUtils.AbstractTest):
    def testApplicationSharedSubscriptions(self):
        appId = str(uuid.uuid4())
        appCliInstance1 = wiotp.sdk.application.ApplicationClient({
            "identity": { "appId": appId },
            "auth": { "key": os.getenv("WIOTP_API_KEY"), "token": os.getenv("WIOTP_API_TOKEN") },
            "options": { "mqtt": { "instanceId": str(uuid.uuid4()) }}
        })
        assert isinstance(appCliInstance1, wiotp.sdk.application.ApplicationClient)

        appCliInstance2 = wiotp.sdk.application.ApplicationClient({
            "identity": { "appId": appId },
            "auth": { "key": os.getenv("WIOTP_API_KEY"), "token": os.getenv("WIOTP_API_TOKEN") },
            "options": { "mqtt": { "instanceId": str(uuid.uuid4()) }}
        })
        assert isinstance(appCliInstance2, wiotp.sdk.application.ApplicationClient)

        appCliInstance1.connect()
        appCliInstance2.connect()
        assert(appCliInstance1.isConnected() == True)
        assert(appCliInstance2.isConnected() == True)

        appCliInstance1.disconnect()
        appCliInstance2.disconnect()
        assert(appCliInstance1.isConnected() == False)
        assert(appCliInstance2.isConnected() == False)
