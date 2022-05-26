import unittest
from ..compute_results.compute_res_funcs import calculate_agg_results_all_datasets
from ..config import RESULTS_PATH


class TestModel(unittest.TestCase):
    def setUp(self):
        self.datasets = ["prison", "tourism"]
        self.algorithms = ["gpf", "mint", "standard_gp_pie", "ets_bu", "deepar", "arima_bu"]

    def test_results_several_algos_parsing(self):
        self.assertTrue(
            calculate_agg_results_all_datasets(
                self.datasets,
                self.algorithms,
                "mase",
                path=RESULTS_PATH,
            )[1].shape
            == (1378, 6),
        )
