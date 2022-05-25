"""
Epsilon sampler strategy
"""
import numpy as np
import random

from science_optimization.algorithms import BaseAlgorithms
from science_optimization.solvers.pareto_samplers import BaseParetoSamplers
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem


class RandomSampler(BaseParetoSamplers):
    """Pareto sampler that uses the non dominated approach with random initial values"""

    # class attributes
    _objective_constraint_index = None
    _n_layers = None

    def __init__(self,
                 optimization_problem: OptimizationProblem,
                 algorithm: BaseAlgorithms = None,
                 n_samples: int = None):
        """Constructor of optimizer class.

        Args:
            optimization_problem: (OptimizationProblem) optimization problem instance.
            algorithm           : (Any) an algorithm instance.
            n_samples           : (int) number of samples.
        """

        # instantiate super class
        super().__init__(optimization_problem, algorithm, n_samples)

    def sample_aux(self) -> OptimizationResults:
        """Hybrid e-constrained/lambda sampler.

        Returns:
            output: (OptimizationResults) optimization results.
        """

        # vertices of pareto front
        x, fx, fx_bounds = self.pareto_vertices()

        n = x.shape[0]      # dimension

        x_bounds = np.zeros((n, 2))

        # limits will be based on the x values of the vertices
        x_bounds[:, 0] = np.amin(x, axis=1)
        x_bounds[:, 1] = np.amax(x, axis=1)

        n_obj = self.optimization_problem.objective.objectives.n_functions

        for _ in range(self.n_samples - n_obj):

            x0 = random.uniform(x_bounds[:, 0], x_bounds[:, 1])
            self.algorithm.x0 = x0.reshape((-1, 1))
            o = self.algorithm.optimize(optimization_problem=self.optimization_problem, debug=False)

            x = np.hstack((x, o.x))
            fx = np.hstack((fx, self.optimization_problem.objective.objectives.eval(o.x)))

        # output
        output = OptimizationResults()
        output.x = x
        output.fx = fx

        return output
