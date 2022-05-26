from math import pow

from deampy.parameters import Constant


class CostHealthOverDeltaT:

    def __init__(self,
                 par_health_per_new_member=None, par_cost_per_new_member=None,
                 par_health_per_unit_of_time=None, par_cost_per_unit_of_time=None):
        """
        :param par_health_per_new_member: (Parameter)
        :param par_cost_per_new_member: (Parameter)
        :param par_health_per_unit_of_time: (Parameter)
        :param par_cost_per_unit_of_time: (Parameter)
        """

        if par_health_per_new_member is None:
            par_health_per_new_member = Constant(value=0)
        if par_cost_per_new_member is None:
            par_cost_per_new_member = Constant(value=0)
        if par_health_per_unit_of_time is None:
            par_health_per_unit_of_time = Constant(value=0)
        if par_cost_per_unit_of_time is None:
            par_cost_per_unit_of_time = Constant(value=0)

        self.deltaTCost = 0
        self.deltaTHealth = 0
        self.deltaT = None  # (double) simulation time step
        self.parHealthPerNewMember = par_health_per_new_member
        self.parCostPerNewMember = par_cost_per_new_member
        self.parHealthPerUnitOfTime = par_health_per_unit_of_time
        self.parCostPerUnitOfTime = par_cost_per_unit_of_time

    def update(self, prevalence, incidence):
        """
        :param prevalence: (float) prevalence over the current time step
        :param incidence: (float) incidence over the current time step
        """

        self.deltaTCost = self.parCostPerNewMember.value * incidence
        self.deltaTHealth = self.parHealthPerNewMember.value * incidence

        ave_prev = self.deltaT * prevalence
        self.deltaTCost += self.parCostPerUnitOfTime.value * ave_prev
        self.deltaTHealth += self.parHealthPerUnitOfTime.value * ave_prev


class CostHealthOverEpidemic:
    """ class to collect the cost and health outcomes over a simulated epidemic """

    def __init__(self, compartments, sum_time_series, interventions, delta_t_discount_rate=0):
        """
        :param delta_t_discount_rate: discounted rate over deltaT
        """

        self.comparts = compartments
        self.sumTimeSeries = sum_time_series
        self.interventions = interventions

        self.deltaTDiscountRate = delta_t_discount_rate

        # sequence of costs and effects over all delta t periods
        self.seqOfCosts = []
        self.seqOfEffects = []
        # total cost and effect accumulated after warm-up discounted to
        # the beginning of the projection period
        self.totalDiscountedCostAfterWarmUp = 0
        self.totalDiscountedEffectAfterWarmUp = 0

        self.discountedCostsOverDecisionPeriodsAfterWarmUp = []
        self.discountedEffectsOverDecisionPeriodsAfterWarmUp = []

        # find if health or cost outcomes are associated with compartments
        self.checkComparts = False
        for c in self.comparts:
            if c.healthCostOverDeltaT is not None:
                self.checkComparts = True
                break
        # find if health or cost outcomes are associated with sum time-series
        self.checkSumTimeSeries = False
        for c in self.sumTimeSeries:
            if c.healthCostOverDeltaT is not None:
                self.checkSumTimeSeries = True
                break

    def reset(self):
        self.seqOfCosts.clear()
        self.seqOfEffects.clear()
        self.totalDiscountedCostAfterWarmUp = 0
        self.totalDiscountedEffectAfterWarmUp = 0
        self.discountedCostsOverDecisionPeriodsAfterWarmUp.clear()
        self.discountedEffectsOverDecisionPeriodsAfterWarmUp.clear()

    def collect_cost_health(self, delta_t):
        """ collects the cost and health outcomes of this period """

        delta_t_cost = 0
        delta_t_effect = 0

        # compartments
        if self.checkComparts:
            # find number of outgoing members from each compartment
            for c in self.comparts:
                econ = c.healthCostOverDeltaT
                if econ is not None:
                    econ.update(prevalence=c.size,
                                incidence=c.n_past_delta_t_incoming)
                    delta_t_cost += econ.deltaTCost
                    delta_t_effect += econ.deltaTHealth

        # sum time-series
        if self.checkSumTimeSeries:
            for s in self.sumTimeSeries:
                econ = s.healthCostOverDeltaT
                if econ is not None:
                    delta_t_cost += econ.deltaTCost
                    delta_t_effect += econ.deltaTHealth

        # interventions
        for i in self.interventions:
            delta_t_cost += i.get_cost_over_delta_t(delta_t=delta_t)

        # record
        self.seqOfCosts.append(delta_t_cost)
        self.seqOfEffects.append(delta_t_effect)

    def process_end_of_sim(self, n_delta_t_warm_up, n_delta_t_decision_period,
                           n_delta_ts_before_first_decision):
        """ calculates the followings at the end of the simulation after discarding
        observations during the warm-up period:
        total discounted cost, total discounted effect,
        sequence of cumulative discounted cost at decision points, and
        sequence of cumulative discounted effect at decision points, """

        # find sequence of costs and effects after the warm up
        seq_of_costs_after_warm_up = [0] * n_delta_t_warm_up
        seq_of_effects_after_warm_up = [0] * n_delta_t_warm_up
        seq_of_costs_after_warm_up.extend(self.seqOfCosts[n_delta_t_warm_up:])
        seq_of_effects_after_warm_up.extend(self.seqOfEffects[n_delta_t_warm_up:])

        # find cost and effect over delta t periods discounted to
        # the beginning of the projection period (at the end of the warm-up period)
        discounted_costs_after_warm_up = [0] * n_delta_t_warm_up
        discounted_effects_after_warm_up = [0] * n_delta_t_warm_up
        for t in range(len(self.seqOfCosts[n_delta_t_warm_up:])):
            multiplier = pow(1 + self.deltaTDiscountRate, -t)
            discounted_costs_after_warm_up.append(seq_of_costs_after_warm_up[n_delta_t_warm_up + t] * multiplier)
            discounted_effects_after_warm_up.append(seq_of_effects_after_warm_up[n_delta_t_warm_up + t] * multiplier)

        # total discounted cost and effect after warm up
        self.totalDiscountedCostAfterWarmUp = sum(discounted_costs_after_warm_up)
        self.totalDiscountedEffectAfterWarmUp = sum(discounted_effects_after_warm_up)

        # find discounted cost and effect over decision periods
        if_continue = True
        t = 0
        while if_continue:

            # find the length of this decision period
            if len(discounted_costs_after_warm_up[t:]) < n_delta_t_decision_period:
                right = len(discounted_costs_after_warm_up[t:])
            else:
                right = n_delta_t_decision_period

            # sum of cost and effect over this decision period
            sum_cost = sum(discounted_costs_after_warm_up[t: t + right])
            sum_effect = sum(discounted_effects_after_warm_up[t: t + right])

            # store cost and affect
            self.discountedCostsOverDecisionPeriodsAfterWarmUp.append(sum_cost)
            self.discountedEffectsOverDecisionPeriodsAfterWarmUp.append(sum_effect)

            # find next index of time
            t += n_delta_t_decision_period

            if t >= len(discounted_costs_after_warm_up):
                if_continue = False

    def get_discounted_cost_over_decision_periods(self):
        return self.discountedCostsOverDecisionPeriodsAfterWarmUp

    def get_discounted_health_over_decision_periods(self):
        return self.discountedEffectsOverDecisionPeriodsAfterWarmUp
