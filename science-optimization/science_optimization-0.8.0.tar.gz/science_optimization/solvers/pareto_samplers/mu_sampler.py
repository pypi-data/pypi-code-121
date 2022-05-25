"""
Mu sampler strategy
"""
from science_optimization.solvers.pareto_samplers import BaseParetoSamplers
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction
from typing import Any
import numpy as np
from copy import deepcopy


class MuSampler(BaseParetoSamplers):
    """P-mu Pareto front sampler with L2-norm."""

    # class attributes
    _objective_index = 0

    def __init__(self,
                 optimization_problem: OptimizationProblem,
                 algorithm: Any = None,
                 n_samples: int = None,
                 objective_index: int = None):
        """Constructor of optimizer class.

        Args:
            optimization_problem: (OptimizationProblem) optimization problem instance.
            algorithm           : (Any) an algorithm instance.
            n_samples           : (int) number os samples.
            objective_index     : (int) objective index for p-epsilon algorithm.
        """

        # instantiate super class
        super().__init__(optimization_problem, algorithm, n_samples)

        # parameters
        if objective_index is not None:
            self.objective_index = objective_index

    # getters
    @property
    def objective_index(self):
        return self._objective_index

    # setters
    @objective_index.setter
    def objective_index(self, objective_index):
        if objective_index == 0 or objective_index == 1:
            self._objective_index = objective_index
        else:
            raise ValueError('Index must be 0 or 1. Not yet implemented more than 2 objectives.')

    def sample_aux(self) -> OptimizationResults:
        """P-mu sampler.

        Returns:
            output: (OptimizationResults) optimization results.
        """

        # verify
        if self.optimization_problem.objective.objectives.n_functions != 2:
            raise ValueError("Sampler only implemented for bi-objective optimization problems.")

        # vertices of pareto front
        x, fx, fx_bounds = self.pareto_vertices()

        # generate mu range
        nph = int(np.ceil(self.n_samples/2))
        mu1 = np.r_[np.tile(fx_bounds[0, 0], (1, nph)),
                    np.linspace(fx_bounds[1, 0], fx_bounds[1, 1], nph).reshape(1, -1)]
        mu2 = np.r_[np.linspace(fx_bounds[0, 0], fx_bounds[0, 1], nph).reshape(1, -1),
                    np.tile(fx_bounds[1, 0], (1, nph))]
        mu = np.c_[mu1[:, :-1], mu2[:, 1:-1]]

        # sample
        for k in range(self.n_samples-2):

            # p-epsilon optimization problem
            op = self.op_mu(mu[:, [k]])

            # optimize
            o = self.algorithm.optimize(optimization_problem=op, debug=False)
            x = np.hstack((x, o.x))
            fx = np.hstack((fx, self.optimization_problem.objective.objectives.eval(o.x)))

        # output
        output = OptimizationResults()
        output.x = x
        output.fx = fx

        return output

    def op_mu(self, mu: np.ndarray):
        """ Builds a p-mu optimization problem.

        Args:
            mu: mu points.

        Returns:
            op: optimization problem.
        """

        # copy of optimization problem
        op = deepcopy(self.optimization_problem)
        obj = deepcopy(self.optimization_problem.objective)

        # create functions
        def f_mu(x):
            return np.linalg.norm(obj.objectives.eval(x) - mu)

        def df_mu(x):
            return (obj.objectives.gradient(x) @ (obj.objectives.eval(x) - mu))/f_mu(x)

        # delete original objectives and evaluate
        op.objective.objectives.clear()  # delete functions
        op.objective.objectives.add(GenericFunction(func=f_mu, grad_func=df_mu, n=op.variables.dimension()))

        return op
