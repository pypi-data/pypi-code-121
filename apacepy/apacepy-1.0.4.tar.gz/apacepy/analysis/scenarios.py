import csv

import deampy.econ_eval as Econ
import deampy.in_out_functions as IO
import deampy.regression_models as Reg
import deampy.statistics as Stat
import matplotlib.pyplot as plt
import numpy as np
from deampy.plots.plot_support import output_figure

plt.rcParams['svg.fonttype'] = 'none'


ALPHA = 0.05    # confidence level
POLY_DEGREES = 2
ERROR_BAR_ALPHA = 0.25


class Scenario:
    def __init__(self, name):
        """
        :param name: scenario's name
        """

        self.name = name
        self.variables = {}     # dictionary of variable values with their name as keys
        self.outcomes = {}      # dictionary of list of outcomes with their names as keys

    def add_variable(self, variable_name, value):
        """
        :param variable_name: (string) variable name
        :param value: value of variable
        """
        self.variables[variable_name] = value

    def add_all_outcomes(self, outcome_name, outcomes):
        """
        :param outcome_name: (string) name of outcome
        :param outcomes: (list) of outcomes
        """
        self.outcomes[outcome_name] = outcomes


class ScenarioDataFrame:
    """ creates a dictionary of all scenarios with scenario names as keys """

    def __init__(self, csv_file_name):
        """
        :param csv_file_name: (string) csv file where scenarios and realizations of outcomes are located
        """

        self.scenarios = {}  # dictionary of all scenarios with scenario names as keys

        # read csv file
        csv_file = open(csv_file_name, "r")
        col_headers = next(csv.reader(csv_file, delimiter=','))
        csv_file.close()

        n_cols = len(col_headers)
        cols = IO.read_csv_cols(file_name=csv_file_name, if_ignore_first_row=True,
                                n_cols=n_cols, if_convert_float=True)

        # parse columns
        row_idx = 0
        col_idx = 0
        scenario_names_and_bounds = []  # stores the name of scenarios and the index of the first row for this scenario
        while col_idx < n_cols:

            # assumes that the scenario names are under "Scenarios" column
            if col_headers[col_idx] == "Scenarios":

                # find the row boundaries of each scenario
                scenario_names_and_bounds = []
                for row_idx, scenario_name in enumerate(cols[col_idx]):
                    if scenario_name not in self.scenarios:
                        self.scenarios[scenario_name] = Scenario(name=scenario_name)
                        scenario_names_and_bounds.append((scenario_name, row_idx))

                scenario_names_and_bounds.append(("dummy", row_idx + 1))
                col_idx += 1

                # store variables
                while col_headers[col_idx] != "ID":
                    for scenario_name, bound in scenario_names_and_bounds[:-1]:
                        self.scenarios[scenario_name].add_variable(variable_name=col_headers[col_idx],
                                                                   value=cols[col_idx][bound])
                    col_idx += 1

            else:
                # store outcomes
                for i in range(len(scenario_names_and_bounds) - 1):
                    scenario_name = scenario_names_and_bounds[i][0]
                    outcomes = cols[col_idx][scenario_names_and_bounds[i][1]:scenario_names_and_bounds[i+1][1]]
                    self.scenarios[scenario_name].add_all_outcomes(outcome_name=col_headers[col_idx],
                                                                   outcomes=outcomes)
                col_idx += 1

    def get_mean_interval(self, scenario_name, outcome_name, multiplier=1, interval_type='p',
                          deci=None, sig_digits=None, form=None):
        """
        :return: mean and percentile interval of the selected outcome for the selected scenario
        """

        stat = Stat.SummaryStat(self.scenarios[scenario_name].outcomes[outcome_name])
        return stat.get_formatted_mean_and_interval(
            interval_type=interval_type, deci=deci, sig_digits=sig_digits, form=form, multiplier=multiplier)

    def get_relative_diff_mean_interval(self, scenario_name_base, scenario_names, outcome_name,
                                        order=0, deci=0, form=None):
        """
        :param scenario_name_base:
        :param scenario_names:
        :param outcome_name:
        :param order: set to 0 to calculate (new-base)/base and to 1 to calculate (base-new)/base
        :param deci:
        :param form:
        :return: dictionary of mean and percentile interval of the relative difference of the selected outcom
        """

        if type(scenario_names) is not list:
            scenario_names = [scenario_names]

        dict_mean_pi = {}
        for name in scenario_names:
            ratio_state = Stat.RelativeDifferencePaired(
                name='',
                x=self.scenarios[name].outcomes[outcome_name],
                y_ref=self.scenarios[scenario_name_base].outcomes[outcome_name],
                order=order)

            dict_mean_pi[name] = ratio_state.get_formatted_mean_and_interval(
                interval_type='p', deci=deci, form=form)

        if len(scenario_names) == 1:
            return dict_mean_pi[scenario_names[0]]
        else:
            return dict_mean_pi

    def plot_relative_diff_by_scenario(self,
                                       scenario_name_base,
                                       scenario_names,
                                       outcome_names,
                                       title=None, x_label=None, x_range=None,
                                       y_labels=None,
                                       markers=('o', 'D'),
                                       colors=('red', 'blue'),
                                       legend=('morbidity', 'mortality'),
                                       distance_from_horizontal_axes=0.5,
                                       fig_size=(4.6, 3.2),
                                       distance_labels_y_axis=100,
                                       filename=None,
                                       ):

        bar_position = []
        if len(outcome_names) > 2:
            raise ValueError('Only up to 2 outcomes could be displayed.')
        elif len(outcome_names) == 2:
            bar_position = [-0.15, 0.15]
        else:
            bar_position = [0]

        plt.rc('font', size=8)  # fontsize of texts
        fig, ax = plt.subplots(figsize=fig_size)

        # find y-values
        y_values = np.arange(len(scenario_names))

        # build series to display
        for k, outcome_name in enumerate(outcome_names):
            list_mean_pi = self.get_relative_diff_mean_interval(scenario_name_base, scenario_names, outcome_name)

            # find x-values
            x_values = []
            x_err_l = []
            x_err_u = []
            for scenario_name in scenario_names:
                x_value = list_mean_pi[scenario_name][0]
                x_pi = list_mean_pi[scenario_name][1]
                x_values.append(100*x_value)
                x_err_l.append(100*(x_value-x_pi[0]))
                x_err_u.append(100*(x_pi[1]-x_value))

            ax.errorbar(x_values, y_values + bar_position[k], xerr=[x_err_l, x_err_u],
                        fmt=markers[k], ecolor=colors[k],
                        elinewidth=1.5, capsize=0, markersize=6, markerfacecolor='white',
                        markeredgecolor=colors[k], markeredgewidth=1.5)

        ax.set_yticks(y_values)
        if y_labels is None:
            ax.set_yticklabels(scenario_names)
        else:
            ax.set_yticklabels(y_labels, horizontalalignment='left')

        ax.yaxis.set_tick_params(pad=distance_labels_y_axis)

        ax.set_ylim(-distance_from_horizontal_axes, len(scenario_names) - 1 + distance_from_horizontal_axes)

        ax.invert_yaxis()  # labels read top-to-bottom
        if x_label:
            ax.set_xlabel(x_label)
        if title:
            ax.set_title(title)
        if x_range:
            ax.set_xlim(x_range)
        ax.legend(legend, fontsize='small')
        plt.axvline(x=0, linestyle='--', color='black', linewidth=1)
        plt.tight_layout()
        if filename is None:
            filename = 'RelativeDifference.png'

        plt.savefig(filename, dpi=300)


    def get_mean_interval_of_loss_in_nmb(self, scenario_name,
                                         cost_outcome_name, effect_outcome_name, wtp_value,
                                         cost_multiplier=1, effect_multiplier=1,
                                         interval_type='p', deci=None, sig_digits=None, form=None):
        """
        :return: mean and percentile interval of the selected outcome for the selected scenario
        """

        loss_in_nmb = wtp_value * self.scenarios[scenario_name].outcomes[effect_outcome_name] * effect_multiplier \
                      + self.scenarios[scenario_name].outcomes[cost_outcome_name] * cost_multiplier
        stat = Stat.SummaryStat(loss_in_nmb)
        return stat.get_formatted_mean_and_interval(
            interval_type=interval_type, deci=deci, sig_digits=sig_digits, form=form)

    def print_cost_effect_loss_in_nmb(self, cost_outcome_name, effect_outcome_name, wtp_value,
                                            cost_multiplier=1, effect_multiplier=1, sig_digits=None):

        for key in self.scenarios:
            print(key + ' |',
                  self.get_mean_interval(
                      scenario_name=key,
                      outcome_name=cost_outcome_name,
                      interval_type='n',
                      sig_digits=sig_digits,
                      multiplier=cost_multiplier) + ' |',
                  self.get_mean_interval(
                      scenario_name=key,
                      outcome_name=effect_outcome_name,
                      interval_type='n',
                      sig_digits=sig_digits,
                      multiplier=effect_multiplier) + ' |',
                  self.get_mean_interval_of_loss_in_nmb(
                      scenario_name=key,
                      cost_outcome_name=cost_outcome_name,
                      effect_outcome_name=effect_outcome_name,
                      cost_multiplier=cost_multiplier,
                      effect_multiplier=effect_multiplier,
                      wtp_value=wtp_value,
                      interval_type='n',
                      sig_digits=sig_digits)
                  )

class _Condition:
    # super class to define conditions on variables or outcomes

    def __init__(self, minimum=0, maximum=1, values=None,
                 if_included_in_label=False, label_format='', label_rules=None):
        """
        :param minimum: minimum acceptable value for this variable/outcome
        :param maximum: maximum acceptable value for this variable/outcome
        :param values: (tuple) of acceptable values
        :param if_included_in_label: if the value of this variable/outcome should be included in labels
                to display on CE plane
        :param label_format: (string) format of this variable/outcome values to display on CE plane (e.g. '{:.2f}')
        :param label_rules: (list of tuples): to convert variable/outcome's value to labels
                for example: [(0, 'A'), (1, 'B')] replaces variable/outcome
                value 0 with A and 1 with B when creating labels
        """
        self.min = minimum
        self.max = maximum

        if values is not None:
            if isinstance(values, list):
                self.values = values
            else:
                self.values = [values]
        else:
            self.values = None

        self.ifIncludedInLabel = if_included_in_label
        self.labelFormat = label_format
        self.labelRules = label_rules


class ConditionOnVariable(_Condition):
    def __init__(self, var_name, minimum=float('-inf'), maximum=float('inf'), values=None,
                 if_included_in_label=False, label_format='', label_rules=None):
        """
        :param var_name: variable name as appears in the scenario csv file
        :param minimum: minimum acceptable value for this variable/outcome
        :param maximum: maximum acceptable value for this variable/outcome
        :param values: (tuple) of acceptable values
        :param if_included_in_label: if the value of this variable/outcome should be included in labels
                to display on CE plane
        :param label_format: (string) format of this variable/outcome values to display on CE plane
                for example: '{:.1%}' or '{:.2f}'
        :param label_rules: (list of tuples): to convert variable/outcome's value to labels
                for example: [(0, 'A'), (1, 'B')] replaces variable/outcome
                value 0 with A and 1 with B when creating labels
        """
        _Condition.__init__(self, minimum=minimum, maximum=maximum, values=values,
                            if_included_in_label=if_included_in_label,
                            label_format=label_format,
                            label_rules=label_rules)
        self.varName = var_name

    def get_label(self, value):
        """ :returns the label associated to this value of the parameter """

        for rule in self.labelRules:
            if rule[0] == value:
                return rule[1]


class ConditionOnOutcome(_Condition):
    def __init__(self, outcome_name, minimum=float('-inf'), maximum=float('inf'), values=None,
                 if_included_in_label=False, label_format='', label_rules=None):
        """
        :param outcome_name: name of the outcome in the scenario csv file
        :param minimum: minimum acceptable value for this variable/outcome
        :param maximum: maximum acceptable value for this variable/outcome
        :param values: (tuple) of acceptable values
        :param if_included_in_label: if the value of this variable/outcome should be included in labels
                to display on CE plane
        :param label_format: (string) format of this variable/outcome values to display on CE plane
                for example: '{:.1%}'
        :param label_rules: (list of tuples): to convert variable/outcome's value to labels
                for example: [(0, 'A'), (1, 'B')] replaces variable/outcome
                value 0 with A and 1 with B when creating labels
        """
        _Condition.__init__(self, minimum=minimum, maximum=maximum, values=values,
                            if_included_in_label=if_included_in_label,
                            label_format=label_format,
                            label_rules=label_rules)
        self.outcomeName = outcome_name


class SetOfScenarios:
    """ a set of scenarios that meet certain conditions """

    def __init__(self,
                 name,
                 scenario_df,
                 color,
                 marker='o',
                 x_y_labels=None,
                 scenario_names=None,
                 conditions_on_variables=(),
                 conditions_on_outcomes=(),
                 if_find_frontier=True,
                 if_show_fitted_curve=True,
                 regression_type='linear',
                 labels_shift_x=0,
                 labels_shift_y=0,
                 ):
        """
        :param name: (string) name of this set of strategies
        :param scenario_df: (ScenarioDataFrame) scenario data frame to pull the data from
        :param color: (string) color code of this series on the CE plane
        :param marker: (string) markers used for this series on the CE plane
        :param x_y_labels: (list of strings) labels to display next to points on the CE plane
        :param scenario_names: (list of strings) names of scenarios to include in this set
        :param conditions_on_variables: (list of ConditionOnVariable) to decide which scenarios to include
                based on variable values
        :param conditions_on_outcomes: (list of ConditionOnOutcome) to decide which scenarios to include
                based on outcome values
        :param if_find_frontier: (bool) select True if CE frontier should be calculated
        :param if_show_fitted_curve: (bool) set True to display a fitted curve
        :param regression_type: (string) 'linear', 'exponential' or 'power'
        :param labels_shift_x: (float) to shift labels horizontally
        :param labels_shift_y: (float) to shift labels vertically
        """

        assert isinstance(scenario_df, ScenarioDataFrame)
        assert regression_type in ('linear', 'exponential', 'power')

        self.name = name
        self.ifPopulated = False
        self.scenarioDF = scenario_df
        self.color = color
        self.marker = marker
        self.ifFindFrontier = if_find_frontier

        # inclusion criteria
        self.scenarioNames = scenario_names
        self.varConditions = conditions_on_variables
        self.outcomeConditions = conditions_on_outcomes

        self.labelsShiftX = labels_shift_x
        self.labelsShiftY = labels_shift_y

        # delta costs and delta effects
        self.allDeltaCosts = np.array([])
        self.allDeltaEffects = np.array([])

        # (x, y) values
        self.xValues = []
        self.yValues = []
        self.xValuesByScenario = []
        self.yValuesByScenario = []
        # confidence or prediction intervals
        self.xIntervals = []
        self.yIntervals = []

        # labels to display next to points
        self.xyLabelsProvided = True if x_y_labels is not None and len(x_y_labels) > 0 else False
        self.xyLabels = x_y_labels

        # frontier values
        self.frontierXValues = []
        self.frontierYValues = []
        self.frontierLabels = []
        # confidence or prediction intervals
        self.frontierXIntervals = []
        self.frontierYIntervals = []

        self.strategies = []    # list of strategies on this series
        self.CEA = None
        self.CBA = None
        self.legend = []

        self.ifShowFittedCurve = if_show_fitted_curve
        self.regressionType = regression_type
        self.fittedCurves = []  # curves fitted to paired (cost, effect) points of strategies
        self.fittedCurve = None  # one curve fitted to the (average cost, average effect) of strategies

    def if_acceptable(self, scenario):
        """ :returns True if this scenario meets the conditions to be on this series """

        if self.scenarioNames is not None:
            # if the name of this scenario is included
            if scenario.name in self.scenarioNames:
                return True
        else:
            for condition in self.varConditions:
                if condition.values is None:
                    if scenario.variables[condition.varName] < condition.min \
                            or scenario.variables[condition.varName] > condition.max:
                        return False
                else:
                    if not(scenario.variables[condition.varName] in condition.values):
                        return False

            for condition in self.outcomeConditions:
                if condition.values is None:
                    # mean of this outcome
                    mean = Stat.SummaryStat(
                        name=condition.outcomeName,
                        data=scenario.outcomes[condition.outcomeName]).get_mean()

                    if mean < condition.min or mean > condition.max:
                        return False

        return True

    def build_CE_curve(self,
                       if_remove_base_scenario=False,
                       health_measure='d',
                       save_cea_results=False,
                       interval_type='n',
                       effect_multiplier=1,
                       cost_multiplier=1,
                       switch_cost_effect_on_figure=False,
                       wtp_range=None):

        # cost-effectiveness analysis
        self.CEA = Econ.CEA(self.strategies,
                            if_paired=True,
                            health_measure=health_measure)

        # CBA
        if wtp_range is not None:
            self.CBA = Econ.CBA(self.strategies,
                                wtp_range=wtp_range,
                                if_paired=True,
                                health_measure=health_measure)

        # if to save the results of the CEA
        if save_cea_results:
            self.CEA.build_CE_table(interval_type=interval_type,
                                    file_name='CEA Table-'+self.name+'.csv',
                                    cost_multiplier=cost_multiplier,
                                    effect_multiplier=effect_multiplier,
                                    effect_digits=0)

        # if the CE frontier should be calculated
        if self.ifFindFrontier:
            # find the (x, y)'s of strategies on the frontier
            for idx, strategy in enumerate(self.CEA.get_strategies_on_frontier()):
                if switch_cost_effect_on_figure:
                    self.frontierXValues.append(strategy.dCost.get_mean() * cost_multiplier)
                    self.frontierYValues.append(strategy.dEffect.get_mean() * effect_multiplier)
                else:
                    self.frontierXValues.append(strategy.dEffect.get_mean() * effect_multiplier)
                    self.frontierYValues.append(strategy.dCost.get_mean() * cost_multiplier)

                self.frontierLabels.append(strategy.name)

                if interval_type != 'n':
                    effect_interval = strategy.dEffect.get_interval(interval_type=interval_type,
                                                                    alpha=ALPHA,
                                                                    multiplier=effect_multiplier)
                    cost_interval = strategy.dCost.get_interval(interval_type=interval_type,
                                                                alpha=ALPHA,
                                                                multiplier=effect_multiplier)
                    if switch_cost_effect_on_figure:
                        self.frontierYIntervals.append(effect_interval)
                        self.frontierXIntervals.append(cost_interval)
                    else:
                        self.frontierXIntervals.append(effect_interval)
                        self.frontierYIntervals.append(cost_interval)

        # find the (x, y) values of strategies to display on CE plane
        if not self.xyLabelsProvided:
            self.xyLabels = []
        for strategy in self.CEA.strategies:
            # if base strategy (the first strategy) should be removed from the cost-effectiveness plot
            if if_remove_base_scenario and strategy.idx == 0:
                continue
            if switch_cost_effect_on_figure:
                self.allDeltaEffects = np.append(self.allDeltaEffects,
                                                 strategy.dEffectObs * effect_multiplier)
                self.allDeltaCosts = np.append(self.allDeltaCosts,
                                               strategy.dCostObs * cost_multiplier)
                self.xValues.append(strategy.dCost.get_mean() * cost_multiplier)
                self.yValues.append(strategy.dEffect.get_mean() * effect_multiplier)

                self.xValuesByScenario.append(strategy.dCostObs * cost_multiplier)
                self.yValuesByScenario.append(strategy.dEffectObs * effect_multiplier)
            else:
                self.allDeltaEffects = np.append(self.allDeltaEffects,
                                                 strategy.effectObs * effect_multiplier)
                self.allDeltaCosts = np.append(self.allDeltaCosts,
                                               strategy.costObs * cost_multiplier)
                self.xValues.append(strategy.dEffect.get_mean() * effect_multiplier)
                self.yValues.append(strategy.dCost.get_mean() * cost_multiplier)

                self.xValuesByScenario.append(strategy.dEffectObs * effect_multiplier)
                self.yValuesByScenario.append(strategy.dCostObs * cost_multiplier)

            if not self.xyLabelsProvided:
                self.xyLabels.append(strategy.label)

            if interval_type != 'n':
                effect_interval = strategy.dEffect.get_interval(interval_type=interval_type,
                                                                alpha=ALPHA,
                                                                multiplier=effect_multiplier)
                cost_interval = strategy.dCost.get_interval(interval_type=interval_type,
                                                            alpha=ALPHA,
                                                            multiplier=cost_multiplier)
                # print(strategy.name, cost_interval, effect_interval)
                if switch_cost_effect_on_figure:
                    self.yIntervals.append(effect_interval)
                    self.xIntervals.append(cost_interval)
                else:
                    self.xIntervals.append(effect_interval)
                    self.yIntervals.append(cost_interval)

    def fit_curve(self, degree):

        x = np.array(self.xValues)
        y = np.array(self.yValues)
        self.fittedCurve = Reg.SingleVarRegression(x, y, degree=degree)

    def fit_curves(self, degree):

        for i in range(len(self.strategies[0].costObs)):
            x_s = []
            y_s = []
            for j in range(len(self.strategies)-1): # excluding base
                x_s.append(self.xValuesByScenario[j][i])
                y_s.append(self.yValuesByScenario[j][i])

            # fit a function to the curve.
            x = np.array(x_s)
            y = np.array(y_s)

            if len(x) == 0 or len(y) == 0:
                raise ValueError('Error in fitting a curve to ')

            self.fittedCurves.append(Reg.SingleVarRegression(x, y, degree=degree))

    def get_frontier_x_err(self):

        lower_err = [self.frontierXValues[i]-self.frontierXIntervals[i][0] for i in range(len(self.frontierXValues))]
        upper_err = [self.frontierXIntervals[i][1]-self.frontierXValues[i] for i in range(len(self.frontierXValues))]

        return [lower_err, upper_err]

    def get_x_err(self):

        lower_err = [self.xValues[i]-self.xIntervals[i][0] for i in range(len(self.xValues))]
        upper_err = [self.xIntervals[i][1]-self.xValues[i] for i in range(len(self.xValues))]

        return [lower_err, upper_err]

    def get_frontier_y_err(self):

        lower_err = [self.frontierYValues[i] - self.frontierYIntervals[i][0] for i in range(len(self.frontierYValues))]
        upper_err = [self.frontierYIntervals[i][1] - self.frontierYValues[i] for i in range(len(self.frontierYValues))]

        return [lower_err, upper_err]

    def get_y_err(self):

        lower_err = [self.yValues[i] - self.yIntervals[i][0] for i in range(len(self.yValues))]
        upper_err = [self.yIntervals[i][1] - self.yValues[i] for i in range(len(self.yValues))]

        return [lower_err, upper_err]

    @staticmethod
    def populate_sets_of_scenarios(list_of_scenario_sets,
                                   name_of_base_scenario,
                                   effect_outcome,
                                   cost_outcome,
                                   list_if_remove_base_scenario,
                                   health_measure='u',
                                   save_cea_results=False,
                                   interval_type=None,
                                   effect_multiplier=1,
                                   cost_multiplier=1,
                                   switch_cost_effect_on_figure=False,
                                   wtp_range=None):
        """
        :param list_of_scenario_sets: (list) of scenario sets
        :param name_of_base_scenario: (string) name of the base strategy
        :param effect_outcome: (string) name of the effect outcome
        :param cost_outcome: (string) name of the cost outcome
        :param list_if_remove_base_scenario: (list of bool) if to remove the base scenario from
                the cost-effectiveness curve of each scenario set
        :param health_measure: ('d' or 'u') disutility or utility as the measure of effect
        :param save_cea_results: set to True if the CE table should be generated
        :param interval_type: 'c' for confidence interval and 'p' for percentile interval
        :param effect_multiplier: (float) to multiple the effect estimates by
        :param cost_multiplier: (float) to multiple the cost estimates by
        :param switch_cost_effect_on_figure: displays cost on the x-axis and effect on the y-axis
        :param wtp_range: (tuple) (min wtp, max wtp) for net monetary benefit analysis
        """

        # populate scenario sets to display on the cost-effectiveness plane
        for i, scenario_set in enumerate(list_of_scenario_sets):

            # if this scenario set is already populated, skip
            if scenario_set.ifPopulated:
                continue

            # create the base strategy
            scn = scenario_set.scenarioDF.scenarios[name_of_base_scenario]
            base_strategy = Econ.Strategy(
                name=name_of_base_scenario,
                label='',
                cost_obs=scn.outcomes[cost_outcome],
                effect_obs=scn.outcomes[effect_outcome],
                color=scenario_set.color
            )

            # add base
            scenario_set.strategies = [base_strategy]
            # add other scenarios
            for key, scenario in scenario_set.scenarioDF.scenarios.items():
                # add only non-Base strategies that can be on this series
                if scenario.name != name_of_base_scenario and scenario_set.if_acceptable(scenario):

                    # find labels of each strategy
                    label_list = []
                    for varCon in scenario_set.varConditions:
                        if varCon.ifIncludedInLabel:

                            # value of this variable
                            value = scenario.variables[varCon.varName]
                            # if there is not label rules
                            if varCon.labelRules is None:
                                if varCon.labelFormat == '':
                                    label_list.append(str(value)+',')
                                else:
                                    label_list.append(varCon.labelFormat.format(value) + ', ')
                            else:
                                label = varCon.get_label(value)
                                if label == '':
                                    pass
                                else:
                                    label_list.append(label + ', ')

                    for outcomeCon in scenario_set.outcomeConditions:
                        if outcomeCon.ifIncludedInLabel:

                            # value of this variable
                            value = Stat.SummaryStat(name=outcomeCon.outcomeName,
                                                     data=scenario.outcomes[outcomeCon.outcomeName]).get_mean()
                            # if there is not label rules
                            if outcomeCon.labelRules is None:
                                if outcomeCon.labelFormat == '':
                                    label_list.append(str(value)+',')
                                else:
                                    label_list.append(outcomeCon.labelFormat.format(value) + ', ')
                            else:
                                label = outcomeCon.get_label(value)
                                if label == '':
                                    pass
                                else:
                                    label_list.append(label + ', ')

                    label = ''.join(str(x) for x in label_list)

                    if len(label) > 0:
                        if label[-1] == ' ' or label[-1] == ',':
                            label = label[:-1]
                        if label[-1] == ' ' or label[-1] == ',':
                            label = label[:-1]

                    # legends
                    scenario_set.legend.append(label)

                    if scenario_set.xyLabelsProvided:
                        label = scenario_set.xyLabels[i]

                    scenario_set.strategies.append(
                        Econ.Strategy(
                            name=scenario.name,
                            label=label,
                            cost_obs=scenario.outcomes[cost_outcome],
                            effect_obs=scenario.outcomes[effect_outcome],
                            color=scenario_set.color)
                    )

            # do CEA on this series
            scenario_set.build_CE_curve(if_remove_base_scenario=list_if_remove_base_scenario[i],
                                        health_measure=health_measure,
                                        save_cea_results=save_cea_results,
                                        interval_type=interval_type,
                                        effect_multiplier=effect_multiplier,
                                        cost_multiplier=cost_multiplier,
                                        switch_cost_effect_on_figure=switch_cost_effect_on_figure,
                                        wtp_range=wtp_range)

            scenario_set.ifPopulated = True

    @staticmethod
    def plot_sub_fig(ax, list_of_scenario_sets,
                     title,
                     show_only_on_frontier=False,
                     x_range=None,
                     y_range=None,
                     show_error_bars=False,
                     wtp_multiplier=1):

        incr_eff_life = []

        for i, ser in enumerate(list_of_scenario_sets):

            # if only points on frontier should be displayed
            if show_only_on_frontier:
                # scatter plot for points on the frontier
                ax.scatter(ser.frontierXValues, ser.frontierYValues,
                           color=ser.color, marker=ser.marker, alpha=0.5, label=ser.name)
                # line plot for frontier line
                ax.plot_trajectories(ser.frontierXValues, ser.frontierYValues, color=ser.color, alpha=0.5)

                # error bars
                if show_error_bars:
                    ax.errorbar(ser.frontierXValues, ser.frontierYValues,
                                xerr=ser.get_frontier_x_err(),
                                yerr=ser.get_frontier_y_err(),
                                fmt='none', color='k', linewidth=1, alpha=ERROR_BAR_ALPHA)

                # y-value labels
                for j, txt in enumerate(ser.frontierLabels):
                    if txt != 'Base':
                        ax.annotate(
                            txt,
                            (ser.frontierXValues[j] + ser.labelsShiftX,
                             ser.frontierYValues[j] + ser.labelsShiftY),
                            color=ser.color,
                        )

            else:  # show all points

                # scatter plot for all points
                ax.scatter(ser.xValues, ser.yValues,
                           color=ser.color, marker=ser.marker, alpha=0.5, zorder=10, s=15, label=ser.name)
                # ax.scatter(ser.allDeltaEffects, ser.allDeltaCosts, color=ser.color, alpha=.5,
                # zorder=10, s=5, label=ser.name)
                # line plot for frontier line
                ax.plot(ser.frontierXValues, ser.frontierYValues, color=ser.color, alpha=0.5)

                # error bars
                if show_error_bars:
                    ax.errorbar(ser.xValues, ser.yValues,
                                xerr=ser.get_x_err(),
                                yerr=ser.get_y_err(),
                                fmt='none', color='k', linewidth=1, alpha=ERROR_BAR_ALPHA, zorder=5)

                if x_range is None:
                    x_range = ax.get_xlim()
                if y_range is None:
                    y_range = ax.get_ylim()

                # y-value labels
                for j in range(len(ser.xValues)):
                    txt = ser.xyLabels[j]
                    if txt != 'Base':
                        ax.annotate(
                            txt,
                            (ser.xValues[j] + ser.labelsShiftX*(x_range[1]-x_range[0]),
                             ser.yValues[j] + ser.labelsShiftY*(y_range[1]-y_range[0])),
                            fontsize=6,
                            color=ser.color,
                        )

                if ser.ifShowFittedCurve:
                    # fit a quadratic function to the curve.
                    y = np.array(ser.yValues)  # allDeltaCosts)
                    x = np.array(ser.xValues)  # allDeltaEffects)
                    if len(x) == 0 or len(y) == 0:
                        raise ValueError('Error in fitting a curve to ' + ser.name)
                    if ser.regressionType == 'linear':
                        reg = Reg.PolyRegression(x, y, degree=POLY_DEGREES)
                        # print derivatives at
                        print()
                        print(title, ' | ', ser.name)
                        print('WTP at min dCost', wtp_multiplier * reg.get_derivative(x=ser.xValues[-1]))
                        root = None
                        try:
                            root = max(reg.get_roots())
                            print('WTP at dCost = 0:', wtp_multiplier * reg.get_derivative(x=root))
                        except ValueError:
                            pass
                        print('WTP at max dCost:', wtp_multiplier * reg.get_derivative(x=ser.xValues[0]))

                        # store root
                        incr_eff_life.append(root)
                        if 0 < i < len(incr_eff_life) and not np.iscomplex(root):
                            print('Increase in effective life of A and B:',
                                  round(incr_eff_life[i] - incr_eff_life[0], 2))

                    elif ser.regressionType == 'exponential':
                        reg = Reg.ExpRegression(x, y, if_c0_zero=True, p0=(0.5, 0.005))
                    elif ser.regressionType == 'power':
                        reg = Reg.PowerRegression(x, y, if_c0_zero=True, p0=(1, 0.001))

                    xs = np.linspace(min(x), max(x), 50)
                    predicted = reg.get_predicted_y(xs)
                    # iv_l, iv_u = poly_reg.get_predicted_y_CI(xs)

                    ax.plot(xs, predicted, '--', linewidth=1, color=ser.color)  # results.fittedvalues

                    # # if show error region:
                    # show_error_region = False
                    # if show_error_region:
                    #     ax.plot(xs, iv_u, '-', color=ser.color, linewidth=0.5, alpha=0.1)  # '#E0EEEE'
                    #     ax.plot(xs, iv_l, '-', color=ser.color, linewidth=0.5, alpha=0.1)
                    #     ax.fill_between(xs, iv_l, iv_u, linewidth=1, color=ser.color, alpha=0.05)

        ax.set_title(title)
        if len(list_of_scenario_sets) > 1:
            ax.legend(loc=2, fontsize='small')

        # x and y ranges
        if x_range is not None:
            ax.set_xlim(x_range)
        if y_range is not None:
            ax.set_ylim(y_range)

        # origin
        ax.axvline(x=0, linestyle='-', color='black', linewidth=0.4)
        ax.axhline(y=0, linestyle='-', color='black', linewidth=0.4)

    @staticmethod
    def plot_list_of_scenario_sets(list_of_scenario_sets, x_label, y_label, title,
                                   show_only_on_frontier=False,
                                   x_range=None,
                                   y_range=None,
                                   show_error_bars=False,
                                   wtp_multiplier=1,
                                   fig_size=None,
                                   l_b_r_t=None,
                                   file_name=None):

        fig = plt.figure(figsize=fig_size)
        ax = fig.add_subplot(111)

        SetOfScenarios.plot_sub_fig(ax=ax, list_of_scenario_sets=list_of_scenario_sets,
                                    title=title,
                                    show_only_on_frontier=show_only_on_frontier,
                                    x_range=x_range,
                                    y_range=y_range,
                                    show_error_bars=show_error_bars,
                                    wtp_multiplier=wtp_multiplier)

        # labels
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        #plt.tight_layout()
        if l_b_r_t is not None:
            fig.subplots_adjust(left=l_b_r_t[0],
                                bottom=l_b_r_t[1],
                                right=l_b_r_t[2],
                                top=l_b_r_t[3],)

        output_figure(plt=fig, filename=file_name)

    @staticmethod
    def multi_plot_scenario_sets(list_of_plots,
                                 list_of_titles,
                                 x_label, y_label,
                                 file_name,
                                 show_only_on_frontier=False,
                                 x_range=None,
                                 y_range=None,
                                 show_error_bars=False,
                                 wtp_multiplier=1,
                                 fig_size=(7.5, 3),
                                 l_b_r_t=None):

        # set default properties
        plt.rc('font', size=8)  # fontsize of texts
        plt.rc('axes', titlesize=8)  # fontsize of the figure title
        labels = ['A)', 'B)', 'C)', 'D)']

        n_cols = len(list_of_plots)
        f, axarr = plt.subplots(1, n_cols, sharey=True, figsize=fig_size)

        # this is to add the common x and y label
        f.add_subplot(111, frameon=False)
        plt.tick_params(labelcolor='none', length=0, top='off', bottom='off', left='off', right='off', pad=10)
        # plt.grid(False)
        plt.xlabel(x_label)
        axarr[0].set_ylabel(y_label)

        for i, fig in enumerate(list_of_plots):

            axarr[i].set_title(labels[i], loc='left', fontweight='bold')

            # plot
            SetOfScenarios.plot_sub_fig(ax=axarr[i],
                                        list_of_scenario_sets=fig,
                                        title=list_of_titles[i],
                                        show_only_on_frontier=show_only_on_frontier,
                                        x_range=x_range,
                                        y_range=y_range,
                                        show_error_bars=show_error_bars,
                                        wtp_multiplier=wtp_multiplier)

        if l_b_r_t is not None:
            plt.tight_layout()
            plt.subplots_adjust(left=l_b_r_t[0],
                                bottom=l_b_r_t[1],
                                right=l_b_r_t[2],
                                top=l_b_r_t[3],
                                wspace=0.1, hspace=0)
        else:
            plt.tight_layout()

        plt.savefig(file_name, dpi=600)
        # plt.show()

    @staticmethod
    def get_expected_diff_from_origin(list_of_scenario_sets,
                                      degree=2):

        # fit curves
        for set_of_scenario in list_of_scenario_sets:
            #set_of_scenario.fit_curves(degree=degree)
            set_of_scenario.fit_curve(degree=degree)

        # expected difference
        crossing_x_axis = []
        diffs = []

        for i in range(len(list_of_scenario_sets)):
            selected_root = max(list_of_scenario_sets[i].fittedCurve.get_zero())
            crossing_x_axis.append(selected_root)
            diffs.append(crossing_x_axis[i]-crossing_x_axis[0])

        return diffs

        # # difference by curve
        # crossings = []
        # for i in range(len(list_of_scenario_sets)):
        #     row = []
        #     for j in range(len(list_of_scenario_sets[i].fittedCurves)):
        #         row.append(list_of_scenario_sets[i].fittedCurves[j].get_zero()[degree - 1])
        #     print(row)
        #     crossings.append(row)
        #
        # for i in range(1, len(crossings)):
        #     stat = Stat.DifferenceStatPaired(name='Diff',
        #                                      x=crossings[i],
        #                                      y_ref=crossings[0])
        #     print(stat.get_mean())


