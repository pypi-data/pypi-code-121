import unittest

import Fumagalli_Motta_Tarantino_2020.Configurations.LoadConfig as Configs
import Fumagalli_Motta_Tarantino_2020.Types as Types
import Fumagalli_Motta_Tarantino_2020.Models as Models


class TestLoadParameters(unittest.TestCase):
    def setUpModel(self, config_id: int):
        self.config = Configs.LoadParameters(config_id)
        self.model = Models.OptimalMergerPolicy(**self.config())

    def test_config_loading(self):
        self.setUpModel(2)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())

    def test_startup_assets(self):
        self.setUpModel(2)
        self.assertEqual(0.05, self.config.params.params["startup_assets"])
        self.config.set_startup_assets(0.09)
        m = Models.OptimalMergerPolicy(**self.config())
        self.assertEqual(0.09, m.startup_assets)

    def test_merger_policy(self):
        self.setUpModel(2)
        self.assertEqual(Types.MergerPolicies.Strict, self.config.params.merger_policy)
        self.config.set_merger_policy(Types.MergerPolicies.Laissez_faire)
        m = Models.OptimalMergerPolicy(**self.config())
        self.assertEqual(Types.MergerPolicies.Laissez_faire, m.merger_policy)

    def test_toggle_development_success(self):
        self.setUpModel(2)
        self.assertTrue(self.model.is_development_successful)
        self.config.toggle_development_success()
        m = Models.OptimalMergerPolicy(**self.config())
        self.assertFalse(m.is_development_successful)

    def test_adjust_parameter(self):
        self.setUpModel(2)
        self.assertEqual(0.1, self.config.params.get("development_costs"))
        self.config.adjust_parameters(development_costs=0.2)
        self.assertEqual(0.2, self.config.params.get("development_costs"))

    def test_load_unavailable_id(self):
        self.assertRaises(
            Configs.Exceptions.IDNotAvailableError, lambda: self.setUpModel(0)
        )
