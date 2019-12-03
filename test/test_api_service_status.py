# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import testUtils


class TestRegistryStatus(testUtils.AbstractTest):

    # =========================================================================
    # Service Status
    # =========================================================================
    def testStatus(self):
        status = self.appClient.serviceStatus()

        assert status.region == "us"
        assert status.dashboard in ["green", "orange", "red"]
        assert status.messaging in ["green", "orange", "red"]
        assert status.thirdParty in ["green", "orange", "red"]
