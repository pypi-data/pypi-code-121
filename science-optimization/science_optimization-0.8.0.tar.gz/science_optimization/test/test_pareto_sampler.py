import numpy as np
import unittest
from matplotlib.contour import QuadContourSet
from matplotlib.collections import PathCollection

import science_optimization.solvers.pareto_samplers as samplers
from science_optimization.function import QuadraticFunction
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import GenericProblem, MIP
from science_optimization.algorithms.linear_programming import Glop


class TestParetoSampler(unittest.TestCase):
    """Test Pareto samplers"""

    def setUp(self):
        """Test set up"""

        # =========== BEGIN TEST 1 =========
        # parameters objective function 1
        Q = np.array([[1, 0], [0, 1]])
        c1 = np.array([[0], [0]])
        d1 = np.array([0])

        # parameters objective function 2
        c2 = np.array([[-2], [-2]])
        d2 = np.array([2])

        # objectives
        f1 = QuadraticFunction(Q=Q, c=c1, d=d1)
        f2 = QuadraticFunction(Q=Q, c=c2, d=d2)
        f = [f1, f2]

        # constraints
        ineq_cons = []
        eq_cons = []

        # bounds
        x_min = np.array([-5, -5]).reshape(-1, 1)  # lower
        x_max = np.array([5, 5]).reshape(-1, 1)  # upper
        x_lim = np.hstack((x_min, x_max))

        # build generic problem instance
        generic = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=eq_cons, ineq_cons=ineq_cons, x_bounds=x_lim))

        # builder samplers
        self.nondominated_sampler = samplers.NonDominatedSampler(optimization_problem=generic, n_samples=9)
        self.epsilon_sampler = samplers.EpsilonSampler(optimization_problem=generic, n_samples=9)
        self.lambda_sampler = samplers.LambdaSampler(optimization_problem=generic, n_samples=9)
        self.mu_sampler = samplers.MuSampler(optimization_problem=generic, n_samples=9)
        self.x1 = np.array([[0], [0]])
        self.x2 = np.array([[1], [1]])
        self.eps = 1e-5
        self.opt_problem = generic
        # =========== END TEST 1 =========

        # =========== BEGIN TEST 2 =========
        # biobjective linear problem
        C = np.array([[3, 1], [-1, -2]])  # objectives
        A = np.array([[3, -1]])  # inequality constraints
        b = np.array([[6]])
        x_bounds = np.array([[0, 10], [0, 3]])

        # problem
        op = OptimizationProblem(builder=MIP(c=C, A=A, b=b, x_bounds=x_bounds))

        # builder optimization
        self.epsilon_sampler2 = samplers.EpsilonSampler(optimization_problem=op, algorithm=Glop(), n_samples=9)

        # pareto front verticies
        self.vertices = np.array([[0, 0], [3, -6], [12, -9]]).T
        # =========== END TEST 2 =========

    def test_nd_sampler(self):
        """Test if samples belong to the line segment x1x2."""

        # result
        result = self.nondominated_sampler.sample()
        samples = result.x

        # co-linearity check
        ab = self.x2 - self.x1
        ac = samples - self.x1
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1/(np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition
        colinear = np.all((cos - 1.) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac)
        within = np.all(K > -self.eps)

        # test
        np.testing.assert_equal(True, colinear and within)

    def test_epsilon_sampler(self):
        """Test if samples belong to the line segment x1x2."""

        # result
        result = self.epsilon_sampler.sample()
        samples = result.x

        # co-linearity check
        ab = self.x2 - self.x1
        ac = samples - self.x1
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1/(np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition
        colinear = np.all((cos - 1.) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac)
        within = np.all(K > -self.eps)

        # test
        np.testing.assert_equal(True, colinear and within)

    def test_lambda_sampler(self):
        """Test if samples belong to the line segment x1x2."""

        # result
        result = self.lambda_sampler.sample()
        samples = result.x

        # co-linearity check
        ab = self.x2 - self.x1
        ac = samples - self.x1
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1/(np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition
        colinear = np.all((cos - 1.) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac)
        within = np.all(K > -self.eps)

        # test
        np.testing.assert_equal(True, colinear and within)

    def test_mu_sampler(self):
        """Test if samples belong to the line segment x1x2."""

        # result
        result = self.mu_sampler.sample()
        samples = result.x

        # co-linearity check
        ab = self.x2 - self.x1
        ac = samples - self.x1
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1/(np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition
        colinear = np.all((cos - 1.) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac)
        within = np.all(K > -self.eps)

        # test
        np.testing.assert_equal(True, colinear and within)

    def test_plot(self):

        self.nondominated_sampler.sample()

        aux = self.opt_problem.plot(show_plot=False)
        self.assertTrue(isinstance(aux, PathCollection))

    def test_epsilon_sampler2(self):
        """Test if samples belong to the line segment x1x2."""

        # result
        result = self.epsilon_sampler2.sample()
        samples = result.fx

        # co-linearity check first segment
        ab = self.vertices[:, [1]] - self.vertices[:, [0]]
        ac = samples - self.vertices[:, [0]]
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1/(np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition first segment
        colinear1 = np.flatnonzero(np.abs((cos - 1.)) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac[:, colinear1])
        within = np.all(K > -self.eps)

        # test first segment
        np.testing.assert_equal(True, len(colinear1) > 0 and within)

        # co-linearity check second segment
        ab = self.vertices[:, [2]] - self.vertices[:, [1]]
        ac = samples - self.vertices[:, [1]]
        ac_norm = np.linalg.norm(ac, axis=0)
        inz = np.where(ac_norm.ravel() > 0)[0]  # exclude samples equal to the extremes
        ac_norm = ac_norm[inz]
        ac = ac[:, inz]
        cos = 1 / (np.linalg.norm(ab) * ac_norm) * np.dot(ab.T, ac)  # angle between segments

        # co-linear points condition second segment
        colinear2 = np.flatnonzero(np.abs((cos - 1.)) < self.eps)

        # samples within pareto vertices
        K = np.dot(ab.T, ab) - np.dot(ab.T, ac[:, colinear2])
        within = np.all(K > -self.eps)

        # test second segment
        np.testing.assert_equal(True, len(colinear2) > 0 and within)

        # test number of samples
        np.testing.assert_equal(True, samples.shape[1]-2 <= (len(colinear1)+len(colinear2)))
