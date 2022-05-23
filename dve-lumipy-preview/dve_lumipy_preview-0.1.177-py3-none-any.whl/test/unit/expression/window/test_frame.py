import unittest

from lumipy.query.expression.window.frame import WindowFrame
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestWindowFrame(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()

    def test_frame_construction_unbounded_to_current(self):

        part = WindowFrame.create(None, 0)
        self.assertEqual(
            standardise_sql_string(part.get_sql()),
            standardise_sql_string('ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW')
        )

    def test_frame_construction_unbounded_to_unbounded(self):

        part = WindowFrame.create(None, None)
        self.assertEqual(
            standardise_sql_string(part.get_sql()),
            standardise_sql_string('ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING')
        )

    def test_frame_construction_current_to_unbounded(self):

        part = WindowFrame.create(0, None)
        self.assertEqual(
            standardise_sql_string(part.get_sql()),
            standardise_sql_string('ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING')
        )

    def test_frame_construction_n_to_current(self):

        part = WindowFrame.create(5, 0)
        self.assertEqual(
            standardise_sql_string(part.get_sql()),
            standardise_sql_string('ROWS BETWEEN 5 PRECEDING AND CURRENT ROW')
        )

    def test_frame_construction_current_to_n(self):

        part = WindowFrame.create(0, 5)
        self.assertEqual(
            standardise_sql_string(part.get_sql()),
            standardise_sql_string('ROWS BETWEEN CURRENT ROW AND 5 FOLLOWING')
        )

    def test_frame_construction_errors(self):

        with self.assertRaises(TypeError):
            WindowFrame('a', 0)

        with self.assertRaises(TypeError):
            WindowFrame(0, 0)

        with self.assertRaises(TypeError):
            WindowFrame(0, 'a')

    def test_bound_string_functions(self):
        with self.assertRaises(ValueError):
            WindowFrame.create('A', 0)

        with self.assertRaises(ValueError):
            WindowFrame.create(0, 'C')
