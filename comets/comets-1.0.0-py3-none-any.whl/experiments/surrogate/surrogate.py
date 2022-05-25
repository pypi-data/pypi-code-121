# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import Registry
from abc import ABC, abstractmethod
from ...core.task import Task

SurrogateRegistry = (
    Registry()
)  # Registry containing the list of all surrogates that are available


class BaseSurrogateModel(Task, ABC):
    """
    Abstract sampler
    """

    def __init__(self):
        pass

    @abstractmethod
    def evaluate(self, input_parameter_set):
        pass

    @abstractmethod
    def fit(self, inputs, observations):
        pass
