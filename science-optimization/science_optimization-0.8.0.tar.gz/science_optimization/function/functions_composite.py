"""
Function Composite class
"""
import numpy as np
from .base_function import BaseFunction
from .linear_function import LinearFunction


# TODO: more than one point at a time
class FunctionsComposite(BaseFunction):
    """Base class for functions list.

    """

    # class attributes
    _functions = None

    _flag_num_g = False

    def __init__(self):
        """Functions composite

        """

        # initialize empty list
        self.functions = list()
        self.n_functions = 0  # number of functions

    # attribute interface
    @property
    def functions(self) -> [BaseFunction]:
        return self._functions

    # attribute setter
    @functions.setter
    def functions(self, function_list):
        if issubclass(type(function_list), list):
            self._functions = function_list
        else:
            raise ValueError("Functions must be a list!")

    def dimension(self):
        return self.functions[0].dimension()

    # methods
    def eval(self, x, idx=None, composition="parallel", weights=None):
        """Evaluation of functions composite.

        Args:
            x           : (n x 1)-array with evaluation point
            idx         : list with indices of functions to be evaluated
            composition : parallel or series composition
            weights     : array with series composition weights, i.g. w'*f

        Returns:
            fx          : (n_functions x 1)-array with functions' values
        """

        # input check
        idx, composition, weights, n_functions = self.input_check(idx=idx,
                                                                  composition=composition,
                                                                  weights=weights)
        # define indices
        if idx is None:
            idx = range(self.n_functions)
        n_functions = len(idx)  # number of functions to be evaluated

        # evaluate
        fx = np.zeros((n_functions, x.shape[1]))  # initialize array
        for i in range(n_functions):
            fx[i, ] = self.functions[idx[i]].eval(x).ravel()

        # series composition
        if composition == "series":
            fx = np.dot(weights, fx)

        return fx

    def gradient(self, x, idx=None, composition="parallel", weights=None):
        """Gradient of functions composite.

        Args:
            x           : (n x 1)-array with evaluation point
            idx         : list with indices of functions to be evaluated
            composition : parallel or series composition
            weights     : array with series composition weights, i.g. w'*f

        Returns:
            dfdx: (n x n_functions)-array with functions' gradients
        """

        # input check
        idx, composition, weights, n_functions = self.input_check(idx=idx,
                                                                  composition=composition,
                                                                  weights=weights)
        # parameters
        n = x.shape[0]

        # compute values
        dfdx = np.zeros((n, n_functions))  # initialize array
        if self.flag_num_g:  # TODO(Matheus):to speed-up evaluation in case of functions with high cost
            fx = self.eval(x, idx=idx)
            eps = np.maximum(np.max(abs(x)), 1) * self.eps
            e = np.eye(n) * eps

            # TODO (Feres) adequate to call method numerical_gradient from BaseFunction
            for i in range(n):
                xd = x + e[:, [i]]
                dfdx[i, :] = (self.eval(xd, idx=idx) - fx).T / eps
        else:
            for i in range(n_functions):
                dfdx[:, i] = self.functions[idx[i]].gradient(x).ravel()

        # series composition
        if composition == "series":
            dfdx = np.sum(weights * dfdx, axis=1).reshape(-1, 1)

        return dfdx

    def hessian(self, x, idx=None, composition="parallel", weights=None):
        """Hessian of functions composite.

        Args:
            x           : (n x 1)-array with evaluation point
            idx         : list with indices of functions to be evaluated
            composition : parallel or series composition
            weights     : array with series composition weights, i.g. w'*f

        Returns:
            hfdx: (n x n x n_functions)-array with functions' hessians
        """

        # input check
        idx, composition, weights, n_functions = self.input_check(idx=idx,
                                                                  composition=composition,
                                                                  weights=weights)
        # parameters
        n = x.shape[0]

        # compute values
        hfdx = np.zeros((n_functions, n, n))  # initialize array
        for i in range(n_functions):
            hfdx[i, :, :] = self.functions[idx[i]].hessian(x)

        # series composition
        if composition == "series":
            hfdx = (weights.reshape(n_functions, 1, 1) * hfdx).sum(0)

        return hfdx

    def add(self, f: BaseFunction):
        """Add function to list.

        Args:
            f: function instance

        """

        # append function
        if issubclass(type(f), BaseFunction):
            self.functions = self.functions + [f]
            self.n_functions += 1

            # if one function has numerical gradient, the composite calculus will use it directly
            self.flag_num_g = self.flag_num_g or f.flag_num_g
        else:
            raise Warning('Function f must be a subclass of BaseFunction!')

    # TODO (Feres) flag_num_g not updated
    def remove(self, idx=None):
        """Remove function from list.

        Args:
            idx: function index on list

        Returns:
            f_pop: deleted function

        """

        if idx is not None:
            f_pop = self.functions.pop(idx)
        else:
            f_pop = self.functions.pop()

        # update number of functions
        self.n_functions -= 1

        return f_pop

    def clear(self):
        """Remove all functions."""

        self.functions.clear()

        # update number of functions
        self.n_functions = 0

        return

    def is_linear(self):
        """True if all functions are linear."""

        linear = [isinstance(f, LinearFunction) for f in self.functions]

        return all(linear)

    def input_check(self, idx, composition, weights):
        """Check composition input.

        Args:
            idx         : list with indices of functions to be evaluated
            composition : parallel or series composition
            weights     : array with series composition weights, i.g. w'*f

        Returns:
            idx         : list with indices of functions to be evaluated
            composition : parallel or series composition
            weights     : array with series composition weights, i.g. w'*f

        """

        # check indices of evaluation functions
        if idx is None:
            idx = range(self.n_functions)

        # check number of functions
        n_functions = len(idx)  # number of functions to be evaluated
        if self.n_functions < n_functions:
            raise ValueError("Number of functions in idx are greater than expected!")

        # check composition
        if not (composition == "parallel" or composition == "series"):
            raise ValueError("composition must be either parallel or series!")

        # weights definition
        if weights is None:
            weights = np.ones((1, n_functions))
        else:
            self.numpy_check(weights)
            if weights.shape[0] != 1 or weights.shape[1] != n_functions:
                raise Warning("weights must be a 1x{}-array!".format(n_functions))

        return idx, composition, weights, n_functions
