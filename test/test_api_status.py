import uuid
from nose.tools import *
from nose import SkipTest

import testUtils

class TestRegistryStatus(testUtils.AbstractTest):
    
    # =========================================================================
    # Service Status
    # =========================================================================
    def testStatus(self):
        status = self.appClient.status.serviceStatus()
        
        # {
        #   'us': {
        #     'dashboard': 'green',
        #     'messaging': 'green',
        #     'thirdParty': 'green'
        #   }
        # }
        assert_equals("us", status.region)
        assert_true(status.dashboard in ["green", "orange", "red"])
        assert_true(status.messaging in ["green", "orange", "red"])
        assert_true(status.thirdParty in ["green", "orange", "red"])
    
