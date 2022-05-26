# pylint: disable-msg=C0111,C0103

import unittest, itertools

import numpy as np
from numpy import array, linspace, sin, cos, pi

from cosapp.utils.surrogate_models.response_surface import ResponseSurface


def branin(x):
    y = (x[1] - (5.1 / (4. * pi ** 2.)) * x[0] ** 2. + 5. * x[0] / pi - 6.) ** 2. + 10. * (1. - 1. / (8. * pi)) * cos(
        x[0]) + 10.
    return y


def branin_1d(x):
    return branin(array([x[0], 2.275]))


class TestResponseSurfaceSurrogate(unittest.TestCase):

    def test_1d_training(self):

        x = array([[0.0], [2.0], [3.0]])
        y = array([[branin_1d(case)] for case in x])
        surrogate = ResponseSurface()
        surrogate.train(x, y)

        for x0, y0 in zip(x, y):
            mu = surrogate.predict(x0)
            self.assertTrue(np.allclose(mu, y0, rtol=1e-9, atol=1e-12))

    def test_1d_predictor(self):
        x = array([[0.0], [2.0], [3.0], [4.0], [6.0]])
        y = array([[branin_1d(case)] for case in x])

        surrogate = ResponseSurface()
        surrogate.train(x, y)

        new_x = array([pi])
        mu = surrogate.predict(new_x)

        self.assertTrue(np.allclose(mu, 1.73114, rtol=1e-4))

    def test_1d_ill_conditioned(self):
        # Test for least squares solver utilization when ill-conditioned
        x = array([[case] for case in linspace(0., 1., 40)])
        y = sin(x)
        surrogate = ResponseSurface()
        surrogate.train(x, y)
        new_x = array([0.5])
        mu = surrogate.predict(new_x)

        self.assertTrue(np.allclose(mu, sin(0.5), rtol=1e-3))

    def test_2d(self):

        x = array([[-2., 0.], [-0.5, 1.5], [1., 1.], [0., .25], [.25, 0.], [.66, .33]])
        y = array([[branin(case)] for case in x])

        surrogate = ResponseSurface()
        surrogate.train(x, y)

        for x0, y0 in zip(x, y):
            mu = surrogate.predict(x0)
            self.assertTrue(np.allclose(mu, y0, rtol=1e-9, atol=1e-12))

        mu = surrogate.predict(array([.5, .5]))

        self.assertTrue(np.allclose(mu, branin([.5, .5]), rtol=1e-1))

    def test_one_pt(self):
        surrogate = ResponseSurface()
        x = array([[0.]])
        y = array([[1.]])

        surrogate.train(x, y)
        self.assertTrue(np.allclose(surrogate.betas, array([[1.], [0.], [0.]]), rtol=1e-9, atol=1e-12))

    def test_vector_input(self):
        surrogate = ResponseSurface()

        x = array([[0., 0., 0.], [1., 1., 1.]])
        y = array([[0.], [3.]])

        surrogate.train(x, y)

        for x0, y0 in zip(x, y):
            mu = surrogate.predict(x0)
            self.assertTrue(np.allclose(mu, y0, rtol=1e-9, atol=1e-12))

    def test_vector_output(self):
        surrogate = ResponseSurface()

        x = array([[0.], [2.], [4.]])
        y = array([[0., 0.], [1., 1.], [2., 0.]])

        surrogate.train(x, y)

        for x0, y0 in zip(x, y):
            mu = surrogate.predict(x0)
            self.assertTrue(np.allclose(mu, y0, rtol=1e-9, atol=1e-12))

    def test_scalar_derivs(self):
        surrogate = ResponseSurface()

        x = array([[0.], [1.], [2.], [3.]])
        y = x.copy()

        surrogate.train(x, y)
        jac = surrogate.linearize(array([[0.]]))

        self.assertTrue(np.allclose(jac[0][0], 1., rtol=1e-3))

    def test_vector_derivs(self):
        surrogate = ResponseSurface()

        x = array([[a, b] for a, b in
                   itertools.product(linspace(0, 1, 10), repeat=2)])
        y = array([[a + b, a - b] for a, b in x])

        surrogate.train(x, y)
        jac = surrogate.linearize(array([[0.5, 0.5]]))
        self.assertTrue(np.allclose(jac, array([[1, 1], [1, -1]]), rtol=1e-5))


if __name__ == "__main__":
    unittest.main()
