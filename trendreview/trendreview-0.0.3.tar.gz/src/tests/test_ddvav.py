# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 16:29:57 2021

@author: jvorsten
"""

# Python imports
from itertools import filterfalse
import inspect
import unittest
import os
from datetime import datetime

# Third party imports
import pandas as pd
import numpy as np

# Local imports
from trendreview.ddvav import (DDVAVRules, DDVAV_TYPES, DDVAV_HEADERS)
from trendreview.helpers import (read_csv, masked_consecutive_elements,
                                 _datetimes_to_seconds_deviation_from_start)
from trendreview.FDDExceptions import FDDException

# Read file into pandas dataframe
# Relative to project root (not relative to __file__)
FILEPATH = '../data/DD03.csv'
FILEPATH2 = '../data/dd64.csv'
FILEPATH3 = '../data/ddvav_test.csv'

# %%


class TestDDVAV(unittest.TestCase):
    """Test file src/trendreview/ddvav.py"""

    def setUp(self):

        self.data = read_csv(FILEPATH, DDVAV_HEADERS, DDVAV_TYPES)
        self.data3 = read_csv(FILEPATH3, DDVAV_HEADERS, DDVAV_TYPES)
        self.ddvavRules = DDVAVRules(FILEPATH3)

        return None

    def test_masked_consecutive_elements(self):
        """A rule must fail when consecutive elements are True for n or more 
        elements in a row.
        masked_consecutive_elements returns the position in a passed array
        where the number of consecutive elements exceeds the passed n"""
        # Rising edge at indicy 3
        data = np.ma.MaskedArray([0, 0, 0, 1, 1, 1, 1, 0, 0, 0])
        res = masked_consecutive_elements(data, 3)
        self.assertEqual(res, [3])

        data = np.ma.MaskedArray([0, 0, 1, 1, 1, 1, 1, 0, 0, 0])
        res = masked_consecutive_elements(data, 3)
        self.assertEqual(res, [2])

        data = np.ma.MaskedArray([1, 1, 1, 1, 1, 1, 1, 0, 0, 0])
        res = masked_consecutive_elements(data, 3)
        self.assertEqual(res, [0])

        data = np.ma.MaskedArray([0, 0, 0, 0, 1, 1, 1, 0, 0, 0])
        res = masked_consecutive_elements(data, 3)
        self.assertEqual(res, [4])

        data = np.ma.MaskedArray([0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1])
        res = masked_consecutive_elements(data, 3)
        self.assertEqual(res, [4, 10])

        return None

    def test_integration_over_time(self):
        """Given a control setpoint and process variable, integrate the
        error accumulated over time"""
        # Theory testing
        control = [10] * 5  # setpoint
        process = [7, 8, 9, 10, 11]  # process variable

        diff = np.array(control) - np.array(process)

        # Prepare datetime to integrate over
        nptimes = np.array(['2021-12-18T10:00:00',
                            '2021-12-18T10:05:00',  # 5 minute interval
                            '2021-12-18T10:10:00',
                            '2021-12-18T10:20:00',  # 10 minute interval
                            '2021-12-18T10:35:00',  # 15 minute interval
                            ], dtype='datetime64[s]')
        datetimes = [datetime.strptime(
            str(x), "%Y-%m-%dT%H:%M:%S") for x in nptimes]
        xs = _datetimes_to_seconds_deviation_from_start(datetimes)

        # Integrations
        deviation = np.trapz(y=diff)  # 4.0, with 1 unit x inferred
        # with defined time interval
        deviation_time = np.trapz(y=diff, x=datetimes)  # 1050 / 60 = 17.5
        # Defined time interval in minutes
        deviation_equ = np.trapz(y=diff, x=[0, 5, 10, 20, 35])  # 17.5

        self.assertEqual(deviation_time.seconds, 1050)
        self.assertEqual(deviation_equ, 17.5)

        return None

    def test_get_methods(self):
        """Get all methods within a class that contain a string pattern"""
        methods = self.ddvavRules.get_rules()
        for method in methods:
            self.assertTrue(str(method).__contains__("rule_"))

        return None

    def test_rule_simultaneous_heating_cooling(self):
        """See rule and documentation defined in ddvav.py"""
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_simultaneous_heating_cooling(self.data3)

        return None

    def test_rule_cooling_airflow_on_closed_damper(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 20-26
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_cooling_airflow_on_closed_damper(self.data3)

        return None

    def test_rule_heating_airflow_on_closed_damper(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 27-32
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_heating_airflow_on_closed_damper(self.data3)
        return None

    def test_rule_cooling_damper_stuck(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 39-46
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_cooling_damper_stuck(self.data3)
        return None

    def test_rule_heating_damper_stuck(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 33-38
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_heating_damper_stuck(self.data3)
        return None

    def test_rule_cooling_opposed_mode(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 50-59
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_cooling_opposed_mode(self.data3)
        return None

    def test_rule_heating_opposed_mode(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 60-69
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_heating_opposed_mode(self.data3)
        return None

    def test_rule_room_temperature_deviation(self):
        """See rule and documentation defined in ddvav.py"""

        # Data row 74-86
        with self.assertRaises(FDDException):
            self.ddvavRules.rule_room_temperature_deviation(self.data3)
        return None

    def test_(self):
        return None


if __name__ == '__main__':
    unittest.main()

    # Alternate methods
    # def suite():
    #     suite = unittest.TestSuite()
    #     suite.addTest(TestDDVAV('test_rule_simultaneous_heating_cooling'))
    #     suite.addTest(TestDDVAV('test_rule_room_temperature_deviation'))
    #     return suite
    # runner = unittest.TextTestRunner()
    # runner.run(suite())
