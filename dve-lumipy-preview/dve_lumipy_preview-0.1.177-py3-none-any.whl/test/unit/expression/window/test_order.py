import unittest

from lumipy.query.expression.window.order import WindowOrder
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestWindowOrdering(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()

    def test_ordering_construction(self):
        order = WindowOrder(
            self.ar.application.ascending(),
            self.ar.method.ascending(),
            self.ar.timestamp.ascending(),
        )
        sql = order.get_sql()
        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('ORDER BY [Application] ASC, [Method] ASC, [Timestamp] ASC')
        )

    def test_ordering_construction_errors(self):
        with self.assertRaises(ValueError):
            WindowOrder()

        with self.assertRaises(TypeError):
            WindowOrder(self.ar.duration)
