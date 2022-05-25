# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import partialclass
from ...utilities.utilities import next_multiple

from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)
import nevergrad as ng
import numpy as np


class NevergradOptimizationAlgorithm(BaseOptimizationAlgorithm):
    """
    Optimization algorithm from nevergrad library (prototype)

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in parallel.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        name (string, optional): Name of the optimization algorithm to use.
    """

    def __init__(self, space, max_evaluations, batch_size, name='NGOpt'):
        self.space = space
        self.batch_size = batch_size
        self.nevergrad_algorithm = ng.optimizers.registry[name](
            parametrization=self.map_space_to_nevergrad_instrumentation(self.space),
            budget=max_evaluations,
            num_workers=self.batch_size,
        )

    def map_space_to_nevergrad_instrumentation(self, space):
        """
        Map a space of decision variables from Comets format to nevergrad format

        Args:
            space : The space of the decision variables over which to optimize.
        Returns:
            ng.p.Dict: Dictionary of nevergrad decision variables
        """
        parameter_dict = {}
        for parameter in space.list_of_variables:
            nevergrad_arguments = {}
            if parameter.init is not None:
                nevergrad_arguments['init'] = parameter.init
            if parameter.init is not None and parameter.dimension > 1:
                nevergrad_arguments['init'] = np.asarray(parameter.init)
            if (
                parameter.size is not None and parameter.init is None
            ):  # Nevergrad accepts only one of 'init' or 'dimension'
                nevergrad_arguments['shape'] = (parameter.dimension,)
            if parameter.type == "categorical":
                # Categorical variables are mapped to a vector of weights
                # We use a deterministic rule to chose variable value (always draw the most likely choice)
                param = ng.p.Choice(
                    parameter.values,
                    repetitions=parameter.size,
                    deterministic=True,
                )
            else:
                nevergrad_arguments['lower'] = parameter.bounds[0]
                nevergrad_arguments['upper'] = parameter.bounds[1]
                if parameter.size is not None:
                    param = ng.p.Array(**nevergrad_arguments)
                else:
                    param = ng.p.Scalar(**nevergrad_arguments)
                if parameter.type == 'int':
                    param = param.set_integer_casting()
            parameter_dict[parameter.name] = param

        return ng.p.Dict(**parameter_dict)

    def decode_nevergrad_parameters(self, parameters):
        """
        Decode parameters provided by Nevergrad so that they match a ParameterSet in Comets.
        Numpy arrays of values should be converted to a list.

        Args:
            parameters: Dictionary containing parameters in Nevergrad format
        Returns:
            ParameterSet
        """
        for param in self.space.list_of_variables:
            if isinstance(param.size, int):
                parameters[param.name] = list(parameters[param.name])
            # elif param.size == 1:
            # parameters[param.name] = [parameters[param.name]]
        return parameters

    def _apply_stop_criteria(self, criteria_max_evaluations):
        max_evaluations = next_multiple(criteria_max_evaluations, self.batch_size)
        self.nevergrad_algorithm.budget = max_evaluations

    def ask(self):
        """
        Return a list of samples points to evaluate

        Returns:
            list of ParameterSet: list of ParameterSet on which the task should be evaluated
        """
        list_of_x = []
        list_of_samples = []
        for _ in range(self.batch_size):
            x = self.nevergrad_algorithm.ask()
            list_of_x.append(x)
            list_of_samples.append(self.decode_nevergrad_parameters(x.value))
        self.last_asked_points = list_of_x
        return list_of_samples

    def tell(self, list_of_samples, list_of_loss):
        """
        Return a list of samples points to evaluate

        Args:
            list_of_samples  (list of ParameterSet): list of ParameterSet on which the task should be evaluated
            list_of_loss : list of values of the objective function evaluated on list_of_samples
        """
        # Note that the list of samples is not used, instead we use the last_asked_points so that the format is directly compatible with nevergrad
        for x, loss in zip(self.last_asked_points, list_of_loss):
            self.nevergrad_algorithm.tell(x, loss)

    def provide_optimal_solution(self):
        """
        Return the optimal decision variables found so far

        Returns:
            ParameterSet: Optimal decision variables
        """
        recommendation = self.nevergrad_algorithm.provide_recommendation()
        return self.decode_nevergrad_parameters(recommendation.value)


# List all oneshot algorithm (perform one loop with fixed number of evaluations and cannot resume with more evaluations
oneshot_algorithms = [
    'AvgMetaRecenteringNoHull',
    'HullAvgMetaRecentering',
    'HullAvgMetaTuneRecentering',
    'MetaCauchyRecentering',
    'MetaRecentering',
    'MetaTuneRecentering',
    "Portfolio",
    "ParaPortfolio",
]
at_least_2d_algorithms = [
    "CM",
    "CMandAS2",
    "CMandAS3",
    "Portfolio",
    "ParaPortfolio",
    "DiscreteDoerrOnePlusOne",
]

# Select meta algorithms that require max_evaluations
requires_max_evaluations = ["NGO"]
for algo_name in ng.optimizers.registry.keys():
    if 'NGOpt' in algo_name or 'Meta' in algo_name:
        requires_max_evaluations.append(algo_name)
    if (
        "LHSSearch" in algo_name
        or "HaltonSearch" in algo_name
        or "HammersleySearch" in algo_name
    ):
        oneshot_algorithms.append(algo_name)
    if "CMA" in algo_name:
        at_least_2d_algorithms.append(algo_name)
# All oneshot algorithms also require max_evaluations
requires_max_evaluations += oneshot_algorithms
# RandomSearch algorithms can be resumed hence are not oneshot
# Portfolio algorithms contain HammersleySearch and CMA

# Algorithm currently not functioning with our API
non_compatible_algorithms = [
    'PymooNSGA2',
    'PCABO',
    'BayesOptimBO',
    'BO',
    'BOSplit',
    'EDA',
    'NGOpt13',
]
# Notes: FCMA is the CMA-ES python implementation in package fcmaes, which requires a new dependency
# Other CMA algorithms use pycma package
# EDA is described as "probably wrong" in ng documentation, and fails most convergence tests
# Remove NGOpt13 because it uses an undefined algorithm: "NameError: name 'HyperOpt' is not defined"

# Register (almost) all nevergrad algorithms in OptimizationAlgorithmRegistry,
# together with information on whether they support parallelization or require max number of evaluations
for algo_name in ng.optimizers.registry.keys():
    # Some algorithms are removed (either because of issues in the libraries, additional dependencies to install or non-compatibility)
    if algo_name not in non_compatible_algorithms:
        OptimizationAlgorithmRegistry[algo_name] = partialclass(
            NevergradOptimizationAlgorithm, name=algo_name
        )
        algo = ng.optimizers.registry[algo_name]
        OptimizationAlgorithmRegistry.information.setdefault(algo_name, {})[
            'SupportsParallelization'
        ] = not algo.no_parallelization
        OptimizationAlgorithmRegistry.information[algo_name][
            'RequiresMaxEvaluations'
        ] = (algo_name in requires_max_evaluations)

        OptimizationAlgorithmRegistry.information[algo_name]['HasIterations'] = (
            algo_name not in oneshot_algorithms
        )

        OptimizationAlgorithmRegistry.information[algo_name]['Supports1D'] = (
            algo_name not in at_least_2d_algorithms
        )
