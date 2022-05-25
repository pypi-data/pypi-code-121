"""
Lambda sampler strategy
"""
from science_optimization.solvers.pareto_samplers import BaseParetoSamplers
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem
from science_optimization.function import GenericFunction, LinearFunction
from typing import Any
import numpy as np
from copy import deepcopy


class LambdaSampler(BaseParetoSamplers):
    """p-lambda Pareto front sampler."""

    def __init__(self,
                 optimization_problem: OptimizationProblem,
                 algorithm: Any = None,
                 n_samples: int = None):
        """Constructor of optimizer class.

        Args:
            optimization_problem: (OptimizationProblem) optimization problem instance.
            algorithm           : (Any) an algorithm instance.
            n_samples           : (int) number os samples.
        """

        # instantiate super class
        super().__init__(optimization_problem, algorithm, n_samples)

    def sample_aux(self) -> OptimizationResults:
        """ p-lambda sampler.

        Returns:
            output: (OptimizationResults) optimization results.
        """

        # cardinalities
        n = self.optimization_problem.variables.dimension()
        o = self.optimization_problem.objective.objectives.n_functions

        # verify
        if self.optimization_problem.objective.objectives.n_functions != 2:
            raise ValueError("Sampler only implemented for bi-objective optimization problems.")

        # generate lambda values from [0, 1]
        l = np.linspace(0, 1, self.n_samples)  # remove vertices

        # sample
        x = np.zeros((n, 0))
        fx = np.zeros((o, 0))
        for k in range(self.n_samples):

            # p-lambda optimization problem
            op = self.op_lambda(l[k])

            # optimize
            o = self.algorithm.optimize(optimization_problem=op, debug=False)
            x = np.hstack((x, o.x))
            fx = np.hstack((fx, self.optimization_problem.objective.objectives.eval(o.x)))

        # output
        output = OptimizationResults()
        output.x = x
        output.fx = fx

        return output

    def op_lambda(self, l):
        """ Builds a p-lambda optimization problem.

        Args:
            l : used in the weighted sum of two objectives.

        Returns:
            op: optimization problem.
        """

        # copy of optimization problem
        op = deepcopy(self.optimization_problem)
        obj = deepcopy(self.optimization_problem.objective)

        # nonparametric functions
        w = np.array([[1-l, l]])
        if not obj.objectives.is_linear():
            def fo(x):
                return obj.objectives.eval(x, composition='series', weights=w)

            # delete original objectives and evaluate
            op.objective.objectives.clear()  # delete functions
            op.objective.objectives.add(GenericFunction(func=fo, n=op.variables.dimension()))
        else:
            # new objective parameters
            c = w @ obj.C()

            # delete original objectives and evaluate
            op.objective.objectives.clear()  # delete functions
            op.objective.objectives.add(LinearFunction(c=c.T))

        return op
