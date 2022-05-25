"""
class that creates a Quadratic problem
"""
import numpy as np
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Variable
from science_optimization.builder import Constraint
from science_optimization.function import FunctionsComposite
from science_optimization.function import QuadraticFunction


class Quadratic(BuilderOptimizationProblem):
    """Concrete builder implementation.

    This class builds an unconstrained quadratic problem.

    """

    # class attributes
    _Q = None
    _c = None
    _d = None
    _x_bounds = None

    def __init__(self, Q, c, d, x_bounds):
        """ Constructor of Quadratic optimization problem builder in the form

            min x'Qx + c'x + d
                x in x_bounds

        Args:
            Q: (n x n)-array with quadratic coefficients
            c: (n x 1)-array with linear coefficients
            d: numeric value
            x_bounds: (n x 2)-array with variables bounds
        """
        self.Q = Q
        self.c = c
        self.d = d
        self.x_bounds = x_bounds

    # attributes interface
    @property
    def Q(self):
        return self._Q

    @property
    def c(self):
        return self._c

    @property
    def d(self):
        return self._d

    @property
    def x_bounds(self):
        return self._x_bounds

    # setters
    @Q.setter
    def Q(self, Q):
        self._Q = Q

    @c.setter
    def c(self, c):
        self._c = c

    @d.setter
    def d(self, d):
        self._d = d

    @x_bounds.setter
    def x_bounds(self, bounds):
        self._x_bounds = bounds

    # methods
    def build_variables(self):

        # bounds
        variables = Variable(x_min=self.x_bounds[:, 0].reshape(-1, 1),
                             x_max=self.x_bounds[:, 1].reshape(-1, 1))

        return variables

    def build_objectives(self):

        # objective
        obj_fun = FunctionsComposite()
        obj_fun.add(f=QuadraticFunction(Q=1.0*np.array(self.Q), c=1.0 * np.array(self.c),
                                        d=1.0*np.array(self.d)))
        objective = Objective(objective=obj_fun)

        return objective

    def build_constraints(self):

        # empty constraints
        constraints = Constraint(eq_cons=FunctionsComposite(), ineq_cons=FunctionsComposite())

        return constraints
