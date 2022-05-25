"""
QuadraticFunction class
"""
import numpy as np
import numpy.matlib
from .base_function import BaseFunction


class QuadraticFunction(BaseFunction):
    """
    Class that implements a quadratic function
    """

    _flag_num_g = False     # this function uses analytical gradient

    def __init__(self, Q, c, d=0):
        """ Set parameters for x'Qx + c'x + d.

       Args:
           Q: quadratic coefficients of equations (n x n)-matrix
           c: scaling n-vector coefficients of equations
           d: constants of equations
       """

        # parameters check
        self.numpy_check(Q, c)

        # set parameters
        self.parameters = {'Q': Q,
                           'c': c,
                           'd': d}

    def dimension(self):
        return self.parameters['Q'].shape[0]

    def eval(self, x):
        """ Quadratic function evaluation.

        Args:
            x: evaluation point

        Returns:
            fx: evaluates the point value in the function
        """

        # input check
        self.input_check(x)

        # define parameters
        Q = self.parameters['Q']
        c = self.parameters['c']
        d = self.parameters['d']

        # evaluates the point
        fx = np.sum(x*(np.dot(Q, x)), axis=0) + np.dot(c.T, x) + d

        return fx

    def gradient(self, x):
        """Derivative relative to input.

        Args:
            x: evaluation point

        Returns:
            dfdx: derivative at evaluation points
        """

        # input check
        self.input_check(x)

        # define parameters
        Q = self.parameters['Q']
        c = self.parameters['c']

        # quadratic function gradient
        dfdx = np.matlib.repmat(c, 1, x.shape[1])
        dfdx = dfdx + np.dot((Q + Q.T), x)

        return dfdx

    def hessian(self, x):
        """Second derivative relative to input.

        Args:
            x: evaluation point

        Returns:
            hfdx: second derivative at evaluation points
        """

        # input check
        self.input_check(x)

        # define parameters
        Q = self.parameters['Q']

        # quadratic function hessian
        hfdx = np.tile(Q + Q.T, (x.shape[1], 1, 1))

        return hfdx

    def input_check(self, x):
        """Check input dimension.

        Args:
            x: point to be evaluated.

        Returns:
            indicator: indicator if input os consistent
        """

        # check if input is numpy
        self.numpy_check(x)

        # check dimension
        x_dim = x.shape
        param_dim = self.parameters['Q'].shape[0]
        if len(x_dim) == 1:
            raise Warning("x must be a {}xm (m>0) array!".format(param_dim))
        if not x_dim[0] == param_dim:
            raise Warning("x must be a {}xm array!".format(param_dim))
