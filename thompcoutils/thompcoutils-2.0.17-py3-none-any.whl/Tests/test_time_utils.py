import os
import logging
import unittest
import datetime
from thompcoutils.config_utils import ConfigManager
from thompcoutils.test_utils import assert_test
from thompcoutils import time_utils

test_path = 'test_ini_files'
if not os.path.exists(test_path):
    os.mkdir(test_path)
log_configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
logging.config.fileConfig(log_configuration_file)


class TestTimeUtils(unittest.TestCase):
    def test_holidays(self):
        christmas = time_utils.Holiday(time_utils.Holiday.CHRISTMAS)
        assert_test(christmas.month == 12, "Should be December")
        assert_test(christmas.day == 25, "Should be 25")

        new_years = time_utils.Holiday(time_utils.Holiday.NEW_YEARS)
        assert_test(new_years.day == 1, "should be January")
        assert_test(new_years.month == 1, "should be 1")

        new_years = time_utils.Holiday("new years")
        assert_test(new_years.day == 1, "should be January")
        assert_test(new_years.month == 1, "should be 1")

        new_years = time_utils.Holiday("nEw yEaRs")
        assert_test(new_years.day == 1, "should be January")
        assert_test(new_years.month == 1, "should be 1")

        independence = time_utils.Holiday(time_utils.Holiday.INDEPENDENCE)
        assert_test(independence.month == 7, "should be July")
        assert_test(independence.day == 4, "should be 4")

        thanksgiving = time_utils.Holiday(time_utils.Holiday.THANKSGIVING)
        assert_test(thanksgiving.month == 11, "should be November")

        memorial = time_utils.Holiday(time_utils.Holiday.MEMORIAL)
        assert_test(memorial.month == 5, "should be November")
        assert_test(memorial.day == 31, "should be 31")

        labor= time_utils.Holiday(time_utils.Holiday.LABOR)
        assert_test(labor.month == 9, "should be September")

    def test_is_weekend(self):
        count = 0
        dt = datetime.datetime(year=datetime.datetime.now().year, month=1, day=1)
        for i in range(7):
            if time_utils.is_weekend(dt):
                count += 1
            dt = datetime.datetime(year=dt.year, month=1, day=dt.day+1)
        assert_test(count == 2, "can only be two weekend days in 7 days")

