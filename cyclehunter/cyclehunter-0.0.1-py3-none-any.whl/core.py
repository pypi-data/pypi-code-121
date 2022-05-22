import numpy as np
from scipy.optimize import minimize

__all__ = ['CycleEquation']

class CycleEquation:

    def __init__(self, n, k, musqr, states=None, basis='symbolic'):
        """
        :param n: int
            Cycle length
        :param k: int
            potential exponent
        :param constants: int
            In this implementation of PhiK, this is mu squared. Naming is simply a convention
        """
        self.n = n
        self.k = k
        self.musqr = musqr
        self.s = musqr + 2
        self.states = states
        self.basis = basis

    @property
    def symbols(self):
        return None

    def eqn(self):
        """ Calculate phi-k equations with respect to a tensor of initial conditions
        lattice_state : np.ndarray
            State variable

        """
        ...

    def cost(self):
        """ Cost function, typically L2 norm of equations used as cost function.

        """
        ...

    def costgrad(self):
        """ Gradient of cost function, i.e. gradient of function: cost

        """
        ...


    def generate_states(self, prime=True):
        """ Produces all possible combinations of k-ary alphabet, puts them in tensor of shape (k**n, n)

        :return:
        """
        ...

    def hunt(self, method='l-bfgs-b', **kwargs):
        ...

    def costwrapper(self):
        """ Functions for scipy routines must take vectors of state variables, not class objects. 


        :return: 
        """

        def minfunc_(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).cost()

        return minfunc_

    def costgradwrapper(self):
        """ Functions for scipy routines must take vectors of state variables, not class objects. 


        :return: 
        """

        def _minjac(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).costgrad()

        return _minjac