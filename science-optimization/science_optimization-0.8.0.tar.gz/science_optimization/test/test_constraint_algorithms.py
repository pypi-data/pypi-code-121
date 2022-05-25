import unittest
import numpy as np
from matplotlib.contour import QuadContourSet

from science_optimization.algorithms.derivative_free import NelderMead
from science_optimization.algorithms.lagrange import AugmentedLagrangian
from science_optimization.algorithms.cutting_plane import EllipsoidMethod
from science_optimization.algorithms.decomposition import DualDecomposition
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction, QuadraticFunction, LinearFunction, PolynomialFunction
from science_optimization.problems import SeparableResourceAllocation, GenericProblem, RosenSuzukiProblem
from science_optimization.solvers import Optimizer


class CommonObjects:
    """
    Stores objects used by more than one test class
    """

    def __init__(self):

        # linear equality constraints
        equal_empty = []
        inequal_empty = []

        # example 1: Linear Constraints
        # example from Python optimization algorithms user guide
        # objective function (quadratic one)
        f_1 = [QuadraticFunction(Q=(np.eye(3)),
                                 c=-2 * np.array([3, 5, 40]).reshape(-1, 1),
                                 d=(3 ** 2 + 5 ** 2 + 40 ** 2))]

        # with linear constraints
        # linear inequality constraints
        cons_ineq_1 = [LinearFunction(c=np.array([1, 1, 0]).reshape(-1, 1),
                                      d=-10)]
        # linear equality constraints
        cons_eq_1 = [LinearFunction(c=np.array([1, -1, 0]).reshape(-1, 1))]

        # bounds
        x_min_1 = np.array([-10, -10, -10]).reshape(-1, 1)  # lower
        x_max_1 = np.array([10, 10, 10]).reshape(-1, 1)  # upper
        x_bounds_1 = np.hstack((x_min_1, x_max_1))

        # starting point
        self.x0_1 = np.array([0, 0, 0]).reshape(-1, 1)

        # build generic problem instance
        self.generic_1 = OptimizationProblem(builder=GenericProblem(f=f_1,
                                                                    eq_cons=cons_eq_1,
                                                                    ineq_cons=cons_ineq_1,
                                                                    x_bounds=x_bounds_1))
        self.result_1 = np.array([4, 4, 10]).reshape(-1, 1)
        self.fx_res_1 = np.array([[902]])

        # example 2: Multiobjective Nonlinear Programming (quadratic)
        # example from Python optimization algorithms user guide
        # objective functions
        x_f = np.array([1, 1, 1]).reshape(-1, 1)
        a_f = 2 * np.eye(3)
        b_f = -np.matmul(a_f, x_f)
        c_f = .5 * np.matmul(np.transpose(x_f), np.matmul(a_f, x_f))
        x_f2 = np.array([-1, -1, -1]).reshape(-1, 1)
        a_f2 = np.diag([1, 2, 4])
        b_f2 = -np.matmul(a_f2, x_f2)
        c_f2 = .5 * np.matmul(np.transpose(x_f2), np.matmul(a_f2, x_f2))
        self.f_2 = [QuadraticFunction(Q=.5 * a_f, c=b_f, d=c_f),
                    QuadraticFunction(Q=.5 * a_f2, c=b_f2, d=c_f2)]

        # inequality constraint function
        a_g = 2 * np.identity(3)
        b_g = np.zeros((3, 1))
        c_g = -1
        x_g2 = np.array([1, 1, 1]).reshape(-1, 1)
        a_g2 = 2 * np.identity(3)
        b_g2 = -np.matmul(a_g2, x_g2)
        c_g2 = .5 * np.matmul(np.transpose(x_g2), np.matmul(a_g2, x_g2)) - 1
        g_2 = [QuadraticFunction(Q=.5 * a_g, c=b_g, d=c_g),
               QuadraticFunction(Q=.5 * a_g2, c=b_g2, d=c_g2)]

        # linear inequality constraints
        cons_ineq_2 = g_2

        # bounds
        x_min_2 = np.array([-10, -10, -10]).reshape(-1, 1)  # lower
        x_max_2 = np.array([10, 10, 10]).reshape(-1, 1)  # upper
        x_bounds_2 = np.hstack((x_min_2, x_max_2))

        # starting point
        self.x0_2 = np.array([20, 20, 20]).reshape(-1, 1)

        # build generic problem instance
        self.generic_2 = OptimizationProblem(
            builder=GenericProblem(f=self.f_2, eq_cons=equal_empty,
                                   ineq_cons=cons_ineq_2, x_bounds=x_bounds_2))

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
        self.x0_3 = np.array([-1, 1]).reshape(-1, 1)

        # build generic problem instance
        self.generic_3 = OptimizationProblem(
            builder=GenericProblem(f=f_3, eq_cons=equal_empty,
                                   ineq_cons=inequal_empty,
                                   x_bounds=x_bounds_3))

        self.result_3 = np.array([-1.5, 2.5]).reshape(-1, 1)
        self.fx_res_3 = np.array([[-0.25]])

        # example 4: convex quadratic
        # example from ENACOMtoolbox
        # objective function
        f_4 = [QuadraticFunction(Q=(np.eye(3)), c=np.zeros((3, 1)))]

        # linear equality constraints
        cons_eq_4 = [LinearFunction(c=np.array([1, 1, 1]).reshape(-1, 1),
                                    d=-3)]

        # starting point
        self.x0_4 = np.array([0, 0, 0]).reshape(-1, 1)

        # bounds
        x_min_4 = np.array([0, 0, 0]).reshape(-1, 1)  # lower
        x_max_4 = np.array([1, 2, 3]).reshape(-1, 1)  # upper
        x_bounds_4 = np.hstack((x_min_4, x_max_4))

        # build generic problem instance
        self.generic_4 = OptimizationProblem(
            builder=GenericProblem(f=f_4, eq_cons=cons_eq_4,
                                   ineq_cons=inequal_empty,
                                   x_bounds=x_bounds_4))

        self.result_4 = np.array([1, 1, 1]).reshape(-1, 1)
        self.fx_res_4 = np.array([[3]])

        # example 5: Booth Function
        # objective function (polynomial one)
        f_5 = [PolynomialFunction(exponents=np.array([[2, 0], [1, 1], [1, 0],
                                                      [0, 2], [0, 1], [0, 0]]),
                                  coefficients=np.array([5, 8, -34, 5, -38, 74]))]
        # without constraints

        # bounds
        x_min_5 = np.array([-10, -10]).reshape(-1, 1)  # lower
        x_max_5 = np.array([10, 10]).reshape(-1, 1)  # upper
        x_bounds_5 = np.hstack((x_min_5, x_max_5))

        # starting point
        self.x0_5 = np.array([0.5, 0.5]).reshape(-1, 1)

        # build generic problem instance
        self.generic_5 = OptimizationProblem(
            builder=GenericProblem(f=f_5, eq_cons=equal_empty,
                                   ineq_cons=inequal_empty, x_bounds=x_bounds_5))

        self.result_5 = np.array([1, 3]).reshape(-1, 1)
        self.fx_res_5 = np.array([[0]])

        # example 6: Zacharov Function
        # objective function (polynomial one)
        f_6 = [PolynomialFunction(
            exponents=np.array(
                [[4, 0, 0], [3, 1, 0], [3, 0, 1], [2, 2, 0], [2, 1, 1],
                 [2, 0, 2], [2, 0, 0], [1, 3, 0], [1, 2, 1], [1, 1, 2],
                 [1, 1, 0], [1, 0, 3], [1, 0, 1], [0, 4, 0], [0, 3, 1],
                 [0, 2, 2], [0, 2, 0], [0, 1, 3], [0, 1, 1], [0, 0, 4],
                 [0, 0, 2]]),
            coefficients=np.array(
                [0.0625, 0.5, 0.75, 1.5, 4.5, 3.375, 1.25, 2, 9, 13.5,
                 1, 6.75, 1.5, 1, 6, 13.5, 2, 13.5, 3, 5.0625, 3.25]))]

        # without constraints

        # bounds
        x_min_6 = np.array([-5, -5, -5]).reshape(-1, 1)  # lower
        x_max_6 = np.array([10, 10, 10]).reshape(-1, 1)  # upper
        x_bounds_6 = np.hstack((x_min_6, x_max_6))

        # starting point
        self.x0_6 = np.array([4, 3, 3]).reshape(-1, 1)

        # build generic problem instance
        self.generic_6 = OptimizationProblem(
            builder=GenericProblem(f=f_6, eq_cons=equal_empty,
                                   ineq_cons=inequal_empty,
                                   x_bounds=x_bounds_6))

        self.result_6 = np.array([0, 0, 0]).reshape(-1, 1)
        self.fx_res_6 = np.array([[0]])

        # example 7: Constrained problem - 5 variables
        # objective function (polynomial one)
        self.f_7 = [PolynomialFunction(
            exponents=np.array([[0, 0, 2, 0, 0], [1, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
            coefficients=np.array(
                [5.3578547, 0.8356891, 37.293239, -40792.141]))]

        # linear inequality constraints
        g_exp_1 = np.array([[0, 0, 0, 0, 0], [0, 1, 0, 0, 1],
                            [1, 0, 0, 1, 0], [0, 0, 1, 0, 1]])
        g_coef_1 = np.array([-6.665593, 0.0056858, 0.0006262,
                             -0.0022053])  # -92 + 85.334407
        g_exp_2 = np.array([[0, 0, 0, 0, 0], [0, 1, 0, 0, 1],
                            [1, 0, 0, 1, 0], [0, 0, 1, 0, 1]])
        g_coef_2 = np.array([-85.334407, -0.0056858,
                             -0.0006262, 0.0022053])
        g_exp_3 = np.array([[0, 0, 0, 0, 0], [0, 1, 0, 0, 1],
                            [1, 1, 0, 0, 0], [0, 0, 2, 0, 0]])
        g_coef_3 = np.array([-29.48751, 0.0071317, 0.0029955,
                             0.0021813])  # -110 + 80.51249
        g_exp_4 = np.array([[0, 0, 0, 0, 0], [0, 1, 0, 0, 1],
                            [1, 1, 0, 0, 0], [0, 0, 2, 0, 0]])
        g_coef_4 = np.array([-9.48751, -0.0071317, -0.0029955,
                             -0.0021813])  # 90 - 80.51249
        g_exp_5 = np.array([[0, 0, 0, 0, 0], [0, 0, 1, 0, 1],
                            [1, 0, 1, 0, 0], [0, 0, 1, 1, 0]])
        g_coef_5 = np.array([-15.699039, 0.0047026, 0.0012547,
                             0.0019085])  # 9.300961 - 25
        g_exp_6 = np.array([[0, 0, 0, 0, 0], [0, 0, 1, 0, 1],
                            [1, 0, 1, 0, 0], [0, 0, 1, 1, 0]])
        g_coef_6 = np.array([10.699039, -0.0047026, -0.0012547,
                             -0.0019085])  # -9.300961 + 20

        cons_ineq_7 = [PolynomialFunction(exponents=g_exp_1, coefficients=g_coef_1),
                       PolynomialFunction(exponents=g_exp_2, coefficients=g_coef_2),
                       PolynomialFunction(exponents=g_exp_3, coefficients=g_coef_3),
                       PolynomialFunction(exponents=g_exp_4, coefficients=g_coef_4),
                       PolynomialFunction(exponents=g_exp_5, coefficients=g_coef_5),
                       PolynomialFunction(exponents=g_exp_6, coefficients=g_coef_6)]

        # bounds
        x_min_7 = np.array([78, 33, 27, 27, 27]).reshape(-1, 1)  # lower
        x_max_7 = np.array([102, 45, 45, 45, 45]).reshape(-1, 1)  # upper
        x_bounds_7 = np.hstack((x_min_7, x_max_7))

        # starting point
        self.x0_7 = np.array([90, 40, 40, 40, 40]).reshape(-1, 1)

        # build generic problem instance
        self.generic_7 = OptimizationProblem(
            builder=GenericProblem(f=self.f_7, eq_cons=equal_empty,
                                   ineq_cons=cons_ineq_7, x_bounds=x_bounds_7))

        self.result_7 = np.array([78, 33, 29.995, 45, 36.7758]).reshape(-1, 1)
        self.fx_res_7 = np.array([[-30665.539]])

        # example 8: Constrained problem - 7 variables
        # objective function (polynomial one)
        f_8 = [PolynomialFunction(
            exponents=np.array([[2, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0, 0], [0, 0, 4, 0, 0, 0, 0], [0, 0, 0, 2, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 6, 0, 0], [0, 0, 0, 0, 0, 2, 0],
                                [0, 0, 0, 0, 0, 0, 4], [0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0]]),
            coefficients=np.array(
                [1, -20, 5, -120, 1, 3, -66, 10, 7, 1, -4, -10, -8, 1183]))]

        # linear inequality constraints
        h_exp_1 = np.array([[0, 0, 0, 0, 0, 0, 0], [2, 0, 0, 0, 0, 0, 0],
                            [0, 4, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0]])
        h_coef_1 = np.array([-127, 2, 3, 1, 4, 5])
        h_exp_2 = np.array([[0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0]])
        h_coef_2 = np.array([-282, 7, 3, 10, 1, -1])
        h_exp_3 = np.array([[0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0],
                            [0, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 2, 0],
                            [0, 0, 0, 0, 0, 0, 1]])
        h_coef_3 = np.array([-196, 23, 1, 6, -8])
        h_exp_4 = np.array([[2, 0, 0, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0, 0],
                            [1, 1, 0, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1]])
        h_coef_4 = np.array([4, 1, -3, 2, 5, -11])

        cons_ineq_8 = [PolynomialFunction(exponents=h_exp_1, coefficients=h_coef_1),
                       PolynomialFunction(exponents=h_exp_2, coefficients=h_coef_2),
                       PolynomialFunction(exponents=h_exp_3, coefficients=h_coef_3),
                       PolynomialFunction(exponents=h_exp_4, coefficients=h_coef_4)]

        # bounds
        x_min_8 = np.array([-10, -10, -10, -10, -10, -10, -10]).reshape(-1, 1)  # lower
        x_max_8 = np.array([10, 10, 10, 10, 10, 10, 10]).reshape(-1, 1)  # upper
        x_bounds_8 = np.hstack((x_min_8, x_max_8))

        # starting point
        self.x0_8 = np.array([0, 0, 0, 0, 0, 0, 0]).reshape(-1, 1)

        # build generic problem instance
        self.generic_8 = OptimizationProblem(
            builder=GenericProblem(f=f_8, eq_cons=equal_empty,
                                   ineq_cons=cons_ineq_8,
                                   x_bounds=x_bounds_8))

        self.result_8 = np.array([2.330499, 1.951372, -0.4775414,
                                  4.365726, -0.6244870, 1.038131,
                                  1.594227]).reshape(-1, 1)
        self.fx_res_8 = np.array([[680.6300573]])

        # pb_svanb
        def f(x):
            return x[0] * np.sqrt(1 + x[1] ** 2)

        f_9 = [GenericFunction(func=f, n=2)]

        def g1(x):
            return 0.124 * np.sqrt(1 + x[1] ** 2) * (8 / x[0] + 1 / (x[0] * x[1])) - 1

        def g2(x):
            return 0.124 * np.sqrt(1 + x[1] ** 2) * (8 / x[0] - 1 / (x[0] * x[1])) - 1

        def g3(x):
            return x[0] ** 2 - x[0] * 4.2 + 0.8

        def g4(x):
            return x[1] ** 2 - x[1] * 1.7 + 0.16

        cons_ineq_9 = [
            GenericFunction(func=g1, n=2),
            GenericFunction(func=g2, n=2),
            GenericFunction(func=g3, n=2),
            GenericFunction(func=g4, n=2),
        ]

        # bounds
        x_min_9 = np.array([0.2, 0.1]).reshape(-1, 1)  # lower
        x_max_9 = np.array([4, 1.6]).reshape(-1, 1)  # upper
        x_bounds_9 = np.hstack((x_min_9, x_max_9))

        # starting point
        self.x0_9 = np.array([3, 1]).reshape(-1, 1)

        self.generic_9 = OptimizationProblem(
            builder=GenericProblem(f=f_9, eq_cons=equal_empty,
                                   ineq_cons=cons_ineq_9,
                                   x_bounds=x_bounds_9))

        self.result_9 = np.array([1.41163, 0.37707]).reshape(-1, 1)
        self.fx_res_9 = np.array([[1.50865]])

        # rosen suzuki problem
        dim = 4
        self.rsp = RosenSuzukiProblem(dim)
        self.x0_rsp = np.array([4] * dim).reshape((-1, 1))
        self.result_10 = self.rsp.x_star


class TestEllipsoidMethod(unittest.TestCase):
    """This class tests the Ellipsoid algorithm method.

    """

    def setUp(self):

        # shallow cut option
        shallow_cut = 1

        self.co = CommonObjects()

        self.optimizer_1 = Optimizer(opt_problem=self.co.generic_1,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_1, n_max=300))

        self.optimizer_2 = Optimizer(opt_problem=self.co.generic_2,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_2,
                                                               n_max=300))

        self.optimizer_3 = Optimizer(opt_problem=self.co.generic_3,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_3,
                                                               n_max=200))

        self.optimizer_4 = Optimizer(opt_problem=self.co.generic_4,
                                     algorithm=EllipsoidMethod(n_max=200))

        self.optimizer_5 = Optimizer(opt_problem=self.co.generic_5,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_5,
                                                               n_max=200))

        self.optimizer_6 = Optimizer(opt_problem=self.co.generic_6,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_6,
                                                               n_max=500))

        self.optimizer_7 = Optimizer(opt_problem=self.co.generic_7,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_7,
                                                               n_max=300,
                                                               shallow_cut=shallow_cut))

        self.optimizer_8 = Optimizer(opt_problem=self.co.generic_8,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_8,
                                                               n_max=300,
                                                               shallow_cut=shallow_cut))

        self.optimizer_9 = Optimizer(opt_problem=self.co.generic_9,
                                     algorithm=EllipsoidMethod(x0=self.co.x0_9, n_max=300))

        self.optimizer_10 = Optimizer(
            opt_problem=OptimizationProblem(builder=self.co.rsp),
            algorithm=EllipsoidMethod(
                x0=self.co.x0_rsp,
                n_max=300,
                shallow_cut=shallow_cut
            )
        )

    def test_optimize(self):
        """Test the algorithm ellipsoid method for problem 1, with linear constraints.

        """
        opt = self.optimizer_1.optimize()
        np.testing.assert_allclose(opt.x, self.co.result_1, atol=1e-09)
        self.assertIsInstance(opt.x, np.ndarray)
        np.testing.assert_allclose(opt.fx, self.co.fx_res_1, atol=1e-09)
        self.assertIsInstance(opt.fx, np.ndarray)

    def test_optimize_2(self):
        """Test the algorithm ellipsoid method for problem 2, a multiobjective nonlinear example.

        """
        opt_2 = self.optimizer_2.optimize()
        dfx1 = self.co.f_2[0].gradient(opt_2.x)
        dfx2 = self.co.f_2[1].gradient(opt_2.x)
        norma1 = np.sqrt(np.sum(dfx1 * dfx1))
        norma2 = np.sqrt(np.sum(dfx2 * dfx2))
        cond1_x = dfx1 / norma1
        cond2_x = dfx2 / norma2

        np.testing.assert_allclose(cond1_x, (-cond2_x), atol=1e-05)
        self.assertIsInstance(opt_2.x, np.ndarray)

    def test_optimize_3(self):
        """Test the algorithm ellipsoid method for problem 3, with a polynomial function.

        """
        opt_3 = self.optimizer_3.optimize()
        np.testing.assert_allclose(opt_3.x, self.co.result_3, atol=1e-09)
        self.assertIsInstance(opt_3.x, np.ndarray)
        np.testing.assert_allclose(opt_3.fx, self.co.fx_res_3, atol=1e-09)
        self.assertIsInstance(opt_3.fx, np.ndarray)

    def test_optimize_4(self):
        """Test the algorithm ellipsoid method for problem 4, with a quadratic function.

        """
        opt_4 = self.optimizer_4.optimize()
        np.testing.assert_allclose(opt_4.x, self.co.result_4, atol=1e-09)
        self.assertIsInstance(opt_4.x, np.ndarray)
        np.testing.assert_allclose(opt_4.fx, self.co.fx_res_4, atol=1e-09)
        self.assertIsInstance(opt_4.fx, np.ndarray)

    def test_optimize_5(self):
        """Test the algorithm ellipsoid method for Booth Function.

        """

        opt_5 = self.optimizer_5.optimize()
        np.testing.assert_allclose(opt_5.x, self.co.result_5, atol=1e-09)
        self.assertIsInstance(opt_5.x, np.ndarray)
        np.testing.assert_allclose(opt_5.fx, self.co.fx_res_5, atol=1e-09)
        self.assertIsInstance(opt_5.fx, np.ndarray)

    def test_optimize_6(self):
        """Test the algorithm ellipsoid method for Zacharov Function.

        """
        opt_6 = self.optimizer_6.optimize()
        np.testing.assert_allclose(opt_6.x, self.co.result_6, atol=1e-09)
        self.assertIsInstance(opt_6.x, np.ndarray)
        np.testing.assert_allclose(opt_6.fx, self.co.fx_res_6, atol=1e-09)
        self.assertIsInstance(opt_6.fx, np.ndarray)

    def test_optimize_7(self):
        """Test the algorithm ellipsoid method for a constrained problem, with 5 variables.

        """

        opt_7 = self.optimizer_7.optimize()
        np.testing.assert_allclose(opt_7.x, self.co.result_7, atol=1e-03)
        # set this tolerance because my result just has this accuracy
        self.assertIsInstance(opt_7.x, np.ndarray)
        np.testing.assert_allclose(opt_7.fx, self.co.fx_res_7, atol=1e-03)
        self.assertIsInstance(opt_7.fx, np.ndarray)

    def test_optimize_8(self):
        """Test the algorithm ellipsoid method for a constrained problem, with 7 variables.

        """

        opt_8 = self.optimizer_8.optimize()
        np.testing.assert_allclose(opt_8.x, self.co.result_8, atol=1e-06)
        self.assertIsInstance(opt_8.x, np.ndarray)
        np.testing.assert_allclose(opt_8.fx, self.co.fx_res_8, atol=1e-06)
        self.assertIsInstance(opt_8.fx, np.ndarray)

    def test_optimize_9(self):
        """Test the algorithm ellipsoid method for a constrained problem, with 7 variables.

        """

        opt_9 = self.optimizer_9.optimize()
        np.testing.assert_allclose(opt_9.x, self.co.result_9, atol=1e-04)
        self.assertIsInstance(opt_9.x, np.ndarray)
        np.testing.assert_allclose(opt_9.fx, self.co.fx_res_9, atol=1e-04)
        self.assertIsInstance(opt_9.fx, np.ndarray)

    def test_debug_optimize(self):
        """Test the debug optimize method for number of iterations.

        """

        d_opt = self.optimizer_1.optimize(debug=True)
        self.assertLess(d_opt.n_iterations, 300)
        d_opt_2 = self.optimizer_2.optimize(debug=True)
        self.assertLess(d_opt_2.n_iterations, 300)
        d_opt_3 = self.optimizer_3.optimize(debug=True)
        self.assertLess(d_opt_3.n_iterations, 200)
        d_opt_4 = self.optimizer_4.optimize(debug=True)
        self.assertLess(d_opt_4.n_iterations, 200)
        d_opt_5 = self.optimizer_5.optimize(debug=True)
        self.assertLess(d_opt_5.n_iterations, 200)
        d_opt_6 = self.optimizer_6.optimize(debug=True)
        self.assertLess(d_opt_6.n_iterations, 500)
        d_opt_7 = self.optimizer_7.optimize(debug=True)
        self.assertLess(d_opt_7.n_iterations, 300)
        d_opt_8 = self.optimizer_8.optimize(debug=True)
        self.assertLess(d_opt_8.n_iterations, 300)

    def test_raises(self):
        """Test some Warnings and ValueErrors from Ellipsoid Method.

        """

        self.assertRaisesRegex(ValueError, "Initial point must be a column vector.",
                               EllipsoidMethod, np.array([[2, 3, 5], [2, 3, 5]]))
        self.assertRaisesRegex(Warning, "x must be a numpy array!", EllipsoidMethod,
                               np.array([[2], [3]]), 23)
        self.assertRaisesRegex(ValueError,
                               "Maximum number of cuts must be a positive number!",
                               EllipsoidMethod, np.array([[2], [3]]),
                               np.array([[]]), -32)
        self.assertRaisesRegex(ValueError, r"Shallow cut must be in \[0, 1\).",
                               EllipsoidMethod, np.array([[2], [3]]),
                               np.array([[]]), 32, 2)
        self.assertRaisesRegex(Warning, "Decomposition must be a boolean!",
                               EllipsoidMethod, np.array([[2], [3]]),
                               np.array([[]]), 32, 1, 0)
        self.assertRaisesRegex(Warning, "Memory must be a boolean!", EllipsoidMethod,
                               np.array([[2], [3]]), np.array([[]]), 32, 1, False, 0)

    def test_plot_mono(self):
        aux = self.optimizer_3.optimization_problem.plot_mono_objective_problem()
        self.assertTrue(isinstance(aux, QuadContourSet))

        self.optimizer_3.optimize()
        aux = self.optimizer_3.optimization_problem.plot(show_plot=False)
        self.assertTrue(isinstance(aux, QuadContourSet))


class TestAugmentedLagrangian(unittest.TestCase):
    """This class tests the Augmented Lagrangian algorithm.

    """

    def setUp(self):

        self.co = CommonObjects()

        self.optimizer_1 = Optimizer(opt_problem=self.co.generic_1,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_1, n_max=50))

        # multiobjective problem, not implemented by the lagrangian
        self.optimizer_2 = Optimizer(opt_problem=self.co.generic_2,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_2, n_max=50))

        self.optimizer_3 = Optimizer(opt_problem=self.co.generic_3,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_3, n_max=50))

        self.optimizer_4 = Optimizer(opt_problem=self.co.generic_4,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_4,
                                                                   n_max=50))

        self.optimizer_5 = Optimizer(opt_problem=self.co.generic_5,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_5,
                                                                   n_max=50))

        self.optimizer_6 = Optimizer(opt_problem=self.co.generic_6,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_6,
                                                                   n_max=50))

        self.optimizer_7 = Optimizer(opt_problem=self.co.generic_7,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_7,
                                                                   n_max=50))

        self.optimizer_8 = Optimizer(opt_problem=self.co.generic_8,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_8,
                                                                   n_max=50))

        self.optimizer_9 = Optimizer(opt_problem=self.co.generic_9,
                                     algorithm=AugmentedLagrangian(x0=self.co.x0_9, n_max=100))

        self.optimizer_10 = Optimizer(
            opt_problem=OptimizationProblem(builder=self.co.rsp),
            algorithm=AugmentedLagrangian(
                x0=self.co.x0_rsp,
                n_max=100
            )
        )

    def test_optimize(self):
        """Test the algorithm ellipsoid method for problem 1, with linear constraints.

        """
        opt = self.optimizer_1.optimize()
        np.testing.assert_allclose(opt.x, self.co.result_1, atol=1e-04)
        self.assertIsInstance(opt.x, np.ndarray)
        np.testing.assert_allclose(opt.fx, self.co.fx_res_1, atol=1e-04)
        self.assertIsInstance(opt.fx, np.ndarray)

    def test_optimize_3(self):
        """Test the algorithm ellipsoid method for problem 3, with a polynomial function.

        """
        opt_3 = self.optimizer_3.optimize()
        np.testing.assert_allclose(opt_3.x, self.co.result_3, atol=1e-04)
        self.assertIsInstance(opt_3.x, np.ndarray)
        np.testing.assert_allclose(opt_3.fx, self.co.fx_res_3, atol=1e-04)
        self.assertIsInstance(opt_3.fx, np.ndarray)

    def test_optimize_4(self):
        """Test the algorithm ellipsoid method for problem 4, with a quadratic function.

        """
        opt_4 = self.optimizer_4.optimize()
        np.testing.assert_allclose(opt_4.x, self.co.result_4, atol=1e-04)
        self.assertIsInstance(opt_4.x, np.ndarray)
        np.testing.assert_allclose(opt_4.fx, self.co.fx_res_4, atol=1e-04)
        self.assertIsInstance(opt_4.fx, np.ndarray)

    def test_optimize_9(self):
        """Test the algorithm ellipsoid method for a constrained problem, with 7 variables.

        """

        opt_9 = self.optimizer_9.optimize()
        np.testing.assert_allclose(opt_9.x, self.co.result_9, atol=1e-04)
        self.assertIsInstance(opt_9.x, np.ndarray)
        np.testing.assert_allclose(opt_9.fx, self.co.fx_res_9, atol=1e-04)
        self.assertIsInstance(opt_9.fx, np.ndarray)

    def test_optimize_10(self):
        """Test the algorithm ellipsoid method for a constrained problem, with 7 variables.

        """

        opt_10 = self.optimizer_10.optimize()
        np.testing.assert_allclose(opt_10.x, self.co.result_10, atol=1e-04)
        self.assertIsInstance(opt_10.x, np.ndarray)


class TestDualDecompositionMethod(unittest.TestCase):
    """This class tests the Dual Decomposition algorithm.

    """

    def setUp(self):
        # dimension
        n = 2

        # objective functions
        def f_1(x): return np.exp(-2 * x[0, :]) + 0 * x[1, :]

        def f_2(x): return np.exp(-2 * x[1, :]) + 0 * x[0, :]

        f_i = [GenericFunction(func=f_1, n=n), GenericFunction(func=f_2, n=n)]  # f_i list

        # inequality constraints functions
        def g_1(x): return x[0, :] - 10

        def g_2(x): return x[1, :]

        g_i = [GenericFunction(func=g_1, n=n), GenericFunction(func=g_2, n=n)]  # g_i list

        # bounds
        x_min = np.array([2, 2]).reshape(-1, 1)  # lower
        x_max = np.array([6, 6]).reshape(-1, 1)  # upper
        x_bounds = np.hstack((x_min, x_max))

        # build generic problem instance
        generic = OptimizationProblem(builder=SeparableResourceAllocation(f_i=f_i,
                                                                          coupling_eq_constraints=[],
                                                                          coupling_ineq_constraints=g_i,
                                                                          x_bounds=x_bounds
                                                                          ))
        # builder optimization
        self.optimizer = Optimizer(opt_problem=generic, algorithm=DualDecomposition(eps=1e-6))
        self.xs = np.array([[5.], [5.]])

    def test_problem(self):
        """Test the dual decomposition method for problem 1.

        """
        results = self.optimizer.optimize()
        np.testing.assert_allclose(results.x, self.xs, atol=1e-6)


class TestNelderMead(unittest.TestCase):
    """This class tests the Nelder Mead algorithm method.

    """

    def setUp(self):

        delta_r = 1.0
        delta_e = 2.0
        delta_ic = 0.5
        delta_oc = 0.5
        delta_s = 0.5

        # ---------- optimization problems without constraints ----------

        def f_obj_1(x):
            return np.square(x[0][0] - 1) + 4*np.square(x[1][0])

        def f_obj_2(x):
            return np.max(np.abs(x * (.5 + 1e-2) - .5 * np.sin(x) * np.cos(x)), axis=0)

        def f_obj_3(x):
            return np.square(x[0][0]) + np.square(x[1][0]) - x[0][0] * x[1][0]

        def f_obj_4(x):
            return 200 * np.square(x[0][0]) + np.square(x[1][0])

        def f_obj_5(x):
            return 100 * np.square((x[1][0] - np.square(x[0][0]))) + np.square(1 - x[0][0])

        def f_obj_6(x):
            return np.square(x[0][0] + 10 * x[1][0]) + 5 * np.square(x[2][0] - x[3][0]) + \
                   np.power((x[1][0] - 2 * x[2][0]), 4) + 10 * np.power(x[0][0] - x[3][0], 4)

        x_min_1 = np.array([-10, -10]).reshape(-1, 1)
        x_max_1 = np.array([10, 10]).reshape(-1, 1)
        self.x_bounds_1 = np.hstack((x_min_1, x_max_1))

        x_min_2 = np.array([[-5], [-5]])
        x_max_2 = np.array([10, 10]).reshape(-1, 1)
        self.x_bounds_2 = np.hstack((x_min_2, x_max_2))

        x_min_3 = np.array([-5, -5]).reshape(-1, 1)
        x_max_3 = np.array([10, 10]).reshape(-1, 1)
        self.x_bounds_3 = np.hstack((x_min_3, x_max_3))

        x_min_4 = np.array([-10, -10]).reshape(-1, 1)
        x_max_4 = np.array([10, 10]).reshape(-1, 1)
        self.x_bounds_4 = np.hstack((x_min_4, x_max_4))

        x_min_5 = np.array([-5, -5]).reshape(-1, 1)
        x_max_5 = np.array([10, 10]).reshape(-1, 1)
        self.x_bounds_5 = np.hstack((x_min_5, x_max_5))

        x_min_6 = np.array([-5, -5, -5, -5]).reshape(-1, 1)  # lower
        x_max_6 = np.array([10, 10, 10, 10]).reshape(-1, 1)  # upper
        self.x_bounds_6 = np.hstack((x_min_6, x_max_6))

        self.f_1 = [GenericFunction(func=f_obj_1, n=2)]
        self.f_2 = [GenericFunction(func=f_obj_2, n=2)]
        self.f_3 = [GenericFunction(func=f_obj_3, n=2)]
        self.f_4 = [GenericFunction(func=f_obj_4, n=2)]
        self.f_5 = [GenericFunction(func=f_obj_5, n=2)]
        self.f_6 = [GenericFunction(func=f_obj_6, n=4)]

        self.ineq_cons_1 = []
        self.eq_cons_1 = []

        self.ineq_cons_2 = []
        self.eq_cons_2 = []

        self.ineq_cons_3 = []
        self.eq_cons_3 = []

        self.ineq_cons_4 = []
        self.eq_cons_4 = []

        self.ineq_cons_5 = []
        self.eq_cons_5 = []

        self.ineq_cons_6 = []
        self.eq_cons_6 = []

        self.x0_1 = np.array([5, 6]).reshape(-1, 1)
        self.x0_2 = np.array([2, 2]).reshape(-1, 1)
        self.x0_3 = np.array([2, 2]).reshape(-1, 1)
        self.x0_4 = np.array([10, 10]).reshape(-1, 1)
        self.x0_5 = np.array([-2, 1]).reshape(-1, 1)
        self.x0_6 = np.array([3, -1, 0, 1]).reshape(-1, 1)

        self.x_result_1 = np.array([1, 0]).reshape(-1, 1)
        self.x_result_2 = np.array([0, 0]).reshape(-1, 1)
        self.x_result_3 = np.array([0, 0]).reshape(-1, 1)
        self.x_result_4 = np.array([0, 0]).reshape(-1, 1)
        self.x_result_5 = np.array([1, 1]).reshape(-1, 1)
        self.x_result_6 = np.array([0, 0, 0, 0]).reshape(-1, 1)

        self.fx_res_1 = 0
        self.fx_res_2 = 0
        self.fx_res_3 = 0
        self.fx_res_4 = 0
        self.fx_res_5 = 0
        self.fx_res_6 = 0

        problem_1 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_1,
                eq_cons=self.eq_cons_1,
                ineq_cons=self.ineq_cons_1,
                x_bounds=self.x_bounds_1
            )
        )

        problem_2 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_2,
                eq_cons=self.eq_cons_2,
                ineq_cons=self.ineq_cons_2,
                x_bounds=self.x_bounds_2
            )
        )

        problem_3 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_3,
                eq_cons=self.eq_cons_3,
                ineq_cons=self.ineq_cons_3,
                x_bounds=self.x_bounds_3
            )
        )

        problem_4 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_4,
                eq_cons=self.eq_cons_4,
                ineq_cons=self.ineq_cons_4,
                x_bounds=self.x_bounds_4
            )
        )

        problem_5 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_5,
                eq_cons=self.eq_cons_5,
                ineq_cons=self.ineq_cons_5,
                x_bounds=self.x_bounds_5
            )
        )

        problem_6 = OptimizationProblem(
            builder=GenericProblem(
                f=self.f_6,
                eq_cons=self.eq_cons_6,
                ineq_cons=self.ineq_cons_6,
                x_bounds=self.x_bounds_6
            )
        )

        self.optimizer_1 = Optimizer(
            opt_problem=problem_1,
            algorithm=NelderMead(self.x0_1, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_2 = Optimizer(
            opt_problem=problem_2,
            algorithm=NelderMead(self.x0_2, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_3 = Optimizer(
            opt_problem=problem_3,
            algorithm=NelderMead(self.x0_3, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_4 = Optimizer(
            opt_problem=problem_4,
            algorithm=NelderMead(self.x0_4, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_5 = Optimizer(
            opt_problem=problem_5,
            algorithm=NelderMead(self.x0_5, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_6 = Optimizer(
            opt_problem=problem_6,
            algorithm=NelderMead(self.x0_6, delta_r, delta_e, delta_ic, delta_oc, delta_s)
        )

        self.optimizer_1.algorithm.n_max = 500
        self.optimizer_2.algorithm.n_max = 500
        self.optimizer_3.algorithm.n_max = 500
        self.optimizer_4.algorithm.n_max = 500
        self.optimizer_5.algorithm.n_max = 500
        self.optimizer_6.algorithm.n_max = 500

        # ---------- optimization problems with constraints ----------

    def test_optimize_1(self):

        opt_1 = self.optimizer_1.optimize()
        np.testing.assert_allclose(opt_1.x, self.x_result_1, atol=1e-06)
        np.testing.assert_allclose(opt_1.fx, self.fx_res_1, atol=1e-06)
        self.assertIsInstance(opt_1.x, np.ndarray)

    def test_optimize_2(self):

        opt_2 = self.optimizer_2.optimize()
        np.testing.assert_allclose(opt_2.x, self.x_result_2, atol=1e-06)
        np.testing.assert_allclose(opt_2.fx, self.fx_res_2, atol=1e-06)
        self.assertIsInstance(opt_2.x, np.ndarray)

    def test_optimize_3(self):

        opt_3 = self.optimizer_3.optimize()
        np.testing.assert_allclose(opt_3.x, self.x_result_3, atol=1e-06)
        np.testing.assert_allclose(opt_3.fx, self.fx_res_3, atol=1e-06)
        self.assertIsInstance(opt_3.x, np.ndarray)

    def test_optimize_4(self):

        opt_4 = self.optimizer_4.optimize()
        np.testing.assert_allclose(opt_4.x, self.x_result_4, atol=1e-06)
        np.testing.assert_allclose(opt_4.fx, self.fx_res_4, atol=1e-06)
        self.assertIsInstance(opt_4.x, np.ndarray)

    def test_optimize_5(self):

        opt_5 = self.optimizer_5.optimize()
        np.testing.assert_allclose(opt_5.x, self.x_result_5, atol=1e-06)
        np.testing.assert_allclose(opt_5.fx, self.fx_res_5, atol=1e-06)
        self.assertIsInstance(opt_5.x, np.ndarray)

    def test_optimize_6(self):

        opt_6 = self.optimizer_6.optimize()
        np.testing.assert_allclose(opt_6.x, self.x_result_6, atol=1e-06)
        np.testing.assert_allclose(opt_6.fx, self.fx_res_6, atol=1e-06)
        self.assertIsInstance(opt_6.x, np.ndarray)


if __name__ == '__main__':
    unittest.main()
