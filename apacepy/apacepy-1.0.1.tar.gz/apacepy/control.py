from deampy.optimization.appx_policy_itr import _ApproxDecisionMaker

from apacepy.features_conditions import _Condition


class DecisionMaker:

    def __init__(self, interventions, epi_history):

        self.interventions = interventions
        self.epiHistory = epi_history
        self.interventionsInEffect = []
        self.statusOfIntvs = None   # switch status of interventions
        self.statusOfIntvsOverPastSimOutPeriods = []  # list of lists
        self.statusOfIntvsOverPastObsPeriods = []     # list of lists

    def initialize(self, delta_t, time_monitor):

        for i in self.interventions:
            i.initialize(delta_t=delta_t, time_monitor=time_monitor)

    def reset(self):

        self.statusOfIntvs = []
        for i in self.interventions:
            i.reset()
            self.statusOfIntvs.append(i.switchValue)

        self.interventionsInEffect.clear()
        self.statusOfIntvsOverPastSimOutPeriods.clear()
        self.statusOfIntvsOverPastObsPeriods.clear()

    def make_a_decision(self, sim_time_index):
        """ tries to make a decision and returns True if a decision was made
        (a decision cannot be made if the epidemic is not yet detected). """

        epi_time_index = self.epiHistory.timeMonitor.get_epidemic_time_index(sim_time_index=sim_time_index)

        if epi_time_index is None:
            a_decision_made = False
        else:
            a_decision_made = True
            self.statusOfIntvs = []
            self.interventionsInEffect = []
            for i in self.interventions:
                # check if the intervention is available
                if i.availCondition is None or (i.availCondition is not None and i.availCondition.value):
                    i.update_switch_status(sim_time_index=sim_time_index, epi_time_index=epi_time_index)

                self.statusOfIntvs.append(i.switchValue)
                if i.switchValue == 1:
                    self.interventionsInEffect.append(i)

        return a_decision_made

    def record_decision_during_past_obs_period(self):
        self.statusOfIntvsOverPastObsPeriods.append(self.statusOfIntvs)

    def record_decision_during_this_sim_outputs(self):

        self.statusOfIntvsOverPastSimOutPeriods.append(self.statusOfIntvs)

    def get_dic_of_intervention_utilization(self, delta_t):
        """
        :return: (dictionary) with the names of interventions as keys
                and their utilization after warmup as values
        """
        result = dict()
        for i in self.interventions:
            result['Duration of ' + i.name + ' (after epidemic warm-up)'] = i.tIndicesInUse*delta_t

        return result


class _Intervention:

    def __init__(self, name, decision_rule=None, availability_condition=None):

        if decision_rule is not None:
            assert isinstance(decision_rule, _DecisionRule)
        else:
            decision_rule = PredeterminedDecisionRule(predetermined_switch_value=1)
        if availability_condition is not None:
            assert isinstance(availability_condition, _Condition)

        self.name = name
        self.decisionRule = decision_rule
        self.availCondition = availability_condition
        self.switchValue = None
        self.ifEverSwitchedOn = None
        self.ifEverSwitchedOff = None
        self.timeMonitor = None  # to access the epidemic time and whether the warm-up period has ended

        self.tIndicesInUse = 0
        self.tIndexOfLastChange = 0
        self.parCostPerUnitOfTime = None

    def initialize(self, delta_t, time_monitor):

        if self.decisionRule is not None:
            self.decisionRule.initialize(delta_t=delta_t)

        self.timeMonitor = time_monitor

    def reset(self):

        if self.decisionRule is not None:
            self.switchValue = self.decisionRule.defaultSwitchValue

        self.ifEverSwitchedOn = True if self.switchValue == 1 else None
        self.ifEverSwitchedOff = None
        self.tIndicesInUse = 0
        self.tIndexOfLastChange = 0

    def setup_econ_outcome(self, par_cost_per_unit_of_time):
        """
        :param par_cost_per_unit_of_time: (Parameter) of the cost that is continuously incurred
        """
        self.parCostPerUnitOfTime = par_cost_per_unit_of_time

    def get_cost_over_delta_t(self, delta_t):
        """ returns: the cost of this intervention during the past deltaT"""

        cost = 0
        if self.parCostPerUnitOfTime is not None:
            if self.switchValue == 1:
                cost = delta_t * self.parCostPerUnitOfTime.value
        return cost

    def update_switch_status(self, sim_time_index=None, epi_time_index=None):

        new_switch_value = self.decisionRule.update_switch_status(epi_time_index=epi_time_index,
                                                                  current_switch_value=self.switchValue)

        if self.ifEverSwitchedOn is None and self.switchValue == 0 and new_switch_value == 1:
            self.ifEverSwitchedOn = True
        if self.ifEverSwitchedOff is None and self.switchValue == 1 and new_switch_value == 0:
            self.ifEverSwitchedOff = True

        if self.switchValue == 0 and new_switch_value == 1:
            self.tIndexOfLastChange = epi_time_index
        elif self.switchValue == 1 and new_switch_value == 0:
            self.update_time_in_use(sim_time_index=sim_time_index, epi_time_index=epi_time_index)
            self.tIndexOfLastChange = epi_time_index

        self.switchValue = new_switch_value

    def add_decision_rule(self, decision_rule):
        assert isinstance(decision_rule, _DecisionRule)
        self.decisionRule = decision_rule
        self.switchValue = self.decisionRule.defaultSwitchValue

    def add_availability_condition(self, availability_condition):
        assert isinstance(availability_condition, _Condition)
        self.availCondition = availability_condition

    def update_time_in_use(self, sim_time_index, epi_time_index):
        # find time it has been in use
        if self.switchValue == 1 and self.timeMonitor.get_if_sim_time_passed_warm_up_period(sim_time_index):
            t0 = max(self.tIndexOfLastChange, self.timeMonitor.nDeltaTsInWarmUpPeriod)
            self.tIndicesInUse += max(epi_time_index - t0, 0)


class InterventionAffectingContacts(_Intervention):

    def __init__(self, name, par_perc_change_in_contact_matrix, decision_rule=None):

        _Intervention.__init__(self, name=name, decision_rule=decision_rule)
        self.parPercChangeInContactMatrix = par_perc_change_in_contact_matrix


class InterventionAffectingEvents(_Intervention):

    def __init__(self, name, decision_rule=None):

        _Intervention.__init__(self, name=name, decision_rule=decision_rule)


class _DecisionRule:
    """ base class for decision rules """

    def __init__(self, default_switch_value):

        self.defaultSwitchValue = default_switch_value

    def update_switch_status(self, epi_time_index=None, current_switch_value=None):
        pass

    def initialize(self, delta_t):
        pass


class PredeterminedDecisionRule(_DecisionRule):
    """ decision rule for fixed actions """

    def __init__(self, predetermined_switch_value):

        _DecisionRule.__init__(self, default_switch_value=predetermined_switch_value)

    def update_switch_status(self, epi_time_index=None, current_switch_value=None):
        return self.defaultSwitchValue


class TimeBasedDecisionRule(_DecisionRule):
    """ decision rule for decision making based on time """

    def __init__(self, time_to_turn_on, time_to_turn_off):

        _DecisionRule.__init__(self, default_switch_value=0)

        self.timeToTurnOn = time_to_turn_on
        self.timeToTurnOff = time_to_turn_off
        self.tIndexToTurnOn = None
        self.tIndexToTurnOff = None

    def initialize(self, delta_t):
        self.tIndexToTurnOn = self.timeToTurnOn / delta_t
        self.tIndexToTurnOff = self.timeToTurnOff / delta_t

    def update_switch_status(self, epi_time_index=None, current_switch_value=None):

        if self.tIndexToTurnOn <= epi_time_index < self.tIndexToTurnOff:
            return 1
        else:
            return 0


class ConditionBasedDecisionRule(_DecisionRule):
    """ decision rule for decision making based on certain conditions """

    def __init__(self, default_switch_value, condition_to_turn_on, condition_to_turn_off):

        _DecisionRule.__init__(self, default_switch_value=default_switch_value)

        self.conditionToTurnOn = condition_to_turn_on
        self.conditionToTurnOff = condition_to_turn_off

    def update_switch_status(self, epi_time_index=None, current_switch_value=None):

        result = current_switch_value
        if current_switch_value == 0:
            if self.conditionToTurnOn.value:
                result = 1
        else:
            if self.conditionToTurnOff.value:
                result = 0
        return result


class DynamicDecisionRule(_DecisionRule):
    """ decision rule for dynamic decision making """

    def __init__(self, approx_decision_maker, continuous_features=None, indicator_features=None):

        assert isinstance(approx_decision_maker, _ApproxDecisionMaker)
        if continuous_features is None and indicator_features is None:
            raise ValueError('At least one continuous feature or one indicator feature should be provided.')

        _DecisionRule.__init__(self, default_switch_value=0)

        self.approxDecisionMaker = approx_decision_maker
        self.continuousFeatures = [] if continuous_features is None else continuous_features
        self.indicatorFeatures = [] if indicator_features is None else indicator_features

    def update_switch_status(self, epi_time_index=None, current_switch_value=None):

        # find feature values
        continuous_feature_values = []
        for f in self.continuousFeatures:
            continuous_feature_values.append(f.value)
        indicator_feature_values = []
        for f in self.indicatorFeatures:
            indicator_feature_values.append(f.value)

        # find the switch value (assumes that there is only 1 action)
        return self.approxDecisionMaker.make_a_decision(
            continuous_feature_values=continuous_feature_values,
            indicator_feature_values=indicator_feature_values)[0]
