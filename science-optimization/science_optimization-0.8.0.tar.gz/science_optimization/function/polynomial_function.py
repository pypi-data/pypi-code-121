"""
PolynomialFunction class
"""
import numpy as np
from .base_function import BaseFunction


class PolynomialFunction(BaseFunction):
    """
    Class that implements a polynomial function
    """

    _flag_num_g = False     # this function uses analytical gradient

    def __init__(self, exponents, coefficients):
        """The constructor for the polynomial function instance.

        Args:
            exponents: A matrix with the exponents of the function in order of the variables
            for each element of the function
            coefficients: A vector with the coefficients of each element of the function

        Example:
            For the function ax² + bxy + cy²:
            exponents : [[2,0],[1,1],[0,2]]
            coefficients : [a, b, c]
        """

        # parameters check
        self.numpy_check(exponents, coefficients)

        self.parameters = {'e': exponents,
                           'c': coefficients}

    @staticmethod
    def aux_eval(f, i, x):
        return ((np.tile((x[:, i]).transpose(), (f.parameters['e'].shape[0], 1)) ** f.parameters['e']).prod(axis=1)
                * f.parameters['c']).sum(axis=0)

    # TODO: explain this function
    def aux_grad_j(self, i, j, x, dfdx):
        C = np.copy(self.parameters['e'])
        val = np.copy(C[:, j])
        d = np.where(val > 0)
        C[d, j] = C[d, j] - 1
        dfdx[j, i] = ((np.tile((x[:, i]).transpose(), (self.parameters['e'].shape[0], 1)) ** C).prod(axis=1) * val *
                      self.parameters['c']).sum(axis=0)

    # TODO: explain this function
    def aux_grad_i(self, i, j, x, dfdx):
        grad_j_vec = np.vectorize(PolynomialFunction.aux_grad_j, excluded=['self', 'i', 'x', 'dfdx'], otypes=[float])
        grad_j_vec(self, i=i, j=j, x=x, dfdx=dfdx)

    def dimension(self):
        return len(self.parameters['e'][0])

    def eval(self, x):
        """ Polynomial function evaluation.

        Args:
            x: A matrix with the evaluation points, the structure of the matrix should have the tuples in the
            columns, so each column is an evaluation point

        Returns:
            aux: Returns a vector with the evaluation value in each point (the index of the value matches the index
            of the column of the evaluation point)

        Example:
            For the function ax² + bxy + cy²:
            With x = [[1,2,3],[3,2,1]]
            Returns: [a + 3b + 9c, 4a + 4b + 4c, 9a + 3b + c]

            For the function x³ + y³ + z³
            With x = [[1],[2],[3]]
            Returns: [36]
        """

        # input check
        self.input_check(x)

        # eval
        num = x.shape[1]
        fx = np.arange(start=0, stop=num, step=1)
        eval_vec = np.vectorize(self.aux_eval, excluded=['f', 'x'])
        fx = eval_vec(f=self, i=fx, x=x)

        return fx

    def gradient(self, x):
        """Polynomial gradient evaluation.

        Args:
            x: A matrix with the evaluation points, the structure of the matrix should have the tuples in the
            columns, so each column is an evaluation point

        Returns:
            dfdx: Returns a matrix with the gradient vector in each point (the index of the row where the gradient is
            matches the index of the column of the evaluation point)

        Example:
            For the function ax² + bxy + cy²:
            With x = [[1,2,3],[3,2,1]]
            The gradient should be : [2ax + by, 2cy + bx]
            Returns:[[2a + 3b, 6c + b],[4a + 2b, 4c + 2b],[6a + b, 2c + 3b]]

            For the function x³ + y³ + z³
            With x = [[1],[2],[3]]
            The gradient should be : [3x²,3y²,3z²]
            Returns: [3, 12, 27]

        """

        # input check
        self.input_check(x)

        # gradient
        rows, columns = x.shape
        if self.parameters['c'].size <= 1:
            dfdx = np.zeros((rows, columns))
        else:
            dfdx = np.zeros((rows, columns))
            auxi = np.arange(start=0, stop=columns, step=1)
            auxj = np.arange(start=0, stop=rows, step=1)
            grad_i_vec = \
                np.vectorize(PolynomialFunction.aux_grad_i, excluded=['self', 'j', 'x', 'dfdx'], otypes={object})
            np.array(grad_i_vec(self, i=auxi, j=auxj, x=x, dfdx=dfdx))

        return dfdx

    def aux_hes_k(self, i, j, k, x, hfdx):
        C = np.copy(self.parameters['e'])
        valj = np.copy(C[:, j])
        d = np.where(valj > 0)  # PolynomialFunction.indices(valj, lambda x: x > 0)
        for a in d:
            C[a, j] = C[a, j] - 1
        valk = np.copy(C[:, k])
        d = np.where(valk > 0)  # PolynomialFunction.indices(valk, lambda x: x > 0)
        for a in d:
            C[a, k] = C[a, k] - 1
        hfdx[j, k, i] = ((np.tile((x[:, i]).transpose(), (self.parameters['e'].shape[0], 1)) ** C).prod(
            axis=1) * valj * valk * self.parameters['c']).sum(axis=0)
        hfdx[k, j, i] = hfdx[j, k, i]
        return hfdx

    def aux_hes_j(self, i, j, k, x, hfdx):
        C = np.copy(self.parameters['e'])
        val = np.copy(C[:, j])
        val = val * (val - 1)
        d = np.where(val > 1)  # PolynomialFunction.indices(val, lambda x: x > 1)
        for a in d:
            C[a, j] = C[a, j] - 2
        hfdx[j, j, i] = ((np.tile((x[:, i]).transpose(), (self.parameters['e'].shape[0], 1)) ** C).prod(axis=1) * val *
                         self.parameters['c']).sum(axis=0)
        grad_hes_k = np.vectorize(PolynomialFunction.aux_hes_k, excluded=['i', 'j', 'x', 'hfdx'], otypes={object})
        grad_hes_k(self, i=i, j=j, k=k, x=x, hfdx=hfdx)

    def aux_hes_i(self, i, j, k, x, hfdx):
        grad_hes_j = np.vectorize(PolynomialFunction.aux_hes_j, excluded=['i', 'k', 'x', 'hfdx'], otypes={object})
        grad_hes_j(self, i=i, j=j, k=k, x=x, hfdx=hfdx)

    def hessian(self, x):
        """Polynomial hessian evaluation.

        Args:
            x: A matrix with the evaluation points, the structure of the matrix should have the tuples in the
            columns, so each column is an evaluation point

        Returns:
            hfdx: Returns a vector of matrices with the hessian matrix in each point (the index of the row where
            the hessian is matches the index of the column of the evaluation point)

         Example:
            For the function ax² + bxy + cy²:
            With x = [[1,2,3],[3,2,1]]
            The gradient should be : [2ax + by, 2cy + bx]
            So the hessian should be : [[2a,b],[b,2c]]
            Returns:[[[2a,b],[b,2c]],[[2a,b],[b,2c]],[[2a,b],[b,2c]]]

            For the function x³ + y³ + z³
            With x = [[1],[2],[3]]
            The gradient should be : [3x²,3y²,3z²]
            So the hessian should be : [[6x,0,0],[0,6y,0],[0,0,6z]]
            Returns: [[6,0,0],[0,12,0],[0,0,18]]

        """

        # input check
        self.input_check(x)

        # hessian
        rows, columns = x.shape
        if self.parameters['c'].size < rows:
            hfdx = np.zeros((rows, rows, columns))
        else:
            hfdx = np.zeros((rows, rows, columns))
            auxi = np.arange(start=0, stop=columns, step=1)
            auxj = np.arange(start=0, stop=rows, step=1)
            auxk = np.arange(start=0, stop=rows, step=1)
            hes_i_vec = np.vectorize(PolynomialFunction.aux_hes_i, excluded=['self', 'j', 'k', 'x', 'hfdx'],
                                     otypes={object})
            np.array(hes_i_vec(self, i=auxi, j=auxj, k=auxk, x=x, hfdx=hfdx))

        return hfdx.transpose()

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
        param_dim = len(self.parameters['e'][0])
        if len(x_dim) == 1:
            raise Warning("x must be a {}xm (m>0) array!".format(param_dim))
        if not x_dim[0] == param_dim:
            raise Warning("x must be a {}xm array!".format(param_dim))
        if not all(len(e) == param_dim for e in self.parameters['e']):
            raise Warning("List of exponents must have the same dimension!")
