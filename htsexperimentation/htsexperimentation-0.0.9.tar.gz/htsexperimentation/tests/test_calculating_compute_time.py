import unittest
from ..compute_results.compute_res_funcs import calculate_computing_time
from ..config import RESULTS_PATH


class TestModel(unittest.TestCase):
    def setUp(self):
        self.datasets = ["prison"]
        self.algorithms = ["gpf", "standard_gp_pie"]

    def test_results_gpf_parsing_prison(self):
        self.assertTrue(
            calculate_computing_time(
                self.datasets,
                self.algorithms,
                path=RESULTS_PATH,
            )
            < 20,
        )
