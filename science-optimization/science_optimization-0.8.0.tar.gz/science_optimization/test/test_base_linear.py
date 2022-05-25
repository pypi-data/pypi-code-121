import unittest
from science_optimization.problems import Diet
from science_optimization.builder import OptimizationProblem
from science_optimization.algorithms.linear_programming import ScipySimplexMethod, ScipyInteriorPointMethod
from science_optimization.solvers import Optimizer
import numpy as np


class TestBaseLinear(unittest.TestCase):
    """Diet Problem test"""

    def setUp(self):
        """Test set up"""

        # minimum and maximum servings of each food
        food = ['corn', 'milk', 'white-bread']
        food_bounds = np.array([[0, 10],
                                [0, 10],
                                [0, 10]])

        # cost of each food
        cost = np.array([.18, .23, .05])

        # minimum and maximum demand of each nutrient
        demand = np.array([[2000, 2250],
                           [5000, 50000]])

        # nutrients on each food
        nutrient = np.array([[72, 121, 65],
                             [107, 500, 0]])

        # builder diet instance
        self.diet = OptimizationProblem(builder=Diet(food=food, food_limits=food_bounds,
                                                     cost=cost, nutrient=nutrient, demand=demand))

        # expected inequality constraints values
        self.A = np.array([[72.0, 121.0, 65.0], [107.0, 500.0, 0.0],
                           [-72.0, -121.0, -65.0], [-107.0, -500.0, -0.0]])

        self.b = np.array([[2250.0], [50000.0], [-2000.0], [-5000.0]])

        # expected equality constraints values
        self.Aeq = None

        self.beq = None

        # expected objective coefficients
        self.C = np.array([[0.18, 0.23, 0.05]])
        self.d = np.array([[0]])

        # builder optimization
        self.optimizer_simplex = Optimizer(opt_problem=self.diet, algorithm=ScipySimplexMethod())
        self.optimizer_ip = Optimizer(opt_problem=self.diet, algorithm=ScipyInteriorPointMethod())
        self.x = np.array([1.944444, 10., 10.]).reshape(-1, 1)
        self.fx = np.array([3.15])

    def test_inequality_constraints(self):
        """Inequality constraints construction test."""

        np.testing.assert_equal(self.diet.constraints.A(), self.A)
        np.testing.assert_equal(self.diet.constraints.b(), self.b)

    def test_equality_constraints(self):
        """Equality constraints construction test."""

        np.testing.assert_equal(self.diet.constraints.Aeq(), self.Aeq)
        np.testing.assert_equal(self.diet.constraints.beq(), self.beq)

    def test_objective_coefficients(self):
        """Objective construction test."""

        np.testing.assert_equal(self.diet.objective.C(), self.C)
        np.testing.assert_equal(self.diet.objective.d(), self.d)

    def test_optimization_simplex(self):
        """Test optimization result of Simplex method."""

        result = self.optimizer_simplex.optimize(debug=False)
        np.testing.assert_allclose(result.x, self.x, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(result.fx, self.fx, rtol=1e-6, atol=1e-6)

    def test_optimization_interior_point(self):
        """Test optimization result of Simplex method."""

        result = self.optimizer_ip.optimize(debug=False)
        np.testing.assert_allclose(result.x, self.x, rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(result.fx, self.fx, rtol=1e-6, atol=1e-6)


if __name__ == '__main__':
    unittest.main()
