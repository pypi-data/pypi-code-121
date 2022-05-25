"""
class that creates the Klee-Minty problem
"""
import numpy as np
from scipy.sparse import csr_matrix
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Constraint
from science_optimization.builder import Variable
from science_optimization.function import FunctionsComposite
from science_optimization.function import LinearFunction


class KleeMinty(BuilderOptimizationProblem):
    """Concrete builder implementation.

       This class builds a Klee-Minty problem.

    """
    # class attributes
    _dimension = None

    def __init__(self, dimension=3):
        """Constructor of KleeMinty optimization problem.

        Args:
            dimension: problem dimension
        """
        self.dimension = dimension

    # attributes interface
    @property
    def dimension(self):
        return self._dimension

    # setters
    @dimension.setter
    def dimension(self, dimension):
        if dimension > 0:
            self._dimension = dimension
        else:
            raise ValueError("Dimension cannot be negative!")

    def build_variables(self):

        # variables bounds
        bounds = np.zeros((self.dimension, 2))
        bounds[:, 1] = np.Inf

        # add variables
        variables = Variable(x_min=bounds[:, 0].reshape(-1, 1),
                             x_max=bounds[:, 1].reshape(-1, 1))
        return variables

    def build_objectives(self):
        # linear objective coefficients
        c = 2. ** np.arange(self.dimension - 1, -1, -1)
        obj_fun = FunctionsComposite()
        obj_fun.add(f=LinearFunction(c=-c.reshape((-1, 1))))
        objective = Objective(objective=obj_fun)
        return objective

    def build_constraints(self):
        # constraints bounds
        d = 100. ** np.arange(0, self.dimension)

        # constraints matrix
        i, j = np.where(np.tril(np.ones((self.dimension, self.dimension))))
        c = csr_matrix((2 * 2 ** (i - j) / ((i == j) + 1), (i, j))).toarray()

        # constraints
        ineq_cons = FunctionsComposite()
        for aux in range(self.dimension):
            ineq_cons.add(f=LinearFunction(c=c[aux, :].reshape((-1, 1)), d=-d[aux]))

        constraints = Constraint(ineq_cons=ineq_cons)

        return constraints
