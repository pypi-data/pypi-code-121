"""
classes that create the problem of Rosen Suzuki (modified to multidimensional)
"""
import numpy as np
from science_optimization.builder import BuilderOptimizationProblem, Objective, Variable, Constraint

from science_optimization.function import BaseFunction, FunctionsComposite


class RosenSuzukiProblem(BuilderOptimizationProblem):
    """Concrete builder implementation.

    This class builds the Rosen-Suzuki problem.
    """
    def build_objectives(self):

        obj_fun = FunctionsComposite()
        obj_fun.add(RosenSuzukiFunction(self.n, self.Q0, self.c))

        objective = Objective(objective=obj_fun)

        return objective

    def build_variables(self):

        variables = Variable(x_min=self.x_min, x_max=self.x_max)

        return variables

    def build_constraints(self):

        constraints = Constraint(eq_cons=FunctionsComposite(), ineq_cons=RosenSuzukiConstraints(self.n, self.b))

        return constraints

    def __init__(self, n):
        """
        Constructor of Rosen-Suzuki optimization problem.

        Args:
            n: desired dimension
        """

        # Step 1
        self.n = n

        x_star = []
        u_star = []
        for i in range(1, self.n):
            x_star.append((-1) ** i)
            u_star.append((-1) ** i + 1)

        x_star.append((-1) ** self.n)

        self.x_star = np.array(x_star).reshape((-1, 1))
        self.u_star = np.array(u_star).reshape((-1, 1))

        self.x_min = np.ones((self.n, 1)) * (-5)
        self.x_max = np.ones((self.n, 1)) * 5

        # Step 2
        mdg = []
        b = []

        for j in range(1, self.n):

            v = []
            a = []
            for i in range(1, self.n+1):

                v.append(2 - (-1) ** (i + j))
                a.append(1 + (-1) ** j + (-1) ** i)

            a = np.array(a).reshape((-1, 1))
            v = np.array(v).reshape((-1, 1))

            Q = np.diag(v.transpose()[0])

            g_now = np.dot(
                np.dot(self.x_star.transpose(), Q), self.x_star
            ) + np.dot(a.transpose(), self.x_star)

            mdg.append(2*np.dot(Q, self.x_star) + a)

            if self.u_star[j-1] > 0:
                b.append(-g_now)

            else:
                b.append(-g_now - 1)

        self.b = np.array(b).reshape((-1, 1))

        mdg = np.array(mdg).transpose()[0]

        # Step 3
        v = []
        for i in range(1, self.n + 1):
            v.append(2 - (-1) ** i)

        v = np.array(v).reshape((-1, 1))
        self.Q0 = np.diag(v.transpose()[0])
        df = 2 * np.dot(self.Q0, self.x_star)
        self.c = -df - np.dot(mdg, self.u_star)


class RosenSuzukiFunction(BaseFunction):
    """
    Rosen-Suzuki objective function
    """
    n = None

    def __init__(self, n, Q0, c):

        # Step 1
        self.n = n
        self.Q0 = Q0
        self.c = c

    def dimension(self):
        return self.n

    def eval(self, x: np.ndarray):
        self.input_check(x)
        return np.dot(np.dot(x.transpose(), self.Q0), x) + np.dot(self.c.transpose(), x)

    def gradient(self, x: np.ndarray):
        self.input_check(x)
        return 2 * np.dot(self.Q0, x) + self.c

    def input_check(self, x):
        # check if input is numpy
        self.numpy_check(x)

        if not x.shape[0] == self.dimension():
            raise Warning("Point x must have {} dimensions.".format(self.parameters['n']))


class RosenSuzukiConstraints(FunctionsComposite):
    """
    Rosen-Suzuki constraints
    """
    def __init__(self, n, b):

        super().__init__()
        self.n = n
        self.n_functions = n-1

        self.b = b

    def dimension(self):
        return self.n

    def eval(self, x, idx=None, composition="parallel", weights=None):

        # input check
        idx, composition, weights, n_functions = self.input_check(idx=idx,
                                                                  composition=composition,
                                                                  weights=weights)

        g = []

        # evaluate
        for j in range(1, self.n_functions+1):

            v = []
            a = []

            for i in range(1, self.n+1):
                v.append(2 - (-1) ** (i + j))
                a.append(1 + (-1) ** j + (-1) ** i)

            a = np.array(a).reshape((-1, 1))
            v = np.array(v).reshape((-1, 1))

            Q = np.diag(v.transpose()[0])

            g.append(
                np.dot(np.dot(x.transpose(), Q), x)[0] + np.dot(a.transpose(), x)[0] + self.b[j-1]
            )

        g_return = np.array(g).reshape((-1, 1))

        # series composition
        if composition == "series":
            g_return = np.dot(weights, g_return)

        return g_return

    def gradient(self, x, idx=None, composition="parallel", weights=None):

        # input check
        idx, composition, weights, n_functions = self.input_check(idx=idx,
                                                                  composition=composition,
                                                                  weights=weights)

        mdg = []

        # evaluate
        for j in range(1, self.n_functions+1):

            v = []
            a = []

            for i in range(1, self.n+1):
                v.append(2 - (-1) ** (i + j))
                a.append(1 + (-1) ** j + (-1) ** i)

            a = np.array(a).reshape((-1, 1))
            v = np.array(v).reshape((-1, 1))

            Q = np.diag(v.transpose()[0])

            mdg.append(2 * np.dot(Q, x) + a)

        j_matrix = np.array(mdg).transpose()[0]    # jacobian (gradient of each constraint)

        # series composition
        if composition == "series":
            j_matrix = np.dot(weights, j_matrix)

        return j_matrix

    def hessian(self, x, idx=None, composition="parallel", weights=None):

        # TODO (Feres) implement hessian analytical calculus
        raise Exception('Not implemented calculus')

