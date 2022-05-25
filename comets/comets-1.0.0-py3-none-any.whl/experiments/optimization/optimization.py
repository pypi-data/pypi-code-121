# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from ...core.space import Space
from ...utilities import get_logger, next_multiple
from .optimalgorithm import (
    OptimizationAlgorithmRegistry,
)
from .space_optim import DecisionVariable
from ...utilities.utilities import to_list


class Optimization(Experiment):
    """
    Optimization class (prototype)

    Args:
        space : The space of the decision variables over which to optimize.
        task (Task): Task the optimization will be performed on.
        algorithm (string) : Name of the algorithm used to optimize.
        objective (string, optional): Name of an output parameter of the task that should be optimized. No objective needs to be provided if the task only has one output parameter.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            Comets parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of an experiment having a loop.
            Default to None, in which case batch_size is set to n_jobs.
            batch_size is not used for experiments without a loop.
        stop_criteria (dict, optional): Stopping criteria of the experiment. The availables criteria are ["max_evaluations", "max_iterations", "max_duration", "callback"].
        maximize (bool, optional): If true, maximization will be performed instead of minimization. Defaults to False.
        blocking (bool, optional): if true, the run method of the optimization will be blocking, otherwise it will run in another thread. Defaults to true.
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable Optimization.task_history
        save_optimization_history (optional): If set on "True", saves the optimization history in a dict with the following keys: "best_objective", "all_objectives", "mean_objective".
            If the argument is set on "all", the following information would be added to the dictionary: "objective_recommendations". Note that, when the argument is set on "all", the
            number of task's evaluation will exceed "max_evaluations". The dictionary is accessible via the variable Optimization.optimization_history. Default to False
        algorithm_options (dict, optional): dictionary with the optimization algorithm's options. The keys of the dictionary are string corresponding to the name of the options.
    """

    def __init__(
        self,
        space,
        task,
        algorithm,
        objective=None,
        n_jobs=1,
        batch_size=None,
        stop_criteria={'max_evaluations': int(10e4)},
        maximize=False,
        blocking=True,
        callbacks=[],
        save_task_history=False,
        save_optimization_history=False,
        algorithm_options={},
    ):

        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            batch_size=batch_size,
            stop_criteria=stop_criteria,
            blocking=blocking,
            callbacks=callbacks,
            save_task_history=save_task_history,
        )
        self.space = Space(to_list(space), DecisionVariable)
        self.objective = objective
        self.maximize = maximize
        self.algorithm_name = algorithm
        self.save_optimization_history = save_optimization_history

        if (
            not OptimizationAlgorithmRegistry.information[self.algorithm_name][
                'Supports1D'
            ]
            and self.space.is_1d()
        ):
            raise ValueError(
                "Algorithm {} does not support 1D optimization".format(
                    self.algorithm_name
                )
            )

        if not OptimizationAlgorithmRegistry.information[self.algorithm_name][
            'SupportsParallelization'
        ]:
            if self.n_jobs != 1 or self.batch_size != 1:
                logger = get_logger(__name__)
                logger.warning(
                    "Algorithm {} does not support parallelization. Will run with parameters n_jobs=1 and batch_size=1".format(
                        self.algorithm_name
                    )
                )
                self.n_jobs = 1
                self.batch_size = 1

        if not OptimizationAlgorithmRegistry.information[self.algorithm_name][
            'HasIterations'
        ]:
            self.has_iterations = False

        if OptimizationAlgorithmRegistry.information[self.algorithm_name][
            'RequiresMaxEvaluations'
        ]:

            self._check_max_evaluations(self.algorithm_name)
            max_evaluations = next_multiple(
                self._stop_criteria._criteria['max_evaluations'], self.batch_size
            )
            self.optimizationalgorithm = OptimizationAlgorithmRegistry[
                self.algorithm_name
            ](
                space=self.space,
                max_evaluations=max_evaluations,
                batch_size=self.batch_size,
                **algorithm_options
            )
        else:
            self.optimizationalgorithm = OptimizationAlgorithmRegistry[
                self.algorithm_name
            ](
                space=self.space,
                max_evaluations=self._MAX_EVALUATIONS,
                batch_size=self.batch_size,
                **algorithm_options
            )

        self.optimization_history = {
            'best_objective': [],
            'all_objectives': [],
            'mean_objective': [],
        }

        if self.save_optimization_history == 'all':
            self.optimization_history['objective_recommendations'] = []

    def _apply_stop_criteria(self):
        if not OptimizationAlgorithmRegistry.information[self.algorithm_name][
            'HasIterations'
        ]:
            raise ValueError(
                "You cannot resume algorithm {}: it does not allow iterations".format(
                    self.algorithm_name
                )
            )
        if OptimizationAlgorithmRegistry.information[self.algorithm_name][
            'RequiresMaxEvaluations'
        ]:
            self._check_max_evaluations(self.algorithm_name)
            self.optimizationalgorithm._apply_stop_criteria(
                self._stop_criteria._criteria['max_evaluations']
            )

    def _execute(self):
        # Generation of new samples to evaluate
        list_of_samples = self.optimizationalgorithm.ask()

        # Evaluation of the task on the samples
        list_of_task_outputs = self._evaluate_tasks(self.task, list_of_samples)
        if (self.objective is None) and len(list_of_task_outputs[0]) == 1:
            list_of_loss = [
                next(iter(task_output.values())) for task_output in list_of_task_outputs
            ]
        elif self.objective is not None:
            list_of_loss = [
                task_output[self.objective] for task_output in list_of_task_outputs
            ]
        else:
            raise ValueError(
                "Task returns several outputs, an objective should be specified"
            )

        # create the history dictionary
        if self.save_optimization_history is not False:
            if self.maximize:
                self.optimization_history['best_objective'].append(max(list_of_loss))
            else:
                self.optimization_history['best_objective'].append(min(list_of_loss))
            self.optimization_history['all_objectives'].append(list_of_loss)
            self.optimization_history['mean_objective'].append(
                sum(list_of_loss) / len(list_of_loss)
            )

        # Provide the results to the optimization algorithm
        if self.maximize:
            list_of_loss = [-loss for loss in list_of_loss]
        self.optimizationalgorithm.tell(list_of_samples, list_of_loss)

        if self.save_optimization_history == 'all':
            recommendation = self.optimizationalgorithm.provide_optimal_solution()
            optimal_value = self.parallelmanager.evaluate_task(
                self.task, recommendation
            )
            if self.objective is not None:
                self.optimization_history['objective_recommendations'].append(
                    optimal_value[self.objective]
                )
            else:
                self.optimization_history['objective_recommendations'].append(
                    next(iter(optimal_value.values()))
                )

    def _execute_no_loop(self):
        while not self._stop_criteria.max_evaluations():
            self._execute()
        # Increment number of iteration to avoid re-initializing oneshot algos when calling resume()
        self.number_of_iterations += 1

    def _finalize(self):
        recommendation = self.optimizationalgorithm.provide_optimal_solution()
        optimal_value = self.parallelmanager.evaluate_task(self.task, recommendation)
        self.results = {
            "Optimal variables": recommendation,
            "Optimal values": optimal_value,
        }
