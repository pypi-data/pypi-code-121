# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import Registry
from abc import ABC, abstractmethod

SensitivityAnalyzerRegistry = (
    Registry()
)  # Registry containing the list of all sensitivity analyzers that are available


class BaseSensitivityAnalyzer(ABC):
    """
    Abstract sensitivity analyzer
    """

    def __init__(self, distribution):
        pass

    @abstractmethod
    def get_samples(self, number_of_samples):
        pass

    @abstractmethod
    def sensitivity_analysis(self, list_of_results):
        pass
