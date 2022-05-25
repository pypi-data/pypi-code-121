# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC

from comets.core.stopcriteria import StopCriteria
from .task import FunctionalTask
from .parallelmanager import ParallelManager
import joblib
import types
import threading
import time


class Experiment(ABC):
    """
    Abstract base experiment class

    Args:
        task (Task): Task the experiment deals with.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            Comets parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of an experiment having a loop.
            Default to None, in which case batch_size is set to n_jobs.
            batch_size is not used for experiments without a loop.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional): Dictionary giving the criteria to stop an experiment.

            The following strings correspond to a valid criterion: "max_evaluations", "max_iterations", "max_duration", "callback". A callback function should have the following prototype:

            `` def callback(Experiment experiment):
                    ...
                    return bool ``
        callbacks: Function or list of functions called at the end of each iteration
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable Optimization.task_history

    Attributes:
        task (Task): Task the experiment deals with.
        parallelmanager (ParallelManager): ParallelManager used by the Experiment to evaluate Tasks.
        number_of_evaluations (int): Number of times the task has been evaluated.
        number_of_iterations (int): Number of iterations the experiment has performed.
        has_iterations (bool): Tells if the experiment algorithm contains a main loop.
        results (dict): Results of the experiment.
    """

    _MAX_ITERATIONS = int(10e14)
    _MAX_EVALUATIONS = int(10e14)

    def __init__(
        self,
        task,
        n_jobs=1,
        blocking=True,
        batch_size=None,
        stop_criteria={'max_evaluations': int(10e4)},
        callbacks=[],
        save_task_history=False,
    ):
        if (
            n_jobs < 0
        ):  # The parallel manager will use the number of CPUs when n_jobs=-1, but so should other parts of the experiment, such as algorithms
            self.n_jobs = (
                joblib.cpu_count() + 1 + n_jobs
            )  # for n_jobs = -2, all CPUs but one are used
        else:
            self.n_jobs = n_jobs
        self.parallelmanager = ParallelManager(n_jobs=n_jobs)

        if batch_size is None:
            self.batch_size = self.n_jobs
        else:
            self.batch_size = batch_size

        if save_task_history:
            self.task_history = {"inputs": [], "outputs": []}
        else:
            self.task_history = None
        # Check that the task is a valid task (it has an 'evaluate' method)
        if callable(getattr(task, "evaluate", None)):
            self.task = task
        elif isinstance(task, types.FunctionType):
            self.task = FunctionalTask(task)
        else:
            raise ValueError(
                "Task provided to the experiment is not a task and has no 'evaluate' method"
            )

        self.number_of_iterations = 0
        self.number_of_evaluations = 0
        self.initial_time = 0
        self.results = {}
        self.blocking = blocking
        self.stop_command = False
        self.thread = None
        self.has_iterations = True
        self.save_task_history = save_task_history

        if callable(callbacks):
            self._callbacks = [callbacks]
        elif isinstance(callbacks, list):
            for callback in callbacks:
                if not callable(callback):
                    raise TypeError(
                        "A callback provided to the experiment is not callable"
                    )
            self._callbacks = callbacks
        else:
            raise TypeError("Provided callbacks do not have a valid type")

        self._set_stop_criteria(stop_criteria)

    def _set_stop_criteria(self, stop_criteria):
        if isinstance(stop_criteria, dict):
            self._stop_criteria = StopCriteria(stop_criteria, self)
        elif isinstance(stop_criteria, StopCriteria):  # pragma: no cover
            self._stop_criteria = stop_criteria
        else:
            raise TypeError("Stopping criterion does not have a valid type")

    def _check_max_evaluations(self, method_name):
        if 'max_evaluations' not in self._stop_criteria._criteria:
            raise ValueError(
                "Algorithm {} requires max_evaluations".format(method_name)
            )

    def _apply_stop_criteria(self):
        pass

    def run(self):
        """
        Method that runs the experiment
        """
        self.stop_command = False
        if self.blocking:
            self._run()
        else:
            self.thread = threading.Thread(target=self._run, args=())
            self.thread.start()

    def _run(self):
        """
        Method that runs the experiment
        """
        if self.number_of_iterations == 0:
            self.initial_time = time.time()
            self._stop_criteria.initialize()
            self._initialize()

        if not self.has_iterations:
            self._execute_no_loop()
        else:
            while not self._stop_criteria.is_finished():

                # This implements a manual stop by the user
                if self.stop_command:
                    break

                self._execute()

                self.number_of_iterations += 1

                # Monitoring callbacks
                for callback in self._callbacks:
                    callback(self)

        self._finalize()

    def _initialize(self):
        pass

    def _execute(self):
        pass

    def _execute_no_loop(self):
        pass

    def _finalize(self):
        pass

    def _evaluate_tasks(self, task, input_parameter_sets):
        """
        Delegate tasks evaluation to the parallel manager. Increment evaluations counter

        Args:
            tasks (Task): A Task or a list of Tasks
            input_parameter_sets (ParameterSet): A list of ParameterSets
        Returns:
            output_parameter_sets (ParameterSet): A list of ParameterSet
        """
        # Compute tasks
        output_parameter_sets = self.parallelmanager.evaluate_tasks(
            task, input_parameter_sets, n_jobs=self.n_jobs
        )
        # Increment number_of_evaluations counter
        self.number_of_evaluations += len(output_parameter_sets)

        # Add the new inputs and outputs to the history
        if self.save_task_history:
            self.task_history["inputs"].extend(input_parameter_sets)
            self.task_history["outputs"].extend(output_parameter_sets)

        return output_parameter_sets

    def stop(self):
        """
        Set a flag stop_command to True (the _run of the experiment needs to check this flag periodically)
        and wait for the thread running the experiment to terminate
        """
        self.stop_command = True
        if self.is_running():
            self.thread.join()

    def is_running(self):
        """
        Check if the experiment is currently running in another thread
        """
        if self.thread is None:
            return False
        else:
            return self.thread.is_alive()

    def resume(self, stop_criteria=None):
        """
        Resume the experiment

        Args:
            stop_criteria (dict, optional): provide new input stopping criteria. Erases the previous criteria.
        """
        if stop_criteria is not None:
            self._set_stop_criteria(stop_criteria)
            self._apply_stop_criteria()
            self._stop_criteria.initialize()
        self.run()
