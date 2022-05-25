import numpy as np
import unittest

from science_optimization.algorithms.search_direction import QuasiNewton, NewtonAlgorithm, GradientAlgorithm
from science_optimization.function import GenericFunction, PolynomialFunction
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import GenericProblem
from science_optimization.solvers import Optimizer


class TestQuasiNewton(unittest.TestCase):
    """Test quasi newton method"""

    def setUp(self):
        """Test set up"""

        # instantiate gradient method
        g = QuasiNewton(x0=np.array([[0]]))

        # build optimization problem
        f = [GenericFunction(func=np.cos, n=1)]
        interval = np.array([[0, 2*np.pi]])
        op = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # optimizer
        self.optimizer = Optimizer(opt_problem=op, algorithm=g)

        # test optimization
        self.x = np.pi

        # example 3: An example from OTEV- page 111
        # objective function (polynomial one)
        f_3 = [PolynomialFunction(exponents=np.array([[2, 0], [0, 2], [1, 1],
                                                      [1, 0], [0, 1], [0, 0]]),
                                  coefficients=np.array([2, 1, 2, 1, -2, 3]))]

        # without constraints

        # bounds
        x_min_3 = np.array([-5, -5]).reshape(-1, 1)  # lower
        x_max_3 = np.array([5, 5]).reshape(-1, 1)  # upper
        x_bounds_3 = np.hstack((x_min_3, x_max_3))

        # starting point
        x0_3 = np.array([-1, 1]).reshape(-1, 1)

        # build generic problem instance
        self.generic_3 = OptimizationProblem(
            builder=GenericProblem(f=f_3, eq_cons=[],
                                   ineq_cons=[],
                                   x_bounds=x_bounds_3))
        self.optimizer_3 = Optimizer(opt_problem=self.generic_3,
                                     algorithm=QuasiNewton(x0=x0_3, n_max=200))
        self.result_3 = np.array([-1.5, 2.5]).reshape(-1, 1)
        self.fx_res_3 = np.array([[-0.25]])

    def test_cos(self):
        """Test minimization of cosine"""

        result = self.optimizer.optimize(debug=False)
        np.testing.assert_almost_equal(result.x, self.x)

    def test_optimize_3(self):
        """Test the algorithm ellipsoid method for problem 3, with a polynomial function.

        """
        opt_3 = self.optimizer_3.optimize()
        np.testing.assert_allclose(opt_3.x, self.result_3, atol=1e-09)
        self.assertIsInstance(opt_3.x, np.ndarray)
        np.testing.assert_allclose(opt_3.fx, self.fx_res_3, atol=1e-09)
        self.assertIsInstance(opt_3.fx, np.ndarray)


class TestNewtonMethod(unittest.TestCase):
    """Test golden section method"""

    def setUp(self):
        """Test set up"""

        # instantiate Newton method
        alg = NewtonAlgorithm(x0=np.array([[0], [0]]))

        # build optimization problem
        def gen_function(x): return (x[0, :] - 4) ** 2 + (x[1, :] - 4) ** 2
        f = [GenericFunction(func=gen_function, n=2)]
        x_bounds = np.array([[-5, 5], [-5, 5]])
        op = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=x_bounds))

        # optimizer
        self.optimizer = Optimizer(opt_problem=op, algorithm=alg)

        # test optimization
        self.x = np.array([[4], [4]])

    def test_cos(self):
        """Test minimization of cosine"""

        result = self.optimizer.optimize(debug=False)
        np.testing.assert_almost_equal(result.x, self.x)


class TestGradientMethod(unittest.TestCase):
    """Test gradient method"""

    def setUp(self):
        """Test set up"""

        # instantiate gradient method
        g = GradientAlgorithm(x0=np.array([[0]]))

        # build optimization problem
        f = [GenericFunction(func=np.cos, n=1)]
        interval = np.array([[0, 2*np.pi]])
        op = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # optimizer
        self.optimizer = Optimizer(opt_problem=op, algorithm=g)

        # test optimization
        self.x = np.pi

    def test_cos(self):
        """Test minimization of cosine"""

        result = self.optimizer.optimize(debug=False)
        np.testing.assert_almost_equal(result.x, self.x)


if __name__ == '__main__':
    unittest.main()
