import numpy as np
import unittest
from science_optimization.algorithms.unidimensional import MultimodalGoldenSection, GoldenSection
from science_optimization.function import GenericFunction
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import GenericProblem
from science_optimization.solvers import Optimizer


class TestMultimodalGoldenSection(unittest.TestCase):
    """Test golden section method"""

    def setUp(self):
        """Test set up"""

        # instantiate golden section
        mgs = MultimodalGoldenSection()

        # build optimization problem 1
        def test_f1(x): return 3*np.sin(2*np.pi*np.cos(np.pi*x)) - 4*np.cos(np.pi*x - 1/4)
        f1 = [GenericFunction(func=test_f1, n=1)]
        interval = np.array([[0, 1]])
        op1 = OptimizationProblem(builder=GenericProblem(f=f1, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # build optimization problem 2
        def test_f2(x): return -10 * x ** 2 + 5 * np.cos(30 * x)
        f2 = [GenericFunction(func=test_f2, n=1)]
        op2 = OptimizationProblem(builder=GenericProblem(f=f2, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # optimizers
        self.optimizer1 = Optimizer(opt_problem=op1, algorithm=mgs)
        self.optimizer2 = Optimizer(opt_problem=op2, algorithm=mgs)

        # test optimization
        self.x1 = np.array([[0.2189, 0.5690, 0.9790]])
        self.x2 = np.array([[0.5259, 0.7363, 0.9467]])

    def test_functions(self):
        """Test minimization of cosine"""

        # algorithms
        result1 = self.optimizer1.optimize(debug=False)
        result2 = self.optimizer2.optimize(debug=False)
        np.testing.assert_almost_equal(result1.x, self.x1, decimal=4)
        np.testing.assert_almost_equal(result2.x, self.x2, decimal=4)


class TestGoldenSection(unittest.TestCase):
    """Test golden section method"""

    def setUp(self):
        """Test set up"""

        # instantiate golden section
        gs = GoldenSection()

        # build optimization problem
        f = [GenericFunction(func=np.cos, n=1)]
        interval = np.array([[0, 2*np.pi]])
        op = OptimizationProblem(builder=GenericProblem(f=f, eq_cons=[], ineq_cons=[], x_bounds=interval))

        # optimizer
        self.optimizer = Optimizer(opt_problem=op, algorithm=gs)

        # test optimization
        self.x = np.pi

        # test number of iteration
        self.max_iter = np.ceil(np.log(gs.eps)/np.log(gs.ratio))

    def test_cos(self):
        """Test minimization of cosine"""

        result = self.optimizer.optimize(debug=False)
        np.testing.assert_almost_equal(result.x, self.x)

    def test_max_iter(self):
        """Test maximum iteration"""
        result = self.optimizer.optimize(debug=True, n_step=1)
        self.assertLessEqual(result.n_iterations, self.max_iter)


if __name__ == '__main__':
    unittest.main()
