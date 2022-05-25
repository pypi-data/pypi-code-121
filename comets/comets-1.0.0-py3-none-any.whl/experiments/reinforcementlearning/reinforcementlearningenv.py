# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.
from ...utilities import get_logger


class ReinforcementLearningEnvironment:
    """
    Provides an interface to a reinforcement learning environment using a StepModelInterface.
    Allows to define the encoding used for configuration (at the beginning of each simulation), actions (applied at each step) and what is the environment state (observed after each step).

    Args:
        modelinterface (StepModelInterface): StepModelInterface.
        name (string, optional): Name of the environment.
        encode_configuration (callable, optional): An encoding function taking as argument a ParameterSet and returning a ParameterSet,
            it is applied to the optional config provided when a simulation is reset. The resulting ParameterSet is applied to the modelinterface at the beginning of a new simulation.
        encode_action (callable, optional): An encoding function taking as argument a ParameterSet and returning a ParameterSet,
            it is applied to the actions, the resulting ParameterSet is applied to the modelinterface at each step.
        get_state (callable, optional): A function taking as argument a modelinterface and returning a ParameterSet,
            is used to compute the state returned by the environment (including eventually the reward and whether the episode has ended).
            Should be provided if the modelinterface has no default outputs.
            Can return a parameter 'sim_halted' equal to True if the simulation reaches an unexpected state and cannot continue.
    """

    def __init__(
        self,
        modelinterface,
        name="CosmoTechSimulator",
        encode_configuration=None,
        encode_action=None,
        get_state=None,
    ):
        self.modelinterface = modelinterface
        self.name = name
        self.encode_action = encode_action
        self.get_state = get_state
        self.encode_configuration = encode_configuration

    def reset(self, config={}):
        """
        Reinitialize the model

        Args:
            config (optional, ParameterSet): ParameterSet applied at the beginning of each simulation

        Returns:
            ParameterSet: observed state after initialization
        """
        self.sim_halted = False
        self.modelinterface.terminate()
        if self.encode_configuration is None:
            self.modelinterface.initialize(config)
        else:
            self.modelinterface.initialize(self.encode_configuration(config))
        return self.state()

    def step(self, action={}):
        """
        Apply an action and advance one step

        Args:
            action (optional, ParameterSet): action applied to the modelinterface

        Returns:
            ParameterSet: observed state after the step
        """
        try:
            if self.encode_action is None:
                self.modelinterface.set_inputs(action)
            else:
                self.modelinterface.set_inputs(self.encode_action(action))
            self.modelinterface.step()
            outputs = self.state()
        except Exception as e:
            logger = get_logger(__name__)
            logger.warning(
                "Error encountered during simulation, ending episode. Exception: {}".format(
                    e
                )
            )
            outputs = {'sim_halted': True}
            self.sim_halted = True
        return outputs

    def state(self):
        """
        Observe the state of the simulation

        Returns:
            ParameterSet: observed state. Contains parameter 'sim_halted', with default value False.
            If it is equal to True it means the simulation has reached an unexpected state or an error and cannot continue.
        """
        if self.get_state is None:
            outputs = self.modelinterface.get_outputs(['all'])
        else:
            outputs = self.get_state(self.modelinterface)
        if 'sim_halted' not in outputs:
            outputs['sim_halted'] = False
        if self.sim_halted:
            outputs['sim_halted'] = True
        return outputs
