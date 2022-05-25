import unittest
from science_optimization.algorithms.utils import box_constraints, hypercube_intersection, sequence_patterns, pareto_set
import numpy as np


class TestBoxConstraints(unittest.TestCase):
    """Test box constraints component"""

    def setUp(self):
        """Test set up"""

        # set up
        self.x_bounds = np.array([[-1, 1], [-1, 1]])
        self.x = np.array([[0], [0]])

        # test 1
        self.x1 = np.array([[0], [0]])

        # test 2
        self.x2 = np.array([[2], [0]])

        # test 3
        self.x3 = np.array([[-2], [0]])

    def test_x_1(self):
        """Test box constraints violations"""

        x = box_constraints(x=self.x1, x_bounds=self.x_bounds)
        np.testing.assert_array_equal(x, self.x)

    def test_x_2(self):
        """Test box constraints violations"""

        x = box_constraints(x=self.x2, x_bounds=self.x_bounds)
        np.testing.assert_array_equal(x, self.x)

    def test_x_3(self):
        """Test box constraints violations"""

        x = box_constraints(x=self.x3, x_bounds=self.x_bounds)
        np.testing.assert_array_equal(x, self.x)


class TestHypercubeIntersection(unittest.TestCase):
    """Test hypercube intersection component"""

    def setUp(self):
        """Test set up"""

        # set up
        self.x = np.array([[0], [0]])
        self.x_bounds = np.array([[-1, 1], [-1, 1]])

        # test 1
        self.d1 = np.array([[1], [1]])
        self.a1 = 1.0

        # test 2
        self.d2 = np.array([[-1], [-1]])
        self.a2 = 1.0

        # test 3
        self.d3 = np.array([[1], [0]])
        self.td3 = 0

        # test 4
        self.d4 = np.array([[0], [1]])
        self.td4 = 1

    def test_a_return_1(self):
        """Test first return a, such that x + a*d lies on hypercube facet"""

        a, _ = hypercube_intersection(x=self.x, d=self.d1, x_bounds=self.x_bounds)
        np.testing.assert_equal(a, self.a1)

    def test_a_return_2(self):
        """Test first return a, such that x + a*d lies on hypercube facet"""

        a, _ = hypercube_intersection(x=self.x, d=self.d2, x_bounds=self.x_bounds)
        np.testing.assert_equal(a, self.a2)

    def test_tight_dim_return_1(self):
        """Test second return tight_dim, such that x + a*d lies on hypercube facet"""

        _, td = hypercube_intersection(x=self.x, d=self.d3, x_bounds=self.x_bounds)
        np.testing.assert_equal(td, self.td3)

    def test_tight_dim_return_2(self):
        """Test second return tight_dim, such that x + a*d lies on hypercube facet"""

        _, td = hypercube_intersection(x=self.x, d=self.d4, x_bounds=self.x_bounds)
        np.testing.assert_equal(td, self.td4)


class TestSequencePattern(unittest.TestCase):
    """Test sequence pattern component"""

    def setUp(self):
        """Test set up"""

        # set up
        self.x = np.array([0, 1, 2, 3, 4, 5])
        self.fx1 = np.array([1, 0, 1, 0, 1, 1])
        self.fx2 = np.array([5, 4, 3, 2, 1, 0])

        # test 1
        self.ivp1 = np.array([1, 3])
        self.iap1 = np.array([2, 4])

        # test 2
        self.ivp2 = np.array([])
        self.iap2 = np.array([])

    def test_pattern_1(self):
        """Test sequence with v-a-patterns"""

        ivp, iap = sequence_patterns(x=self.x, fx=self.fx1)
        np.testing.assert_equal(ivp, self.ivp1)
        np.testing.assert_equal(iap, self.iap1)

    def test_pattern_2(self):
        """Test sequence with no v-a-pattern"""

        ivp, iap = sequence_patterns(x=self.x, fx=self.fx2)
        np.testing.assert_equal(ivp, self.ivp2)
        np.testing.assert_equal(iap, self.iap2)


class TestParetoSet(unittest.TestCase):
    """Test Pareto samplers"""

    def setUp(self):
        """Test set up"""

        # generate points (objective space)
        np.random.seed(51)
        self.fx = np.random.randn(2, 20)

        # pareto set
        self.ip = [False, False, False, True, False, False, False, False, False, False, True, False, True, False, False,
                   False, True, True, False, False]

    def test_pareto_set(self):
        """Test pareto set."""

        # indexes
        ip = pareto_set(self.fx)

        # test
        np.testing.assert_equal(self.ip, ip)


if __name__ == '__main__':
    unittest.main()
