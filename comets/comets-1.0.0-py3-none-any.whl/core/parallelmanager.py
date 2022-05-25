# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from joblib import Parallel, delayed
import os


class ParallelManager:
    """
    Class in charge of managing the evaluation of tasks, in particular their parallelization.

    Args:
        n_jobs (int, optional): Number of tasks to evaluate in parallel. Defaults to -1, in which case the number of CPUs is used.
    """

    def __init__(self, n_jobs=-1):
        self.n_jobs = n_jobs

    def evaluate_task(self, task, input_parameter_set, loglevel=None):
        """
        Evaluate one task on one ParameterSet.

        Args:
            task (Task): Task to evaluate
            input_parameter_set (ParameterSet): Input ParameterSet of the Task
            loglevel (str, optional): Logging level, useful for propagating logging level when using parallelization
        Returns:
            ParameterSet: output of the Task
        """
        # Propagate logging level environment variable if provided
        if loglevel is not None:
            os.environ['COMETSLOGLEVEL'] = loglevel

        # Evaluate the task
        output_parameter_set = task.evaluate(input_parameter_set)
        return output_parameter_set

    def evaluate_tasks(self, tasks, input_parameter_sets, n_jobs=None):
        """
        Evaluate one or several tasks on one or several ParameterSets and return the output ParameterSets.
        If a task is provided, it will be evaluated with all ParameterSets in the list input_parameter_sets.
        If a list of task is provided, the list of tasks must have the same length as input_parameter_sets
        and the first task will be evaluated on the first ParameterSet, the second task will be evaluated on the second ParameterSet, etc...
        The list of output ParameterSets is returned in the same order.

        Args:
            tasks (Task): A Task or a list of Tasks
            input_parameter_sets (ParameterSet): A list of ParameterSets
            n_jobs (int, optional): Number of tasks to evaluate in parallel, defaults to self.n_jobs
        Returns:
            A list of ParameterSet
        """

        if n_jobs is None:
            n_jobs = self.n_jobs

        if isinstance(tasks, list):
            # tasks is a list

            if len(tasks) != len(input_parameter_sets):
                raise ValueError(
                    "The list tasks and the list input_parameter_sets should have the same length"
                )

            output_parameter_sets = Parallel(n_jobs=n_jobs, backend="loky")(
                delayed(self.evaluate_task)(
                    task, input_parameter_set, os.environ['COMETSLOGLEVEL']
                )
                for task, input_parameter_set in zip(tasks, input_parameter_sets)
            )
        else:
            # tasks is a task
            output_parameter_sets = Parallel(n_jobs=n_jobs, backend="loky")(
                delayed(self.evaluate_task)(
                    tasks, input_parameter_set, os.environ['COMETSLOGLEVEL']
                )
                for input_parameter_set in input_parameter_sets
            )

        return output_parameter_sets
