import unittest

from science_optimization.function import LinearFunction, QuadraticFunction
from science_optimization.problems import Quadratic, KleeMinty, GenericProblem
from science_optimization.builder import OptimizationProblem, Objective, Constraint, Variable
import numpy as np


class TestQuadraticProblem(unittest.TestCase):
    """Quadratic problem test"""

    def setUp(self):
        """Test set up"""

        # Problem: (x[0]-1)^2 + 4.0*x[1]^2
        self.Q = np.array([[1, 0], [0, 4]])
        self.c = np.array([-2, 0]).reshape(-1, 1)
        self.d = np.array([[1]])

        # bounds
        x_min = np.array([-10, -10]).reshape(-1, 1)  # lower bound
        x_max = np.array([10, 10]).reshape(-1, 1)  # upper bound
        self.x_bounds = np.hstack((x_min, x_max))

        # builder quadratic problem instance
        self.quadratic = OptimizationProblem(builder=Quadratic(Q=self.Q, c=self.c, d=self.d, x_bounds=self.x_bounds))

        # expected quadratic objective function
        self.n_functions = 1

        # expected inequality constraints values
        self.A = None
        self.b = None

        # expected equality constraints values
        self.Aeq = None
        self.beq = None

    def test_var_bounds(self):
        """Variables bounds construction test."""

        np.testing.assert_equal(self.quadratic.variables.x_min, self.x_bounds[:, 0].reshape(-1, 1))
        np.testing.assert_equal(self.quadratic.variables.x_max, self.x_bounds[:, 1].reshape(-1, 1))

    def test_inequality_constraints(self):
        """Inequality constraints construction test."""

        np.testing.assert_equal(self.quadratic.constraints.A(), self.A)
        np.testing.assert_equal(self.quadratic.constraints.b(), self.b)

    def test_equality_constraints(self):
        """Equality constraints construction test."""

        np.testing.assert_equal(self.quadratic.constraints.Aeq(), self.Aeq)
        np.testing.assert_equal(self.quadratic.constraints.beq(), self.beq)

    def test_objective_coefficients(self):
        """Objective construction test."""

        np.testing.assert_equal(self.quadratic.objective.objectives.functions[0].parameters['Q'], self.Q)
        np.testing.assert_equal(self.quadratic.objective.objectives.functions[0].parameters['c'], self.c)
        np.testing.assert_equal(self.quadratic.objective.objectives.functions[0].parameters['d'], self.d)
        np.testing.assert_equal(self.quadratic.objective.objectives.n_functions, self.n_functions)

    def test_has_constraints(self):

        self.assertEqual(self.quadratic.has_equality_constraints(), False)
        self.assertEqual(self.quadratic.has_inequality_constraints(), False)


class TestKleeMintyProblem(unittest.TestCase):
    """Klee-Minty problem build test"""

    def setUp(self):
        """Test set up"""

        # builder klee-minty
        self.km = OptimizationProblem(builder=KleeMinty(dimension=3))

        # expected inequality constraints values
        self.A = np.array([[1., 0., 0.], [4., 1.0, 0.0], [8., 4., 1.]])

        self.b = np.array([[1e0], [1e2], [1e4]])

        # expected equality constraints values
        self.Aeq = None

        self.beq = None

        # expected objective coefficients
        self.C = -np.array([[4., 2., 1.]])
        self.d = np.array([[0]])

    def test_inequality_constraints(self):
        """Inequality constraints construction test."""

        np.testing.assert_equal(self.km.constraints.A(), self.A)
        np.testing.assert_equal(self.km.constraints.b(), self.b)

    def test_equality_constraints(self):
        """Equality constraints construction test."""

        np.testing.assert_equal(self.km.constraints.Aeq(), self.Aeq)
        np.testing.assert_equal(self.km.constraints.beq(), self.beq)

    def test_objective_coefficients(self):
        """Objective construction test."""

        np.testing.assert_equal(self.km.objective.C(), self.C)
        np.testing.assert_equal(self.km.objective.d(), self.d)

    def test_has_constraints(self):

        self.assertEqual(self.km.has_equality_constraints(), False)
        self.assertEqual(self.km.has_inequality_constraints(), True)


class TestGenericProblem(unittest.TestCase):
    """Test the Concrete builder implementation.

    """

    def setUp(self):
        self.fun = [QuadraticFunction(Q=(np.eye(3)), c=-2 * np.array([3, 5, 40]).reshape(-1, 1),
                                      d=(3 ** 2 + 5 ** 2 + 40 ** 2))]
        self.ineq_cons = [LinearFunction(c=np.array([1, 1, 0]).reshape(-1, 1), d=-10)]
        self.eq_cons = [LinearFunction(c=np.array([1, -1, 0]).reshape(-1, 1))]
        x_min = np.array([-10, -10, -10]).reshape(-1, 1)  # lower
        x_max = np.array([10, 10, 10]).reshape(-1, 1)  # upper
        self.x_bounds = np.hstack((x_min, x_max))
        self.problem = OptimizationProblem(
            builder=GenericProblem(f=self.fun, ineq_cons=self.ineq_cons,
                                   eq_cons=self.eq_cons, x_bounds=self.x_bounds))

    def test_build_objectives(self):
        """Test the built of objectives inside the generic problem.

        """

        self.assertIsInstance(self.problem.objective, Objective)
        f_x = self.problem.objective.objectives.eval(np.array([4, 4, 10]).reshape(-1, 1))
        np.testing.assert_allclose(f_x, self.fun[0].eval(np.array([4, 4, 10]).reshape(-1, 1)),
                                   atol=1e-06)

    def test_build_constraints(self):
        """Test the built of constraints inside the generic problem.

        """

        self.assertIsInstance(self.problem.constraints, Constraint)
        fx_eq = self.problem.constraints.equality_constraints.eval(np.array([[2], [2], [0]]))
        np.testing.assert_allclose(fx_eq, self.eq_cons[0].eval(np.array([[2], [2], [0]])),
                                   atol=1e-06)
        fx_ineq = self.problem.constraints.inequality_constraints.eval(np.array([[2], [2], [0]]))
        np.testing.assert_allclose(fx_ineq, self.ineq_cons[0].eval(np.array([[2], [2], [0]])),
                                   atol=1e-06)

    def test_build_variables(self):
        """Test the built of variables inside the generic problem.

        """

        self.assertIsInstance(self.problem.variables, Variable)

    def test_has_constraints(self):

        self.assertEqual(self.problem.has_equality_constraints(), True)
        self.assertEqual(self.problem.has_inequality_constraints(), True)


if __name__ == '__main__':
    unittest.main()
