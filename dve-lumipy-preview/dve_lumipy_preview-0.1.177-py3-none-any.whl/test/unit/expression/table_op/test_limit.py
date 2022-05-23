import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestLimit(unittest.TestCase):

    def setUp(self):
        atlas = make_test_atlas()
        self.source = atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )
        self.test_select = self.source.select('^')

    def test_limit_object_is_immutable(self):
        assert_locked_lockable(self, self.test_select.limit(100))

    def test_limit_validation_wrong_type_value(self):
        with self.assertRaises(TypeError) as te:
            self.test_select.limit(self.source.duration)
        self.assertIn('only accepts int values', str(te.exception))
        with self.assertRaises(TypeError) as te:
            self.test_select.limit(100.1)
        self.assertIn('only accepts int values', str(te.exception))
        with self.assertRaises(TypeError) as te:
            self.test_select.limit('100')
        self.assertIn('only accepts int values', str(te.exception))

    def test_limit_validation_must_be_nonzero_positive(self):
        with self.assertRaises(ValueError) as ve:
            self.test_select.limit(0)
        self.assertIn('must be non-zero and positive', str(ve.exception))
        with self.assertRaises(ValueError) as ve:
            self.test_select.limit(-2)
        self.assertIn('must be non-zero and positive', str(ve.exception))

    def test_limit_construction_correct_sql(self):
        limit = self.test_select.limit(100)
        lim_sql_str = standardise_sql_string(limit.get_sql())
        sel_sql_str = standardise_sql_string(self.test_select.get_sql())

        self.assertIn(sel_sql_str, lim_sql_str)
        self.assertIn('LIMIT 100', lim_sql_str)
        sel_hashes = [hash(c) for c in self.test_select.get_columns()]
        lim_hashes = [hash(c) for c in limit.get_columns()]
        self.assertEqual(set(sel_hashes), set(lim_hashes))
