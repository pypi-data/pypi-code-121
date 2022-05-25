"""
Golden section algorithm (multimodal)
"""
import numpy as np
from .base_unidimensional import BaseUnidimensional
from science_optimization.algorithms.unidimensional import GoldenSection
from science_optimization.algorithms.utils import sequence_patterns
from science_optimization.problems import GenericProblem
from science_optimization.builder import OptimizationProblem
from science_optimization import solvers


class MultimodalGoldenSection(BaseUnidimensional):
    """Golden section algorithm class.

    """

    # class attributes
    ratio = (np.sqrt(5)-1)/2  # golden ratio
    _all_minima = None

    def __init__(self, eps=None, all_minima=True):
        """Class constructor.

        Args:
            eps: float with precision.
            all_minima: indicator whether to return all minima or best solution only
        """

        # super class construction
        super().__init__(eps=eps)

        # parameters
        self.all_minima = all_minima

    # get
    @property
    def all_minima(self):
        return self._all_minima

    # set
    @all_minima.setter
    def all_minima(self, am):
        if isinstance(am, bool):
            self._all_minima = am
        else:
            raise ValueError("all_minima must be a boolean!")

    # optimize method
    def optimize(self, optimization_problem, debug, n_step=1):
        """Optimize method for golden section.

        Args:
            optimization_problem: optimization problem
            debug               : debug option indicator
            n_step              : iterations step to store optimization results

        Returns:
            optimization_results: an OptimizationResults instance with feasible solution

        """

        # TODO
        if debug:
            raise ValueError("Debug option not supported for MGS algorithm yet!")

        # parameters
        f, interval = self.input(optimization_problem=optimization_problem)

        # interval
        a = interval[0, 0]
        b = interval[0, 1]

        # compute all sub-intervals of search
        s = self.compute_subintervals(f=f, a=a, b=b)

        # instantiate results
        opt_result = solvers.OptimizationResults()
        opt_result.fx = np.zeros((1, 0))
        opt_result.x = np.zeros((1, 0))

        # execute golden section: TODO: parallel processing, change object op x_bounds instead of instantiate
        n = s.shape[0]  # number of subintervals
        for i in range(n):
            # instantiate
            gs = GoldenSection(eps=self.eps)

            # build optimization problem
            si = s[i, ].reshape(1, -1)
            op = OptimizationProblem(builder=GenericProblem(f=[f], eq_cons=[], ineq_cons=[], x_bounds=si))

            # optimizer
            o = solvers.Optimizer(opt_problem=op, algorithm=gs)
            output = o.optimize(debug=False)  # TODO: improve this
            opt_result.x = np.c_[opt_result.x, output.x]
            opt_result.fx = np.c_[opt_result.fx, output.fx]

        if not self.all_minima:
            imin = np.argmin(opt_result.fx)
            opt_result.fx = opt_result.fx[0, imin]
            opt_result.x = opt_result.x[0, imin]

        return opt_result

    def compute_subintervals(self, f, a, b, p=np.array([]), a_min=None, a_max=None):
        """Compute all subintervals within the search space.

        Args:
            f   : function handler.
            a   : initial point of the current search space.
            b   : last point of the current search space.
            p   : previous points.
            a_min: initial point of the original search space.
            a_max: last point of the original search space.

        Returns:
            s: (n x 2)-array with n intervals of search.
        """

        # input
        if a_min is None:
            a_min = a

        if a_max is None:
            a_max = b

        # search sub-intervals
        s = np.zeros((0, 2))

        # sequence
        delta = b - a
        x = np.array([a, b - delta * self.ratio, a + delta * self.ratio, b])

        # find initial patterns: TODO: improve (reduce) number of function evaluations
        ivp, iap = sequence_patterns(x=x, fx=f.eval(x.reshape(1, -1)).ravel())

        # recursive call
        if iap.size == 0:  # no a-pattern found

            si = np.array([a, b])
            s = np.vstack((s, si))

        else:  # a-pattern found

            # v-patterns points
            xp = np.unique(np.hstack((x, p)))
            ivp2, _ = sequence_patterns(x=xp, fx=f.eval(xp.reshape(1, -1)).ravel())
            xvp = xp[ivp2]

            # find v-pattern before a-pattern
            ix1 = xvp[xvp < x[iap]]
            if ix1.size == 0:
                # if there is no v-pattern, complete till a_min
                x1 = a_min
            else:
                # if there is a v-pattern
                x1 = np.max(xp[xp < np.max(ix1)]).item()

            # recursive call
            si = self.compute_subintervals(f=f, a=x1, b=x[iap].item(), p=xp, a_min=a_min, a_max=a_max)
            s = np.vstack((s, si))

            # find v-pattern after a-pattern
            ix4 = xvp[xvp > x[iap]]
            if ix4.size == 0:
                # if there is no v-pattern, complete till a_max
                x4 = a_max
            else:
                # if there a v-pattern
                x4 = np.min(xp[xp > np.min(ix4)]).item()

            # recursive call
            si = self.compute_subintervals(f=f, a=x[iap].item(), b=x4, p=xp, a_min=a_min, a_max=a_max)
            s = np.vstack((s, si))

        return s
