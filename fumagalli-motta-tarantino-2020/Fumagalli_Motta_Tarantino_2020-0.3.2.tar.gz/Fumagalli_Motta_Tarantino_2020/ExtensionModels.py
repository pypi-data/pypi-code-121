import Fumagalli_Motta_Tarantino_2020 as Models
import Fumagalli_Motta_Tarantino_2020.Types as Types


class ProCompetitiveModel(Models.OptimalMergerPolicy):
    def __init__(self, consumer_surplus_without_innovation: float = 0.3, **kwargs):
        super(ProCompetitiveModel, self).__init__(
            consumer_surplus_without_innovation=consumer_surplus_without_innovation,
            **kwargs
        )

    def _check_assumption_four(self):
        assert (
            self._success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            < self.development_costs
            < self._success_probability * (self.w_duopoly - self.w_without_innovation)
        ), "Adjusted assumption 4 in this model"

    def _check_asset_distribution_threshold_strict(self):
        pass

    def _calculate_h0(self) -> float:
        return 0

    def _calculate_h1(self) -> float:
        return (1 - self.asset_threshold_cdf) * (
            self.success_probability * (self.w_duopoly - self.w_without_innovation)
            - self.development_costs
        )

    def _calculate_h2(self) -> float:
        return 0

    def _solve_game_strict_merger_policy(self) -> None:
        assert self.merger_policy is Types.MergerPolicies.Strict
        self._set_takeovers(
            early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
        )

    def _solve_game_late_takeover_prohibited(self) -> None:
        if self.asset_threshold_cdf < self.asset_distribution_threshold_intermediate:
            self._set_takeovers(early_takeover=Types.Takeover.Pooling)
        else:
            self._set_takeovers(
                early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
            )

    def _solve_game_late_takeover_allowed(self) -> None:
        if (
            self.asset_threshold_late_takeover_cdf
            < self.asset_distribution_threshold_laissez_faire
        ):
            self._set_takeovers(early_takeover=Types.Takeover.Pooling)
        else:
            if self.is_startup_credit_rationed:
                self._set_takeovers(
                    early_takeover=Types.Takeover.No,
                    late_takeover=Types.Takeover.No,
                )
            else:
                if self.development_success:
                    self._set_takeovers(late_takeover=Types.Takeover.Pooling)
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.No,
                        late_takeover=Types.Takeover.No,
                    )

    def is_intermediate_optimal(self) -> bool:
        return (
            (
                self.is_incumbent_expected_to_shelve()
                and self.is_financial_imperfection_severe()
            )
            or not self.is_incumbent_expected_to_shelve()
        ) and not self.is_strict_optimal()

    def is_laissez_faire_optimal(self) -> bool:
        return False


class ResourceWaste(ProCompetitiveModel):
    def __init__(self, consumer_surplus_duopoly=0.41, **kwargs):
        super(ResourceWaste, self).__init__(
            consumer_surplus_duopoly=consumer_surplus_duopoly, **kwargs
        )

    def _check_assumption_four(self):
        assert (
            self._success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            < self._success_probability * (self.w_duopoly - self.w_without_innovation)
            < self.development_costs
        ), "Adjusted assumption 4 in this model"

    def _calculate_h1(self) -> float:
        return self.asset_threshold_cdf * (
            self.success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            - self.development_costs
        )

    def _solve_game_strict_merger_policy(self) -> None:
        assert self.merger_policy is Types.MergerPolicies.Strict
        if self.asset_threshold_cdf < self.asset_distribution_threshold_intermediate:
            self._set_takeovers(early_takeover=Types.Takeover.Pooling)
        else:
            self._set_takeovers(
                early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
            )
