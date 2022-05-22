import unittest

from worker_bunch.astral_times.astral_times_config import AstralTime


class TestAstralTime(unittest.TestCase):

    def test_list_astral_values(self):
        values = AstralTime.values()
        self.assertTrue(values)
        self.assertIn("sunset", values)

        extended_values = AstralTime.extended_values()
        self.assertTrue(values)
        self.assertIn("sunset", values)
        self.assertTrue(len(values) < len(extended_values))

    def test_astral_values_exist(self):
        self.assertTrue(AstralTime.extended_value_exists("sunrise"))
        self.assertFalse(AstralTime.extended_value_exists("unknown..."))
