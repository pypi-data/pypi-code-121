import unittest

from lumipy.query.expression.window.partition import WindowPartition
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestWindowPartition(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()

    def test_partition_construction(self):
        part = WindowPartition(self.ar.application, self.ar.method)
        sql = part.get_sql()
        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('PARTITION BY [Application], [Method]')
        )

    def test_partition_construction_errors(self):

        with self.assertRaises(ValueError):
            WindowPartition()

        with self.assertRaises(TypeError):
            WindowPartition(self.ar)
