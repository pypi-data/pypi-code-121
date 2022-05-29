from typing import Optional, Union

import Fumagalli_Motta_Tarantino_2020.Types as Types
import Fumagalli_Motta_Tarantino_2020.Utilities as Utilities


class BaseModel:
    """
    There are three players in our game: an Antitrust Authority (AA), which at the beginning of the game decides its
    merger policy; a monopolist $\t{I}$ncumbent; and a $\t{S}$tart-up. The start-up owns a “prototype” (or project)
    that, if developed, can give rise to an innovation: for instance a substitute/higher quality product to the
    incumbent’s existing product, or a more efficient production process. The start-up does not have enough own
    resources to develop the project. It has two options: it can either obtain additional funds from competitive
    capital markets, or sell out to the incumbent. The incumbent will have to decide whether and when it wants to
    acquire the start-up (and if it does so before product development, it has to decide whether to develop the
    prototype or shelve it), conditional on the AA’s approval of the acquisition. We assume that the takeover
    involves a negligible but positive transaction cost. The AA commits at the beginning of the game to a merger
    policy, in the form of a maximum threshold of “harm”, that it is ready to tolerate. Harm from a proposed merger
    consists of the difference between the expected welfare levels if the merger goes ahead, and in the counterfactual
    where it does not take place (derived of course by correctly anticipating the continuation equilibrium of the
    game). A proposed merger will be prohibited only if the tolerated harm level H is lower than the expected harm
    from the merger, if any.

    Timing of the game:

    | Time | Action                                                                                                                                                 |
    |------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
    | 0    | The AA commits to the standard for merger approval, $\\bar{H}$.                                                                                        |
    | 1(a) | $\t{I}$ can make a takeover offer to $\t{S}$, which can accept or reject.                                                                              |
    | 1(b) | The AA approves or blocks the takeover proposal.                                                                                                       |
    | 1(c) | The firm ($\t{I}$ or $\t{S}$) that owns the prototype decides whether to develop or shelve it.                                                         |
    | 1(d) | The owner of the prototype engages in financial contracting (if needed). After that, uncertainty about the success or failure of the project resolves. |
    | 2(a) | $\t{I}$ can make a take-it-or-leave-it offer to $\t{S}$ (if it did not already buy it at t = 1, and if the development of the project was successful). |
    | 2(b) | The AA approves or blocks the takeover proposal.                                                                                                       |
    | 3    | Active firms sell in the product market, payoffs are realised and contracts are honored.
    """

    def __init__(
        self,
        merger_policy: Types.MergerPolicies = Types.MergerPolicies.Strict,
        development_costs: float = 0.1,
        startup_assets: float = 0.05,
        success_probability: float = 0.7,
        development_success: bool = True,
        private_benefit: float = 0.05,
        consumer_surplus_without_innovation: float = 0.2,
        incumbent_profit_without_innovation: float = 0.4,
        consumer_surplus_duopoly: float = 0.5,
        incumbent_profit_duopoly: float = 0.2,
        startup_profit_duopoly: float = 0.2,
        consumer_surplus_with_innovation: float = 0.3,
        incumbent_profit_with_innovation: float = 0.5,
        asset_distribution: Union[
            Utilities.NormalDistributionFunction, Utilities.UniformDistributionFunction
        ] = Utilities.NormalDistributionFunction,
    ):
        """
        Initializes a valid base model according to the assumptions given in the paper.

        The following assumptions have to be met:

        | Condition                    | Remark                                                                                                                                                                                                                                                                                                                                                        | Page (Assumption) |
        |------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
        | $\\bar{H} \\ge 0$            | The tolerated level of harm has to be bigger than 0.                                                                                                                                                                                                                                                                                                          | p.6               |
        | $p \\in (0,1]$               | Probability that the prototype is developed successfully depends on the non-contractible effort exerted by the entrepreneur of the firm that owns the project. In case of no effort the project fails for sure, but the entrepreneur obtains a positive private benefit. In case of failure the project yields no profit.                                     | p.8               |
        | $B>0$                        | Private benefit of the entrepreneur in case of failure.                                                                                                                                                                                                                                                                                                       | p.8               |
        | $A \\in (0,K)$               | The startup does not hold sufficient assets at the beginning to cover the costs.                                                                                                                                                                                                                                                                              | p.8               |
        | $\\pi^m_I>\\pi^d_I$          | Profit of the incumbent has to be bigger without the innovation than in the duopoly.                                                                                                                                                                                                                                                                          | p.7               |
        | $\\pi^M_I>\\pi^m_I$          | Industry profits are higher with a multi-product monopolist than a single product monopolist (otherwise, the incumbent would always shelve).                                                                                                                                                                                                                                                                 | p.7               |
        | $CS^M \\ge CS^m$             | Consumer surplus with the innovation has to weakly bigger than without the innovation (consumers like variety).                                                                                                                                                                                                                                                                        | p.7               |
        | $\\pi^M_I>\\pi^d_I+\\pi^d_S$ | Industry profits are higher under monopoly than under duopoly. If this assumption did not hold, the takeover would not take place.                                                                                                                                                                                                                            | p.7 (A1)          |
        | $\\pi^d_S>\\pi^M_I-\\pi^m_I$ | An incumbent has less incentive to innovate (in a new/better product or a more efficient production process) than a potential entrant because the innovation would cannibalise the incumbent’s current profits. (Corresponds to Arrow's replacement effect)                                                                                                   | p.7 (A2)          |
        | $p\\pi^d_S>K$                | In case of effort it is efficient to develop the prototype, i.e., development has a positive net present value (NPV) for the start-up                                                                                                                                                                                                                         | p.8 (A3)          |
        | $p(W^M-W^m)>K$               | The development of the project is not only privately beneficial for the start-up, but also for society as a whole, whether undertaken by the incumbent or the start-up (implies $\\;p(W^d-W^m)>K\\;$).                                                                                                                                                                                       | p.8 (A4)          |
        | $B-K<0$$B-(p\\pi^d_S-K)>0$   | The first inequality implies that if S shirks the project has negative value; thus, no financial contract could be signed unless the startup makes effort. The second implies that the start-up may be financially constrained, that is, it may hold insufficient assets to fund the development of the prototype even though the project has a positive NPV. | p.8 (A5)          |

        Parameters
        ----------
        development_costs : float
            ($K$) Fixed costs to invest for development.
        startup_assets : float
            ($A$) Assets of the startup at the beginning.
        success_probability : float
            ($p$) Probability of success in case of effort (otherwise the projects fails for sure).
        development_success : bool
            Decides whether an attempted development will be successful (true $\\rightarrow$ attempted development succeeds).
        private_benefit : float
            ($B$) Private benefit of the entrepreneur in case of failure.
        consumer_surplus_without_innovation : float
            ($CS^m$) Consumer surplus for the case that the innovation is not introduced by the incumbent into the market.
        incumbent_profit_without_innovation : float
            ($\\pi^m_I$) Profit of the monopolist with a single product (without innovation).
        consumer_surplus_duopoly : float
            ($CS^d$) Consumer surplus for the case that the innovation is introduced into the market and a duopoly exists.
        incumbent_profit_duopoly : float
            ($\\pi^d_I$) Profit of the incumbent in the case of a duopoly.
        startup_profit_duopoly : float
            ($\\pi^d_S$) Profit of the startup in the case of a duopoly.
        consumer_surplus_with_innovation : float
             ($CS^M$) Consumer surplus for the case that the innovation is introduced by the incumbent into the market.
        incumbent_profit_with_innovation : float
            ($\\pi^M_I$) Profit of the monopolist with multiple products (with innovation).
        """
        self._merger_policy = merger_policy
        self._development_costs = development_costs
        self._startup_assets = startup_assets
        self._success_probability = success_probability
        self._development_success = development_success
        self._private_benefit = private_benefit

        # product market payoffs (p.6ff.)
        # with innovation
        self._incumbent_profit_with_innovation = incumbent_profit_with_innovation
        self._cs_with_innovation = consumer_surplus_with_innovation

        # without innovation
        self._incumbent_profit_without_innovation = incumbent_profit_without_innovation
        self._cs_without_innovation = consumer_surplus_without_innovation

        # with duopoly
        self._startup_profit_duopoly = startup_profit_duopoly
        self._incumbent_profit_duopoly = incumbent_profit_duopoly
        self._cs_duopoly = consumer_surplus_duopoly

        # set asset distribution
        self.asset_distribution = asset_distribution

        # pre-conditions given for the parameters (p.6-8)
        self._check_preconditions()

        # post-condition given (p.6-8)
        self._check_postconditions()

    def _check_postconditions(self):
        assert (
            self.w_without_innovation < self.w_with_innovation < self.w_duopoly
        ), "Ranking of total welfare not valid (p.7)"
        self._check_assumption_four()

    def _check_preconditions(self):
        self._check_merger_policy()
        # preconditions given (p.6-8)
        assert self.private_benefit > 0, "Private benefit has to be bigger than 0"
        assert (
            0 < self.success_probability <= 1
        ), "Success probability of development has to be between 0 and 1"
        self._check_startup_assets()
        assert (
            self.incumbent_profit_without_innovation > self.incumbent_profit_duopoly
        ), "Profit of the incumbent has to be bigger without the innovation than in the duopoly"
        assert (
            self.incumbent_profit_with_innovation
            > self.incumbent_profit_without_innovation
        ), "Profit of the incumbent has to be bigger with the innovation than without the innovation"
        assert (
            self.cs_with_innovation >= self.cs_without_innovation
        ), "Consumer surplus with the innovation has to weakly bigger than without the innovation"
        self._check_assumption_one()
        self._check_assumption_two()
        self._check_assumption_three()
        self._check_assumption_five()

    def _check_merger_policy(self):
        assert self._merger_policy is not None

    def _check_startup_assets(self):
        assert (
            0 < self.startup_assets < self.development_costs
        ), "Startup has not enough assets for development"

    def _check_assumption_five(self):
        assert (
            self.private_benefit - self.development_costs
            < 0
            < self.private_benefit
            - (
                self.success_probability * self._startup_profit_duopoly
                - self.development_costs
            )
        ), "A5 not satisfied (p.8)"

    def _check_assumption_four(self):
        assert (
            self._success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            > self._development_costs
        ), "A4 not satisfied (p.8)"

    def _check_assumption_three(self):
        assert (
            self.success_probability * self.startup_profit_duopoly
            > self._development_costs
        ), "A3 not satisfied (p.8)"

    def _check_assumption_two(self):
        assert (
            self.startup_profit_duopoly
            > self.incumbent_profit_with_innovation
            - self.incumbent_profit_without_innovation
        ), "A2 not satisfied (p.7)"

    def _check_assumption_one(self):
        assert (
            self.incumbent_profit_with_innovation
            > self.incumbent_profit_duopoly + self.startup_profit_duopoly
        ), "A1 not satisfied (p.7)"

    @property
    def development_costs(self) -> float:
        """
        ($K$) Fixed costs to invest for development.
        """
        return self._development_costs

    @property
    def startup_assets(self) -> float:
        """
        ($A$) Assets of the startup at the beginning.
        """
        return self._startup_assets

    @startup_assets.setter
    def startup_assets(self, value: float) -> None:
        """
        ($A$) Assets of the startup at the beginning.

        Parameters
        ----------
        value: float
            New value for the start-up assets (important the assumptions have to remain valid).
        """
        self._startup_assets = value
        self._check_startup_assets()

    @property
    def success_probability(self) -> float:
        """
        ($p$) Probability of success in case of effort (otherwise the projects fails for sure).
        """
        return self._success_probability

    @property
    def development_success(self) -> bool:
        """
        Decides whether an attempted development will be successful.

        If true, every attempted development will be successful.
        """
        return self._development_success

    @property
    def private_benefit(self) -> float:
        """
        ($B$) Private benefit of the entrepreneur in case of failure.
        """
        return self._private_benefit

    @property
    def incumbent_profit_with_innovation(self):
        """
        ($\\pi^M_I$) Profit of the monopolist with multiple products (with innovation).
        """
        return self._incumbent_profit_with_innovation

    @property
    def cs_with_innovation(self) -> float:
        """
        ($CS^M$) Consumer surplus for the case that the innovation is introduced by the incumbent into the market.
        """
        return self._cs_with_innovation

    @property
    def w_with_innovation(self) -> float:
        """
        ($W^M$) Total welfare for the case that the innovation is introduced by the incumbent into the market.
        """
        return self._cs_with_innovation + self._incumbent_profit_with_innovation

    @property
    def incumbent_profit_without_innovation(self) -> float:
        """
        ($\\pi^m_I$) Profit of the monopolist with a single product (without innovation).
        """
        return self._incumbent_profit_without_innovation

    @property
    def cs_without_innovation(self) -> float:
        """
        ($CS^m$) Consumer surplus for the case that the innovation is not introduced by the incumbent into the market.
        """
        return self._cs_without_innovation

    @property
    def w_without_innovation(self) -> float:
        """
        ($W^m$) Total welfare for the case that the innovation is not introduced by the incumbent into the market.
        """
        return self._cs_without_innovation + self._incumbent_profit_without_innovation

    @property
    def startup_profit_duopoly(self) -> float:
        """
        ($\\pi^d_S$) Profit of the startup in the case of a duopoly.
        """
        return self._startup_profit_duopoly

    @property
    def incumbent_profit_duopoly(self) -> float:
        """
        ($\\pi^d_I$) Profit of the incumbent in the case of a duopoly.
        """
        return self._incumbent_profit_duopoly

    @property
    def cs_duopoly(self) -> float:
        """
        ($CS^d$) Consumer surplus for the case that the innovation is introduced into the market and a duopoly exists.
        """
        return self._cs_duopoly

    @property
    def w_duopoly(self) -> float:
        """
        ($W^d$) Total welfare for the case that the innovation is introduced into the market and a duopoly exists.
        """
        return (
            self._cs_duopoly
            + self._startup_profit_duopoly
            + self._incumbent_profit_duopoly
        )


class MergerPolicy(BaseModel):
    """
    In this class all merger policies and their respective outcomes are calculated.

    The available merger policies are documented in Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies.
    """

    def __init__(self, *args, **kwargs):
        """
        Takes the same arguments as BaseModel.__init__.
        """
        super(MergerPolicy, self).__init__(*args, **kwargs)
        self._probability_credit_constrained_default: float = 0
        self._probability_credit_constrained_merger_policy: float = 0

        self._early_bid_attempt: Optional[Types.Takeover] = None
        self._late_bid_attempt: Optional[Types.Takeover] = None
        self._early_takeover: Optional[bool] = None
        self._late_takeover: Optional[bool] = None

        self._check_asset_distribution_thresholds()
        self._solve_game()

    def _check_asset_distribution_thresholds(self) -> None:
        """
        Checks the asset distributions thresholds on validity.

        Every threshold has to be between 0 and 1. If this condition is not satisfied, an assertion error is raised.
        """
        assert (
            0 < self.asset_distribution_threshold < 1
        ), "Violates A.2 (has to be between 0 and 1)"
        if self.merger_policy is Types.MergerPolicies.Strict:
            self._check_asset_distribution_threshold_strict()
        elif (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_prohibited
            and self.is_incumbent_expected_to_shelve()
        ):
            assert (
                0 <= self.asset_distribution_threshold_intermediate < 1
            ), "Violates Condition A-3 (has to be between 0 and 1)"
        elif (
            self.merger_policy is Types.MergerPolicies.Laissez_faire
            and self.is_incumbent_expected_to_shelve()
        ):
            assert (
                0 < self.asset_distribution_threshold_laissez_faire < 1
            ), "Violates Condition 4 (has to be between 0 and 1)"

    def _check_asset_distribution_threshold_strict(self):
        assert (
            0 < self.asset_distribution_threshold_strict < 1
        ), "Violates Condition 2 (has to be between 0 and 1)"

    @property
    def merger_policy(
        self,
    ) -> Types.MergerPolicies:
        """
        Returns the merger policy used to determine the outcome, given by the thresholds for tolerated harm.

        The levels of tolerated harm are defined in A.4 (p.36ff.). See Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies
        for the available merger policies.
        """
        # if self.tolerated_harm <= self._calculate_h0():
        #     return Types.MergerPolicies.Strict
        # if self.tolerated_harm < self._calculate_h1():
        #     return Types.MergerPolicies.Intermediate_late_takeover_prohibited
        # if self.tolerated_harm < self._calculate_h2():
        #     return Types.MergerPolicies.Intermediate_late_takeover_allowed
        return self._merger_policy

    @merger_policy.setter
    def merger_policy(self, merger_policy: Types.MergerPolicies) -> None:
        self._merger_policy = merger_policy
        # if merger_policy is Types.MergerPolicies.Strict:
        #     self.tolerated_harm = 0
        # elif (
        #     merger_policy is Types.MergerPolicies.Intermediate_late_takeover_prohibited
        # ):
        #     self.tolerated_harm = (self._calculate_h0() + self._calculate_h1()) / 2
        # elif merger_policy is Types.MergerPolicies.Intermediate_late_takeover_allowed:
        #     self.tolerated_harm = (self._calculate_h1() + self._calculate_h2()) / 2
        # else:
        #     self.tolerated_harm = self._calculate_h2() + 1
        self._recalculate_model()

    @property
    def tolerated_harm(self) -> float:
        """
        ($\\bar{H}$) The AA commits at the beginning of the game to a merger policy. The tolerated harm is the maximal loss of welfare the AA is ready to accept.
        """
        if self.merger_policy is Types.MergerPolicies.Strict:
            return self._calculate_h0()
        if (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_prohibited
        ):
            return self._calculate_h1()
        if (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_allowed
        ):
            return self._calculate_h2()
        return float("inf")

    @property
    def asset_threshold(self) -> float:
        """
        Threshold level $\\bar{A} = B - (\\pi^d_S - K)$
        """
        return self.private_benefit - (
            self.success_probability * self.startup_profit_duopoly
            - self.development_costs
        )

    @property
    def asset_threshold_cdf(self) -> float:
        """
        Returns the value of the continuous distribution function for the asset threshold.
        """
        return self.asset_distribution.cumulative(self.asset_threshold)

    @property
    def asset_threshold_late_takeover(self) -> float:
        """
        The prospect that the start-up will be acquired at $t = 2$ alleviates financial constraints: there exists a
        threshold level $\\bar{A}^T = B - (\\pi_I^M - K)$
        """
        return self.private_benefit - (
            self.success_probability * self.incumbent_profit_with_innovation
            - self.development_costs
        )

    @property
    def asset_threshold_late_takeover_cdf(self) -> float:
        """
        Returns the value of the continuous distribution function for the asset threshold under laissez-faire.
        """
        return self.asset_distribution.cumulative(self.asset_threshold_late_takeover)

    @BaseModel.startup_assets.setter
    def startup_assets(self, value: float) -> None:
        BaseModel.startup_assets.fset(self, value)
        self._recalculate_model()

    @property
    def get_early_bidding_type(self) -> Types.Takeover:
        """
        Returns the bidding attempt of the incumbent at $t = 1$.

        See Fumagalli_Motta_Tarantino_2020.Types.Takeover for the available options.
        """
        assert self._early_bid_attempt is not None
        return self._early_bid_attempt

    @property
    def get_late_bidding_type(self) -> Types.Takeover:
        """
        Returns the bidding attempt of the incumbent at $t = 2$.

        See Fumagalli_Motta_Tarantino_2020.Types.Takeover for the available options.
        """
        assert self._late_bid_attempt is not None
        return self._late_bid_attempt

    @property
    def is_early_takeover(self) -> bool:
        """
        Returns whether the start-up is acquired by the incumbent at $t=1$.

        Returns
        -------
        True
            If the start-up is acquired by the incumbent at $t=1$.
        """
        assert self._early_takeover is not None
        return self._early_takeover

    @property
    def is_late_takeover(self) -> bool:
        """
        Returns whether the start-up is acquired by the incumbent at $t=2$.

        Returns
        -------
        True
            If the start-up is acquired by the incumbent at $t=2$.
        """
        assert self._late_takeover is not None
        return self._late_takeover

    @property
    def is_owner_investing(self) -> bool:
        """
        A start-up that expects external investors to deny financing will not undertake the investment. Conversely, the incumbent
        has the financial ability to invest, but it does not always have the incentive to do so. Indeed, the innovation
        increases the incumbent’s profits less than the (unconstrained) start-up’s. (This result follows directly from
        the Arrow’s replacement effect) The increase in the incumbent’s profits may not be large enough to cover the investment
        cost. When this is the case, the incumbent will shelve the project and the acquisition turns out to be a killer acquisition.

        Investment decision under the strict merger policy:
        - An unconstrained start-up always invests in the development of the prototype.
        - The incumbent invests if (and only if): $p*(\\pi^M_I-\\pi^m_I) \\ge K$

        Returns
        -------
        True
            If the owner of the innovation at $t=1$ invests in the project, instead of shelving.
        """
        assert self.is_startup_credit_rationed is not None
        assert self.is_early_takeover is not None
        if (not self.is_startup_credit_rationed and not self.is_early_takeover) or (
            not self.is_incumbent_expected_to_shelve() and self.is_early_takeover
        ):
            return True
        return False

    @property
    def is_development_successful(self) -> bool:
        """
        Returns whether the development was successful or not.

        The following two conditions have to be satisfied:
        - The owner of the product at $t=1$ has to invest in the development
        - The development success variable has to be set to True (attempted development always successful).

        Returns
        -------
        True
            If both conditions are met.
        """
        assert self.is_owner_investing is not None
        return self.is_owner_investing and self._development_success

    @property
    def is_startup_credit_rationed(self) -> bool:
        """
        If no takeover took place at t = 1(b), a start-up that decided to develop the project searches for funding at $t = 1(d)$.

        Strict and Intermediate (late takeover prohibited):
        - $A < \\bar{A}$, the start-up is credit-rationed and cannot invest.
        - $A \\ge \\bar{A}$, the start-up obtains external funding.

        Laissez-Faire and Intermediate (late takeover allowed): $$
        - $A < \\bar{A}^T$, the start-up is credit-rationed and cannot invest.
        - $A \\ge \\bar{A}^T$, the start-up obtains external funding.

        Returns
        -------
        True
            If the start-up is credit rationed.
        """
        # financial contracting (chapter 3.2)
        if self.merger_policy in [
            Types.MergerPolicies.Strict,
            Types.MergerPolicies.Intermediate_late_takeover_prohibited,
        ]:
            if self.startup_assets < self.asset_threshold:
                return True
            return False
        if self.startup_assets < self.asset_threshold_late_takeover:
            return True
        return False

    @property
    def asset_distribution_threshold_strict(self) -> float:
        """
        Threshold defined in Lemma 3 :$\\;\\Gamma(\\cdot)=\\frac{p(W^d-W^M)}{p(W^d-W^m)-K}$
        """
        return (
            self.success_probability * (self.w_duopoly - self.w_with_innovation)
        ) / (
            self.success_probability * (self.w_duopoly - self.w_without_innovation)
            - self.development_costs
        )

    @property
    def asset_distribution_threshold(self) -> float:
        """
        Threshold defined in Condition 3 :$\\;\\Phi(\\cdot)=\\frac{p(\\pi^M_I-\\pi^d_I-\\pi^d_S)}{p(\\pi^M_I-\\pi^d_I)-K}$
        """
        return (
            self.success_probability
            * (
                self.incumbent_profit_with_innovation
                - self.incumbent_profit_duopoly
                - self.startup_profit_duopoly
            )
        ) / (
            self.success_probability
            * (self.incumbent_profit_with_innovation - self.incumbent_profit_duopoly)
            - self.development_costs
        )

    @property
    def asset_distribution_threshold_laissez_faire(self) -> float:
        """
        Threshold defined in Condition 4 :$\\;\\Phi^T(\\cdot)=\\frac{p(\\pi^m_I-\\pi^M_I)+K}{p(\\pi^m_I+\\pi^d_S-\\pi^M_I)}$
        """
        return (
            self.success_probability
            * (
                self.incumbent_profit_without_innovation
                - self.incumbent_profit_with_innovation
            )
            + self.development_costs
        ) / (
            self.success_probability
            * (
                self.incumbent_profit_without_innovation
                + self.startup_profit_duopoly
                - self.incumbent_profit_with_innovation
            )
        )

    @property
    def asset_distribution_threshold_intermediate(self) -> float:
        """
        Threshold defined in A-3 :$\\;\\Phi^{\\prime}(\\cdot)=\\frac{p(\\pi^m_I-\\pi^d_I-\\pi^d_S)+K}{p(\\pi^m_I+\\pi^d_I)}$
        """
        return (
            self.success_probability
            * (
                self.incumbent_profit_without_innovation
                - self.incumbent_profit_duopoly
                - self.startup_profit_duopoly
            )
            + self.development_costs
        ) / (
            self.success_probability
            * (self.incumbent_profit_without_innovation - self.incumbent_profit_duopoly)
        )

    def is_incumbent_expected_to_shelve(self) -> bool:
        """
        Returns whether the incumbent is expected to shelve, whenever it acquires the entrant (Condition 1).

        - True (expected to shelve): $p*(\\pi^M_I-\\pi^m_I) < K$

        - False (not expected to shelve): $p*(\\pi^M_I-\\pi^m_I) \\ge K$

        """
        return self.incumbent_expected_additional_profit_from_innovation() < 0

    def incumbent_expected_additional_profit_from_innovation(self) -> float:
        """
        Returns the additional expected profit for the incumbent, if it does not shelve the product after an acquisition.

        $ Expected \\; additional \\; profit = p*(\\pi^M_I-\\pi^m_I)-K$
        """
        return (
            self.success_probability
            * (
                self.incumbent_profit_with_innovation
                - self.incumbent_profit_without_innovation
            )
            - self.development_costs
        )

    def _calculate_h0(self) -> float:
        """
        Calculates the minimal threshold of tolerated harm to achieve for an intermediate merger policy (late takeover prohibited).
        """
        return max(
            (1 - self.asset_threshold_cdf)
            * (self.success_probability * (self.w_duopoly - self.w_with_innovation))
            - self.asset_threshold_cdf
            * (
                self.success_probability
                * (self.w_with_innovation - self.w_without_innovation)
                - self.development_costs
            ),
            0,
        )

    def _calculate_h1(self) -> float:
        """
        Calculates the minimal threshold of tolerated harm to achieve for an intermediate merger policy (late takeover allowed).
        """
        return (1 - self.asset_threshold_cdf) * (
            self.success_probability * (self.w_duopoly - self.w_without_innovation)
            - self.development_costs
        )

    def _calculate_h2(self) -> float:
        """
        Calculates the minimal threshold of tolerated harm to achieve for a laissez-faire merger policy.
        """
        return max(
            self.w_duopoly - self.w_with_innovation,
            (1 - self.asset_threshold_late_takeover_cdf)
            * (
                self.success_probability
                * (self.w_with_innovation - self.w_without_innovation)
                - self.development_costs
            ),
        )

    def _solve_game(self) -> None:
        """
        Solves the game according to the set Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies.
        """
        if self.merger_policy is Types.MergerPolicies.Strict:
            self._solve_game_strict_merger_policy()
        elif (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_prohibited
        ):
            self._solve_game_late_takeover_prohibited()
        elif (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_allowed
        ):
            self._solve_game_late_takeover_allowed()
        else:
            self._solve_game_laissez_faire()

    def _recalculate_model(self) -> None:
        """
        Organizes the recalculation of the model after a property changed value.
        """
        self._early_bid_attempt = None
        self._late_bid_attempt = None
        self._early_takeover = None
        self._late_takeover = None
        self._solve_game()

    def _solve_game_laissez_faire(self) -> None:
        """
        Solves the game under a laissez-faire merger policy, based on section 4 in the paper.
        """
        assert self.merger_policy is Types.MergerPolicies.Laissez_faire
        if self.is_incumbent_expected_to_shelve():
            if (
                self.asset_threshold_late_takeover_cdf
                >= self.asset_distribution_threshold_laissez_faire
            ):
                if not self.is_startup_credit_rationed and self.development_success:
                    self._set_takeovers(late_takeover=Types.Takeover.Pooling)
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.No,
                        late_takeover=Types.Takeover.No,
                    )
            else:
                self._set_takeovers(early_takeover=Types.Takeover.Pooling)
        else:
            if self.is_startup_credit_rationed:
                self._set_takeovers(early_takeover=Types.Takeover.Separating)
            else:
                if self.development_success:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                        late_takeover=Types.Takeover.Pooling,
                    )
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                        late_takeover=Types.Takeover.No,
                    )

    def _solve_game_late_takeover_allowed(self) -> None:
        """
        Solves the game under an intermediate merger policy (late takeover allowed), based on section 5.2 in the paper.
        """
        assert (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_allowed
        )
        if self.is_incumbent_expected_to_shelve():
            if not self.is_startup_credit_rationed and self.development_success:
                self._set_takeovers(late_takeover=Types.Takeover.Pooling)
            else:
                self._set_takeovers(
                    early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
                )
        else:
            if self.is_startup_credit_rationed:
                self._set_takeovers(early_takeover=Types.Takeover.Separating)
            else:
                if self.development_success:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                        late_takeover=Types.Takeover.Pooling,
                    )
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                    )

    def _solve_game_late_takeover_prohibited(self) -> None:
        """
        Solves the game under an intermediate merger policy (late takeover prohibited),
        based on section 5.1 in the paper.
        """
        assert (
            self.merger_policy
            is Types.MergerPolicies.Intermediate_late_takeover_prohibited
        )
        if self.is_incumbent_expected_to_shelve():
            if (
                self.asset_threshold_cdf
                >= self.asset_distribution_threshold_intermediate
            ):
                self._set_takeovers(
                    early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
                )
            else:
                self._set_takeovers(early_takeover=Types.Takeover.Pooling)
        else:
            if self.asset_threshold_cdf >= self.asset_distribution_threshold:
                if self.is_startup_credit_rationed:
                    self._set_takeovers(early_takeover=Types.Takeover.Separating)
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                    )
            else:
                self._set_takeovers(Types.Takeover.Pooling)

    def _solve_game_strict_merger_policy(self) -> None:
        """
        Solves the game under a strict merger policy, based on section 3 in the paper.
        """
        assert self.merger_policy is Types.MergerPolicies.Strict
        if self.is_incumbent_expected_to_shelve():
            self._set_takeovers(
                early_takeover=Types.Takeover.No, late_takeover=Types.Takeover.No
            )
        else:
            if (
                self.asset_distribution_threshold_strict
                < self.asset_threshold_cdf
                < max(
                    self.asset_distribution_threshold,
                    self.asset_distribution_threshold_strict,
                )
            ):
                self._set_takeovers(early_takeover=Types.Takeover.Pooling)
            else:
                if self.is_startup_credit_rationed:
                    self._set_takeovers(early_takeover=Types.Takeover.Separating)
                else:
                    self._set_takeovers(
                        early_takeover=Types.Takeover.Separating,
                        early_takeover_accepted=False,
                    )

    def _set_takeovers(
        self,
        early_takeover: Types.Takeover = Types.Takeover.No,
        late_takeover: Types.Takeover = Types.Takeover.No,
        early_takeover_accepted=True,
        late_takeover_accepted=True,
    ) -> None:
        """
        Sets the takeover variables of the class.

        Parameters
        ----------
        early_takeover: Fumagalli_Motta_Tarantino_2020.Types.Takeover
            Type of the early bid attempt/takeover (if existing).
        late_takeover: Fumagalli_Motta_Tarantino_2020.Types.Takeover
            Type of the early bid attempt/takeover (if existing).
        early_takeover_accepted: bool
            If true, the early takeover comes through, otherwise the takeover is blocked by AA or the start-up.
        late_takeover_accepted
            If true, the late takeover comes through, otherwise the takeover is blocked by AA or the start-up.
        """
        assert self._early_bid_attempt is None and self._early_takeover is None
        assert self._late_bid_attempt is None and self._late_takeover is None
        assert not (
            early_takeover in [Types.Takeover.Separating, Types.Takeover.Pooling]
            and early_takeover_accepted
            and late_takeover in [Types.Takeover.Separating, Types.Takeover.Pooling]
            and late_takeover_accepted
        ), "Only one takeover can occur."
        self._early_takeover = (
            False
            if early_takeover is Types.Takeover.No or not early_takeover_accepted
            else True
        )
        self._early_bid_attempt = early_takeover
        self._late_takeover = (
            False
            if late_takeover is Types.Takeover.No or not late_takeover_accepted
            else True
        )
        self._late_bid_attempt = late_takeover

    def summary(self) -> Types.Summary:
        """
        Returns the calculated outcome of the model with the defined parameters.

        The resulting dictionary contains the following information (and keys):
        - 'set_policy' : Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies -> Defines the chosen merger policy based on the tolerated level of harm.
        - 'credit_rationed' : True, if the start-up is credit rationed.
        - 'early_bidding_type' : Fumagalli_Motta_Tarantino_2020.Types.Takeover -> Defines the bidding type of the incumbent at t=1.
        - 'late_bidding_type' : 'Fumagalli_Motta_Tarantino_2020.Types.Takeover -> Defines the bidding type of the incumbent at t=2.
        - 'development_attempt' : True, if the owner (start-up or incumbent after a takeover) tries to develop the product.
        - 'development_outcome' : True, if the product is developed successfully.
        - 'early_takeover' : True, if a takeover takes place at $t=1$.
        - 'late_takeover' : True, if a takeover takes place at $t=2$.

        Returns
        -------
        Types.Summary
            Containing the result of the model with the defined parameters.
        """
        return Types.Summary(
            set_policy=self.merger_policy,
            credit_rationed=self.is_startup_credit_rationed,
            early_bidding_type=self.get_early_bidding_type,
            late_bidding_type=self.get_late_bidding_type,
            development_attempt=self.is_owner_investing,
            development_outcome=self.is_development_successful,
            early_takeover=self.is_early_takeover,
            late_takeover=self.is_late_takeover,
        )

    def is_killer_acquisition(self) -> bool:
        """
        Returns whether a killer acquisition occurred in the model.

        For a killer acquisition to take place the following condition have to satisfied:
        - An early takeover takes place
        - The incumbent does not develop the product

        Returns
        -------
        True
            if a killer acquisition occurred in the model.
        """
        return self.is_early_takeover and not self.is_owner_investing

    def __str__(self) -> str:
        return (
            f"Merger Policy: {self.merger_policy}\n"
            f"Is start-up credit rationed?: {self.is_startup_credit_rationed}\n"
            f"Type of early takeover attempt: {self.get_early_bidding_type}\n"
            f"Is the early takeover approved?: {self.is_early_takeover}\n"
            f"Does the owner attempt the development?: {self.is_owner_investing}\n"
            f"Is the development successful?: {self.is_development_successful}\n"
            f"Type of late takeover attempt: {self.get_late_bidding_type}\n"
            f"Is the late takeover approved?: {self.is_late_takeover}"
        )


class OptimalMergerPolicy(MergerPolicy):
    """
    Add functionality to determine the optimal merger policy for a given set of parameters.

    Annotation: As discussed in section 5.1, a policy that is more lenient with respect to early acquisitions is always
    dominated by a strict merger policy. Therefore, only the three remaining policies are discussed.
    """

    def __init__(self, *args, **kwargs):
        super(OptimalMergerPolicy, self).__init__(*args, **kwargs)

    def get_optimal_merger_policy(
        self,
    ) -> Types.MergerPolicies:
        """
        A strict merger policy is always optimal when the incumbent is expected to invest. When the incumbent is expected
        to shelve, a more lenient policy (that either authorises any type of takeover, or that blocks early takeovers when
        the incumbent makes a pooling bid and plans to shelve, and authorises late takeovers) may be optimal, but under the
        cumulative conditions indicated in proposition 4.

        See: OptimalMergerPolicy.is_laissez_faire_optimal, OptimalMergerPolicy.is_intermediate_optimal and OptimalMergerPolicy.is_strict_optimal

        """
        if self.is_laissez_faire_optimal():
            return Types.MergerPolicies.Laissez_faire
        if self.is_intermediate_optimal():
            return Types.MergerPolicies.Intermediate_late_takeover_allowed
        return Types.MergerPolicies.Strict

    def is_laissez_faire_optimal(self) -> bool:
        """
        Returns whether a laissez-faire policy is optimal.


        A laissez-faire policy (that authorises any takeover) is optimal, if:
        1. Incumbent is expected to shelve ($p(\\pi^M_I-\\pi^m_I) < K$).
        2. Financial imperfections are severe ($F(\\bar{A}^T)\\ge\\Phi^T(\\cdot)$).
        3. Approving early takeovers followed by shelving is optimal ($F(\\bar{A}^T)\\ge\\Lambda(\\cdot)$).
        4. Detrimental effect of less intense product market competition is dominated by the benefit of making it more
        likely that the innovation is commercialised (Condition 6 not satisfied).


        Returns
        -------
        True
            If a laissez-faire merger policy is optimal.
        """
        return (
            self.is_incumbent_expected_to_shelve()
            and self.is_financial_imperfection_severe()
            and self.is_shelving_after_early_takeover_optimal()
            and not self.is_strict_optimal()
        )

    def is_intermediate_optimal(self) -> bool:
        """
        Returns whether an intermediate merger policy (late takeover allowed) is optimal.

        An intermediate merger policy (late takeovers allowed) is optimal, if:
        1. Incumbent is expected to shelve ($p(\\pi^M_I-\\pi^m_I) < K$).
        2. Approving early takeovers followed by shelving is not optimal ($F(\\bar{A}^T) < \\Lambda(\\cdot)$).
        3. Detrimental effect of less intense product market competition is dominated by the benefit of making it more
        likely that the innovation is commercialised (Condition 6 not satisfied).

        Returns
        -------
        True
            If an intermediate merger policy (late takeover allowed) is optimal.
        """
        return (
            self.is_incumbent_expected_to_shelve()
            and not self.is_shelving_after_early_takeover_optimal()
            and not self.is_strict_optimal()
        )

    def is_strict_optimal(self) -> bool:
        """
        Returns whether the strict merger policy is optimal.

        The strict merger is optimal, if Condition 6 is met: $\\frac{p(W^d-W^m)-K}{p(W^M-W^m)-K} \\ge \\frac{1-F(\\bar{A}^T)}{1-F(\\bar{A})}$

        Returns
        -------
        True
            If the strict merger policy is optimal.
        """
        return (
            self.success_probability * (self.w_duopoly - self.w_without_innovation)
            - self.development_costs
        ) / (
            self.success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            - self.development_costs
        ) >= (
            1 - self.asset_threshold_late_takeover_cdf
        ) / (
            1 - self.asset_threshold_cdf
        )

    def is_financial_imperfection_severe(self) -> bool:
        """
        Returns whether financial imperfections are severe.

        Returns
        -------
        True
            If the financial imperfections are severe.
        """
        return (
            self.asset_threshold_late_takeover_cdf
            >= self.asset_distribution_threshold_laissez_faire
        )

    def is_shelving_after_early_takeover_optimal(self) -> bool:
        """
        If the harm to welfare caused by an early takeover is lower than the one, caused by a late takeover, then also
        early takeovers must be approved, even in the case of a pooling offer followed by shelving. Such a scenario occurs
        if (and only if): $F(\\bar{A}^T)\\ge\\Lambda(\\cdot)$

        Returns
        -------
        True
            If the above mentioned condition is met.
        """
        return (
            self.asset_threshold_late_takeover_cdf
            >= self.asset_distribution_threshold_intermediate_approval_despite_shelving
        )

    @property
    def asset_distribution_threshold_intermediate_approval_despite_shelving(
        self,
    ) -> float:
        """
        Threshold defined in Condition 5 :$\\;\\Lambda(\\cdot)=\\frac{p(W^M-W^m)-K-(W^d-W^M)}{p(W^M-W^m)-K}$
        """
        return (
            self.success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            - self.development_costs
            - (self.w_duopoly - self.w_with_innovation)
        ) / (
            self.success_probability
            * (self.w_with_innovation - self.w_without_innovation)
            - self.development_costs
        )

    def summary(self) -> Types.OptimalMergerPolicySummary:
        """
        Returns the calculated outcome of the model with the defined parameters.

        Additional information compared to Fumagalli_Motta_Tarantino_2020.Models.MergerPolicyModel.summary:
        - 'optimal_policy' : Fumagalli_Motta_Tarantino_2020.Types.MergerPolicies -> Defines the welfare maximizing merger policy.

        Returns
        -------
        Types.Summary
            Containing the result of the model with the defined parameters.
        """
        return Types.OptimalMergerPolicySummary(
            set_policy=self.merger_policy,
            credit_rationed=self.is_startup_credit_rationed,
            early_bidding_type=self.get_early_bidding_type,
            late_bidding_type=self.get_late_bidding_type,
            development_attempt=self.is_owner_investing,
            development_outcome=self.is_development_successful,
            early_takeover=self.is_early_takeover,
            late_takeover=self.is_late_takeover,
            optimal_policy=self.get_optimal_merger_policy(),
        )

    def __str__(self) -> str:
        return (
            super(OptimalMergerPolicy, self).__str__()
            + f"\nOptimal merger policy: {self.get_optimal_merger_policy()}"
        )
