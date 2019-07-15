# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from datetime import date, timedelta, datetime
import pytest
import testUtils
from wiotp.sdk.api.usage import DayDataTransfer, DataTransferSummary

# @pytest.mark.skip(reason="See: https://github.ibm.com/wiotp/tracker/issues/1914")
class TestRegistryUsage(testUtils.AbstractTest):

    # =========================================================================
    # Service Status
    # =========================================================================
    def testDataTransfer(self):
        usage = self.appClient.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today())
        # {u'end': u'2018-07-01', u'average': 435696, u'start': u'2018-06-01', u'total': 13506585}

        assert "average" in usage
        assert "end" in usage
        assert "start" in usage
        assert "total" in usage

        assert isinstance(usage.average, int)
        assert usage.average == usage["average"]

        assert isinstance(usage.total, int)
        assert usage.total == usage["total"]

        assert isinstance(usage.start, date)
        assert isinstance(usage.end, date)

    # =========================================================================
    # Service Status
    # =========================================================================
    def testDetailedDataTransfer(self):
        usage = self.appClient.usage.dataTransfer(datetime.today() - timedelta(days=10), datetime.today(), True)
        # {u'end': u'2018-07-01', u'average': 435696, u'start': u'2018-06-01', u'total': 13506585}

        assert "average" in usage
        assert "end" in usage
        assert "start" in usage
        assert "total" in usage

        assert isinstance(usage, DataTransferSummary)

        assert isinstance(usage.average, int)
        assert usage.average == usage["average"]

        assert isinstance(usage.total, int)
        assert usage.total == usage["total"]

        assert isinstance(usage.start, date)
        assert isinstance(usage.end, date)

        # Going back 10 days means we should have 11 data points in the collection
        assert len(usage.days) == 11

        for day in usage.days:
            assert isinstance(day, DayDataTransfer)
            assert isinstance(day.date, date)
