# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from .analyzer import StatAnalyzer
from ..sampling.sampling import CompositeSampling
from ..sampling.sequenceregistry import SequenceRegistry
from ...utilities.utilities import to_list


class UncertaintyAnalysis(Experiment):
    """
    Perform an uncertainty analysis on a task.

    Args:
        sampling (dict or list of dicts): defines the function to generate samples on the input parameters. It consists in a list of distributions or generators.
        task (Task): Task the analysis will be performed on.
        method (string, optional, default to "random"): Sampling method to use.
        analyzer (string or list of strings, optional, default to “standard”): string or list of strings, specifies the list of output statistics computed at the end of the experiment.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            Comets parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of an experiment having a loop.
            Default to None, in which case batch_size is set to n_jobs.
            batch_size is not used for experiments without a loop.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional) : Stopping criteria of the experiment. The availables criteria are ["max_evaluations", "max_iterations", "max_duration", "callback"].
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable UncertaintyAnalysis.task_history

    Example
    -------
    Imagine that we have a function f that takes as an input a parameter 'orders' and returns the profit.
    We want to perform an uncertainty analysis on this function where the uncertainty on the orders is
    modeled by a variable following a discrete uniform distribution.

    >>> import comets
    >>>
    >>> def f(parameter):
    >>>    profit = parameter['orders']*3.2 - 12
    >>>    return {'profit': profit}
    >>> mytask = comets.FunctionalTask(f)
    >>>
    >>> sampling = [
    >>>    {
    >>>        "name": 'orders',
    >>>        "sampling": "discreteuniform",
    >>>        "parameters": {'low': 0, 'high': 201},
    >>>    }]
    >>>
    >>> ua = comets.UncertaintyAnalysis(
    >>>    task = mytask,
    >>>    sampling = sampling,
    >>>    stop_criteria = {'max_evaluations' : 1000})
    >>>
    >>> ua.run()
    >>> ua.results
    {'statistics':             mean      std         sem       confidence interval of the mean at 95%
                       profit  305.3568  182.796618  5.780537  (294.0134133497827, 316.70018665021735)}

    """

    def __init__(
        self,
        sampling,
        task,
        method='random',
        analyzer='standard',
        n_jobs=1,
        batch_size=None,
        stop_criteria={'max_evaluations': int(10e4)},
        blocking=True,
        callbacks=[],
        save_task_history=False,
    ):
        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            batch_size=batch_size,
            blocking=blocking,
            stop_criteria=stop_criteria,
            callbacks=callbacks,
            save_task_history=save_task_history,
        )
        self.input_sampling = to_list(sampling)

        # Check if the experiment has loops:
        if not SequenceRegistry.information[method]["HasIterations"]:
            self.has_iterations = False
            self._check_max_evaluations(method)
        self.sampler = CompositeSampling(self.input_sampling, rule=method)
        self.analyzer = StatAnalyzer(to_list(analyzer))

    def _initialize(self):
        self.list_of_results = []

    def _execute(self):
        """
        Method to sample and evaluate tasks when the uncertainty analysis is performed with iterations
        """

        # Generation of new samples to evaluate
        list_of_samples = self.sampler.get_samples(number_of_samples=self.batch_size)

        # Evaluation of the task on the samples
        self.list_of_results.extend(self._evaluate_tasks(self.task, list_of_samples))

    def _execute_no_loop(self):
        """
        Method to sample and evaluate tasks when the uncertainty analysis is performed without iterations
        """
        # Generation of new samples to evaluate
        list_of_samples = self.sampler.get_samples(
            number_of_samples=self._stop_criteria._criteria['max_evaluations']
        )

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, list_of_samples)

    def _finalize(self):
        self.results = self.analyzer.run(self.list_of_results)
