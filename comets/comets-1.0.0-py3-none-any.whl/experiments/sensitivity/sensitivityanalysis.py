# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from .sensitivityanalyzer import SensitivityAnalyzerRegistry
from ...utilities import get_logger
from ...utilities.utilities import to_list


class SensitivityAnalysis(Experiment):
    """
    Sensitivity analysis class (prototype)

    Args:
        distribution : The distribution over which to sample.
        task (Task): Task the analysis will be performed on.
        method (string, optional): Sensitivity analysis method to use.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            Comets parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional): Stopping criteria of the experiment. The availables criteria are ["max_evaluations", "max_iterations", "max_duration", "callback"].
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable SensitivityAnalysis.task_history

    """

    def __init__(
        self,
        distribution,
        task,
        method='FAST',
        n_jobs=1,
        stop_criteria={'max_evaluations': int(10e4)},
        blocking=True,
        callbacks=[],
        save_task_history=False,
    ):
        # Checks if stop_criteria contains a 'max_evaluations' criteria
        if 'max_evaluations' not in stop_criteria:
            raise ValueError("Stop criteria must contain a max_evaluations criterion")

        # Inform the user that the only stop_criteria for this analysis is 'max_evaluation'
        if len(stop_criteria) > 1:
            logger = get_logger(__name__)
            logger.warning(
                "The only stop criterion used in this experiment is 'max_evaluations', other criteria will be ignored"
            )

        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            stop_criteria=stop_criteria,
            blocking=blocking,
            callbacks=callbacks,
            save_task_history=save_task_history,
        )
        self.distribution = to_list(distribution)
        self.initial_time = 0
        self.sensitivityanalyzer = SensitivityAnalyzerRegistry[method](
            distribution=self.distribution
        )
        # None of the actual algorithm has iterations yet
        self.has_iterations = False

    def _initialize(self):
        pass

    def _execute_no_loop(self):
        # Generation of samples to evaluate
        self.list_of_samples = self.sensitivityanalyzer.get_samples(
            number_of_samples=self._stop_criteria._criteria['max_evaluations']
        )

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, self.list_of_samples)

    def _finalize(self):
        # Compute sensitivity indices
        self.results = self.sensitivityanalyzer.sensitivity_analysis(
            self.list_of_results
        )
