import unittest
import pickle
import numpy as np
from matplotlib.contour import QuadContourSet

from science_optimization.function import QuadraticFunction, PolynomialFunction, LinearFunction, FunctionsComposite, \
    GenericFunction


class TestQuadraticFunction(unittest.TestCase):
    """This class tests a Quadratic Function constructor.
    Function form: f(x) = x'Qx + c'x + d
    """

    def setUp(self):
        """
        Set parameters
        """

        # 1st test:
        # file with data and results
        with open('science_optimization/test/valuesquad.pickle', 'rb') as quad:
            valuesquad = pickle.load(quad)

        # dim x = (3,100), 100 random decimal evaluation points
        # coefficients were also chosen randomly
        # 3 variables
        self.exqfull = QuadraticFunction(Q=valuesquad.get('Q'), c=valuesquad.get('c'),
                                         d=valuesquad.get('d'))
        self.xfull = valuesquad.get("x")
        self.fxfullr = valuesquad.get('fx')
        self.dfdxfullr = valuesquad.get('dfdx')
        self.hfdxfullr = valuesquad.get('hfdx')

        # 2nd test:
        # including decimal and negative points, and 2 variables, multiple points
        self.exq = QuadraticFunction(Q=np.array([[1, 0], [0, 4]]),
                                     c=(np.array([-2, 0]).reshape(-1, 1)), d=1)
        # dim x = (2,10)
        self.x_1 = np.array([[0.58492761, 0.4712184, 0.44607568, 0.47011531, 0.79212303,
                              0.12377401, 0.64318432, 0.09558947, 0.97544578, 0.7841664],
                             [0.16544039, 0.73910926, 0.93273155, 0.3036412, 0.64141055,
                              0.56221874, 0.09234208, 0.4291622, 0.48548053, 0.12629585]])

        # dim x_2 = (2, 1)
        self.x_2 = np.array([[3], [6]])
        # dim x_3 = (2, 2)
        self.x_3 = np.array([[0.00056, -6.2037], [-1.05674, 2.000069]])
        # dim x_4 = (2, 3)
        self.x_4 = np.array([[3, 6, 2], [3, 6, 2]])

        self.x_i = 23
        self.x_c = np.array([[2], [1], [3]])

        # 3rd test:
        # file with data - quadratic coefficients are represented by a sparse matrix
        with open('science_optimization/test/valuessparse.pickle', 'rb') as quad_s:
            valuessparse = pickle.load(quad_s)
        # dim x = (3,100)
        self.exqs = QuadraticFunction(Q=valuessparse.get('Q'), c=valuessparse.get('c'),
                                      d=valuessparse.get('d'))
        self.x_s = valuessparse.get("x")
        self.fxsr = valuessparse.get('fx')
        self.dfdxsr = valuessparse.get('dfdx')
        self.hfdxsr = valuessparse.get('hfdx')

    def test_eval_1(self):
        """ Test the quadratic function evaluation for 100 points and 3 variables.
        Test the result and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        fxfull = self.exqfull.eval(self.xfull)
        np.testing.assert_allclose(fxfull, self.fxfullr, atol=1e-09)
        self.assertIsInstance(fxfull, np.ndarray)

    def test_eval_2(self):
        """ Test the quadratic function evaluation for multiple points, but 2 variables.
        Test the result and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        fx_1 = self.exq.eval(self.x_1)
        np.testing.assert_allclose(fx_1, np.array([[0.28176718, 2.46473997, 3.78678473,
                                                    0.6495697, 1.68884281, 2.03213163,
                                                    0.16142567, 1.55467918, 0.94336829,
                                                    0.11038671]]),
                                   atol=1e-09)
        self.assertIsInstance(fx_1, np.ndarray)

        fx_2 = self.exq.eval(self.x_2)
        np.testing.assert_allclose(fx_2, np.array([[148]]), atol=1e-09)
        self.assertIsInstance(fx_2, np.ndarray)

        fx_3 = self.exq.eval(self.x_3)
        np.testing.assert_allclose(fx_3, np.array([[5.46567802, 67.89439771]]), atol=1e-09)
        self.assertIsInstance(fx_3, np.ndarray)

        fx_4 = self.exq.eval(self.x_4)
        np.testing.assert_allclose(fx_4, np.array([[40, 169, 17]]), atol=1e-09)
        self.assertIsInstance(fx_4, np.ndarray)

    def test_eval_3(self):
        """ Test the quadratic function evaluation. An example with sparse matrix.
        Test the result and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        fxs = self.exqs.eval(self.x_s)
        np.testing.assert_allclose(fxs, self.fxsr, atol=1e-09)
        self.assertIsInstance(fxs, np.ndarray)

    def test_gradient_1(self):
        """Test the derivative relative to input with 100 points, and 3 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        dfdxfull = self.exqfull.gradient(self.xfull)
        np.testing.assert_allclose(dfdxfull, self.dfdxfullr, atol=1e-09)
        np.testing.assert_array_equal(dfdxfull.shape, (3, 100), 'The dimension is not correct!')
        self.assertIsInstance(dfdxfull, np.ndarray)

    def test_gradient_2(self):
        """Test the derivative relative to input with multiple points, but 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        dfdx = self.exq.gradient(self.x_1)
        np.testing.assert_allclose(dfdx, np.array([[-0.83014478, -1.0575632, -1.10784864,
                                                    -1.05976938, -0.41575394, -1.75245198,
                                                    -0.71363136, -1.80882106, -0.04910844,
                                                    -0.4316672],
                                                   [1.32352312, 5.91287408, 7.4618524,
                                                    2.4291296, 5.1312844, 4.49774992,
                                                    0.73873664, 3.4332976, 3.88384424,
                                                    1.0103668]]),
                                   atol=1e-09)
        np.testing.assert_array_equal(dfdx.shape, (2, 10), 'The dimension is not correct!')
        self.assertIsInstance(dfdx, np.ndarray)

        dfdx_2 = self.exq.gradient(self.x_2)
        np.testing.assert_allclose(dfdx_2, np.array([[4], [48]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_2.shape, (2, 1), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_2, np.ndarray)

        dfdx_3 = self.exq.gradient(self.x_3)
        np.testing.assert_allclose(dfdx_3, np.array([[-1.99888, -14.4074],
                                                     [-8.45392, 16.000552]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_3.shape, (2, 2), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_3, np.ndarray)

        dfdx_4 = self.exq.gradient(self.x_4)
        np.testing.assert_allclose(dfdx_4, np.array([[4, 10, 2], [24, 48, 16]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_4.shape, (2, 3), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_4, np.ndarray)

    def test_gradient_3(self):
        """Test the derivative relative to input. An example with sparse matrix.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        dfdxs = self.exqs.gradient(self.x_s)
        np.testing.assert_allclose(dfdxs, self.dfdxsr, atol=1e-09)
        np.testing.assert_array_equal(dfdxs.shape, (3, 100), 'The dimension is not correct!')
        self.assertIsInstance(dfdxs, np.ndarray)

    def test_hessian_1(self):
        """ Test the second derivative relative to input with 100 points, and 3 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        hfdxfull = self.exqfull.hessian(self.xfull)
        np.testing.assert_allclose(hfdxfull, self.hfdxfullr, atol=1e-09)
        np.testing.assert_array_equal(hfdxfull.shape, (100, 3, 3),
                                      'The dimension is not correct!')
        self.assertIsInstance(hfdxfull, np.ndarray)

    def test_hessian_2(self):
        """ Test the second derivative relative to input with multiple points, but 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        hfdx = self.exq.hessian(self.x_1)
        np.testing.assert_allclose(hfdx, np.array(
            [[[2, 0], [0, 8]], [[2, 0], [0, 8]], [[2, 0], [0, 8]],
             [[2, 0], [0, 8]], [[2, 0], [0, 8]], [[2, 0], [0, 8]],
             [[2, 0], [0, 8]], [[2, 0], [0, 8]], [[2, 0], [0, 8]],
             [[2, 0], [0, 8]]]), atol=1e-09)
        np.testing.assert_array_equal(hfdx.shape, (10, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx, np.ndarray)

        hfdx_2 = self.exq.hessian(self.x_2)
        np.testing.assert_allclose(hfdx_2, np.array([[[2, 0], [0, 8]]]), atol=1e-09)
        np.testing.assert_array_equal(hfdx_2.shape, (1, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_2, np.ndarray)

        hfdx_3 = self.exq.hessian(self.x_3)
        np.testing.assert_allclose(hfdx_3, np.array([[[2, 0], [0, 8]], [[2, 0], [0, 8]]]),
                                   atol=1e-09)
        np.testing.assert_array_equal(hfdx_3.shape, (2, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_3, np.ndarray)

        hfdx_4 = self.exq.hessian(self.x_4)
        np.testing.assert_allclose(hfdx_4, np.array([[[2, 0], [0, 8]], [[2, 0], [0, 8]],
                                                     [[2, 0], [0, 8]]]), atol=1e-09)
        np.testing.assert_array_equal(hfdx_4.shape, (3, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_4, np.ndarray)

    def test_hessian_3(self):
        """ Test the second derivative relative to input. An example with sparse matrix.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        hfdxs = self.exqs.hessian(self.x_s)
        np.testing.assert_allclose(hfdxs, self.hfdxsr, atol=1e-09)
        np.testing.assert_array_equal(hfdxs.shape, (100, 3, 3), 'The dimension is not correct!')
        self.assertIsInstance(hfdxs, np.ndarray)

    def test_input_check_quad(self):
        """ Check if input_check is working correctly.

        """

        with self.assertRaisesRegex(Warning, 'x must be a numpy array!'):
            self.exq.input_check(self.x_i)

        dimension = self.exq.parameters['Q'].shape[0]

        with self.assertRaisesRegex(Warning, 'x must be a {}xm array!'.format(dimension)):
            self.exq.input_check(self.x_c)

    def test_plot_value(self):

        x_lim = np.array([[-5, 5], [-5, 5]])
        aux_plot = self.exq.plot(x_lim, show_plot=False)

        self.assertTrue(isinstance(aux_plot, QuadContourSet))


class TestPolynomialFunction(unittest.TestCase):
    """This class tests a Polynomial Function constructor.

    """

    def setUp(self):
        """
        Set parameters: exponents and coefficients.

        """

        # 1st test:
        self.expol = PolynomialFunction(exponents=np.array([[3, 0, 0], [0, 3, 0], [0, 0, 3]]),
                                        coefficients=np.array([1, 1, 1]))
        # dim x = (3,1)
        self.x_1 = np.array([[1], [2], [3]])
        # dim x = (3,2)
        self.x_2 = np.array([[1, 1], [2, 2], [3, 3]])

        # 2nd test:
        # an example with 6 terms and random exponents
        self.expol2 = PolynomialFunction(
            exponents=np.array([[4, 0, 0], [2, 0, 0], [1, 1, 0], [0, 0, 3], [0, 0, 1],
                                [0, 0, 0]]), coefficients=np.array([1, 1, 1, 4, 3, -4]))

        # 3rd test:
        # example with 8 terms, and random exponents, random coefficients
        # (decimal or negative points)
        self.expol3 = PolynomialFunction(exponents=np.array([[1, 4, 0], [3, 3, 3],
                                                             [0, 5, 1], [0, 1, 2],
                                                             [4, 1, 4], [4, 2, 3],
                                                             [1, 0, 2], [0, 5, 3]]),
                                         coefficients=np.array([0.884563, 12,
                                                                -5.32, 0.00076, -2,
                                                                -3.0444, 2, -1.02]))
        # dim x = (3,3) and (3,1)
        self.x_3 = np.array([[2, 0, 0.02304], [3.5543, -1, 0.1678], [0.0023, -4, 1.02945]])
        self.x3_1 = np.array([[2], [3.5543], [0.0023]])

        self.x_i = 23
        self.x_dim = np.array([3])
        self.x_dim2 = np.array([[3], [2]])
        self.pol = PolynomialFunction(exponents=np.array([[3, 0, 0], [0, 3], [0, 0, 3]]),
                                      coefficients=np.array([1, 1, 1]))

    def test_eval_1(self):
        """ Test the polynomial function evaluation. An example, only integers.
        Test the result and if it is a numpy array.
        """

        fx1 = self.expol.eval(self.x_1)
        np.testing.assert_allclose(fx1, np.array([36]), atol=1e-09)
        self.assertIsInstance(fx1, np.ndarray)

    def test_eval_2(self):
        """ Test the polynomial function evaluation. 6 terms, only integers.
        Test the result and if it is a numpy array.
        """

        fx2 = self.expol2.eval(self.x_2)
        np.testing.assert_allclose(fx2, np.array([117, 117]), atol=1e-09)
        self.assertIsInstance(fx2, np.ndarray)

    def test_eval_3(self):
        """ Test the polynomial function evaluation. 8 terms, decimal and negatives points.
        Test the result and if it is a numpy array.
        """

        fx3 = self.expol3.eval(self.x_3)
        np.testing.assert_allclose(fx3, np.array([2.75400997e+02, -8.65721600e+01,
                                                  4.81093910e-02]), atol=1e-09)
        self.assertIsInstance(fx3, np.ndarray)

        fx3_1 = self.expol3.eval(self.x3_1)
        np.testing.assert_allclose(fx3_1, np.array([2.75400997e+02]), atol=1e-09)
        self.assertIsInstance(fx3_1, np.ndarray)

    def test_gradient_1(self):
        """ Test the derivative relative to input. An example, only integers.
        Test the result, its dimension, and if it is a numpy array.
        """

        dfdx = self.expol.gradient(self.x_1)
        np.testing.assert_allclose(dfdx, np.array([[3], [12], [27]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx.shape, (3, 1), 'The dimension is not correct!')
        self.assertIsInstance(dfdx, np.ndarray)

    def test_gradient_2(self):
        """ Test the derivative relative to input. 6 terms, only integers.
        Test the result, its dimension, and if it is a numpy array.
        """

        dfdx2 = self.expol2.gradient(self.x_2)
        np.testing.assert_allclose(dfdx2, np.array([[8, 8], [1, 1], [111, 111]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx2.shape, (3, 2), 'The dimension is not correct!')
        self.assertIsInstance(dfdx2, np.ndarray)

    def test_gradient_3(self):
        """ Test the derivative relative to input. 8 terms, decimal and negatives points.
        Test the result, its dimension, and if it is a numpy array.
        """

        dfdx3 = self.expol3.gradient(self.x_3)
        np.testing.assert_array_equal(dfdx3.shape, (3, 3), 'The dimension is not correct!')
        np.testing.assert_allclose(dfdx3, np.array(
            [[1.41170946e+02, 3.28845630e+01, 2.12031138e+00],
             [3.07982560e+02, 4.32812160e+02, -2.49177482e-02],
             [-3.01767367e+03, 5.42860800e+01, 9.39992468e-02]]), rtol=1e-05, atol=1e-05)
        self.assertIsInstance(dfdx3, np.ndarray)

        dfdx3_1 = self.expol3.gradient(self.x3_1)
        np.testing.assert_array_equal(dfdx3_1.shape, (3, 1), 'The dimension is not correct!')
        np.testing.assert_allclose(dfdx3_1, np.array([[1.41170946e+02],
                                                      [3.07982560e+02],
                                                      [-3.01767367e+03]]),
                                   rtol=1e-05, atol=1e-05)
        self.assertIsInstance(dfdx3_1, np.ndarray)

    def test_hessian_1(self):
        """ Test the second derivative relative to input. An example, only integers.
        Test the result, its dimension, and if it is a numpy array.
        """

        hfdx = self.expol.hessian(self.x_1)
        np.testing.assert_allclose(hfdx, np.array([[[6, 0, 0], [0, 12, 0], [0, 0, 18]]]),
                                   atol=1e-09)
        np.testing.assert_array_equal(hfdx.shape, (1, 3, 3), 'The dimension is not correct!')
        self.assertIsInstance(hfdx, np.ndarray)

    def test_hessian_2(self):
        """ Test the second derivative relative to input. 6 terms, only integers.
        Test the result, its dimension, and if it is a numpy array.
        """

        hfdx2 = self.expol2.hessian(self.x_2)
        np.testing.assert_allclose(hfdx2,
                                   np.array([[[14, 1, 0], [1, 0, 0], [0, 0, 72]],
                                             [[14, 1, 0], [1, 0, 0], [0, 0, 72]]]),
                                   atol=1e-09)
        np.testing.assert_array_equal(hfdx2.shape, (2, 3, 3), 'The dimension is not correct!')
        self.assertIsInstance(hfdx2, np.ndarray)

    def test_hessian_3(self):
        """ Test the second derivative relative to input. 8 terms, decimal and negatives points.
        Test the result, its dimension, and if it is a numpy array.
        """

        hfdx3 = self.expol3.hessian(self.x_3)
        np.testing.assert_array_equal(hfdx3.shape, (3, 3, 3), 'The dimension is not correct!')
        np.testing.assert_allclose(hfdx3,
                                   np.array([[[5.61990013e-05, 1.58873301e+02, 9.22702056e-02],
                                              [1.58873301e+02, 2.57206248e+02, -4.24515879e+03],
                                              [9.22702056e-02, -4.24515879e+03, 5.10073654e+01]],
                                             [[0.00000000e+00, -3.53825000e+00, -1.60000000e+01],
                                              [-3.53825000e+00, -1.73120000e+03, -2.71406080e+02],
                                              [-1.60000000e+01, -2.71406080e+02, -2.44815200e+01]],
                                             [[5.55408641e-03, 1.83139288e-02, 4.11800208e+00],
                                              [1.83139288e-02, -6.15622298e-01, -3.23428103e-02],
                                              [4.11800208e+00, -3.23428103e-02, 9.15798475e-02]]]),
                                   rtol=1e-05, atol=1e-05)
        self.assertIsInstance(hfdx3, np.ndarray)

        hfdx3_1 = self.expol3.hessian(self.x3_1)
        np.testing.assert_array_equal(hfdx3_1.shape, (1, 3, 3), 'The dimension is not correct!')
        np.testing.assert_allclose(hfdx3_1,
                                   np.array([[[5.61990013e-05, 1.58873301e+02, 9.22702056e-02],
                                              [1.58873301e+02, 2.57206248e+02, -4.24515879e+03],
                                              [9.22702056e-02, -4.24515879e+03, 5.10073654e+01]]]),
                                   rtol=1e-05, atol=1e-05)
        self.assertIsInstance(hfdx3_1, np.ndarray)

    def test_input_check_pol(self):
        """ Check if input_check is working correctly.

        """

        with self.assertRaisesRegex(Warning, 'x must be a numpy array!'):
            self.expol.input_check(self.x_i)
        with self.assertRaisesRegex(Warning, 'x must be a 3xm array!'):
            self.expol.input_check(self.x_dim2)
        with self.assertRaisesRegex(Warning, 'List of exponents must have the same dimension!'):
            self.pol.input_check(self.x_1)


class TestLinearFunction(unittest.TestCase):
    """This class tests a Linear Function constructor.
    Function form: f(x) = c'x + d
    """

    def setUp(self):
        """
        Set parameters.
        """

        # 1st test:
        # file with data and results
        with open('science_optimization/test/valueslinear.pickle', 'rb') as lin_f:
            valueslinear = pickle.load(lin_f)

        # dim x = (3,100), 100 random decimal evaluation points
        # coefficients were also chosen randomly
        # 3 variables
        self.exlin = LinearFunction(c=valueslinear.get('c'), d=valueslinear.get('d'))
        self.x_1 = valueslinear.get("x")
        self.fxr = valueslinear.get('fx')
        self.dfdxr = valueslinear.get('dfdx')
        self.hfdxr = valueslinear.get('hfdx')

        # 2nd test:
        # dim x = 1 (specific case)
        self.exlin_u = LinearFunction(c=(np.array([[-2]])), d=1)
        self.x_u = np.array([[3]])

        # 2 variables
        # 3rd test:
        # dim x_2 = (2, 1)
        self.exlin2 = LinearFunction(c=(np.array([-2, 0]).reshape(-1, 1)), d=1)
        self.x_3 = np.array([[3], [6]])

        # 4th test:
        # including negative points
        # dim x_3 = (2, 2)
        self.x_4 = np.array([[-2.56, -0.00827], [0.00345, 1.45]])

        self.x_i = 23
        self.x_c = np.array([[2], [1], [3]])

    def test_eval_1(self):
        """ Test the linear function evaluation for 100 points and 3 variables.
        Test the result and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        fx_1 = self.exlin.eval(self.x_1)
        np.testing.assert_allclose(fx_1, self.fxr, atol=1e-09)
        self.assertIsInstance(fx_1, np.ndarray)

    def test_eval_2(self):
        """ Test the linear function evaluation for an unit size example.
        Test the result and if it is a numpy array, with a tolerance.
        """

        fx_u = self.exlin_u.eval(self.x_u)
        np.testing.assert_allclose(fx_u, np.array([[-5]]), atol=1e-09)
        self.assertIsInstance(fx_u, np.ndarray)

    def test_eval_3(self):
        """ Test the linear function evaluation for 1 point and 2 variables.
        Test the result and if it is a numpy array, with a tolerance.
        """

        fx_3 = self.exlin2.eval(self.x_3)
        np.testing.assert_allclose(fx_3, np.array([[-5]]), atol=1e-09)
        self.assertIsInstance(fx_3, np.ndarray)

    def test_eval_4(self):
        """ Test the linear function evaluation for 2 points and 2 variables.
        Test the result and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        fx_4 = self.exlin2.eval(self.x_4)
        np.testing.assert_allclose(fx_4, np.array([[6.12, 1.01654]]), atol=1e-09)
        self.assertIsInstance(fx_4, np.ndarray)

    def test_gradient_1(self):
        """ Test the derivative relative to input with 100 points, and 3 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        dfdx = self.exlin.gradient(self.x_1)
        np.testing.assert_allclose(dfdx, self.dfdxr, atol=1e-09)
        np.testing.assert_array_equal(dfdx.shape, (3, 100), 'The dimension is not correct!')
        self.assertIsInstance(dfdx, np.ndarray)

    def test_gradient_2(self):
        """ Test the derivative relative to input. An unit size example.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        """

        dfdx_u = self.exlin_u.gradient(self.x_u)
        np.testing.assert_allclose(dfdx_u, np.array([[-2]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_u.shape, (1, 1), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_u, np.ndarray)

    def test_gradient_3(self):
        """ Test the derivative relative to input with 1 points, and 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        """

        dfdx_3 = self.exlin2.gradient(self.x_3)
        np.testing.assert_allclose(dfdx_3, np.array([[-2], [0]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_3.shape, (2, 1), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_3, np.ndarray)

    def test_gradient_4(self):
        """ Test the derivative relative to input with 2 points, and 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        dfdx_4 = self.exlin2.gradient(self.x_4)
        np.testing.assert_allclose(dfdx_4, np.array([[-2, -2], [0, 0]]), atol=1e-09)
        np.testing.assert_array_equal(dfdx_4.shape, (2, 2), 'The dimension is not correct!')
        self.assertIsInstance(dfdx_4, np.ndarray)

    def test_hessian_1(self):
        """ Test the second derivative relative to input with 100 points, and 3 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal points.
        """

        hfdx = self.exlin.hessian(self.x_1)
        np.testing.assert_allclose(hfdx, self.hfdxr, atol=1e-09)
        np.testing.assert_array_equal(hfdx.shape, (100, 3, 3), 'The dimension is not correct!')
        self.assertIsInstance(hfdx, np.ndarray)

    def test_hessian_2(self):
        """ Test the second derivative relative to input. An unit size example.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        """

        hfdx_u = self.exlin_u.hessian(self.x_u)
        np.testing.assert_allclose(hfdx_u, np.array([[[0.]]]), atol=1e-09)
        np.testing.assert_array_equal(hfdx_u.shape, (1, 1, 1), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_u, np.ndarray)

    def test_hessian_3(self):
        """ Test the second derivative relative to input with 1 points, and 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        """

        hfdx_3 = self.exlin2.hessian(self.x_3)
        np.testing.assert_allclose(hfdx_3, np.array([[[0., 0.], [0., 0.]]]), atol=1e-09)
        np.testing.assert_array_equal(hfdx_3.shape, (1, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_3, np.ndarray)

    def test_hessian_4(self):
        """ Test the second derivative relative to input with 2 points, and 2 variables.
        Test the result, its dimension, and if it is a numpy array, with a tolerance.
        The points include decimal and negative points.
        """

        hfdx_4 = self.exlin2.hessian(self.x_4)
        np.testing.assert_allclose(hfdx_4, np.array([[[0., 0.], [0., 0.]], [[0., 0.], [0., 0.]]]),
                                   atol=1e-09)
        np.testing.assert_array_equal(hfdx_4.shape, (2, 2, 2), 'The dimension is not correct!')
        self.assertIsInstance(hfdx_4, np.ndarray)

    def test_input_check_linear(self):
        """ Check if input_check is working correctly.

        """

        with self.assertRaisesRegex(Warning, 'x must be a numpy array!'):
            self.exlin2.input_check(self.x_i)

        dimension = self.exlin2.parameters['c'].shape[0]

        with self.assertRaisesRegex(Warning, 'x must be a {}xm array!'.format(dimension)):
            self.exlin2.input_check(self.x_c)


class TestFunctionsComposite(unittest.TestCase):
    """This class tests the function constructor for a functions list.

    """

    def setUp(self):
        """
        Initialize an object from Functions Composite,
        add functions to the list, and set parameters.

        """

        self.f_c = FunctionsComposite()
        self.f_c.add(LinearFunction(c=(np.array([-2, 0]).reshape(-1, 1)), d=1))
        self.f_c.add(QuadraticFunction(Q=np.array([[1, 0], [0, 4]]),
                                       c=(np.array([-2, 0]).reshape(-1, 1)), d=1))
        self.f_c.add(PolynomialFunction(exponents=np.array([[3, 0], [0, 3]]),
                                        coefficients=np.array([1, 1])))

        self.x = np.array([[3], [6]])
        self.fxr = np.array([[-5], [148], [243]])
        self.dfdxr = np.array([[-2, 4, 27], [0, 48, 108]])
        self.hfdxr = np.array([[[0, 0], [0, 0]], [[2, 0], [0, 8]], [[18, 0], [0, 36]]])

    def test_eval(self):
        """Test the evaluation of functions composite.
        Test the result, its dimension, and it is a numpy array.
        """

        # parallel composition
        f_x = self.f_c.eval(self.x)
        np.testing.assert_allclose(f_x, self.fxr, atol=1e-09)
        self.assertIsInstance(f_x, np.ndarray)
        np.testing.assert_array_equal(f_x.shape, (3, 1), 'The dimension is not correct!')

        # series composition
        f_x = self.f_c.eval(self.x, composition="series")
        np.testing.assert_allclose(f_x, np.sum(self.fxr, axis=0).reshape(-1, 1), atol=1e-09)
        self.assertIsInstance(f_x, np.ndarray)
        np.testing.assert_array_equal(f_x.shape, (1, 1), 'The dimension is not correct!')

    def test_gradient(self):
        """Test the gradient of functions composite.
        Test the result, its dimension, and it is a numpy array.
        """

        # parallel composition
        dfdx = self.f_c.gradient(self.x)
        np.testing.assert_allclose(dfdx, self.dfdxr, atol=1e-05)
        self.assertIsInstance(dfdx, np.ndarray)
        np.testing.assert_array_equal(dfdx.shape, (2, 3), 'The dimension is not correct!')

        # series composition
        dfdx = self.f_c.gradient(self.x, composition="series", weights=np.array([[.5, .5, .5]]))
        np.testing.assert_allclose(dfdx, np.sum(.5 * self.dfdxr, axis=1).reshape(-1, 1), atol=1e-03)
        self.assertIsInstance(dfdx, np.ndarray)
        np.testing.assert_array_equal(dfdx.shape, (2, 1), 'The dimension is not correct!')

    def test_hessian(self):
        """Test the hessian of functions composite.
        Test the result, its dimension, and it is a numpy array.
        """

        hfdx = self.f_c.hessian(self.x)
        np.testing.assert_allclose(hfdx, self.hfdxr, atol=1e-09)
        self.assertIsInstance(hfdx, np.ndarray)
        np.testing.assert_array_equal(hfdx.shape, (3, 2, 2), 'The dimension is not correct!')

    def test_add(self):
        """Test the method to add function to list.
        """

        n_f1 = self.f_c.n_functions
        self.f_c.add(LinearFunction(c=(np.array([[-2]])), d=1))
        n_f2 = self.f_c.n_functions
        self.assertEqual(n_f2, (n_f1 + 1))

    def test_remove(self):
        """Test the method to remove function from list.
        """

        n_f_r = self.f_c.n_functions
        self.f_c.remove(0)
        n_f = self.f_c.n_functions
        self.assertEqual(n_f, (n_f_r - 1))


class TestFunctionEnsemble(unittest.TestCase):
    """Test the class that build the optimization problem constraints.

    """

    def setUp(self):
        # quadratic function: -x_1*(1 + x_2 - x_1)
        Q = np.array([[-1, 1 / 2], [1 / 2, 0]])
        c = np.array([[1], [0]])
        f1 = QuadraticFunction(Q=-Q, c=-c)

        # linear function: [1 0]'*x
        f2 = LinearFunction(c=c)

        # polynomial function x1*x2
        f3 = PolynomialFunction(exponents=np.array([[1, 1]]), coefficients=np.array([1]))

        # generic function e^(x_1 + x_2)
        f4 = GenericFunction(func=lambda x: np.exp(x[0, :] + x[1, :]).reshape(-1, 1), n=2)

        # functions ensemble
        self.fe1 = f1 + f2
        self.fe2 = f1 + f2 - f3
        self.fe3 = f1 * f4
        self.fe4 = f1 / f4
        self.fe5 = f1 + f2 * f3

        # expected results fe1
        self.x = np.array([[np.pi], [np.pi]])
        self.fe1_fx = f1.eval(self.x) + f2.eval(self.x)
        self.fe1_gx = f1.gradient(self.x) + f2.gradient(self.x)
        self.fe1_hx = f1.hessian(self.x) + f2.hessian(self.x)

        # expected results fe2
        self.fe2_fx = f1.eval(self.x) + f2.eval(self.x) - f3.eval(self.x)
        self.fe2_gx = f1.gradient(self.x) + f2.gradient(self.x) - f3.gradient(self.x)
        self.fe2_hx = f1.hessian(self.x) + f2.hessian(self.x) - f3.hessian(self.x)

        # expected results fe3
        self.fe3_fx = f1.eval(self.x) * f4.eval(self.x)
        self.fe3_gx = f1.eval(self.x) * f4.gradient(self.x) + f1.gradient(self.x) * f4.eval(self.x)
        self.fe3_hx = (
                f1.hessian(self.x) * f4.eval(self.x) + f1.eval(self.x) * f4.hessian(self.x) +
                2 * f1.gradient(self.x) * f4.gradient(self.x)
        )

        # expected results fe4
        self.fe4_fx = f1.eval(self.x) / f4.eval(self.x)
        self.fe4_gx = 1/f4.eval(self.x)**2 * (f4.eval(self.x)*f1.gradient(self.x)-f1.eval(self.x)*f4.gradient(self.x))
        self.fe4_hx = (
                1 / f4.eval(self.x) ** 3 *
                (
                        f4.eval(self.x) ** 2 * f1.hessian(self.x) - f4.eval(self.x) *
                        (2 * f1.gradient(self.x) * f4.gradient(self.x) + f1.eval(self.x) * f4.hessian(self.x)) +
                        2 * f1.eval(self.x) * f4.gradient(self.x) ** 2
                )
        )

        # expected results fe5
        self.fe5_fx = f1.eval(self.x) + (f2.eval(self.x) * f3.eval(self.x))
        self.fe5_gx = (
                f1.gradient(self.x) + f2.gradient(self.x) * f3.eval(self.x) +
                f2.eval(self.x) * f3.gradient(self.x)
        )
        self.fe5_hx = (
                f1.hessian(self.x) + f3.eval(self.x) * f2.hessian(self.x) +
                2 * f2.gradient(self.x) * f3.gradient(self.x) + f2.eval(self.x) * f3.hessian(self.x)
        )

    def test_function_ensemble1(self):
        """ Test function ensemble."""

        # evaluate ensemble
        fx = self.fe1.eval(self.x)
        gx = self.fe1.gradient(self.x)
        hx = self.fe1.hessian(self.x)

        # test
        np.testing.assert_equal(self.fe1_fx, fx)
        np.testing.assert_equal(self.fe1_gx, gx)
        np.testing.assert_equal(self.fe1_hx, hx)

    def test_function_ensemble2(self):
        """ Test function ensemble."""

        # evaluate ensemble
        fx = self.fe2.eval(self.x)
        gx = self.fe2.gradient(self.x)
        hx = self.fe2.hessian(self.x)

        # test
        np.testing.assert_equal(self.fe2_fx, fx)
        np.testing.assert_equal(self.fe2_gx, gx)
        np.testing.assert_equal(self.fe2_hx, hx)

    def test_function_ensemble3(self):
        """ Test function ensemble."""

        # evaluate ensemble
        fx = self.fe3.eval(self.x)
        gx = self.fe3.gradient(self.x)
        hx = self.fe3.hessian(self.x)

        # test
        np.testing.assert_equal(self.fe3_fx, fx)
        np.testing.assert_equal(self.fe3_gx, gx)
        np.testing.assert_equal(self.fe3_hx, hx)

    def test_function_ensemble4(self):
        """ Test function ensemble."""

        # evaluate ensemble
        fx = self.fe4.eval(self.x)
        gx = self.fe4.gradient(self.x)
        hx = self.fe4.hessian(self.x)

        # test
        np.testing.assert_equal(self.fe4_fx, fx)
        np.testing.assert_equal(self.fe4_gx, gx)
        np.testing.assert_equal(self.fe4_hx, hx)

    def test_function_ensemble5(self):
        """ Test function ensemble."""

        # evaluate ensemble
        fx = self.fe5.eval(self.x)
        gx = self.fe5.gradient(self.x)
        hx = self.fe5.hessian(self.x)

        # test
        np.testing.assert_equal(self.fe5_fx, fx)
        np.testing.assert_equal(self.fe5_gx, gx)
        np.testing.assert_equal(self.fe5_hx, hx)


if __name__ == '__main__':
    unittest.main()
