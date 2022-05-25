"""
GenericFunction class
"""
from .base_function import BaseFunction


class GenericFunction(BaseFunction):
    """Class to convert a python function to a BaseFunction instance."""

    def __init__(self, func, n, grad_func=None):
        """Constructor of a generic function.

        Args:
            func     : (callable) instance of a python function for function evaluation
            n        : (int) number of function arguments
            grad_func: (callable) instance of a python function for gradient evaluation
        """

        # check if object is a function
        if not callable(func):
            raise Warning("func must be callable.")

        if grad_func is not None and not callable(grad_func):
            raise Warning("grad_func must be callable.")

        if grad_func is not None:
            self.flag_num_g = False

        # set parameters
        self.parameters = {'func': func,
                           'n': n,
                           'grad_func': grad_func}

    def dimension(self):
        return self.parameters['n']

    def eval(self, x):
        """Evaluates generic function

        Args:
            x: (numpy array) evaluation point.

        Returns:
            fx: (numpy array) function evaluation at point x.
        """

        # input check
        self.input_check(x)

        # function evaluation
        f = self.parameters['func']
        fx = f(x)

        return fx

    def gradient(self, x):
        """Gradient of generic function

        Args:
            x: (numpy array) evaluation point.

        Returns:
            dfx: (numpy array) function evaluation at point x.
        """

        # gradient evaluation
        df = self.parameters['grad_func']

        # input check
        self.input_check(x)

        if df is not None:

            # evaluate
            dfx = df(x)

            # check dimension
            if dfx.shape[0] != self.parameters['n']:
                raise ValueError('Callable grad_func must return a {}xm array'.format(self.parameters['n']))

        else:
            dfx = self.numerical_gradient(x)

        return dfx

    def input_check(self, x):
        """Check input dimension.

        Args:
            x: (numpy array) point to be evaluated.
        """

        # check if input is numpy
        self.numpy_check(x)

        if not x.shape[0] == self.parameters['n']:
            raise Warning("Point x must have {} dimensions.".format(self.parameters['n']))
