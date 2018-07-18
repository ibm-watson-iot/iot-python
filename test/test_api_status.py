import uuid
from nose.tools import *
from nose import SkipTest

import testUtils
from ibmiotf.api.status import Status

class TestRegistryDevices(testUtils.AbstractTest):
    
    @classmethod
    def setup_class(self):
        self.status = Status(self.WIOTP_API_KEY, self.WIOTP_API_TOKEN)


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
    
