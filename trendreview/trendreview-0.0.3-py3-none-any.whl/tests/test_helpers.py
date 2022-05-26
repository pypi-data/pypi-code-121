# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 11:02:54 2021

@author: jvorsten
"""

# Python imports
import unittest
from datetime import date, time

# Thrid party imports
import numpy as np
import pandas as pd

# Local imports
from trendreview.helpers import read_csv, _correct_time_str_HM, _parse_date_time_str_YmdHM
from trendreview.ddvav import DDVAV_HEADERS, DDVAV_TYPES

# Read file into pandas dataframe
FILEPATH = '../data/DD03.csv'
FILEPATH2 = '../data/dd64.csv'

# %%


class TestNumpyDateTimeIterables(unittest.TestCase):
    """Convert datetime strings to numpy iterables"""

    def test_date_time_iterables_to_numpy(self):
        """dates: (list) of strings representing date in format %Y-%m-%d
        times: (list) of strings representing time in format %H:%M"""

        data = {
            "Date": ['2022-01-02', '2022-01-03', '2022-01-04'],
            "Time": ['01:10', '10:10', '20:21'],
        }

        datetimes = _parse_date_time_str_YmdHM(data["Date"], data["Time"])

        return None


if __name__ == '__main__':
    unittest.main()
