import Fumagalli_Motta_Tarantino_2020 as Models
import Fumagalli_Motta_Tarantino_2020.Types as Types


class MicroFoundationModel(Models.OptimalMergerPolicy):
    def __init__(self, gamma=0.3, *args, **kwargs):
        assert 0 < gamma < 1, "Gamma has to be between 0 and 1."
        self._gamma = gamma
        super(MicroFoundationModel, self).__init__(*args, **kwargs)
        assert (
            self.development_costs < self.success_probability / 4
        ), "K >= p/4 is not valid"
        self._incumbent_profit_without_innovation = 0.25
        self._cs_without_innovation = 0.125
        self._incumbent_profit_with_innovation = 1 / (2 + 2 * self.gamma)
        self._cs_with_innovation = 1 / (4 + 4 * self.gamma)
        self._incumbent_profit_duopoly = 1 / (2 + self.gamma) ** 2
        self._startup_profit_duopoly = self._incumbent_profit_duopoly
        self._cs_duopoly = (1 + self.gamma) / ((2 + self.gamma) ** 2)

    def _check_assumption_one(self):
        assert (self.gamma**2) / (
            ((2 + self.gamma) ** 2) * (2 + 2 * self.gamma)
        ) > 0, "A1 adjusted for the micro foundation model."

    def _check_assumption_two(self):
        assert (self.gamma * (self.gamma**2 + 3 * self.gamma + 4)) / (
            ((2 + self.gamma) ** 2) * (4 + 4 * self.gamma)
        ) > 0, "A2 adjusted for the micro foundation model."

    def _check_assumption_three(self):
        assert (
            self._gamma_assumption_three > self.gamma
        ), "A3 adjusted for the micro foundation model."

    def _check_assumption_four(self):
        assert (
            self._gamma_assumption_four > self.gamma
        ), "A4 adjusted for the micro foundation model."

    def _check_assumption_five(self):
        assert (
            self.success_probability / ((2 + self.gamma) ** 2) - self.development_costs
            < self.private_benefit
            < self.development_costs
        ), "A5 adjusted for the micro foundation model."

    def incumbent_expected_additional_profit_from_innovation(self) -> float:
        return (self.success_probability - 4 * self.development_costs) / (
            self.success_probability + 4 * self.development_costs
        ) - self.gamma

    @property
    def asset_threshold(self) -> float:
        return (
            self.private_benefit
            + self.development_costs
            - (self.success_probability / ((2 + self.gamma) ** 2))
        )

    @property
    def gamma(self) -> float:
        return self._gamma

    @property
    def _gamma_assumption_three(self) -> float:
        return ((self.success_probability / self.development_costs) ** (1 / 2)) - 2

    @property
    def _gamma_assumption_four(self) -> float:
        return (3 * self.success_probability - 8 * self.development_costs) / (
            8 * self.development_costs + 3 * self.success_probability
        )

    def is_laissez_faire_optimal(self) -> bool:
        return False

    def is_intermediate_optimal(self) -> bool:
        return (
            self.is_investment_cost_sufficiently_high()
            and self.is_degree_substitutability_moderate()
            and self.is_financial_imperfection_severe()
        )

    def is_strict_optimal(self) -> bool:
        return not self.is_intermediate_optimal()

    def is_investment_cost_sufficiently_high(self) -> float:
        return (
            (
                -5 * (self.success_probability**3)
                + 64 * (self.development_costs**3) * (3 + self.success_probability)
                + 12
                * self.development_costs
                * (self.success_probability**2)
                * (3 * self.success_probability - 1)
                + 16
                * (self.development_costs**2)
                * self.success_probability
                * (5 + 6 * self.success_probability)
            )
            / (
                8
                * self.success_probability
                * ((4 * self.development_costs + 3 * self.success_probability) ** 2)
            )
        ) > 0

    def is_degree_substitutability_moderate(self):
        return 0 < self.success_probability * (
            self.w_with_innovation - self.w_without_innovation
        ) - self.development_costs - (self.w_duopoly - self.w_with_innovation)


class PerfectInformationModel(Models.OptimalMergerPolicy):
    def _solve_game_strict_merger_policy(self) -> None:
        assert self.merger_policy is Types.MergerPolicies.Strict
        if (
            self.is_startup_credit_rationed
            and not self.is_incumbent_expected_to_shelve()
        ):
            self._set_takeovers(early_takeover=Types.Takeover.Separating)
        else:
            self._set_takeovers(
                early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
            )

    def _solve_game_laissez_faire(self) -> None:
        assert self.merger_policy is Types.MergerPolicies.Laissez_faire
        if self.is_startup_credit_rationed and self.is_incumbent_expected_to_shelve():
            self._set_takeovers(
                early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
            )
        else:
            if self.is_startup_credit_rationed:
                self._set_takeovers(early_takeover=Types.Takeover.Separating)
            else:
                self._set_takeovers(early_takeover=Types.Takeover.Pooling)

    def _solve_game_late_takeover_allowed(self) -> None:
        assert (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        if self.is_incumbent_expected_to_shelve():
            if self.is_startup_credit_rationed or not self.development_success:
                self._set_takeovers(
                    early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
                )
            else:
                self._set_takeovers(late_takeover=Types.Takeover.Pooling)
        else:
            if self.is_startup_credit_rationed:
                self._set_takeovers(early_takeover=Types.Takeover.Separating)
            else:
                self._set_takeovers(early_takeover=Types.Takeover.Pooling)

    def is_laissez_faire_optimal(self) -> bool:
        return False

    def is_intermediate_optimal(self) -> bool:
        return (
            self.is_incumbent_expected_to_shelve()
            and not self.is_strict_optimal()
            and self.success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            - self.development_costs
            >= self.w_duopoly - self.w_with_innovation
        )


class EquityContract(Models.OptimalMergerPolicy):
    @property
    def asset_threshold_late_takeover(self) -> float:
        return self.asset_threshold

    # TODO: Adjust optimal merger policies
