# -*- coding: utf-8 -*-
"""
Created on 2022-4-13

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
from trendreview.trendreview import parser

# Read file into pandas dataframe
# Relative to project root (not relative to __file__)
FILEPATH = '../data/ddvav_test.csv'
# --report-path - represents stdout for argparse.ArgumentParser
REPORT_FILEPATH = '-'

# %%


class TestGraphAll(unittest.TestCase):
    """Test trendreview.GraphAll"""

    def test_parse_args_inclusive(self):
        """Generic test for parser where all command line arguments are supplied"""
        args = ['--filepath', FILEPATH, '--type', 'ddvav', '--report-path', REPORT_FILEPATH,
                '--graph-columns', 'column a', 'column b', 'column c', '--datetime-header', 'timestamp']
        namespace = parser.parse_args(args)
        filepath = os.path.abspath(namespace.filepath)
        equipment_type = namespace.type
        log_filepath = os.path.abspath(namespace.log_filepath.name)
        namespace.log_filepath.close()
        independent_axis_name = namespace.independent_axis_name
        graph_columns = namespace.graph_columns
        self.assertEqual(independent_axis_name, 'timestamp')
        self.assertListEqual(
            graph_columns, ['column a', 'column b', 'column c'])

        # Close file because argparse does not close the file for us
        namespace.log_filepath.close()

        return None

    def test_parse_args_graph_columns_default(self):
        """Default value of graph_columns should be None
        None indicates that all columns are graphed from the supplied .csv file"""
        args = ['--filepath', FILEPATH, '--type', 'ddvav', '--report-path', REPORT_FILEPATH,
                '--datetime-header', 'timestamp']
        namespace = parser.parse_args(args)
        graph_columns = namespace.graph_columns
        self.assertEqual(graph_columns, None)

        # Close file because argparse does not close the file for us
        namespace.log_filepath.close()

        return None

    def test_parse_args_datetime_header_default(self):
        """Datetime should default to DateTime in absense of
        independent axis name being supplied"""
        args = ['--filepath', FILEPATH, '--type', 'ddvav',
                '--report-path', REPORT_FILEPATH]
        namespace = parser.parse_args(args)
        independent_axis_name = namespace.independent_axis_name
        self.assertEqual(independent_axis_name, 'DateTime')

        # Close file because argparse does not close the file for us
        namespace.log_filepath.close()

        return None

    def test_parse_args(self):
        """Generic testing parser. Values input to parser should
        equal the values output from the parser"""

        args = ['--filepath', FILEPATH, '--type', 'ddvav', '--report-path', REPORT_FILEPATH,
                '--graph-columns', 'column a', 'column b', 'column c',
                '--datetime-header', 'timestamp']
        namespace = parser.parse_args(args)
        filepath = os.path.abspath(namespace.filepath)
        equipment_type = namespace.type
        log_filepath = os.path.abspath(namespace.log_filepath.name)
        namespace.log_filepath.close()
        independent_axis_name = namespace.independent_axis_name
        graph_columns = namespace.graph_columns
        self.assertEqual(equipment_type, 'ddvav')
        self.assertEqual(independent_axis_name, 'timestamp')
        self.assertListEqual(
            graph_columns, ['column a', 'column b', 'column c'])

        args = ['--filepath', filepath, '--type', 'ddvav', '--report-path', REPORT_FILEPATH,
                '--graph-columns', 'column a', 'column b', 'column c',
                '--datetime-header', 'timestamp']
        namespace = parser.parse_args(args)

        return None


if __name__ == '__main__':
    unittest.main()
