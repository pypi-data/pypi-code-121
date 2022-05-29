import unittest.mock as mock

import Fumagalli_Motta_Tarantino_2020.Types as Types
import Fumagalli_Motta_Tarantino_2020.Models as Models
import Fumagalli_Motta_Tarantino_2020.Utilities as Utilities


def mock_optimal_merger_policy(
    asset_threshold: float = 0.5,
    asset_threshold_late_takeover: float = -1,
    takeover: bool = False,
    shelving: bool = False,
    credit_constrained: bool = False,
    successful: bool = True,
    policy: Types.MergerPolicies = Types.MergerPolicies.Intermediate_late_takeover_prohibited,
) -> Models.OptimalMergerPolicy:
    def set_summary(
        credit_rationed=False,
        early_bidding_type=Types.Takeover.No,
        late_bidding_type=Types.Takeover.No,
        development_attempt=True,
        development_outcome=True,
        early_takeover=False,
        late_takeover=False,
        set_policy=policy,
    ) -> Types.OptimalMergerPolicySummary:
        if takeover:
            early_bidding_type = Types.Takeover.Separating
            early_takeover = True
            development_attempt = not shelving
            development_outcome = successful

        return Types.OptimalMergerPolicySummary(
            credit_rationed=credit_rationed,
            set_policy=set_policy,
            early_bidding_type=early_bidding_type,
            late_bidding_type=late_bidding_type,
            development_attempt=development_attempt,
            development_outcome=development_outcome,
            early_takeover=early_takeover,
            late_takeover=late_takeover,
            optimal_policy=set_policy,
        )

    def summary(
        policy: Types.MergerPolicies = Types.MergerPolicies.Intermediate_late_takeover_prohibited,
    ):
        if model.startup_assets < asset_threshold_late_takeover:
            return set_summary(
                credit_rationed=True,
                development_attempt=False,
                development_outcome=False,
                early_bidding_type=Types.Takeover.Separating,
                early_takeover=True,
                set_policy=policy,
            )
        if model.startup_assets < asset_threshold:
            return set_summary(
                credit_rationed=False,
                development_outcome=False,
                early_bidding_type=Types.Takeover.Pooling,
                early_takeover=False,
                set_policy=policy,
            )
        return set_summary(set_policy=policy, credit_rationed=credit_constrained)

    model: Models.OptimalMergerPolicy = mock.Mock(spec=Models.OptimalMergerPolicy)
    type(model).merger_policy = policy
    type(model).startup_assets = 3.5
    type(model).private_benefit = 0.18
    type(model).development_costs = 1.5
    type(model).success_probability = 0.38
    type(model).tolerated_harm = 0.48
    type(model).cs_duopoly = 0.58
    type(model).incumbent_profit_duopoly = 0.68
    type(model).startup_profit_duopoly = 0.78
    type(model).w_duopoly = (
        model.incumbent_profit_duopoly + model.startup_profit_duopoly + model.cs_duopoly
    )
    type(model).cs_without_innovation = 0.88
    type(model).incumbent_profit_without_innovation = 0.98
    type(model).w_without_innovation = (
        model.incumbent_profit_without_innovation + model.cs_without_innovation
    )
    type(model).cs_with_innovation = 1.08
    type(model).incumbent_profit_with_innovation = 1.18
    type(model).w_with_innovation = (
        model.incumbent_profit_with_innovation + model.cs_with_innovation
    )

    type(model).asset_threshold = mock.PropertyMock(return_value=asset_threshold)
    type(model).asset_threshold_late_takeover = mock.PropertyMock(
        return_value=asset_threshold_late_takeover
    )
    type(model).asset_distribution_threshold = 0.4
    type(model).asset_distribution_threshold_strict = 0.6
    type(model).asset_threshold_late_takeover_cdf = 0.7
    type(model).asset_distribution_threshold_laissez_faire = 0.8
    type(model).asset_threshold_cdf = 0.9
    type(model).asset_distribution_threshold_intermediate = 1
    model.asset_distribution = Utilities.NormalDistributionFunction

    model.summary = lambda: summary(policy=model.merger_policy)
    return model
