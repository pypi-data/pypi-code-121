import unittest
import numpy as np
from science_optimization.function import FunctionsComposite, QuadraticFunction, GenericFunction
from science_optimization.function import LinearFunction
from science_optimization.builder import Constraint, Objective, Variable, OptimizationProblem
from science_optimization.problems import GenericProblem


class TestConstraints(unittest.TestCase):
    """Test the class that build the optimization problem constraints.

    """

    def setUp(self):
        self.inequalities = LinearFunction(c=np.array([1, 1, 0]).reshape(-1, 1), d=-10)
        self.equalities = LinearFunction(c=np.array([1, -1, 0]).reshape(-1, 1))
        self.x_1 = np.array([[2], [2], [0]])
        self.x_2 = np.array([[3], [10], [0]])
        self.f_c = FunctionsComposite()

    def test_equality_constraints(self):
        """ Test the warning when equality constraints are not a functions composite instance.

        """

        self.assertRaisesRegex(Warning, 'Equality constraints must be'
                                        ' a FunctionsComposite instance.',
                               Constraint, self.equalities, None)

    def test_inequality_constraints(self):
        """ Test the warning when inequality constraints are not a functions composite instance.

        """

        self.assertRaisesRegex(Warning, 'Inequality constraints must be'
                                        ' a FunctionsComposite instance.',
                               Constraint, None, self.inequalities)

    def test_equality_constraints_feasibility(self):
        """Test the feasibility method for equality constraints.

        """

        self.f_c.add(self.equalities)
        test_cons = Constraint(eq_cons=self.f_c)
        eval_cons1 = test_cons.equality_constraints_feasibility(self.x_1)
        eval_cons2 = test_cons.equality_constraints_feasibility(self.x_2)
        self.assertEqual(eval_cons1, [True])
        self.assertEqual(eval_cons2, [False])

    def test_inequality_constraints_feasibility(self):
        """Test the feasibility method for inequality constraints.

        """

        self.f_c.add(self.inequalities)
        test_cons = Constraint(ineq_cons=self.f_c)
        eval_cons1 = test_cons.inequality_constraints_feasibility(self.x_1)
        eval_cons2 = test_cons.inequality_constraints_feasibility(self.x_2)
        self.assertEqual(eval_cons1, [True])
        self.assertEqual(eval_cons2, [False])

    def test_A(self):
        """ Test for A method.

        """

        self.f_c.add(self.inequalities)
        c = np.array([1, 1, 0]).reshape(-1, 1)
        test_cons = Constraint(ineq_cons=self.f_c)
        test_a = test_cons.A()
        np.testing.assert_array_equal(test_a, c.T)

    def test_b(self):
        """ Test for b method.

        """

        self.f_c.add(self.inequalities)
        b = 10
        test_cons = Constraint(ineq_cons=self.f_c)
        test_b = test_cons.b()
        np.testing.assert_array_equal(test_b, b)

    def test_Aeq(self):
        """ Test for Aeq method.

        """

        self.f_c.add(self.equalities)
        c = np.array([1, -1, 0]).reshape(-1, 1)
        test_cons = Constraint(eq_cons=self.f_c)
        test_a_eq = test_cons.Aeq()
        np.testing.assert_array_equal(test_a_eq, c.T)

    def test_beq(self):
        """ Test for beq method.

        """

        self.f_c.add(self.equalities)
        b = 0
        test_cons = Constraint(eq_cons=self.f_c)
        test_beq = test_cons.beq()
        np.testing.assert_array_equal(test_beq, b)


class TestObjective(unittest.TestCase):
    """Test the class that build the optimization objectives.

    """

    def setUp(self):
        self.f_c = FunctionsComposite()
        self.f_c.add(LinearFunction(c=(np.array([-2, 0]).reshape(-1, 1)), d=1))
        self.quad = QuadraticFunction(Q=np.array([[1, 0], [0, 4]]),
                                      c=(np.array([-2, 0]).reshape(-1, 1)), d=1)

    def test_objective_functions(self):
        """ Test the construction of an objective function.

        """

        testobjective = Objective(objective=self.f_c)
        self.assertIsInstance(testobjective, Objective)
        f_x = testobjective.objectives.eval(np.array([[3], [6]]))
        np.testing.assert_allclose(f_x, self.f_c.eval(np.array([[3], [6]])), atol=1e-06)

    def test_objective_functions_2(self):
        """ Test the warning when an objective function is not a functions composite instance.

        """

        self.assertRaisesRegex(Warning, 'Objective must be a FunctionsComposite instance.',
                               Objective, self.quad)

    def test_C(self):
        """ Test for C method.

        """

        c = np.array([-2, 0]).reshape(-1, 1)
        test_objective = Objective(objective=self.f_c)
        test_c = test_objective.C()
        np.testing.assert_array_equal(test_c, c.T)

    def test_d(self):
        """Test for D method.

        """

        d = 1
        test_objective = Objective(objective=self.f_c)
        test_d = test_objective.d()
        np.testing.assert_array_equal(test_d, d)


class TestVariables(unittest.TestCase):
    """Test the class that build the optimization variables.

    """

    def setUp(self):
        # example 1 - complete variable
        self.var_bounds = np.array([[-2, 2], [-2, 2], [-2, 2]])
        self.var = Variable(x_min=self.var_bounds[:, 0].reshape(-1, 1),
                            x_max=self.var_bounds[:, 1].reshape(-1, 1))

    def test_variables(self):
        """Test the built of variables from an opt. problem.

        """

        self.assertIsInstance(self.var, Variable)

    def test_x_min(self):
        """Test the built of a vector with lower bounds.

        """

        np.testing.assert_equal(self.var.x_min, np.array([[-2], [-2], [-2]]))

    def test_x_max(self):
        """Test the built of a vector with upper bounds.

        """

        np.testing.assert_equal(self.var.x_max, np.array([[2], [2], [2]]))


class TestOptimizationProblem(unittest.TestCase):
    """Diet Problem test"""

    def setUp(self):
        """Test set up"""

        # objectives
        f1 = lambda x: x ** 2
        f2 = lambda x: (x - 1) ** 3

        # constraints
        g1 = lambda x: x + 2
        g2 = lambda x: -x - 1
        h1 = lambda x: x

        # bounds
        x_bounds = np.array([[-10, 10]])

        # build a multiobjective optimization problem
        f = [GenericFunction(func=f1, n=1), GenericFunction(func=f2, n=1)]
        g = [GenericFunction(func=g1, n=1), GenericFunction(func=g2, n=1)]
        h = [GenericFunction(func=h1, n=1)]
        self.op = OptimizationProblem(builder=GenericProblem(f=f, ineq_cons=g, eq_cons=h, x_bounds=x_bounds))
        self.x = np.array([[0.]])

        # expected output
        self.f = np.array([[0], [-1]])
        self.g = np.array([[2], [-1]])
        self.h = np.array([[0]])

        self.df = np.array([[0, 3]])
        self.dg = np.array([[1, -1]])
        self.dh = np.array([[1]])

        self.hf = np.zeros((2, 1, 1))
        self.hf[0, ...] = np.array([[2]])
        self.hf[1, ...] = np.array([[-6]])
        self.hg = np.zeros((2, 1, 1))
        self.hg[0, ...] = np.array([[0]])
        self.hg[1, ...] = np.array([[0]])
        self.hh = np.zeros((1, 1, 1))
        self.hh[0, ...] = np.array([[0]])

    def test_op_evaluation(self):
        """Optimization problem evaluation."""

        f, g, h, df, dg, dh, hf, hg, hh = self.op(self.x)
        np.testing.assert_almost_equal(f, self.f)
        np.testing.assert_almost_equal(g, self.g)
        np.testing.assert_almost_equal(h, self.h)

        np.testing.assert_almost_equal(df, self.df, decimal=3)
        np.testing.assert_almost_equal(dg, self.dg, decimal=3)
        np.testing.assert_almost_equal(dh, self.dh, decimal=3)

        np.testing.assert_almost_equal(hf, self.hf, decimal=3)
        np.testing.assert_almost_equal(hg, self.hg, decimal=3)
        np.testing.assert_almost_equal(hh, self.hh, decimal=3)


if __name__ == '__main__':
    unittest.main()
