"""
Optimization objectives
"""
import numpy as np
from science_optimization.function import FunctionsComposite
from science_optimization.function import LinearFunction


class Objective:
    """Class for optimization objectives.

    """

    # class attributes
    _objectives = FunctionsComposite()

    def __init__(self, objective: FunctionsComposite):
        """ Constructor of a linear objective.

        Args:
            objective: (FunctionsComposite) objective function

        """

        self.objectives = objective

    # attributes interface
    @property
    def objectives(self):
        return self._objectives

    @objectives.setter
    def objectives(self, objective):
        if isinstance(objective, FunctionsComposite):
            self._objectives = objective
        else:
            raise Warning('Objective must be a FunctionsComposite instance.')

    # methods
    def C(self):
        """Matrix of linear objectives coefficients

        Returns:
            C: matrix of linear objectives

        """

        c = None
        if self.objectives is not None:

            c = [obj.parameters['c'].T for obj in self.objectives.functions
                 if isinstance(obj, LinearFunction)]

            if c:
                c = np.vstack(np.array(c))
            else:
                c = None

        return c

    def d(self):
        """Vector of linear objectives constants

        Returns:
            d: vector of linear objectives constants
        """
        d = None
        if self.objectives is not None:

            d = [obj.parameters['d'] for obj in self.objectives.functions
                 if isinstance(obj, LinearFunction)]

            if d:
                d = np.vstack(np.array(d).reshape(-1, 1))
            else:
                d = None

        return d
