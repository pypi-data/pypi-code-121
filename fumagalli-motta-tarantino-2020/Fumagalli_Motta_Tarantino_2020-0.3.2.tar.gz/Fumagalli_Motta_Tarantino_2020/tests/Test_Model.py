import unittest

import Fumagalli_Motta_Tarantino_2020.Types as Types
import Fumagalli_Motta_Tarantino_2020.Models as Models


class TestBaseModel(unittest.TestCase):
    def setupModel(self, **kwargs) -> None:
        self.model = Models.BaseModel(**kwargs)

    @staticmethod
    def are_floats_equal(f1: float, f2: float, tolerance: float = 10 ** (-10)) -> float:
        return abs(f1 - f2) < tolerance

    @staticmethod
    def get_default_value(arg_name: str, model=Models.BaseModel) -> float:
        args_name = model.__init__.__code__.co_varnames[1:]  # "self" is not needed
        default_value = model.__init__.__defaults__
        arg_index = args_name.index(f"{arg_name}")
        return default_value[arg_index]

    def get_welfare_value(self, market_situation: str) -> float:
        consumer_surplus = self.get_default_value(
            f"consumer_surplus_{market_situation}"
        )
        incumbent_profit = self.get_default_value(
            f"incumbent_profit_{market_situation}"
        )
        try:
            # handle case of duopoly
            startup_profit = self.get_default_value(
                f"startup_profit_{market_situation}"
            )
        except ValueError:
            startup_profit = 0
        return consumer_surplus + incumbent_profit + startup_profit

    def get_default_cs_without_innovation(self) -> float:
        return self.get_default_value("consumer_surplus_without_innovation")

    def get_default_cs_duopoly(self) -> float:
        return self.get_default_value("consumer_surplus_duopoly")

    def test_valid_setup_default_values(self):
        self.setupModel()

    def test_invalid_merger_policy(self):
        self.assertRaises(AssertionError, lambda: self.setupModel(merger_policy=None))

    def test_invalid_private_benefit(self):
        self.assertRaises(AssertionError, lambda: self.setupModel(private_benefit=-0.1))

    def test_invalid_profit(self):
        self.assertRaises(
            AssertionError,
            lambda: self.setupModel(
                incumbent_profit_without_innovation=0.2, incumbent_profit_duopoly=0.3
            ),
        )
        self.assertRaises(
            AssertionError,
            lambda: self.setupModel(
                incumbent_profit_with_innovation=0.2,
                incumbent_profit_without_innovation=0.3,
            ),
        )
        self.assertRaises(
            AssertionError,
            lambda: self.setupModel(
                incumbent_profit_with_innovation=0.2,
                incumbent_profit_duopoly=0.3,
                startup_profit_duopoly=0.2,
            ),
        )
        self.assertRaises(
            AssertionError,
            lambda: self.setupModel(
                startup_profit_duopoly=0.2,
                incumbent_profit_with_innovation=0.5,
                incumbent_profit_duopoly=0.3,
            ),
        )

    def test_invalid_consumer_surplus(self):
        self.assertRaises(
            AssertionError,
            lambda: self.setupModel(
                consumer_surplus_with_innovation=0.2,
                consumer_surplus_without_innovation=0.3,
            ),
        )

    def test_invalid_success_probability(self):
        self.assertRaises(
            AssertionError, lambda: self.setupModel(success_probability=0)
        )
        self.assertRaises(
            AssertionError, lambda: self.setupModel(success_probability=1.1)
        )

    def test_properties(self):
        self.setupModel()
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("development_costs"),
                self.model.development_costs,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("startup_assets"), self.model.startup_assets
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("success_probability"),
                self.model.success_probability,
            )
        )
        self.assertTrue(self.model.development_success)
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("private_benefit"), self.model.private_benefit
            )
        )

    def test_properties_profits_consumer_surplus(self):
        self.setupModel()
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_cs_without_innovation(),
                self.model.cs_without_innovation,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("incumbent_profit_without_innovation"),
                self.model.incumbent_profit_without_innovation,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_cs_duopoly(),
                self.model.cs_duopoly,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("incumbent_profit_duopoly"),
                self.model.incumbent_profit_duopoly,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("startup_profit_duopoly"),
                self.model.startup_profit_duopoly,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("consumer_surplus_with_innovation"),
                self.model.cs_with_innovation,
            )
        )
        self.assertTrue(
            self.are_floats_equal(
                self.get_default_value("incumbent_profit_with_innovation"),
                self.model.incumbent_profit_with_innovation,
            )
        )

    def test_welfare_properties(self):
        self.setupModel()
        self.assertEqual(self.get_welfare_value("duopoly"), self.model.w_duopoly)
        self.assertEqual(
            self.get_welfare_value("without_innovation"),
            self.model.w_without_innovation,
        )
        self.assertEqual(
            self.get_welfare_value("with_innovation"), self.model.w_with_innovation
        )


class TestMergerPolicyModel(TestBaseModel):
    def setupModel(self, **kwargs) -> None:
        self.model = Models.MergerPolicy(**kwargs)

    def test_tolerated_harm_strict(self):
        self.setupModel()
        self.assertTrue(
            self.are_floats_equal(
                0.014561171, self.model.tolerated_harm, tolerance=10**-8
            )
        )

    def test_tolerated_harm_intermediate_late_takeover_allowed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        self.assertTrue(
            self.are_floats_equal(
                0.054561171, self.model.tolerated_harm, tolerance=10**-8
            )
        )

    def test_tolerated_harm_intermediate_late_takeover_prohibited(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        self.assertTrue(
            self.are_floats_equal(0.1, self.model.tolerated_harm, tolerance=10**-8)
        )

    def test_tolerated_harm_laissez_faire(self):
        self.setupModel(merger_policy=Types.MergerPolicies.Laissez_faire)
        self.assertEqual(float("inf"), self.model.tolerated_harm)


class TestLaissezFaireMergerPolicyModel(TestMergerPolicyModel):
    def test_not_profitable_below_assets_threshold_not_credit_rationed(self):
        self.setupModel(merger_policy=Types.MergerPolicies.Laissez_faire)
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertTrue(self.model.is_killer_acquisition())

    def test_not_profitable_above_assets_threshold_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire,
            startup_assets=0.01,
            private_benefit=0.099,
            success_probability=0.51,
            development_costs=0.1,
            startup_profit_duopoly=0.339,
            incumbent_profit_duopoly=0.01,
            incumbent_profit_with_innovation=0.35,
            consumer_surplus_with_innovation=0.4,
            incumbent_profit_without_innovation=0.3,
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())

    def test_not_profitable_above_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire, private_benefit=0.075
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())

    def test_not_profitable_below_assets_threshold_not_credit_rationed_unsuccessful(
        self,
    ):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire,
            private_benefit=0.075,
            development_success=False,
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())

    def test_profitable_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire,
            private_benefit=0.075,
            startup_assets=0.005,
            development_costs=0.076,
            success_probability=0.79,
            incumbent_profit_with_innovation=0.179,
            incumbent_profit_without_innovation=0.08,
            incumbent_profit_duopoly=0.05,
            startup_profit_duopoly=0.1,
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())

    def test_profitable_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire,
            private_benefit=0.075,
            development_costs=0.078,
            success_probability=0.76,
            incumbent_profit_with_innovation=0.51,
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())

    def test_profitable_not_credit_rationed_unsuccessful(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Laissez_faire,
            private_benefit=0.075,
            development_costs=0.078,
            success_probability=0.76,
            incumbent_profit_with_innovation=0.51,
            development_success=False,
        )
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)
        self.assertFalse(self.model.is_killer_acquisition())


class TestIntermediateLateTakeoverAllowedMergerPolicyModel(TestMergerPolicyModel):
    def test_not_profitable_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_late_takeover)

    def test_not_profitable_not_credit_rationed_unsuccessful(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            development_success=False,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            startup_assets=0.01,
            private_benefit=0.099,
            success_probability=0.51,
            development_costs=0.1,
            startup_profit_duopoly=0.339,
            incumbent_profit_duopoly=0.01,
            incumbent_profit_with_innovation=0.35,
            consumer_surplus_with_innovation=0.4,
            incumbent_profit_without_innovation=0.3,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            incumbent_profit_with_innovation=0.59,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertTrue(self.model.is_late_takeover)

    def test_profitable_not_credit_rationed_unsuccessful(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            incumbent_profit_with_innovation=0.59,
            development_success=False,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_allowed,
            private_benefit=0.075,
            startup_assets=0.005,
            development_costs=0.076,
            success_probability=0.79,
            incumbent_profit_with_innovation=0.179,
            incumbent_profit_without_innovation=0.08,
            incumbent_profit_duopoly=0.05,
            startup_profit_duopoly=0.1,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)


class TestIntermediateLateTakeoverProhibitedMergerPolicyModel(TestMergerPolicyModel):
    def test_not_profitable_below_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_above_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            success_probability=0.74,
            private_benefit=0.08,
            development_costs=0.09,
            incumbent_profit_without_innovation=0.38,
            startup_profit_duopoly=0.22,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_below_assets_threshold_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            development_costs=0.075,
            success_probability=0.79,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            startup_profit_duopoly=0.11,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_below_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            startup_assets=0.06,
            development_costs=0.075,
            success_probability=0.79,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            startup_profit_duopoly=0.11,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_above_assets_threshold_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            startup_assets=0.055,
            development_costs=0.071,
            success_probability=0.75,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            consumer_surplus_duopoly=0.7,
            incumbent_profit_duopoly=0.29,
            startup_profit_duopoly=0.11,
            consumer_surplus_with_innovation=0.21,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_above_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            merger_policy=Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            startup_assets=0.062,
            development_costs=0.071,
            success_probability=0.75,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            consumer_surplus_duopoly=0.7,
            incumbent_profit_duopoly=0.29,
            startup_profit_duopoly=0.11,
            consumer_surplus_with_innovation=0.21,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)


class TestStrictMergerPolicyModel(TestMergerPolicyModel):
    def test_not_profitable_not_credit_rationed_summary(self):
        self.setupModel()
        summary: Types.Summary = self.model.summary()
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertFalse(summary.credit_rationed)
        self.assertEqual(Types.Takeover.No, summary.early_bidding_type)
        self.assertEqual(Types.Takeover.No, summary.late_bidding_type)
        self.assertTrue(summary.development_attempt)
        self.assertTrue(summary.development_outcome)
        self.assertFalse(summary.early_takeover)
        self.assertFalse(summary.late_takeover)

    def test_not_profitable_not_credit_rationed(self):
        self.setupModel()
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_not_profitable_credit_rationed(self):
        self.setupModel(private_benefit=0.09, development_costs=0.11)
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.No, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertFalse(self.model.is_owner_investing)
        self.assertFalse(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_set_startup_assets_recalculation(self):
        self.setupModel(
            development_costs=0.075,
            success_probability=0.75,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            consumer_surplus_duopoly=0.7,
            incumbent_profit_duopoly=0.25,
            startup_profit_duopoly=0.11,
            consumer_surplus_with_innovation=0.21,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertTrue(self.model.is_early_takeover)
        self.model.startup_assets = 0.065
        self.assertFalse(self.model.is_early_takeover)

    def test_set_tolerated_harm_recalculation(self):
        self.setupModel()
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.model.merger_policy = Types.MergerPolicies.Laissez_faire
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)

    def test_set_merger_policy(self):
        self.setupModel()
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.model.merger_policy = (
            Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
            self.model.merger_policy,
        )
        self.model.merger_policy = (
            Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.merger_policy,
        )
        self.model.merger_policy = Types.MergerPolicies.Laissez_faire
        self.assertEqual(Types.MergerPolicies.Laissez_faire, self.model.merger_policy)
        self.model.merger_policy = Types.MergerPolicies.Strict
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)

    def test_profitable_below_assets_threshold_credit_rationed(self):
        self.setupModel(
            development_costs=0.075,
            success_probability=0.79,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            startup_profit_duopoly=0.11,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_below_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            startup_assets=0.06,
            development_costs=0.075,
            success_probability=0.79,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            startup_profit_duopoly=0.11,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Pooling, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_above_assets_threshold_credit_rationed(self):
        self.setupModel(
            development_costs=0.075,
            success_probability=0.75,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            consumer_surplus_duopoly=0.7,
            incumbent_profit_duopoly=0.25,
            startup_profit_duopoly=0.11,
            consumer_surplus_with_innovation=0.21,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertTrue(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertTrue(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)

    def test_profitable_above_assets_threshold_not_credit_rationed(self):
        self.setupModel(
            development_costs=0.075,
            startup_assets=0.065,
            success_probability=0.75,
            private_benefit=0.07,
            incumbent_profit_without_innovation=0.3,
            consumer_surplus_duopoly=0.7,
            incumbent_profit_duopoly=0.25,
            startup_profit_duopoly=0.11,
            consumer_surplus_with_innovation=0.21,
            incumbent_profit_with_innovation=0.4,
        )
        self.assertEqual(Types.MergerPolicies.Strict, self.model.merger_policy)
        self.assertFalse(self.model.is_startup_credit_rationed)
        self.assertEqual(Types.Takeover.Separating, self.model.get_early_bidding_type)
        self.assertEqual(Types.Takeover.No, self.model.get_late_bidding_type)
        self.assertTrue(self.model.is_owner_investing)
        self.assertTrue(self.model.is_development_successful)
        self.assertFalse(self.model.is_early_takeover)
        self.assertFalse(self.model.is_late_takeover)


class TestOptimalMergerPolicyModel(TestMergerPolicyModel):
    def setupModel(self, **kwargs) -> None:
        self.model = Models.OptimalMergerPolicy(**kwargs)

    def test_strict_optimal_merger_policy_summary(self):
        self.setupModel()
        summary: Types.OptimalMergerPolicySummary = self.model.summary()
        self.assertEqual(Types.MergerPolicies.Strict, summary.optimal_policy)

    def test_strict_optimal_merger_policy(self):
        self.setupModel()
        self.assertEqual(
            Types.MergerPolicies.Strict, self.model.get_optimal_merger_policy()
        )
        self.assertTrue(self.model.is_strict_optimal())

    def test_intermediate_optimal_merger_policy(self):
        self.setupModel(
            private_benefit=0.09,
            startup_profit_duopoly=0.15,
            incumbent_profit_duopoly=0.16,
            incumbent_profit_without_innovation=0.36,
        )
        self.assertEqual(
            Types.MergerPolicies.Intermediate_late_takeover_allowed,
            self.model.get_optimal_merger_policy(),
        )
        self.assertTrue(self.model.is_intermediate_optimal())

    def test_laissez_faire_optimal_merger_policy(self):
        self.setupModel(
            development_costs=3,
            private_benefit=2,
            consumer_surplus_with_innovation=4,
            consumer_surplus_duopoly=6,
            consumer_surplus_without_innovation=2,
            incumbent_profit_duopoly=1,
            incumbent_profit_without_innovation=3,
            incumbent_profit_with_innovation=7,
            startup_profit_duopoly=5,
        )
        self.assertEqual(
            Types.MergerPolicies.Laissez_faire, self.model.get_optimal_merger_policy()
        )
        self.assertTrue(self.model.is_laissez_faire_optimal())

    def test_string_representation(self):
        self.setupModel()
        self.assertEqual(
            "Merger Policy: Strict\n"
            "Is start-up credit rationed?: False\n"
            "Type of early takeover attempt: No bid\n"
            "Is the early takeover approved?: False\n"
            "Does the owner attempt the development?: True\n"
            "Is the development successful?: True\n"
            "Type of late takeover attempt: No bid\n"
            "Is the late takeover approved?: False\n"
            "Optimal merger policy: Strict",
            str(self.model),
        )
