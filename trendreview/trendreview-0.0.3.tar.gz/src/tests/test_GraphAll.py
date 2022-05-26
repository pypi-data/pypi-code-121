# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 10:49:09 2022

@author: jvorsten
"""

# Python imports
import unittest
from datetime import datetime

# Third party imports
import pandas as pd
import numpy as np

# Local imports
from trendreview.GraphAll import GraphAll
from trendreview.reporting import FDDReporting
from trendreview.FDDExceptions import FDDException

# Read file into pandas dataframe
# Relative to project root (not relative to __file__)
FILEPATH = '../data/DD03.csv'
FILEPATH2 = '../data/dd64.csv'
FILEPATH3 = '../data/ddvav_test.csv'
LOG_FILEPATH = '../reports/testreport.txt'
DEPENDENT_AXIS_NAMES = ['DischargeTemperature', 'CoolingDamperCommand']

# %%


class TestGraphAll(unittest.TestCase):
    """Graph all data column entries in a .csv file versus the
    independent axis (DateTIme). If 10 columns are present in a .csv file, then
    9 graphs will be created assuming the first column is data representing 'DateTime' and
    the other columns are valid data
    Equivalent command line argument: --equipment-type GraphAll from argument parser"""

    def setUp(self):
        """Load test data"""
        self.data = pd.read_csv(FILEPATH, sep=',', parse_dates=['DateTime'])
        self.data3 = pd.read_csv(FILEPATH3, sep=',', parse_dates=['DateTime'])
        self.graphall = GraphAll(FILEPATH3)

        return None

    def test_graph_all_data(self):
        """Graph all instances against independent axis and save a log"""

        independent_axis_name = 'DateTime'
        reporter = FDDReporting(log_filepath=LOG_FILEPATH)
        self.graphall.graph_all_data(
            reporter, independent_axis_name, DEPENDENT_AXIS_NAMES)
        return None


if __name__ == '__main__':
    unittest.main()
