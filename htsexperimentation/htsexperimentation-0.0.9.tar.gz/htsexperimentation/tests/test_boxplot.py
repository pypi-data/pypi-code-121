import unittest
from ..compute_results.compute_res_funcs import calculate_agg_results_all_datasets
from ..config import RESULTS_PATH
from ..visualization.plotting import boxplot_error


class TestModel(unittest.TestCase):
    def setUp(self):
        self.datasets = ["prison", "tourism", "m5", "police"]
        self.algorithms = [
            "gpf",
            "mint",
            "standard_gp_pie",
            "ets_bu",
            "deepar",
            "arima_bu",
        ]

    def test_boxplot_several_algos(self):
        df_orig_list = calculate_agg_results_all_datasets(
            self.datasets,
            self.algorithms,
            "mase",
            path=RESULTS_PATH,
        )

        boxplot_error(df_orig_list, 'mase', self.datasets)

