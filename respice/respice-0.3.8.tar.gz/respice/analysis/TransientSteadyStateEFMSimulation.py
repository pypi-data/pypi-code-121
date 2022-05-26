import numpy as np

from .TransientEFMSimulation import TransientEFMSimulation


class TransientSteadyStateEFMSimulation(TransientEFMSimulation):
    def get_steadystate(self, component):
        """
        Returns the computed steady-state solution for a component.

        :param component:
            The component.
        :return:
            The steady-state vector.
        """
        return np.array(self._component_states[component][0][0])
