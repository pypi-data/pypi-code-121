"""
Ellipsoid algorithm
"""
import nlpalg
import numpy as np
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem


class EllipsoidMethod(BaseAlgorithms):
    """Ellipsoid algorithm method.

    """

    # attributes
    _x0 = None
    _Q0 = None
    _max_cuts = None
    _shallow_cut = None
    _decomposition = None
    _memory = None

    def __init__(self,
                 x0: np.ndarray=np.array([[]]).reshape(-1, 1),
                 Q0: np.ndarray=np.array([[]]),
                 max_cuts: int=32,
                 shallow_cut: float=0,
                 decomposition: bool=True,
                 memory: bool=True,
                 n_max: int=None,
                 eps: float=None):
        """Ellipsoid algorithm constructor.

        Args:
            x0           : (np.ndarray) initial point.
            Q0           : (np.ndarray) initial inverse ellipsoid matrix.
            max_cuts     : (int) maximum number of ellipsoid cuts per iteration.
            shallow_cut  : (float) shallow cut option [0, 1].
            decomposition: (bool) is matrix decomposition indicator (True: sqrt decomposition).
            memory       : (bool) cut memory indicator.
            n_max        : (int) maximum number of iterations for stop criterion.
            eps          : (float) maximum uncertainty for stop criterion.
        """

        # parameters
        self.x0 = 1.0 * x0
        self.Q0 = Q0
        self.max_cuts = max_cuts
        self.shallow_cut = shallow_cut
        self.decomposition = decomposition
        self.memory = memory
        if n_max is not None:
            self.n_max = n_max
        if eps is not None:
            self.eps = eps

    # getters
    @property
    def x0(self):
        return self._x0

    @property
    def Q0(self):
        return self._Q0

    @property
    def max_cuts(self):
        return self._max_cuts

    @property
    def shallow_cut(self):
        return self._shallow_cut

    @property
    def decomposition(self):
        return self._decomposition

    @property
    def memory(self):
        return self._memory

    # setters
    @x0.setter
    def x0(self, x0):
        if x0.shape[1] == 1:
            self._x0 = x0
        else:
            raise ValueError("Initial point must be a column vector.")

    @Q0.setter
    def Q0(self, Q0):
        # check if input is numpy
        if not isinstance(Q0, np.ndarray):
            raise Warning("x must be a numpy array!")
        else:
            self._Q0 = Q0

    @max_cuts.setter
    def max_cuts(self, k):
        if k > 0:
            self._max_cuts = k
        else:
            raise ValueError("Maximum number of cuts must be a positive number!")

    @shallow_cut.setter
    def shallow_cut(self, s):
        if 0 <= s <= 1:
            self._shallow_cut = s
        else:
            raise ValueError("Shallow cut must be in [0, 1).")

    @decomposition.setter
    def decomposition(self, d):
        # check if input is numpy
        if not isinstance(d, bool):
            raise Warning("Decomposition must be a boolean!")
        else:
            self._decomposition = d

    @memory.setter
    def memory(self, m):
        # check if input is numpy
        if not isinstance(m, bool):
            raise Warning("Memory must be a boolean!")
        else:
            self._memory = m

    def optimize(self,
                 optimization_problem: OptimizationProblem,
                 debug: bool=True,
                 n_step: int=5) -> OptimizationResults:
        """Optimization core of Ellipsoid method.

        Args:
            optimization_problem: (OptimizationProblem) an optimization problem.
            debug               : (bool) debug option indicator.
            n_step              : (int) iterations steps to store optimization results.

        Returns:
            optimization_results: (OptimizationResults) optimization results.

        """

        # get input arguments
        f, df, _, _, g, dg, A, b, Aeq, beq, x_min, x_max, _ = optimization_problem.op_arguments()

        # optimization results
        optimization_results = OptimizationResults()

        # call method
        if not debug:
            # method output
            xb, fxb, _, _, _, stop = nlpalg.ellipsoidmethod(f, df, g, dg, A, b, Aeq, beq, x_min, x_max, self.x0,
                                                            self.Q0, self.eps, self.n_max, self.max_cuts,
                                                            self.shallow_cut, self.decomposition, self.memory, debug)

            # results
            optimization_results.x = xb
            optimization_results.fx = fxb

        else:
            # TODO (matheus): implement iterative run
            _, _, x, fx, Qi, stop = nlpalg.ellipsoidmethod(f, df, g, dg, A, b, Aeq, beq, x_min, x_max, self.x0, self.Q0,
                                                           self.eps, self.n_max, self.max_cuts, self.shallow_cut,
                                                           self.decomposition, self.memory, debug)

            # optimization results
            optimization_results.n_iterations = x.shape[1]  # number of iterations
            optimization_results.x = x[:, 0::n_step]
            optimization_results.fx = fx[:, 0::n_step]
            optimization_results.parameter = {'Q': Qi[..., 0::n_step]}

        # stop criteria
        if stop == 0:
            optimization_results.message = 'Stop by maximum number of iterations.'
        elif stop == 1:
            optimization_results.message = 'Stop by ellipsoid volume reduction.'
        elif stop == 2:
            optimization_results.message = 'Stop by empty localizing set.'
        elif stop == 3:
            optimization_results.message = 'Stop by degenerate ellipsoid.'
        else:
            optimization_results.message = 'Unknown termination cause.'

        return optimization_results
