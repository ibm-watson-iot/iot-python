import uuid
from nose.tools import *
from nose import SkipTest

from datetime import date, timedelta, datetime
import testUtils
from ibmiotf.api.usage import DayDataTransfer, DataTransferSummary

class TestRegistryUsage(testUtils.AbstractTest):
    
    # =========================================================================
    # Service Status
    # =========================================================================
    def testDataTransfer(self):
        usage = self.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today())
        # {u'end': u'2018-07-01', u'average': 435696, u'start': u'2018-06-01', u'total': 13506585}
        
        assert_true("average" in usage)
        assert_true("end" in usage)
        assert_true("start" in usage)
        assert_true("total" in usage)
        
        assert_true(isinstance(usage.average, int))
        assert_equals(usage.average, usage["average"])
        
        assert_true(isinstance(usage.total, int))
        assert_equals(usage.total, usage["total"])
        
        assert_true(isinstance(usage.start, date))
        assert_true(isinstance(usage.end, date))

    # =========================================================================
    # Service Status
    # =========================================================================
    def testDetailedDataTransfer(self):
        usage = self.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today(), True)
        # {u'end': u'2018-07-01', u'average': 435696, u'start': u'2018-06-01', u'total': 13506585}
        
        assert_true("average" in usage)
        assert_true("end" in usage)
        assert_true("start" in usage)
        assert_true("total" in usage)
        
        assert_true(isinstance(usage, DataTransferSummary))
        
        assert_true(isinstance(usage.average, int))
        assert_equals(usage.average, usage["average"])
        
        assert_true(isinstance(usage.total, int))
        assert_equals(usage.total, usage["total"])
        
        assert_true(isinstance(usage.start, date))
        assert_true(isinstance(usage.end, date))
        
        # Going back 10 days means we should have 11 data points in the collection
        assert_equals(len(usage.days), 11) 
        
        for day in usage.days:
            assert_true(isinstance(day, DayDataTransfer))
            assert_true(isinstance(day.date, date))
