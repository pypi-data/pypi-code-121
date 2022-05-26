from inspect import signature

from deampy.in_out_functions import write_dictionary_to_csv

from apacepy.inputs import ModelSettings
from apacepy.multi_epidemics import MultiEpidemics
from apacepy.support import extend_a_dict


class ScenarioSimulator:

    def __init__(self, model_settings, scenario_names, variable_names, scenario_definitions):
        """
        :param model_settings: model settings
        :param scenario_names: (list) of scenario names
        :param variable_names: (list) of variable names that define the scenarios
        :param scenario_definitions: (list) of scenarios. Each scenario is a list of values (float, string, etc.)
        """

        assert isinstance(model_settings, ModelSettings)

        if len(scenario_names) != len(scenario_definitions):
            raise ValueError('There should be an equal number of scenario names and scenario definitions.')
        for s in scenario_definitions:
            if len(s) != len(variable_names):
                raise ValueError('A scenario definition should have the same number of variables as variable names.\n'
                                 'Variable names: {} \nScenario definitions: {}'
                                 .format(variable_names, s))

        self.modelSets = model_settings
        self.scenariosNames = scenario_names
        self.varNames = variable_names
        self.scenarioDefinitions = scenario_definitions
        self.results = dict()

    def simulate(self, function_to_populate_model, num_of_sims=1, if_run_in_parallel=False,
                 seeds=None, weights=None, sample_seeds_by_weights=True,
                 print_summary_stats=False, sig_digits=5, interval='p'):
        """
        :param function_to_populate_model: (function) function to build the epidemic model
                (should take 'model' as an argument)
        :param num_of_sims: (int) number of epidemics to simulate
        :param if_run_in_parallel: (bool) set to True to run simulations in parallel
        :param seeds: (list) of seeds
        :param weights: (list) probability weights over seeds
        :param sample_seeds_by_weights: (bool) set to False to only use seeds with positive weights
        :param print_summary_stats: (bool) set to True to print the summary statistics of each scenario in the console
        :param sig_digits: (int) number of significant digits to use when printing statistics in the console
        :param interval: (string) 'c' for confidence interval and 'p' for percentile interval
        """

        # dictionary (with one key) of scenario names
        dict_of_scenario_names = dict()
        dict_of_scenario_names['Scenarios'] = []

        # crete the dictionary of columns representing scenario variables
        dict_of_variables = dict()
        # scenario variable names
        for name in self.varNames:
            dict_of_variables[name] = []
        # values of scenario variables
        for i, scenario_values in enumerate(self.scenarioDefinitions):
            dict_of_scenario_names['Scenarios'].extend([self.scenariosNames[i]]*num_of_sims)

            for j, name in enumerate(self.varNames):
                dict_of_variables[name].extend([scenario_values[j]]*num_of_sims)

        # simulate scenarios
        dict_of_summaries_and_projections = dict()
        n = len(self.scenarioDefinitions)
        for i, variable_values in enumerate(self.scenarioDefinitions):

            # check
            sig = signature(self.modelSets.update_settings)
            sig_list = [key for key in sig.parameters]
            if len(sig.parameters) != len(variable_values):
                raise ValueError("The function 'update_settings' of ModelSettings should have the same number of "
                                 "argument as the number of variables used to define a scenario.\n"
                                 "Number of arguments: {}, number of scenario variables: {}.\n"
                                 "Arguments: {}\nScenario variables:{}"
                                 .format(len(sig.parameters), len(variable_values), sig_list, variable_values))

            # update the model settings for this scenario
            self.modelSets.update_settings(*variable_values)

            # build multiple epidemics
            multi_model = MultiEpidemics(model_settings=self.modelSets)

            # simulate multiple epidemics
            multi_model.simulate(function_to_populate_model=function_to_populate_model,
                                 n=num_of_sims,
                                 seeds=seeds,
                                 weights=weights,
                                 sample_seeds_by_weights=sample_seeds_by_weights,
                                 if_run_in_parallel=if_run_in_parallel)

            # summary and projections
            extend_a_dict(existing_dict=dict_of_summaries_and_projections,
                          new_dict=multi_model.get_dict_summary_and_projections())

            # print
            text = "Scenario '{}' is done... ({} of {})".format(self.scenariosNames[i], i, n)
            if print_summary_stats:
                print('\n', text)
                multi_model.print_summary_stats(interval=interval, sig_digits=sig_digits)
            else:
                print(text)

        # making sure there are the same number of rows for all columns
        n = len(dict_of_summaries_and_projections['ID'])
        for key, value in dict_of_summaries_and_projections.items():
            if len(value) != n:
                raise ValueError("The number of observations for column '{}' is less than expected."
                                 "This might be because the model in "
                                 "some of scenarios didn't include the intervention(s).".format(key))

        # making sure the names are not repeated
        for key in dict_of_variables:
            if key in dict_of_summaries_and_projections:
                raise ValueError("The variable '{}' is also the name of a model outcome. "
                                 "Rename the variable name.".format(key))

        self.results = dict_of_scenario_names | dict_of_variables | dict_of_summaries_and_projections

    def export_results(self, filename='simulated_scenarios.csv'):

        # save
        write_dictionary_to_csv(dictionary=self.results,
                                file_name=filename,
                                directory=self.modelSets.folderToSaveScenarioAnalysis)

