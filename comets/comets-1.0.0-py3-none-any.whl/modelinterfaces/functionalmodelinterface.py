# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ..core.modelinterface import ModelInterface


class FunctionalModelInterface(ModelInterface):
    """
    ModelInterface for a model that is a simple python function mapping a ParameterSet to another ParameterSet.

    Args:
        function (callable): A function taking as input a ParameterSet and returning a ParameterSet.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change during an experiment.
            These parameters will be appended to any additional input ParameterSet set using set_inputs.

    Attributes:
        outputs (ParameterSet): output ParameterSet containing all the outputs of the function.
    """

    def __init__(self, function, cold_input_parameter_set={}):
        self.function = function
        self.cold_input_parameter_set = cold_input_parameter_set
        self.initialize()

    def initialize(self):
        """
        Reset the inputs, outputs and load the initial_input_parameter_set
        """
        self.outputs = {}
        self.inputs = {}
        self.set_inputs(self.cold_input_parameter_set)

    def set_inputs(self, input_parameter_set={}):
        """
        Set the value of input parameters of the model.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        """
        self.inputs.update(input_parameter_set)

    def get_outputs(self, parameter_names=[]):
        """
        Return the value of specific output parameters of the model. If parameter_names is ['all'], return all output parameters of the function.

        Args:
            parameter_names: a list of string
        Returns:
            ParameterSet: ParameterSet containing the requested parameters
        """
        if parameter_names == ['all']:
            outputs = self.outputs
        else:
            outputs = {key: self.outputs[key] for key in parameter_names}
        return outputs

    def run(self):
        """
        Run the model by applying the function.
        """
        self.outputs = self.function(self.inputs)

    def terminate(self):
        pass
