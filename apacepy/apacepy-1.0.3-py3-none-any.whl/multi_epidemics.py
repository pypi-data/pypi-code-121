import multiprocessing as mp

import numpy as np
from deampy.in_out_functions import delete_files, write_dictionary_to_csv
from deampy.statistics import SummaryStat
from deampy.support.simulation import SeedGenerator
from numpy.random import RandomState

from apacepy.epidemic import EpiModel
from apacepy.inputs import ModelSettings
from apacepy.support import append_to_a_dict


class MultiEpidemics:
    """ simulates multiple epidemic models """

    def __init__(self, model_settings):
        """
        :param model_settings: model settings
        """

        assert isinstance(model_settings, ModelSettings)

        self.modelSets = model_settings        
        self.multiModelOutputs = MultiEpidemicsOutputs()
        self.nTrajsDiscarded = 0

    def simulate(self, function_to_populate_model, n,
                 if_export_trajs=None, trajs_folder=None,
                 seeds=None, weights=None, sample_seeds_by_weights=True,
                 if_run_in_parallel=False, if_run_until_a_feasible_traj=False, max_tries=100):
        """
        :param function_to_populate_model: function to build the epidemic model (should take 'model' as an argument)
        :param n: number of epidemics to simulate
        :param if_export_trajs: (bool) set to True to export simulated trajectories
        :param trajs_folder: (string) folder to store the simulated trajectories to
        :param seeds: (list) of seeds
        :param weights: (list) probability weights over seeds
        :param sample_seeds_by_weights: (bool) set to False to only use seeds with positive weights
        :param if_run_in_parallel: set to True to run models in parallel
        :param if_run_until_a_feasible_traj: (bool) if run until a feasible trajectory is obtained
        :param max_tries: (int) maximum number of simulation runs to try to find a feasible trajectory
        """

        # seeds generator
        seed_generator = SeedGenerator(seeds=seeds, weights=weights)
        seeds = seed_generator.next_seeds(n=n, rng=RandomState(0), sample_by_weight=sample_seeds_by_weights)

        if if_export_trajs is None:
            if_export_trajs = self.modelSets.exportTrajectories
        if trajs_folder is None:
            trajs_folder = self.modelSets.folderToSaveTrajs

        # delete csv files
        delete_files('.csv', path=trajs_folder)

        self.nTrajsDiscarded = 0  # total trajectories discarded to find feasible trajectories

        if not if_run_in_parallel:
            for i in range(n):

                # make an empty epidemic model
                model = EpiModel(id=i, settings=self.modelSets)
                # populate the model according to the function
                function_to_populate_model(model)

                # simulate
                if if_run_until_a_feasible_traj:
                    model.simulate_until_a_feasible_traj(seed=seeds[i], max_tries=max_tries)
                    self.nTrajsDiscarded += model.nTrajsDiscarded
                    print('ID: {}, # discarded: {}, lnl = {}'.format(model.id, model.nTrajsDiscarded, model.lnl[0]))
                else:
                    model.simulate(seed=seeds[i])

                # save trajectories
                if if_export_trajs:
                    model.export_trajectories(folder=trajs_folder, delete_existing_files=False)

                # store outputs
                self.multiModelOutputs.extract_outputs(simulated_model=model,
                                                       store_param_values=self.modelSets.storeParameterValues)
                # reset the model
                model.reset()

        else:  # if run models in parallel
            # create models
            models = []
            for i in range(n):
                model = EpiModel(id=i, settings=self.modelSets)
                models.append(model)

            # create a list of arguments for simulating the cohorts in parallel
            args = [(model,
                     function_to_populate_model,
                     seeds[model.id],
                     if_run_until_a_feasible_traj,
                     max_tries) for model in models]

            # simulate all cohorts in parallel
            n_processes = mp.cpu_count()  # maximum number of processors

            pool = mp.Pool(n_processes)
            simulated_models = pool.starmap(simulate_this_model, args)
            pool.close()

            # save trajectories and record outcomes from simulating all cohorts
            for model in simulated_models:
                self.nTrajsDiscarded += model.nTrajsDiscarded
                if if_export_trajs:
                    model.export_trajectories(folder=trajs_folder, delete_existing_files=False)
                self.multiModelOutputs.extract_outputs(simulated_model=model,
                                                       store_param_values=self.modelSets.storeParameterValues)
                # reset the model
                model.reset()
        # calculate summary statistics on performance_analysis measures
        self.multiModelOutputs.calculate_summary_stats()

    def get_dict_summary_and_projections(self):

        # ID, seed, and run-time
        dict_of_summary = {'ID': self.multiModelOutputs.ids,
                           'Seed': self.multiModelOutputs.seeds,
                           'Run time': self.multiModelOutputs.runTimes
                           }
        # cost and health outcomes
        if self.modelSets.collectEconEval:
            dict_of_summary['Discounted cost'] = self.multiModelOutputs.discountedCosts
            dict_of_summary['Discounted health'] = self.multiModelOutputs.discountedHealths

        # other projected outcomes
        if self.modelSets.storeProjectedOutcomes:
            for key, value in self.multiModelOutputs.dictOfProjectedOutcomes.items():
                dict_of_summary[key] = value

        return dict_of_summary

    def save_summary(self):
        """ exports the summary of simulation into csv files.
            - a file with trajectory id, seeds, discounted health, discounted cost, projected outcomes,
            - a file with parameter values

            To get discounted health and cost, set the collectEconEval attribute of the model settings to True,
            To get projected outcomes, set storeProjectedOutcomes attribute of the model settings to True,
            To get parameter values, set the storeParameterValues attribute of the model settings to True. """

        # summary and projections
        dict_of_summary = self.get_dict_summary_and_projections()

        # save
        write_dictionary_to_csv(dictionary=dict_of_summary,
                                file_name='simulation_summary.csv',
                                directory=self.modelSets.folderToSaveSummary)

        # report sampled parameters
        if self.modelSets.storeParameterValues:
            # ID and seeds
            dict_of_param_values = {'ID': self.multiModelOutputs.ids,
                                    'Seed': self.multiModelOutputs.seeds}

            # parameter values
            for param_name, param_values in self.multiModelOutputs.dictParameterValues.items():
                dict_of_param_values[param_name] = param_values

            # save
            write_dictionary_to_csv(dictionary=dict_of_param_values,
                                    file_name='parameter_values.csv',
                                    directory=self.modelSets.folderToSaveSummary)

    def print_summary_stats(self, wtp=None, health_multiplier=1, cost_multiplier=1, interval='p', sig_digits=5):
        """ prints summary statistics
                (simulation run-time, discounted cost, health, and net monetary benefit, and projected outcomes)
            To get discounted health and cost, set the collectEconEval attribute of the model settings to True,
            To get projected outcomes, set storeProjectedOutcomes attribute of the model settings to True,
            To get get parameter values, set the storeParameterValues attribute of the model settings to True.
        :param wtp: (float) willingness-to-pay value to calculate the discounted loss in net monetary benefit
        :param health_multiplier: (float) to multiply the estimated health by
        :param cost_multiplier: (float) to multiply the estimated cost by
        :param interval: 'p' for percentile interval and 'c' for confidence interval
        :param sig_digits: (int) number of significant digits to use
        """

        # print simulation run time
        print('Simulation run time (seconds):',
              self.multiModelOutputs.statRunTimes.get_formatted_mean_and_interval(
                  interval_type=interval, deci=sig_digits))

        # print economic evaluation outcomes
        if self.modelSets.collectEconEval:
            print('Discounted cost:',
                  self.multiModelOutputs.statCost.get_formatted_mean_and_interval(
                      multiplier=cost_multiplier, interval_type=interval, sig_digits=sig_digits))
            print('Discounted health:',
                  self.multiModelOutputs.statHealth.get_formatted_mean_and_interval(
                      multiplier=health_multiplier, interval_type=interval, sig_digits=sig_digits))
            if wtp is not None:
                stat = self.multiModelOutputs.get_nmb_loss_stat(
                    wtp=wtp, health_multiplier=health_multiplier, cost_multiplier=cost_multiplier)
                print('Discounted loss in net monetary benefit:',
                      stat.get_formatted_mean_and_interval(interval_type=interval, sig_digits=sig_digits))

        # print project outcomes
        for key, value in self.multiModelOutputs.dictOfStatsForProjectedOutcomes.items():
            print(key+': ', value.get_formatted_mean_and_interval(
                interval_type=interval, sig_digits=sig_digits))


class MultiEpidemicsOutputs:
    """ collects the outputs from multiple epidemic models """

    def __init__(self):

        # statistics to collect
        self.ids = []   # ids of simulated epidemics
        self.seeds = []  # random number seeds
        self.ifFeasible = []  # list of feasibility status
        self.runTimes = []  # run times
        self.discountedCosts = []   # discounted costs
        self.discountedHealths = []  # discounted healths
        self.dictOfProjectedOutcomes = dict()  # dictionary of outcomes collected after the warm-up period

        # summary statistics to calculate mean and confidence interval
        self.statRunTimes = None
        self.statCost = None
        self.statHealth = None
        self.dictOfStatsForProjectedOutcomes = None

        # parameter values
        self.dictParameterValues = dict()   # dictionary of sampled parameter values
        self.listOfParamValues = []   # list of parameter values

        # calibration
        self.lnL = []

    def extract_outputs(self, simulated_model, store_param_values=False):
        """ extracts outputs from each simulated epidemic model """

        # store the id, seed, if feasible, and run-time of this trajectory
        self.ids.append(simulated_model.id)
        self.seeds.append(simulated_model.seed)
        self.ifFeasible.append(simulated_model.ifAFeasibleTraj)
        self.runTimes.append(simulated_model.runTime)

        # store economic evaluation outcomes
        if simulated_model.econEval:
            self.discountedCosts.append(simulated_model.econEval.totalDiscountedCostAfterWarmUp)
            self.discountedHealths.append(simulated_model.econEval.totalDiscountedEffectAfterWarmUp)

        # store outcomes collected after the warm-up period
        if simulated_model.settings.storeProjectedOutcomes:

            # for time-series of sum incidence and sum cumulative incidence
            append_to_a_dict(existing_dict=self.dictOfProjectedOutcomes,
                             new_dict=simulated_model.epiHistory.get_dic_of_projected_outcomes())
            # intervention utilization
            append_to_a_dict(existing_dict=self.dictOfProjectedOutcomes,
                             new_dict=simulated_model.decisionMaker.get_dic_of_intervention_utilization(
                                 delta_t=simulated_model.settings.deltaT))

        # store parameter values
        if store_param_values:
            # list of parameter values
            self.listOfParamValues.append(simulated_model.params.get_list_of_parameter_samples())
            # dictionary of parameter values
            append_to_a_dict(existing_dict=self.dictParameterValues,
                             new_dict=simulated_model.params.get_dic_of_parameter_samples())

        # likelihood
        self.lnL.append(simulated_model.lnl)

    def calculate_summary_stats(self):
        """ calculates the summary statistics for each output """

        self.statRunTimes = SummaryStat(name='Run time', data=self.runTimes)
        if len(self.discountedCosts) > 0:
            self.statCost = SummaryStat(name='Discounted cost', data=self.discountedCosts)
            self.statHealth = SummaryStat(name='Discounted Health', data=self.discountedHealths)

        self.dictOfStatsForProjectedOutcomes = dict()
        for key, value in self.dictOfProjectedOutcomes.items():
            self.dictOfStatsForProjectedOutcomes[key] = SummaryStat(name=key, data=value)

    def get_nmb_loss_stat(self, wtp=None, health_multiplier=1, cost_multiplier=1, ):

        nmb_loss = wtp * np.array(self.discountedHealths) * health_multiplier \
                   + np.array(self.discountedCosts) * cost_multiplier

        return SummaryStat(name='Discounted loss in NMB', data=nmb_loss)


def simulate_this_model(model, function_to_populate_model, seed, if_until_a_feasible_traj, max_tries):

    # populate the model according to the function
    function_to_populate_model(model)
    # simulate and return the model
    if if_until_a_feasible_traj:
        model.simulate_until_a_feasible_traj(seed=seed, max_tries=max_tries)
        print('ID: {}, # discarded: {}, lnl = {}'.format(model.id, model.nTrajsDiscarded, model.lnl[0]))
    else:
        model.simulate(seed)
    return model
