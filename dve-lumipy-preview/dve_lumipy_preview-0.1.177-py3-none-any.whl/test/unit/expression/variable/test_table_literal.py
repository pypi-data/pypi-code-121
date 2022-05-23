import unittest
import lumipy as lm
import numpy as np
import pandas as pd
import datetime as dt
from test.unit.utilities.test_utils import standardise_sql_string


class TestTableLiterals(unittest.TestCase):

    def test_table_literal_from_array(self):
        int_vals = [[1, 2, 3], [4, 5, 6]]
        flt_vals = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        d = dt.datetime(2021, 1, 1)
        dt_vals = [
            [d + dt.timedelta(days=i) for i in range(3)],
            [d + dt.timedelta(days=i+3) for i in range(3)],
        ]
        str_vals = [["A", "B", "C"], ["D", "E", "F"]]
        bool_vals = [[True, False, True], [False, True, False]]

        # Int test
        int_tv = lm.from_array(int_vals)
        int_sql = standardise_sql_string(int_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [Col0], [column2] AS [Col1], [column3] AS [Col2] FROM (VALUES (1, 2, 3), (4, 5, 6))",
            int_sql
        )

        # Float test
        flt_tv = lm.from_array(flt_vals)
        flt_sql = standardise_sql_string(flt_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [Col0], [column2] AS [Col1], [column3] AS [Col2] "
            "FROM (VALUES (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))",
            flt_sql
        )

        # Datetime test
        dt_tv = lm.from_array(dt_vals)
        dt_sql = standardise_sql_string(dt_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [Col0], [column2] AS [Col1], [column3] AS [Col2] "
            "FROM (VALUES (#2021-01-01 00:00:00.000000#, #2021-01-02 00:00:00.000000#, #2021-01-03 00:00:00.000000#), "
            "(#2021-01-04 00:00:00.000000#, #2021-01-05 00:00:00.000000#, #2021-01-06 00:00:00.000000#))",
            dt_sql
        )

        # String test
        str_tv = lm.from_array(str_vals)
        str_sql = standardise_sql_string(str_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [Col0], [column2] AS [Col1], [column3] AS [Col2] "
            "FROM (VALUES (\'A\', \'B\', \'C\'), (\'D\', \'E\', \'F\'))",
            str_sql
        )

        # Bool test
        bool_tv = lm.from_array(bool_vals)
        bool_sql = standardise_sql_string(bool_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [Col0], [column2] AS [Col1], [column3] AS [Col2] FROM (VALUES (1, 0, 1), (0, 1, 0))",
            bool_sql
        )

    def test_table_literal_from_pandas(self):

        x = np.arange(5)
        d = {"A": x, "B": x**2, "C": x**3}
        df = pd.DataFrame(d)

        pd_tv = lm.from_pandas(df)
        pd_sql = standardise_sql_string(pd_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [A], [column2] AS [B], [column3] AS [C] "
            "FROM (VALUES (0, 0, 0), (1, 1, 1), (2, 4, 8), (3, 9, 27), (4, 16, 64))",
            pd_sql
        )

    def test_table_literal_from_flat_list(self):

        flat_tv = lm.from_array(np.arange(5), ['x'])
        flat_sql = standardise_sql_string(flat_tv.select('*').get_sql())
        self.assertIn(
            "SELECT [column1] AS [x] FROM (VALUES (0), (1), (2), (3), (4))",
            flat_sql
        )

    def test_errors_with_bad_inputs(self):

        bad_vals_empty = []
        bad_vals_empty_2d = [[], []]
        bad_vals_extra_dim = np.random.uniform(size=(3, 3, 3))

        with self.assertRaises(ValueError) as ve:
            lm.from_array(bad_vals_empty)

        with self.assertRaises(ValueError) as ve:
            lm.from_array(bad_vals_empty_2d)

        with self.assertRaises(ValueError) as ve:
            lm.from_array(bad_vals_extra_dim)

        with self.assertRaises(TypeError) as te:
            lm.from_array([{"A": 1}])
