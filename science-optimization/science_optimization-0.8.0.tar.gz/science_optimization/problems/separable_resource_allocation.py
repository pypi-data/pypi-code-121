"""
class that creates a dual decomposition problem
"""
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Variable
from science_optimization.builder import Constraint
from science_optimization.function import FunctionsComposite


class SeparableResourceAllocation(BuilderOptimizationProblem):
    """Concrete builder implementation.

    This class builds a dual decomposition optimization problem.

    """

    # objective function(s)
    _f_i = None

    # equality constraint function(s)
    _coupling_eq_constraints = None

    # inequality constraint function(s)
    _coupling_ineq_constraints = None

    # the variables' bounds
    _x_bounds = None

    def __init__(self, f_i, coupling_eq_constraints, coupling_ineq_constraints, x_bounds):
        """Constructor of a Dual Decomposition problem builder.

        Args:
            f_i                      : Objective functions composition with i individual functions.
            coupling_eq_constraints  : Composition with functions in equality coupling.
            coupling_ineq_constraints: Composition with functions in inequality coupling.
            x_bounds                 : Lower bound and upper bounds.
        """

        self.f_i = f_i
        self.coupling_eq_constraints = coupling_eq_constraints
        self.coupling_ineq_constraints = coupling_ineq_constraints
        self.x_bounds = x_bounds

    # gets
    @property
    def f_i(self):
        return self._f_i

    @property
    def coupling_eq_constraints(self):
        return self._coupling_eq_constraints

    @property
    def coupling_ineq_constraints(self):
        return self._coupling_ineq_constraints

    @property
    def x_bounds(self):
        return self._x_bounds

    @f_i.setter
    def f_i(self, value):
        self._f_i = value

    # sets
    @coupling_eq_constraints.setter
    def coupling_eq_constraints(self, value):
        self._coupling_eq_constraints = value

    @coupling_ineq_constraints.setter
    def coupling_ineq_constraints(self, value):
        self._coupling_ineq_constraints = value

    @x_bounds.setter
    def x_bounds(self, value):
        self._x_bounds = value

    # methods
    def build_objectives(self):

        # instantiate composition
        obj_fun = FunctionsComposite()

        for f in self.f_i:
            obj_fun.add(f)

        objective = Objective(objective=obj_fun)

        return objective

    def build_constraints(self):

        # instantiate composition
        eq_cons = FunctionsComposite()
        ineq_cons = FunctionsComposite()

        for eq_g in self.coupling_eq_constraints:
            eq_cons.add(eq_g)

        for ineq_g in self.coupling_ineq_constraints:
            ineq_cons.add(ineq_g)

        constraints = Constraint(eq_cons=eq_cons, ineq_cons=ineq_cons)

        return constraints

    def build_variables(self):

        # variables
        variables = Variable(x_min=self.x_bounds[:, 0].reshape(-1, 1),
                             x_max=self.x_bounds[:, 1].reshape(-1, 1))

        return variables
