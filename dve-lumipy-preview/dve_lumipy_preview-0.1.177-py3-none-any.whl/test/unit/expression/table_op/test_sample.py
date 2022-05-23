import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string
from lumipy.query.expression.variable.table_variable import TableVariable


class TestTableSample(unittest.TestCase):

    def setUp(self) -> None:
        atlas = make_test_atlas()
        self.source = atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )

    def test_table_sample_with_n(self):

        rand = self.source.select('*').sample(n=1000)
        self.assertIsInstance(rand, TableVariable)
        sql_str = rand.select('*').get_sql()
        target_piece = """
        ORDER BY
          (1 - 0)*(0.5 - RANDOM() / CAST(-18446744073709551616 AS REAL)) + 0 ASC
        LIMIT
          1000;
        """
        self.assertIn(standardise_sql_string(target_piece), standardise_sql_string(sql_str))

    def test_table_sample_with_frac(self):
        rand = self.source.select('*').sample(frac=0.5)
        self.assertIsInstance(rand, TableVariable)
        sql_str = rand.select('*').get_sql()
        target_piece = """
        WHERE
          (((1 - 0)*(0.5 - RANDOM() / CAST(-18446744073709551616 AS REAL)) + 0) < 0.5);
        """
        self.assertIn(standardise_sql_string(target_piece), standardise_sql_string(sql_str))

    def test_table_sample_errors_with_neither(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample()

    def test_table_sample_errors_with_both(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample(n=10, frac=0.2)

    def test_table_sample_errors_with_bad_n(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample(n=-1)

        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample(n=0.5)

    def test_table_sample_errors_with_bad_frac(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample(frac=-0.2)
            
        with self.assertRaises(ValueError) as ve:
            self.source.select('*').sample(frac=2.5)
