# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)
from .space_optim import StandardizedSpace
from ...utilities import get_logger
import numpy as np
import cma


@OptimizationAlgorithmRegistry.register_with_info(
    SupportsParallelization=True,
    RequiresMaxEvaluations=False,
    Supports1D=False,
    HasIterations=True,
)
class CMAES(BaseOptimizationAlgorithm):
    """
    CMA-ES optimization algorithm
    This algorithm wraps the implementation at https://github.com/CMA-ES/pycma

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in parallel. By default equal to population size.
        max_evaluations (int): Maximum number of times the task should been evaluated
        algorithm_options (dict,optional): Additional keyword arguments passed to cma.CMAEvolutionStrategy. May include:

            * 'x0' (list): initial starting point;
            * 'sigma0' (float): sigma0 of initial population, defaults to 0.2;
            * 'inopts' (dict): dictionary containing additional options such as 'maxfevals','popsize,'bounds','CMA_diagonal' (bool, whether to use only the diagonal of the covariance matrix)


    """

    def __init__(self, space, max_evaluations, batch_size, **algorithm_options):
        self.space = space
        self.standardized_space = StandardizedSpace(space)
        self.default_batch_size = int(
            4 + 3 * np.log(self.standardized_space.dimension)
        )  # Default batch size used in case the default batch size of the experiment (1) is provided

        algorithm_options.setdefault('x0', self.standardized_space.initial_value())
        algorithm_options.setdefault('sigma0', 0.2)
        algorithm_options.setdefault('inopts', {})
        algorithm_options['inopts'].setdefault('maxfevals', max_evaluations)
        algorithm_options['inopts'].setdefault(
            'bounds', self.standardized_space.list_of_variables[0].bounds.copy()
        )  # Copy the bounds since cma modifies them
        if 'popsize' not in algorithm_options['inopts']:
            if batch_size < 3:
                logger = get_logger(__name__)
                logger.warning(
                    "Algorithm CMAES requires a batch size of at least 3. Batch sized used by the algorithm is changed to {}, note that this doesn't change the attribute batch_size of the experiment".format(
                        self.default_batch_size
                    )
                )
                batch_size = self.default_batch_size
            algorithm_options['inopts']['popsize'] = batch_size

        self.es = cma.CMAEvolutionStrategy(**algorithm_options)

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        self.lastask = self.es.ask()  # returns a list of numpy arrays
        return self.standardized_space.map_to_original_space(np.array(self.lastask))

    def tell(self, list_of_samples, list_of_loss):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        # Use lastask instead of list_of_samples to avoid an inverse transform (that would moreover not return exactly lastask)
        self.es.tell(self.lastask, list_of_loss)

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return self.standardized_space.map_to_original_space(self.es.result[0])
