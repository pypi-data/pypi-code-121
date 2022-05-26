import numpy as np

from .TransientSimulation import TransientSimulation


class TransientSteadyStateSimulation(TransientSimulation):
    def get_steadystate(self, component) -> np.ndarray:
        """
        Returns the computed steady-state solution for a component.

        :param component:
            The component.
        :return:
            The steady-state vector.
        """
        return np.array(self.get_states(component)[0])
