from science_optimization.builder import OptimizationProblem
from science_optimization.algorithms import BaseAlgorithms
from science_optimization.algorithms.search_direction import BaseSearchDirection
from science_optimization.algorithms.cutting_plane import EllipsoidMethod
from science_optimization.algorithms.unidimensional import BaseUnidimensional
from science_optimization.algorithms.decomposition import DualDecomposition
from science_optimization.algorithms.linear_programming import ScipyBaseLinear


class Optimizer:
    """Optimizer interface.

    """

    # class attributes
    _optimization_problem = None
    _algorithm = None

    def __init__(self, opt_problem, algorithm):
        """Constructor of optimizer class.

        Args:
            opt_problem: OptimizationProblem instance
            algorithm: an algorithm instance
        """

        self.optimization_problem = opt_problem
        self.algorithm = algorithm

    # attributes interface
    @property
    def optimization_problem(self):
        return self._optimization_problem

    @property
    def algorithm(self):
        return self._algorithm

    # setters
    @optimization_problem.setter
    def optimization_problem(self, opt_problem):
        if isinstance(opt_problem, OptimizationProblem):
            self._optimization_problem = opt_problem

    @algorithm.setter
    def algorithm(self, algorithm):
        # verify instances
        if issubclass(type(algorithm), BaseSearchDirection) or issubclass(type(algorithm), EllipsoidMethod) or \
                issubclass(type(algorithm), BaseUnidimensional) or issubclass(type(algorithm), DualDecomposition) or \
                issubclass(type(algorithm), BaseAlgorithms) or issubclass(type(algorithm), ScipyBaseLinear):
            self._algorithm = algorithm
        else:
            raise Warning("Algorithm not implemented!")

    # methods
    def optimize(self, debug=False, n_step=5):
        """Run optimization

        Args:
            debug : debug algorithm indicator
            n_step: update results every n_steps

        Returns:
            OptimizationResults instance

        """

        # input check
        if not isinstance(debug, bool):
            raise Warning("Debug must be a boolean!")
        if n_step <= 0:
            raise Warning("n_step must be greater than 0!")

        results = self.algorithm.optimize(optimization_problem=self.optimization_problem, debug=debug, n_step=n_step)

        # update optimization problem parameter and return results
        self.optimization_problem.results_ = results
        return results
