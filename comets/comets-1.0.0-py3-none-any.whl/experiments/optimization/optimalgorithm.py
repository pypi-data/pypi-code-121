# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import Registry
from abc import ABC, abstractmethod

OptimizationAlgorithmRegistry = (
    Registry()
)  # Registry containing the list of all optimization algorithms that are available, with information on whether they support parallelization or not


class BaseOptimizationAlgorithm(ABC):
    """
    Abstract optimization algorithm
    """

    def __init__(self, space, max_evaluations, batch_size, **algorithm_options):
        """
        Initialize the optimization algorithm
        """

    @abstractmethod
    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """

    @abstractmethod
    def tell(self, list_of_samples, list_of_loss):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        You may use the last asked samples (that you can save in self.ask()) instead of list_of_samples.
        Updates the optimization algorithm.
        """

    @abstractmethod
    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
