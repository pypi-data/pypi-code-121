"""
class that creates a generic problem
"""
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Variable
from science_optimization.builder import Constraint
from science_optimization.function import FunctionsComposite


class GenericProblem(BuilderOptimizationProblem):
    """Concrete builder implementation.

    This class builds a generic optimization problem.

    """

    # objective function(s)
    _f = None

    # equality constraint function(s)
    _eq_cons = None

    # inequality constraint function(s)
    _ineq_cons = None

    # the variables' bounds
    _x_bounds = None

    def __init__(self, f, eq_cons, ineq_cons, x_bounds, x_type=None):
        """Constructor of a generic optimization problem.

        Args:
            f        : Objective functions.
            eq_cons  : Equality constraint functions.
            ineq_cons: Inequality constraint functions.
            x_bounds : Lower bound and upper bounds.
            x_type: (np.ndarray) (n x 1)-list with variables' type ('c': continuous or 'd': discrete).
        """

        self.f = f
        self.eq_cons = eq_cons
        self.ineq_cons = ineq_cons
        self.x_bounds = x_bounds
        self.x_type = x_type

    @property
    def f(self):
        return self._f

    @property
    def eq_cons(self):
        return self._eq_cons

    @property
    def ineq_cons(self):
        return self._ineq_cons

    @property
    def x_bounds(self):
        return self._x_bounds

    @f.setter
    def f(self, value):
        self._f = value

    @eq_cons.setter
    def eq_cons(self, value):
        self._eq_cons = value

    @ineq_cons.setter
    def ineq_cons(self, value):
        self._ineq_cons = value

    @x_bounds.setter
    def x_bounds(self, value):
        self._x_bounds = value

    def build_objectives(self):

        obj_fun = FunctionsComposite()

        for f in self.f:
            obj_fun.add(f)

        objective = Objective(objective=obj_fun)

        return objective

    def build_constraints(self):

        eq_cons = FunctionsComposite()
        ineq_cons = FunctionsComposite()

        for eq_g in self.eq_cons:
            eq_cons.add(eq_g)

        for ineq_g in self.ineq_cons:
            ineq_cons.add(ineq_g)

        constraints = Constraint(eq_cons=eq_cons, ineq_cons=ineq_cons)

        return constraints

    def build_variables(self):

        variables = Variable(x_min=self.x_bounds[:, 0].reshape(-1, 1),
                             x_max=self.x_bounds[:, 1].reshape(-1, 1),
                             x_type=self.x_type)

        return variables
