"""
BaseFunction and FunctionEnsemble classes
"""
import abc
import numpy as np
import types
import matplotlib.pyplot as plt


class BaseFunction(metaclass=abc.ABCMeta):
    """Base Function.

    This class is responsible for constructing all the parts of a problem.

    """

    # class attribute
    _parameters = None
    _eps = 1e-6
    _flag_num_g = True      # indicates function uses numerical gradient calculus

    # plot attribute
    step = 0.1

    # attribute interface
    @property
    def parameters(self):
        return self._parameters

    @property
    def eps(self):
        return self._eps

    @property
    def flag_num_g(self):
        return self._flag_num_g

    # attribute setter
    @parameters.setter
    def parameters(self, parameters):
        self._parameters = {i: parameter for i, parameter in parameters.items()}

    @eps.setter
    def eps(self, eps):
        if eps > 0:
            self._eps = eps
        else:
            raise Warning("Numerical precision must be positive!")

    @flag_num_g.setter
    def flag_num_g(self, flag_num_g):
        if type(flag_num_g) is bool:
            self._flag_num_g = flag_num_g
        else:
            raise Warning("Numerical gradient flag must be a boolean value")

    @abc.abstractmethod
    def dimension(self):
        pass

    @abc.abstractmethod
    def eval(self, *args):
        pass

    def gradient(self, x):
        """Derivative relative to input.

            Args:
                x: evaluation point

            Returns:
                dfdx: derivative at evaluation points
            """

        # input check
        self.input_check(x)

        return self.numerical_gradient(x)

    def numerical_gradient(self, x):
        """
        Calculate gradient using black box approach
        Args:
            x: evaluation point

        Returns:
            dfdx: derivative at evaluation points
        """

        # finite difference
        dim = x.shape
        eps = np.maximum(np.max(abs(x)), 1) * self.eps
        e = eps * np.eye(dim[0])
        fx = self.eval(x)
        dfdx = np.zeros(dim)
        for i in range(dim[0]):
            xd = x + e[:, i].reshape(-1, 1)
            dfdx[i, :] = (self.eval(xd) - fx) / eps
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

        # finite difference Hessian
        dim = np.shape(x)
        eps = np.maximum(np.max(abs(x)), 1) * self.eps
        e = eps * np.eye(dim[0])
        fx = self.gradient(x)
        hfdx = np.zeros((dim[1], dim[0], dim[0]))
        for i in range(dim[1]):
            for j in range(dim[0]):
                xd = x + e[:, j].reshape(-1, 1)
                hfdx[i, :, j] = (self.gradient(xd) - fx).ravel() / eps

        return hfdx

    @abc.abstractmethod
    def input_check(self, *args):
        """Check input dimension.

        Args:
            args: input.

        """
        pass

    @staticmethod
    def numpy_check(*args):
        """Check if x is a numpy array.

        Args:
            args: point to be evaluated.

        """

        # check if input is numpy
        for x in args:
            if not isinstance(x, np.ndarray):
                raise Warning("x must be a numpy array!")

    # overloading add operator
    def __add__(self, other):

        # error check
        if self.dimension() != other.dimension():
            raise ValueError("Functions must have the same dimension!")

        # eval, gradient and hessian of self
        fs = self.eval
        gs = self.gradient
        hs = self.hessian

        # eval, gradient and hessian of other
        fo = other.eval
        go = other.gradient
        ho = other.hessian

        # new function
        f_new = FunctionEnsemble(other.dimension())

        # if one function uses numerical gradient, it's better to evaluate directly
        f_new.flag_num_g = self.flag_num_g or other.flag_num_g

        # define new eval, gradient and hessian calls
        def aeval(_, x):
            return fs(x) + fo(x)

        def agradient(_, x):
            return gs(x) + go(x)

        def ahessian(_, x):
            return hs(x) + ho(x)

        # patching methods
        f_new.eval = types.MethodType(aeval, f_new)
        f_new.gradient = types.MethodType(agradient, f_new)
        f_new.hessian = types.MethodType(ahessian, f_new)

        return f_new

    # overloading subtraction operator
    def __sub__(self, other):

        # error check
        if self.dimension() != other.dimension():
            raise ValueError("Functions must have the same dimension!")

        # eval, gradient and hessian of self
        fs = self.eval
        gs = self.gradient
        hs = self.hessian

        # eval, gradient and hessian of other
        fo = other.eval
        go = other.gradient
        ho = other.hessian

        # new function
        f_new = FunctionEnsemble(other.dimension())
        f_new.flag_num_g = self.flag_num_g or other.flag_num_g

        # define new eval, gradient and hessian calls
        def aeval(_, x):
            return fs(x) - fo(x)

        def agradient(_, x):
            return gs(x) - go(x)

        def ahessian(_, x):
            return hs(x) - ho(x)

        # patching methods
        f_new.eval = types.MethodType(aeval, f_new)
        f_new.gradient = types.MethodType(agradient, f_new)
        f_new.hessian = types.MethodType(ahessian, f_new)

        return f_new

    # overloading multiplication operator
    def __mul__(self, other):

        # error check
        if self.dimension() != other.dimension():
            raise ValueError("Functions must have the same dimension!")

        # eval, gradient and hessian of self
        fs = self.eval
        gs = self.gradient
        hs = self.hessian

        # eval, gradient and hessian of other
        fo = other.eval
        go = other.gradient
        ho = other.hessian

        # new function
        f_new = FunctionEnsemble(other.dimension())
        f_new.flag_num_g = self.flag_num_g or other.flag_num_g

        # define new eval, gradient and hessian calls
        def aeval(_, x):
            return fs(x) * fo(x)

        def agradient(_, x):
            return fs(x) * go(x) + gs(x) * fo(x)

        def ahessian(_, x):
            return hs(x) * fo(x) + fs(x) * ho(x) + 2*gs(x)*go(x)

        # patching methods
        f_new.eval = types.MethodType(aeval, f_new)
        f_new.gradient = types.MethodType(agradient, f_new)
        f_new.hessian = types.MethodType(ahessian, f_new)

        return f_new

    # overloading divide operator
    def __truediv__(self, other):

        # error check
        if self.dimension() != other.dimension():
            raise ValueError("Functions must have the same dimension!")

        # eval, gradient and hessian of self
        fs = self.eval
        gs = self.gradient
        hs = self.hessian

        # eval, gradient and hessian of other
        fo = other.eval
        go = other.gradient
        ho = other.hessian

        # new function
        f_new = FunctionEnsemble(other.dimension())
        f_new.flag_num_g = self.flag_num_g or other.flag_num_g

        # define new eval, gradient and hessian calls
        def aeval(_, x):
            return 1/fo(x) * fs(x)

        def agradient(_, x):
            return 1/fo(x)**2 * (fo(x) * gs(x) - fs(x) * go(x))

        def ahessian(_, x):
            return 1/fo(x)**3 * (fo(x)**2 * hs(x) - fo(x)*(2*gs(x)*go(x) + fs(x)*ho(x)) + 2*fs(x)*go(x)**2)

        # patching methods
        f_new.eval = types.MethodType(aeval, f_new)
        f_new.gradient = types.MethodType(agradient, f_new)
        f_new.hessian = types.MethodType(ahessian, f_new)

        return f_new

    def plot(self, x_lim, ax_instance=None, colors=None, levels=None, l_width=0.8, show_plot=True):
        """
        plots the function evaluation inside the considered limits
        Args:
            x_lim: np array that informs the box limits
            ax_instance: passed if the plot is called by another method, as pl.subplots() returns
            colors: plot colors
            levels: level curves desired (if dimension is 2)
            l_width: lines width
            show_plot: boolean, choose if plot will be directly shown

        Returns: QuadContourSet instance (from matplotlib)

        """
        x_min = x_lim[:, 0]
        x_max = x_lim[:, 1]

        n = len(x_max)

        if n != self.dimension():
            raise Exception('Invalid x_lim')

        if n == 1:      # TODO (feres) complete case

            x_vec = np.arange(x_min, x_max, self.step)
            f_vec = self.eval(np.array([x_vec]))

            aux_plot = plt.plot(x_vec.reshape(-1), f_vec.reshape(-1))

        elif n == 2:

            # creating grid and evaluate each point
            try:
                x_grid = np.arange(x_min[0], x_max[0], self.step).reshape(-1)
                y_grid = np.arange(x_min[1], x_max[1], self.step).reshape(-1)
            except ValueError:
                raise Exception('Invalid bounds information')

            X, Y = np.meshgrid(x_grid, y_grid)
            XY = np.vstack((X.reshape(1, -1), Y.reshape(1, -1)))
            f1eval = np.reshape(self.eval(XY), X.shape)

            # plot
            if ax_instance is None:
                aux_plot = plt.contour(X, Y, f1eval, colors=colors, levels=levels)
                plt.clabel(aux_plot, inline=1, fontsize=10)
                plt.ylabel('$x_2$')
                plt.xlabel('$x_1$')

            else:
                aux_plot = ax_instance.contour(X, Y, f1eval, colors=colors, linewidths=l_width, levels=levels)

        else:
            raise Exception('Plot not implemented')

        if show_plot:
            plt.show()

        return aux_plot


class FunctionEnsemble(BaseFunction):

    def __init__(self, n: int):
        """ Initialize function ensemble.

        Args:
            n: variables dimension.
        """

        self.n = n

    def eval(self, x):
        pass

    def gradient(self, x):
        pass

    def hessian(self, x):
        pass

    def input_check(self, *args):
        pass

    def dimension(self):
        return self.n
