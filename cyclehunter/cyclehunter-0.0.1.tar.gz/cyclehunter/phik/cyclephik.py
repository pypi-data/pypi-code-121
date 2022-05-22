import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eig
from ..core import CycleEquation

__all__ = ['PhiK']

class PhiK(CycleEquation):

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
        return [-1, 0, 1]

    def eqn(self):
        """ Calculate phi-k equations with respect to a tensor of initial conditions
        lattice_state : np.ndarray
            State variable

        """
        s = self.s
        k = self.k
        states_tensor = self.states
        # the equations of motion
        eqn_tensor = (-1 * np.roll(states_tensor, -1, axis=1) + (-1 * (s - 2) * states_tensor ** k +
                                                                 s * states_tensor) - np.roll(states_tensor, 1, axis=1))
        # the l2 norm, giving us a scalar cost functional
        return eqn_tensor

    def cost(self):
        """ L2 norm of equations used as cost function.

        """
        return (0.5 * np.linalg.norm(self.eqn(), axis=1) ** 2).sum()

    def costgrad(self):
        """ Gradient of L2 norm of equations used as cost function.

        """
        s = self.s
        states = self.states
        Ftensor = self.eqn()
        JTF = -np.roll(Ftensor, 1, axis=1) - np.roll(Ftensor, -1, axis=1) + (
                -3 * (s - 2) * states ** 2 + s) * Ftensor
        return JTF.ravel()

    def jac_tensor(self):
        """ Calculate all Jacobians for cuurent state

        """
        n, k = self.n, self.k
        all_n_cycle = self.states
        J = np.zeros([3 ** n, n, n])
        upper_rows, upper_cols = _kth_diag_indices(J[0], -1)
        lower_rows, lower_cols = _kth_diag_indices(J[0], 1)
        zeroth = np.repeat(np.arange(3 ** n), len(upper_rows))
        upper_rows = np.tile(upper_rows, 3 ** n)
        upper_cols = np.tile(upper_cols, 3 ** n)
        lower_rows = np.tile(lower_rows, 3 ** n)
        lower_cols = np.tile(lower_cols, 3 ** n)

        J[zeroth, upper_rows, upper_cols] = -1
        J[zeroth, lower_rows, lower_cols] = -1
        J[:, 0, -1] = -1
        J[:, -1, 0] = -1
        tensor_diagonal = (-3 * (s - 2) * all_n_cycles ** 2 + s).ravel()

        rows, cols = np.diag_indices(n)
        zeroth = np.repeat(np.arange(3 ** n), len(rows))

        J[zeroth, np.tile(rows, 3 ** n), np.tile(cols, 3 ** n)] = tensor_diagonal
        return J

    def _kth_diag_indices(self, a, k):
        rows, cols = np.diag_indices_from(a)
        if k < 0:
            return rows[-k:], cols[:k]
        elif k > 0:
            return rows[:-k], cols[k:]
        else:
            return rows, cols

    def n_cycle_everything(self):
        n = self.n
        all_n_cycles = find_cycle_tensor(n)

        n_jacobians = all_n_cycle_jacobians(all_n_cycles, n)

        all_eig_val = []
        all_eig_vec = []
        for each_jac in n_jacobians:
            val, vec = eig(each_jac)
            all_eig_val.append(val)
            all_eig_vec.append(vec[np.newaxis])
        all_eig_val = np.concatenate(all_eig_val)
        all_eig_vec = np.concatenate(all_eig_vec)
        return all_n_cycles, all_eig_val, all_eig_vec, n_jacobians

    def generate_states(self, prime=True):
        """ Produces all possible combinations of k-ary alphabet, puts them in tensor of shape (k**n, n)

        :return:
        """
        n, k = self.n, self.k
        self.states = np.concatenate([coord.ravel().reshape(-1, 1) for coord in np.meshgrid(*(self.symbols for i in
                                                                                              range(n)))],
                                     axis=1)
        if prime:
            self.states = self.prime_orbits()

        return self

    def hunt(self, method='l-bfgs-b', **kwargs):
        options = kwargs.get('scipy_options')
        cycles = minimize(self.costwrapper(), self.states, jac=self.costgradwrapper(), method=method,
                          options=options)
        cycle_tensor = cycles.x.reshape(-1, self.n)
        return cycle_tensor

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

    def change_basis(self, to=None):
        if to is None or self.basis == to:
            return self.states
        elif to == 'symbolic':
            return self.states - 2
        elif to == 'proxy':
            return self.states + 2

    def vectorized_comparison(self, symbols, symbols_to_compare_against, offdiag=0):
        counts = np.char.count(symbols_to_compare_against.astype(str).reshape(-1, 1),
                               symbols.astype(str).reshape(1, -1))
        lower_idx = np.tril_indices(len(counts), offdiag)
        mask = np.zeros_like(counts)
        mask[lower_idx] = 1
        masked_counts = np.ma.masked_array(counts, mask=mask)
        return masked_counts

    def prime_orbits(self, check_neg=True, check_rev=True):
        """ Maps a set of initial conditions for phi-k equations into a set of prime representatives

        states: np.ndarray
            An M x N shaped array where N is the cycle length and M is however many states are being mapped.

        check_neg : bool
            If true, quotients -1 -> 1 symmetry

        check_rev : bool
            If true, quotients reversal symmetry, i.e equivariance w.r.t. array[::-1]

        Notes
        -----

        The different flags are essentially equivalent to calling the same function just on modified inputs. 
        What the code does is a vectorized comparison using numpy broadcasting. That is, given two vectors v1, v2 of length M,
        all possible pairs are compared, to see if v1 occurs as a substring in v2. This pairwise comparison results in a matrix; 
        the ij-th element of the matrix, M_ij, counts the number of occurrences of v1_i in v2_j. 

        This can be used along with boolean logic and summation to see if any off-diagonal elements are non-zero; a prime
        set would result in a diagonal matrix under this comparison.

        """
        states = self.states
        if -1 in states:
            states = states + 2

        # symbol representation
        symbols = np.sort(np.array(states.astype(str), dtype=object).sum(axis=1))
        # double repeats
        doubles = symbols + symbols

        # the function which does the vectorized comparison
        masked_counts = self.vectorized_comparison(symbols, doubles, offdiag=-1)

        # The index positions of cycles which are prime (so far)
        admissible_index = list(np.where(((masked_counts == 1).sum(axis=0) == 0))[0]) + [0]
        # The comparison fails to capture cycles like '111', handle them explicitly
        not_pure_cyclic = np.where(masked_counts.sum(axis=1) != 2)[0]
        admissible_index = list(set(admissible_index).intersection(set(not_pure_cyclic)))
        # keep only the admissible states
        states = states[admissible_index]
        doubles = doubles[admissible_index]
        if check_neg:
            # just doing the same as above, but for negative states
            # Just want a fast way of mapping 1,2,3 -> 3,2,1; doesn't matter how, this does that. 
            states = -1 * (states % -4)
            symbols = np.array(states.astype(str), dtype=object).sum(axis=1)
            masked_counts = self.vectorized_comparison(symbols, doubles)
            admissible_index = list(np.where(masked_counts.sum(axis=0) != 1)[0])
            states = states[admissible_index]
            doubles = doubles[admissible_index]
            # mapping is its own inverse
            states = -1 * (states % -4)
        if check_rev:
            # just doing same as above except for reversed states, re-using variable name for convenience.
            states = states[..., ::-1]
            symbols = np.array(states.astype(str), dtype=object).sum(axis=1)
            masked_counts = self.vectorized_comparison(symbols, doubles)

            admissible_index = list(np.where(masked_counts.sum(axis=0) != 1)[0])
            states = states[admissible_index]
            reversed_states = states.copy()
            states = states[..., ::-1]

            # to capture all reversed states properly, need to do comparison against non-doubled as well.
            symbols = np.array(states.astype(str), dtype=object).sum(axis=1)
            reversed_symbols = np.array(reversed_states.astype(str), dtype=object).sum(axis=1)
            masked_counts = self.vectorized_comparison(symbols, reversed_symbols)
            admissible_index = list(np.where(masked_counts.sum(axis=0) != 1)[0])
            states = states[admissible_index]
        return states - 2
