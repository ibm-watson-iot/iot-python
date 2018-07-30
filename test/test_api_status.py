import uuid
from nose.tools import *
from nose import SkipTest

import testUtils

class TestRegistryStatus(testUtils.AbstractTest):
    
    # =========================================================================
    # Service Status
    # =========================================================================
    def testStatus(self):
        status = self.status.serviceStatus()
        
        # {
        #   'us': {
        #     'dashboard': 'green',
        #     'messaging': 'green',
        #     'thirdParty': 'green'
        #   }
        # }
        assert_true("us" in status)
        assert_true("dashboard" in status["us"])
        assert_true("messaging" in status["us"])
        assert_true("thirdParty" in status["us"])
    
