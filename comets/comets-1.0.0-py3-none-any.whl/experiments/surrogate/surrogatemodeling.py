# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from .surrogate import SurrogateRegistry
from ..sampling.sampling import DistributionSampling
from ...utilities.utilities import to_list


class SurrogateModeling(Experiment):
    """
    Surrogate Modeling class (prototype)

    Args:
        objective (string, optional) : Objective of the surrogate.
        surrogate (string, optional) : Method used for the creation of the surrogate.
        sampler (string, optional): Sampling method to use.
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
            This history is stored in the variable SurrogateModeling.task_history

    Attributes:
        space : Space over which your parameters are defined.
        task (Task): Task the analysis will be performed on.

    """

    def __init__(
        self,
        space,
        task,
        objective=None,
        surrogate='GaussianProcessRegressor',
        method='random',
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

        self.space = to_list(space)
        self.objective = objective
        self.sampler = DistributionSampling(
            self.map_space_to_uniform_distribution(self.space), rule=method
        )
        self.surrogate = SurrogateRegistry[surrogate](objective=self.objective)

    def map_space_to_uniform_distribution(self, space):
        distribution = []
        for parameter in space:
            if parameter['type'] == 'float':
                dist = {
                    'name': parameter['name'],
                    "sampling": 'uniform',
                    "parameters": {
                        'loc': parameter['bounds'][0],
                        'scale': parameter['bounds'][1] - parameter['bounds'][0],
                    },
                }
                distribution.append(dist)
            else:
                raise ValueError(
                    "Type {} not implemented for surrogate modeling".format(
                        parameter['type']
                    )
                )  # pragma: no cover
        return distribution

    def _initialize(self):
        # Define void list of results and all_samples,
        # storage of samples and results not yet implemented in the generic experiment class
        # Eventually remove later from here when this functionality exists in the generic class
        self.list_of_results = []
        self.all_samples = []
        # list of outputs of tasks evaluations must be defined as attribute of the class
        # as it is used to obtain the name of the objective when it is no given
        # TODO: defining the outputs of the tasks within the task object creation would result
        # in a clear code.  Rather than needing a task evaluation to know the name, it could be
        # simply asked to the task object.
        # No local storage of the list of outputs as attributes will be needed.
        self.list_of_task_outputs = []

    def _execute(self):
        list_of_samples = self.sampler.get_samples(number_of_samples=self.batch_size)

        self.all_samples.extend(list_of_samples)
        self.list_of_task_outputs = self._evaluate_tasks(self.task, list_of_samples)

        if (self.objective is None) and len(self.list_of_task_outputs[0]) == 1:
            list_of_objectives = [
                next(iter(task_output.values()))
                for task_output in self.list_of_task_outputs
            ]
        elif self.objective is not None:
            list_of_objectives = [
                task_output[self.objective] for task_output in self.list_of_task_outputs
            ]
        else:
            raise ValueError(
                "Task returns several outputs, an objective for the surrogate should be specified"
            )
        self.list_of_results.extend(list_of_objectives)

    def _finalize(self):
        if (self.objective is None) and len(self.list_of_task_outputs[0]) == 1:
            self.surrogate.objective = next(iter(self.list_of_task_outputs[0].keys()))
        self.surrogate.fit(self.all_samples, self.list_of_results)
        self.results = self.surrogate
