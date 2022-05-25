# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from ...core.space import Space
from .space_parametersweep import Variable
from ...utilities.utilities import to_list
import itertools


class ParameterSweep(Experiment):
    """
    Parameter sweep analysis class

    Args:
        task (Task): Task the analysis will be performed on.
        space (list of Variable): The space of the variables over which to perform the parameter sweep. Space is a list of Variables where each Variable represents one variable and may contain the following keys:

            - **name** (str) - Name of the decision variable.
            - **type** (str) - Type of decision variable, among 'float','int' and 'categorical'.
            - **bounds** (list, optional) - Bounds between which the variable is defined (list with lower and upper value).
            - **number_of_points** (int, optional) - Number of points used to perform a parameter sweep of the space.
            - **values** (list, optional) - Used when the decision variable type is 'categoric', list of values that will be tested during the parameter sweep.
            - **size** (int, optional) - Used when the variable is a list of parameters. Shape is the length of this list.

        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            Comets parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable ParameterSweep.task_history
    """

    def __init__(
        self,
        task,
        space,
        n_jobs=1,
        save_task_history=False,
    ):
        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            save_task_history=save_task_history,
        )
        self.space = Space(to_list(space), Variable)

        # This experiments has no iterations
        self.has_iterations = False

    def _initialize(self):
        pass

    def _execute_no_loop(self):
        # Compute all the point for each dimension
        list_of_points_before_cartesian_product = []
        for elements in self.space.list_of_variables:
            for i in range(elements.dimension):
                list_of_points_per_dimension = []
                if elements.type == 'categorical':
                    list_of_points_before_cartesian_product.append(elements.values)
                else:
                    if elements.type == 'int':
                        step = abs(elements.bounds[1] - elements.bounds[0]) // (
                            elements.number_of_points - 1
                        )
                    elif elements.type == 'float':
                        step = abs(elements.bounds[1] - elements.bounds[0]) / (
                            elements.number_of_points - 1
                        )

                    for i in range(elements.number_of_points):
                        list_of_points_per_dimension.append(
                            elements.bounds[0] + i * step
                        )
                    list_of_points_before_cartesian_product.append(
                        list_of_points_per_dimension
                    )

        # Compute the cartesian product between the points of all dimensions
        self.list_of_coordinates_to_evaluate = []
        tuple_of_point_before_cartesian_product = tuple(
            list_of_points_before_cartesian_product
        )
        for coordinates in itertools.product(*tuple_of_point_before_cartesian_product):
            self.list_of_coordinates_to_evaluate.append(coordinates)

        # Encode the results of the cartesian product to a parameterset format
        self.list_of_samples = self.encode(self.list_of_coordinates_to_evaluate)

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, self.list_of_samples)

    def _finalize(self):
        # Decode the results in the following format: {'inputs': list_of_parameter_set, 'outputs': list_of_parameter_set}
        self.results = {'inputs': self.list_of_samples, 'outputs': self.list_of_results}
        if self.save_task_history:
            self.task_history = self.results

    def encode(self, list_of_coordinates_to_evaluate):
        self.parameter_names = []
        list_of_coordinates_to_evaluate_with_tuple = []

        for elements in self.space.list_of_variables:
            self.parameter_names.append(elements.name)

        for coordinates in list_of_coordinates_to_evaluate:
            count = 0
            coordinates_with_tuple = []
            for elements in self.space.list_of_variables:

                if isinstance(elements.size, int):
                    coordinates_with_tuple.append(
                        list(coordinates[count : count + elements.size])
                    )
                    count += elements.size
                else:
                    coordinates_with_tuple.append(coordinates[count])
                    count += 1
            list_of_coordinates_to_evaluate_with_tuple.append(coordinates_with_tuple)

        sample_input = []
        for i in range(len(list_of_coordinates_to_evaluate_with_tuple)):
            sample_input.append(
                {
                    key: value
                    for key, value in zip(
                        self.parameter_names,
                        list_of_coordinates_to_evaluate_with_tuple[i],
                    )
                }
            )
        return sample_input
