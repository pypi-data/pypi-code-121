"""
Optimization constraints
"""
import numpy as np
from science_optimization.function import FunctionsComposite
from science_optimization.function import LinearFunction


class Constraint:
    """Base class for optimization problem constraints.

    """

    # class attributes
    _equality_constraints = FunctionsComposite()
    _inequality_constraints = FunctionsComposite()

    def __init__(self, eq_cons: FunctionsComposite=None, ineq_cons: FunctionsComposite=None):
        """Constraints constructor.

        Args:
            eq_cons  : (FunctionsComposite) equality constraints.
            ineq_cons: (FunctionsComposite) inequality constraints (<=).
        """

        if eq_cons is not None:
            self.equality_constraints = eq_cons
        if ineq_cons is not None:
            self.inequality_constraints = ineq_cons

    # attributes interface
    @property
    def equality_constraints(self):
        return self._equality_constraints

    @property
    def inequality_constraints(self):
        return self._inequality_constraints

    # attributes setter
    @equality_constraints.setter
    def equality_constraints(self, eq_cons):
        if isinstance(eq_cons, FunctionsComposite):
            self._equality_constraints = eq_cons
        else:
            raise Warning('Equality constraints must be a FunctionsComposite instance.')

    @inequality_constraints.setter
    def inequality_constraints(self, ineq_cons):
        if isinstance(ineq_cons, FunctionsComposite):
            self._inequality_constraints = ineq_cons
        else:
            raise Warning('Inequality constraints must be a FunctionsComposite instance.')

    # methods
    def equality_constraints_feasibility(self, x, tol=1e-6):
        """Evaluate feasibility of point x.

        Args:
            x  : evaluation point
            tol: tolerance

        Returns:
            is_feasible: feasibility of x on equality constraints

        """

        is_feasible = []
        for cons in self.equality_constraints.eval(x):
            is_feasible.append((np.abs(cons) <= tol).all())

        return is_feasible

    def inequality_constraints_feasibility(self, x, tol=1e-6):
        """Evaluate feasibility of point x.

        Args:
            x  : evaluation point
            tol: tolerance

        Returns:
            is_feasible: feasibility of x on inequality constraints

        """

        is_feasible = []
        for cons in self.inequality_constraints.eval(x):
            is_feasible.append((cons <= tol).all())

        return is_feasible

    def A(self):
        """Matrix of linear inequality constraints coefficients

        Returns:
            A: linear inequality constraints coefficients

        """
        a = None
        if self.inequality_constraints is not None:

            a = [obj.parameters['c'] for obj in self.inequality_constraints.functions
                 if isinstance(obj, LinearFunction)]

            if a:
                a = [c.T if c.shape[1] == 1 else c for c in a]
                a = np.vstack(np.array(a))
            else:
                a = None

        return a

    def b(self):
        """Vector of linear inequality constraints constants

        Returns:
            b: linear inequality constraints constants

        """
        b = None
        if self.inequality_constraints is not None:

            b = [obj.parameters['d'] for obj in self.inequality_constraints.functions
                 if isinstance(obj, LinearFunction)]

            if b:
                b = -1 * np.vstack(np.array(b).reshape(-1, 1))
            else:
                b = None

        return b

    def Aeq(self):
        """Matrix of linear equality constraints coefficients

        Returns:
            Aeq: linear equality constraints coefficients

        """
        aeq = None
        if self.equality_constraints is not None:

            aeq = [obj.parameters['c'] for obj in self.equality_constraints.functions
                   if isinstance(obj, LinearFunction)]

            if aeq:
                aeq = [c.T if c.shape[1] == 1 else c for c in aeq]
                aeq = np.vstack(np.array(aeq))
            else:
                aeq = None

        return aeq

    def beq(self):
        """Vector of linear equality constraints constants

        Returns:
            beq: linear equality constraints constants

        """
        beq = None
        if self.equality_constraints is not None:

            beq = [obj.parameters['d'] for obj in self.equality_constraints.functions
                   if isinstance(obj, LinearFunction)]

            if beq:
                beq = -1 * np.vstack(np.array(beq).reshape(-1, 1))
            else:
                beq = None

        return beq
