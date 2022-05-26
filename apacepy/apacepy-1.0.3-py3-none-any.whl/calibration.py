import time
import warnings
from math import exp

from deampy.in_out_functions import write_csv, read_csv_cols
from numpy.random import RandomState

from apacepy.inputs import ModelSettings
from apacepy.multi_epidemics import MultiEpidemics


class CalibResultOfATraj:
    """ calibration result of a simulation trajectory (id, seed, log likelihood, and probability weight). """
    def __init__(self, epi_id, seed, lnl, message, param_values=None):

        self.epiID = epi_id
        self.seed = seed
        self.lnL = lnl
        self.message = message
        self.prob = None
        self.paramValues = param_values


class _Calibration:

    def __init__(self, model_settings):
        """
        :param model_settings: ModelSettings
        """

        assert isinstance(model_settings, ModelSettings)

        self.sets = model_settings
        self.runTime = None
        self.nTrajsDiscarded = 0
        self.nTrajsWithNonZeroProb = 0
        self.listOfParameterNames = []
        self.calibResultsOfTrajs = [] # list of calibration results for all trajectories
        self.ifSaveParamValues = self.sets.storeParameterValues

        # change model settings to calculate likelihoods
        self.sets.calcLikelihood = True
        # model_settings.storeParameterValues = True
        self.sets.storeProjectedOutcomes = False

        # build multiple epidemics
        self.multiModel = MultiEpidemics(model_settings=self.sets)

    def run(self, function_to_populate_model, num_of_iterations, if_run_in_parallel=True):
        pass

    def save_results(self, filename=None):
        """ sorts trajectories in decreasing order of probabilities and save the calibration
        results in a csv file with columns ID, seed, probability, parameter values. """

        # sort trajectories based on their likelihood
        self.calibResultsOfTrajs.sort(key=get_prob, reverse=True)

        # rows of the csv file
        header = ['ID', 'Seed', 'LnL', 'Probability', 'Message']
        header.extend(self.listOfParameterNames)
        rows = [header]

        for result in self.calibResultsOfTrajs:
            row = [result.epiID, result.seed, result.lnL, result.prob, result.message]
            if self.ifSaveParamValues:
                row.extend(result.paramValues)
            rows.append(row)

        if filename is None:
            write_csv(rows=rows, file_name=self.sets.folderToSaveCalibrationResults)
        else:
            write_csv(rows=rows, file_name=filename)

    def _calculate_probs(self):

        self.nTrajsWithNonZeroProb = 0

        # find the maximum lnl
        max_lnl = float('-inf')
        for s in self.calibResultsOfTrajs:
            if s.lnL > max_lnl:
                max_lnl = s.lnL

        # find probability weights
        sum_prob = 0
        for s in self.calibResultsOfTrajs:
            if s.lnL == float('-inf'):
                s.prob = 0
            else:
                s.prob = exp(s.lnL-max_lnl)
                sum_prob += s.prob

        if sum_prob <= 0:
            warnings.warn('No feasible trajectory found.')

        # normalize the probability weights
        if sum_prob > 0:
            for s in self.calibResultsOfTrajs:
                s.prob /= sum_prob
                if s.prob > 0:
                    self.nTrajsWithNonZeroProb += 1
        else:
            for s in self.calibResultsOfTrajs:
                s.prob = 0


class CalibrationWithRandomSampling(_Calibration):

    def __init__(self, model_settings, parallelization_approach='few-many', max_tries=100):
        """
        :param model_settings: ModelSettings
        :param parallelization_approach: (string)
            'few-many' to create a few processors each of which will run many simulation
            until a feasible trajectory is found.
            'many-once' to create many processors each of which will run the model once.
        :param max_tries: (int) maximum number of simulation runs to try to find a feasible trajectory
            when 'few-many' option is selected
        """

        _Calibration.__init__(self, model_settings=model_settings)

        self.parallApproach = parallelization_approach
        self.maxTries = max_tries

    def run(self, function_to_populate_model, num_of_iterations, if_run_in_parallel=True):
        """
        :param function_to_populate_model: function to build the epidemic model (should take 'model' as an argument)
        :param num_of_iterations: number of calibration iterations
        :param if_run_in_parallel: set to True to run calibration iterations in parallel
        """

        self.runTime = time.time()

        if self.parallApproach == 'few-many':
            if_run_until_a_feasible_traj = True
        elif self.parallApproach == 'many-once':
            if_run_until_a_feasible_traj = False
        else:
            raise ValueError('Invalid parallelization approach.')

        self.multiModel.simulate(function_to_populate_model=function_to_populate_model,
                                 n=num_of_iterations,
                                 if_export_trajs=self.multiModel.modelSets.exportCalibrationTrajs,
                                 trajs_folder=self.multiModel.modelSets.folderToSaveCalibrationTrajs,
                                 if_run_in_parallel=if_run_in_parallel,
                                 if_run_until_a_feasible_traj=if_run_until_a_feasible_traj,
                                 max_tries=self.maxTries)

        self.nTrajsDiscarded = self.multiModel.nTrajsDiscarded

        outputs = self.multiModel.multiModelOutputs

        # find names of parameters
        self.listOfParameterNames = outputs.dictParameterValues.keys()

        # calculate likelihood of each trajectory
        for i in range(num_of_iterations):

            # calibration summary for this trajectory
            summary = CalibResultOfATraj(
                epi_id=outputs.ids[i],
                seed=outputs.seeds[i],
                lnl=outputs.lnL[i][0],
                message=outputs.lnL[i][1],
                param_values=outputs.listOfParamValues[i] if self.ifSaveParamValues else None
            )

            self.calibResultsOfTrajs.append(summary)

        # this is to make sure the likelihood are not calculated if the model is used for simulation
        self.multiModel.modelSets.calcLikelihood = False
        self.multiModel.modelSets.storeProjectedOutcomes = True

        # calculate probabilities
        self._calculate_probs()

        self.runTime = time.time() - self.runTime


def get_seeds_lnl_probs(filename):
    """
    :param filename: (string) filename where the calibration summary is located with columns (id, seed, probability)
    :return: tuple (list of seeds, list of lnl, list of probabilities)
    """

    # read the columns of the csv files containing the calibration results
    cols = read_csv_cols(
        file_name=filename,
        if_ignore_first_row=True,
        if_convert_float=True)

    return cols[1].astype(int), cols[2], cols[3]


def get_seeds_with_non_zero_prob(filename, random_state=None):
    """
    :param filename: (string) filename where the calibration summary is located with columns (id, seed, probability)
    :param random_state: (None, int, or numpy.RandomState) if provided seeds are randomized
    :return: tuple (list of seeds) with non-zero probability
    """

    seeds, lnls, weights = get_seeds_lnl_probs(filename)

    result = []
    for s, w in zip(seeds, weights):
        if w > 0:
            result.append(s)

    # randomize seeds
    if random_state is not None:
        if isinstance(random_state, RandomState):
            result = random_state.permutation(result)
        elif type(random_state) == int:
            result = RandomState(random_state).permutation(result)
        else:
            raise TypeError('Invalid value for random_state.')

    return result


def get_prob(calib_results_of_a_traj):
    """ this is for sorting trajectories in decreasing order of their likelihoods """
    return calib_results_of_a_traj.prob
