import unittest
import tsaugmentation as tsag
from ..compute_results.compute_res_funcs import get_output
import properscoring as ps


class TestModel(unittest.TestCase):
    def setUp(self):
        self.data = tsag.preprocessing.PreprocessDatasets("prison").apply_preprocess()
        self.true = self.data["predict"]["data"].reshape((32, 48)).T
        self.path = "htsexperimentation/tests/results_probabilistic"

    def test_results_gpf_parsing_prison(self):
        series = 9
        e = get_output("prison", "gpf", "jitter", self.path)
        self.assertAlmostEqual(
            ps.crps_ensemble(
                self.true[-8:, series],
                e["predictions"]["samples"]["bottom"][-8:, series, :],
            ).mean(),
            8.944,
            3,
        )

    def test_results_mint_parsing_prison(self):
        series = 9
        e = get_output("prison", "mint", "jitter", self.path)
        self.assertAlmostEqual(
            ps.crps_ensemble(
                self.true[-8:, series],
                e["predictions"]["samples"]["bottom"][-8:, series, :],
            ).mean(),
            10.336,
            3,
        )

    def test_results_deepar_parsing_prison(self):
        series = 9
        e = get_output("prison", "deepar", "jitter", self.path)
        self.assertAlmostEqual(
            ps.crps_ensemble(
                self.true[-8:, series],
                e["predictions"]["samples"]["bottom"][-8:, series, :],
            ).mean(),
            6.313,
            3,
        )
