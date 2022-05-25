"""
LinearFunction class
"""
import numpy as np
import numpy.matlib
from .base_function import BaseFunction


class LinearFunction(BaseFunction):
    """
    Class that implements a linear function
    """

    _flag_num_g = False     # this function uses analytical gradient

    def parameter_check(self, c: np.ndarray, d):

        # checking c parameter
        self.numpy_check(c)

        if len(c.shape) != 2 or c.shape[1] != 1:
            raise Exception("Invalid format for 'c' parameter")

        # checking d parameter
        try:
            int(d)
        except (ValueError, TypeError):
            raise Exception("'d' parameter must be a valid number")

    def __init__(self, c, d=0):
        """ Linear Function constructor: c'x + d.

       Args:
           c: scaling n-vector coefficients of equations
           d: constants of equations
       """

        self.parameter_check(c, d)

        # set parameters
        self.parameters = {'c': c,
                           'd': d}

    def dimension(self):
        """Linear problem dimension."""
        return self.parameters['c'].shape[0]

    def eval(self, x):
        """ Linear function evaluation.

        Args:
            x: evaluation point

        Returns:
            fx: evaluates the point value in the function
        """

        # input check
        self.input_check(x)

        # define parameters
        c = self.parameters['c']
        d = self.parameters['d']

        # evaluates the point
        fx = np.dot(c.T, x) + d

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
        c = self.parameters['c']

        # linear function gradient
        dim = x.shape
        if len(dim) == 1:
            dfdx = c
        else:
            dfdx = np.matlib.repmat(c, 1, dim[1])

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

        # linear function hessian
        dim = x.shape
        input_dimension = dim[0]
        if len(dim) == 1:
            input_number = 1
        else:
            input_number = dim[1]
        hfdx = np.zeros((input_number, input_dimension, input_dimension))

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
        param_dim = self.parameters['c'].shape[0]
        if len(x_dim) == 1:
            raise Warning("x must be a {}xm (m>0) array!".format(param_dim))
        if not x_dim[0] == param_dim:
            raise Warning("x must be a {}xm array!".format(param_dim))
