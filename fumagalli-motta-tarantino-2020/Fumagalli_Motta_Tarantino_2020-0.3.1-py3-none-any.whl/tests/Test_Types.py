import unittest

import Fumagalli_Motta_Tarantino_2020.Types as Types


class TestThresholdItem(unittest.TestCase):
    def test_comparison_true_unequal(self):
        a = Types.ThresholdItem("a", 1)
        b = Types.ThresholdItem("b", 2)
        self.assertTrue(a < b)

    def test_comparison_false_unequal(self):
        a = Types.ThresholdItem("a", 1)
        b = Types.ThresholdItem("b", 2)
        self.assertFalse(a > b)

    def test_comparison_true_equal(self):
        a = Types.ThresholdItem("a", 1)
        b = Types.ThresholdItem("b", 1)
        self.assertTrue(a == b)

    def test_comparison_false_equal(self):
        a = Types.ThresholdItem("a", 1)
        b = Types.ThresholdItem("b", 2)
        self.assertFalse(a == b)

    def test_max_list(self):
        threshold_items = [
            Types.ThresholdItem("a", 1),
            Types.ThresholdItem("b", 2),
            Types.ThresholdItem("c", 3),
        ]
        self.assertEqual(3, max(item.value for item in threshold_items))

    def test_min_list(self):
        threshold_items = [
            Types.ThresholdItem("a", 1),
            Types.ThresholdItem("b", 2),
            Types.ThresholdItem("c", 3),
        ]
        self.assertEqual(1, min(item.value for item in threshold_items))
