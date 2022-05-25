# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod
from ..utilities import get_logger


class Task(ABC):
    """
    Abstract Task class.
    """

    @abstractmethod
    def evaluate(self, input_parameter_set={}):
        """
        Method mapping a ParameterSet to another ParameterSet

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        Returns:
            ParameterSet: output ParameterSet
        """
        pass


class FunctionalTask(Task):
    """
    Task for which the evaluation corresponds to the evaluation of a function provided at the creation of the FunctionalTask.

    Args:
        function (callable): A python function taking a ParameterSet as input and returning a ParameterSet.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change.
            These parameters will be appended to any additional input ParameterSet of the task. New parameters may replace the 'cold' parameters values.

    Example
    -------
    Imagine we have a function f that returns a dictionary of the form: ``{'y': y}``.

    >>> def f(input_parameter_set):
    >>>     return {'y': input_parameter_set['x'] + 1}
    >>> task = FunctionalTask(f)
    >>> task.evaluate({'x': 0})
    {'y': 1}

    """

    def __init__(self, function, cold_input_parameter_set={}):
        """
        Constructor of the FunctionalTask
        """
        self.function = function
        self.cold_input_parameter_set = cold_input_parameter_set

    def evaluate(self, input_parameter_set={}, *args, **kwargs):
        """
        Apply the function to an input ParameterSet and return the resulting ParameterSet.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        Returns:
            ParameterSet: output ParameterSet
        """

        logger = get_logger(__name__)
        logger.debug(
            "Running task with cold input parameter set %s and input parameter set: %s",
            self.cold_input_parameter_set,
            input_parameter_set,
        )

        inputs = {}
        inputs.update(self.cold_input_parameter_set)
        inputs.update(input_parameter_set)

        outputs = self.function(inputs, *args, **kwargs)

        logger.debug("Output of task: %s", outputs)

        return outputs
