# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod


class ModelInterface(ABC):
    """
    Abstract class defining a generic interface to a model (that may be a simulator, a machine learning model, etc...).
    The common interface allows the library to use different types of models.


    """

    @abstractmethod
    def __init__(self):
        """
        Method to declare things that need to be done only once, at the creation of the ModelInterface instance.
        'Cold' parameters that won't change during the experiment should be provided to the __init__ method.
        The ModelInterface should be serializable (using pickle) after its creation, non-serializable attributes such as an external simulator may be created in the initialize method.
        """

    @abstractmethod
    def initialize(self):
        """
        Method to declare things that need to be done each time the model needs to be initialized.
        This method will be called each time the model is reinitialized.
        The loading of 'cold' parameters that have been provided in the __init__ method should be done in the initialize method.
        """
        pass

    @abstractmethod
    def set_inputs(self, input_parameter_set={}):
        """
        Method to set the value of input parameters of the model.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        """
        pass

    @abstractmethod
    def get_outputs(self, parameter_names=[]):
        """
        Method to return the value of specific output parameters of the model.
        When called with parameter_names = ['all'] it should return all default output parameters of the model.

        Args:
            parameter_names: a list of string
        Returns:
            ParameterSet: ParameterSet containing the requested parameters
        """
        pass

    @abstractmethod
    def run(self):
        """
        Method for running the model.
        """
        pass

    @abstractmethod
    def terminate(self):
        """
        Things to perform once the run is over and the output results have been collected.
        It may be useful to destroy some attributes to render the ModelInterface serializable.
        """
        pass


class StepModelInterface(ModelInterface, ABC):
    """
    Abstract class defining a generic interface to a model (that may be a simulator, a machine learning model, etc...) that can run step by step.
    The common interface allows the library to use different types of models.

    .. automethod:: __init__
    """

    @abstractmethod
    def initialize(self, config={}):
        """
        Method to declare things that need to be done each time the model needs to be initialized.
        This method will be called each time the model is reinitialized.
        The loading of 'cold' parameters that have been provided in the __init__ method should be done in the initialize method.
        The loading of additional config parameters (typically provided by a ReinforcementLearningEnvironment) should be done in this method.
        """
        pass

    @abstractmethod
    def step(self):
        """
        Method to advance one step the run of the model.
        """
        pass
