"""
class that creates a mixed integer linear problem
"""
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Variable
from science_optimization.builder import Constraint
from science_optimization.function import FunctionsComposite, LinearFunction
import numpy as np
from typing import List


class MIP(BuilderOptimizationProblem):
    """This class builds a mixed integer linear problem."""

    # objective function(s)
    _c = None

    # inequality constraint matrix
    _A = None

    # inequality constraint vector
    _b = None

    # the variables' bounds
    _x_bounds = None

    # variables' type
    _x_type = None

    # equality constraint matrix
    _Aeq = None

    # equality constraint vector
    _beq = None

    def __init__(self,
                 c: np.ndarray,
                 A: np.ndarray,
                 b: np.ndarray,
                 x_bounds: np.ndarray=None,
                 x_type: List[str]=None,
                 Aeq: np.ndarray=None,
                 beq: np.ndarray=None):
        """Constructor of a generic mixed-integer linear problem.

            min c'  @ x
            st. A   @ x <= b
                Aeq @ x == beq
            x_min  <= x <=  x_max

        Args:
            c       : (np.ndarray) (n x 1)-objective function coefficients.
            A       : (np.ndarray) (m1 x n)-inequality linear constraints matrix.
            b       : (np.ndarray) (m1 x 1)-inequality linear constraints bounds.
            x_bounds: (np.ndarray) (n x 2)-lower bound and upper bounds.
            x_type  : (List[str]) variables' types ('c' or 'd').
            Aeq     : (m2 x n)-equality linear constraints matrix.
            beq     : (m2 x 1)-equality linear constraints bounds.

        """

        # set parameters
        self.c = c
        self.A = A
        self.b = b
        self.x_bounds = x_bounds
        self.x_type = x_type
        self.Aeq = Aeq
        self.beq = beq

    # getters
    @property
    def c(self):
        return self._c

    @property
    def A(self):
        return self._A

    @property
    def b(self):
        return self._b

    @property
    def Aeq(self):
        return self._Aeq

    @property
    def beq(self):
        return self._beq

    @property
    def x_bounds(self):
        return self._x_bounds

    @property
    def x_type(self):
        return self._x_type

    # setters
    @c.setter
    def c(self, value):
        self._c = value

    @A.setter
    def A(self, value):
        self._A = value

    @b.setter
    def b(self, value):
        self._b = value

    @x_bounds.setter
    def x_bounds(self, value):
        self._x_bounds = value

    @x_type.setter
    def x_type(self, value):
        self._x_type = value

    @Aeq.setter
    def Aeq(self, value):
        self._Aeq = value

    @beq.setter
    def beq(self, value):
        self._beq = value

    def build_objectives(self):

        # cardinalities
        m, n = self.c.shape

        # composition
        obj_fun = FunctionsComposite()

        # mono-objective problem
        if (m > 1 and n == 1) or (m == 1 and n > 1):
            # add to function composition
            obj_fun.add(LinearFunction(c=self.c.reshape(-1, 1)))
        elif m >= 1 and n >= 1:
            for i in range(m):
                # add to function composition
                obj_fun.add(LinearFunction(c=self.c[i, :].reshape(-1, 1)))
        else:
            raise ValueError("({}x{})-array not supported!".format(m, n))

        objective = Objective(objective=obj_fun)

        return objective

    def build_constraints(self):

        # cardinalities
        mi = self.A.shape[0]
        me = self.Aeq.shape[0] if self.Aeq is not None else 0

        # create object
        ineq_cons = FunctionsComposite()
        eq_cons = FunctionsComposite()

        # add linear inequality functions
        for i in range(mi):
            ineq_cons.add(LinearFunction(c=self.A[i, :].reshape(-1, 1), d=-self.b[i, 0]))

        # add linear equality functions
        for i in range(me):
            eq_cons.add(LinearFunction(c=self.Aeq[i, :].reshape(-1, 1), d=-self.beq[i, 0]))

        # set constraints
        constraints = Constraint(eq_cons=eq_cons, ineq_cons=ineq_cons)

        return constraints

    def build_variables(self):

        # default unbounded variables
        if self.x_bounds is None:
            self.x_bounds = np.ones((self.c.shape[0], 2))
            self.x_bounds[:, 0] = -np.inf
            self.x_bounds[:, 1] = np.inf

        # create variables
        variables = Variable(x_min=self.x_bounds[:, 0].reshape(-1, 1),
                             x_max=self.x_bounds[:, 1].reshape(-1, 1),
                             x_type=self.x_type)

        return variables
