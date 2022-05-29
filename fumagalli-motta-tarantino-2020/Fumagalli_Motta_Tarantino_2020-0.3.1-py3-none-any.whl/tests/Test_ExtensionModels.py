import Fumagalli_Motta_Tarantino_2020.tests.Test_Model as Test

import Fumagalli_Motta_Tarantino_2020.Types as Types
import Fumagalli_Motta_Tarantino_2020.Configurations.LoadConfig as Configs
import Fumagalli_Motta_Tarantino_2020.ExtensionModels as ExtensionModels


class TestProCompetitive(Test.TestOptimalMergerPolicyModel):
    def setupModel(self, **kwargs) -> None:
        self.model = ExtensionModels.ProCompetitiveModel(**kwargs)

    def setUpConfiguration(
        self, config_id: int, merger_policy=Types.MergerPolicies.Strict, **kwargs
    ) -> None:
        config = Configs.LoadParameters(config_id)
        config.adjust_parameters(**kwargs)
        config.params.merger_policy = merger_policy
        self.setupModel(**config())

    def get_default_cs_without_innovation(self) -> float:
        return self.get_default_value(
            "consumer_surplus_without_innovation",
            model=ExtensionModels.ProCompetitiveModel,
        )

    def test_welfare_properties(self):
        self.setupModel()
        self.assertTrue(self.are_floats_equal(0.9, self.model.w_duopoly))
        self.assertTrue(self.are_floats_equal(0.7, self.model.w_without_innovation))
        self.assertTrue(self.are_floats_equal(0.8, self.model.w_with_innovation))

    def test_tolerated_harm_strict(self):
        self.setupModel()
        self.assertEqual(0, self.model.tolerated_harm)

    def test_tolerated_harm_intermediate_late_takeover_prohibited(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        self.assertTrue(
            self.are_floats_equal(
                0.019840426, self.model.tolerated_harm, tolerance=10**-8
            )
        )

    def test_tolerated_harm_intermediate_late_takeover_allowed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        self.assertEqual(0, self.model.tolerated_harm)

    def test_laissez_faire_optimal_merger_policy(self):
        self.setupModel()
        self.assertFalse(self.model.is_laissez_faire_optimal())

    def test_intermediate_optimal_merger_policy(self):
        # TODO: Implement optimal merger policy
        pass

    def test_strict_optimal_merger_policy(self):
        # TODO: Implement optimal merger policy
        pass


class TestStrictProCompetitive(TestProCompetitive):
    def test_not_profitable(self):
        self.setUpConfiguration(config_id=30)
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)


class TestIntermediateLateTakeoverProhibitedProCompetitive(TestProCompetitive):
    def test_not_profitable_above_threshold(self):
        self.setUpConfiguration(
            config_id=30,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_below_threshold(self):
        self.setUpConfiguration(
            config_id=31,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertTrue(self.model.is_killer_acquisition())


class TestIntermediateLateTakeoverAllowedProCompetitive(TestProCompetitive):
    def test_not_profitable_above_threshold_not_credit_rationed(self):
        self.setUpConfiguration(
            config_id=30,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_late_takeover)

    def test_not_profitable_above_threshold_not_credit_rationed_unsuccessful(self):
        self.setUpConfiguration(
            config_id=30,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            development_success=False,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_above_threshold_credit_rationed(self):
        self.setUpConfiguration(
            config_id=32,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_below_threshold(self):
        self.setUpConfiguration(
            config_id=31,
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertTrue(self.model.is_killer_acquisition())


class TestResourceWaste(TestProCompetitive):
    def setupModel(self, **kwargs) -> None:
        self.model = ExtensionModels.ResourceWaste(**kwargs)

    def get_default_cs_without_innovation(self) -> float:
        return self.get_default_value(
            "consumer_surplus_without_innovation",
            model=ExtensionModels.ProCompetitiveModel,
        )

    def get_default_cs_duopoly(self) -> float:
        return self.get_default_value(
            "consumer_surplus_duopoly",
            model=ExtensionModels.ResourceWaste,
        )

    def test_welfare_properties(self):
        self.setupModel()
        self.assertTrue(self.are_floats_equal(0.81, self.model.w_duopoly))
        self.assertTrue(self.are_floats_equal(0.7, self.model.w_without_innovation))
        self.assertTrue(self.are_floats_equal(0.8, self.model.w_with_innovation))

    def test_tolerated_harm_intermediate_late_takeover_prohibited(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        self.assertTrue(
            self.are_floats_equal(
                -0.015119680, self.model.tolerated_harm, tolerance=10**-8
            )
        )

    def test_string_representation(self):
        pass

    def test_not_profitable_above_threshold(self):
        self.setUpConfiguration(config_id=34)
        self.assertEqual(
            Types.MergerPolicies.Strict,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_below_threshold(self):
        self.setUpConfiguration(config_id=33)
        self.assertEqual(
            Types.MergerPolicies.Strict,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_incumbent_expected_to_shelve())
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertTrue(self.model.is_killer_acquisition())

    def test_intermediate_optimal_merger_policy(self):
        # TODO: Implement optimal merger policy
        pass

    def test_strict_optimal_merger_policy(self):
        # TODO: Implement optimal merger policy
        pass
