# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 13:48:56 2021

@author: jvorsten
"""

# Python imports
from typing import List, MutableMapping
import unittest

# Third party imports
from pandas import Timestamp

# Local imports
from trendreview.FDDExceptions import FDDException

# %%


class FDDExceptionTest(unittest.TestCase):
    """Create an FDD exception and attempt to write the exception to file
    """

    def setUp(self):
        """Create dummy data"""
        self.msg = """Excessive deviation in process variable versus setpoint. 1.25 DegF*hour 
        calculated deviation during hour long measurement period; threshold=1
        Failure threshold exceeded"""
        self.data = {'DateTime': [Timestamp('2021-11-19 22:00:00'),
                                  Timestamp('2021-11-19 22:05:00'),
                                  Timestamp('2021-11-19 22:10:00'),
                                  Timestamp('2021-11-19 22:15:00'),
                                  Timestamp('2021-11-19 22:20:00'),
                                  Timestamp('2021-11-19 22:25:00'),
                                  Timestamp('2021-11-19 22:30:00'),
                                  Timestamp('2021-11-19 22:35:00'),
                                  Timestamp('2021-11-19 22:40:00'),
                                  Timestamp('2021-11-19 22:45:00'),
                                  Timestamp('2021-11-19 22:50:00'),
                                  Timestamp('2021-11-19 22:55:00'),
                                  Timestamp('2021-12-03 09:30:00')],
                     'ControlTemperature': [68.0,
                                            68.0,
                                            68.0,
                                            68.0,
                                            67.75,
                                            67.75,
                                            67.75,
                                            67.25,
                                            67.25,
                                            67.75,
                                            67.75,
                                            67.75,
                                            69.25],
                     'RoomTemperature': [68.0,
                                         68.0,
                                         68.0,
                                         68.0,
                                         67.75,
                                         67.75,
                                         67.75,
                                         67.25,
                                         67.25,
                                         67.75,
                                         67.75,
                                         67.75,
                                         69.25],
                     'primary_axis_label': 'DateTime',
                     'dependent_axis_labels': ['RoomTemperature']}
        return None

    def test_init(self):

        FDDException(self.msg, self.data)

        return None

    def test_init_without_primary_axis_key(self):
        """Data must contain label of primary key related to
        independent axis label"""
        self.data.pop('primary_axis_label')

        with self.assertRaises(KeyError):
            FDDException(self.msg, self.data)

        return None

    def test_init_without_dependent_axis_labels(self):
        """Data must contain label of primary key related to
        independent axis label"""
        self.data.pop('dependent_axis_labels')

        with self.assertRaises(KeyError):
            FDDException(self.msg, self.data)

        return None

    def test_init_without_dependent_labels(self):
        """Data must contain data related to all keys within 'dependent_axis_labels'
        """
        self.data.pop('RoomTemperature')

        with self.assertRaises(KeyError):
            FDDException(self.msg, self.data)

        return None
