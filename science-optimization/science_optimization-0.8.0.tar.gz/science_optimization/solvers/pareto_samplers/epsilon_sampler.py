"""
Epsilon sampler strategy
"""
from science_optimization.solvers.pareto_samplers import BaseParetoSamplers, NonDominatedSampler
from science_optimization.solvers import OptimizationResults
from science_optimization.builder import OptimizationProblem
import science_optimization.function as sfunc
from typing import Any
import numpy as np
from copy import deepcopy


class EpsilonSampler(BaseParetoSamplers):
    """Hybrid e-constrained/lambda Pareto front sampler."""

    # class attributes
    _objective_constraint_index = None
    _n_layers = None

    def __init__(self,
                 optimization_problem: OptimizationProblem,
                 algorithm: Any = None,
                 n_samples: int = None,
                 n_layers: int = None,
                 objective_constraint_index: int = None):
        """Constructor of optimizer class.

        Args:
            optimization_problem: (OptimizationProblem) optimization problem instance.
            algorithm           : (Any) an algorithm instance.
            n_samples           : (int) number of samples.
            n_layers            : (int) number of layers of Pareto fronts (used for 3 objectives only).
            objective_constraint_index    : (int) objective constraint index for p-epsilon algorithm.
        """

        # instantiate super class
        super().__init__(optimization_problem, algorithm, n_samples)

        # parameters
        if objective_constraint_index is not None:
            self.objective_constraint_index = objective_constraint_index
        else:
            self.objective_constraint_index = optimization_problem.objective.objectives.n_functions - 1
        if n_layers is not None:
            self.n_layers = n_layers
        else:
            self.n_layers = (self.n_samples-3) // 2

    # getters
    @property
    def objective_constraint_index(self):
        return self._objective_constraint_index

    @property
    def n_layers(self):
        return self._n_layers

    # setters
    @objective_constraint_index.setter
    def objective_constraint_index(self, objective_index):
        if objective_index == 0 or objective_index == 1 or objective_index == 2:
            self._objective_constraint_index = objective_index
        else:
            raise ValueError('Index must be 0, 1 or 2. Not yet implemented more than 3 objectives.')

    @n_layers.setter
    def n_layers(self, n):
        if 0 < n <= self.n_samples:
            self._n_layers = n
        else:
            raise ValueError('Number of layers must be a positive integer less than {}.'.format(self.n_samples))

    def sample_aux(self) -> OptimizationResults:
        """Hybrid e-constrained/lambda sampler.

        Returns:
            output: (OptimizationResults) optimization results.
        """

        # verify
        if self.optimization_problem.objective.objectives.n_functions > 3:
            raise ValueError("Sampler not implemented for more than 3 objective functions.")
        if self.optimization_problem.objective.objectives.n_functions < 3 and self.objective_constraint_index == 2:
            raise ValueError("Objective index out of bounds!")

        # vertices of pareto front
        x, fx, fx_bounds = self.pareto_vertices()
        ic = self.objective_constraint_index  # constraint index

        # bi-objective optimization
        if self.optimization_problem.objective.objectives.n_functions == 2:
            # generate epsilon values for objective ic
            epsilon = np.linspace(fx_bounds[ic, 0], fx_bounds[ic, 1], self.n_samples)
            epsilon = epsilon[1:-1]  # remove vertices

            # sample
            for k in range(len(epsilon)):

                # p-epsilon optimization problem
                op = self.op_hybrid(epsilon[k])

                # optimize
                o = self.algorithm.optimize(optimization_problem=op, debug=False)
                x = np.hstack((x, o.x))
                fx = np.hstack((fx, self.optimization_problem.objective.objectives.eval(o.x)))

        # three-objective optimization
        else:
            # number of samples per surface TODO (Feres) maybe implement a way to change this value for each surface
            nss = (self.n_samples - 3) // self.n_layers
            n_samples_surface = [nss] * self.n_layers
            n_samples_surface[0] = n_samples_surface[0] + self.n_samples - sum(n_samples_surface) - 3

            # generate log-spaced epsilon values for objective ic
            dx = 1/self.n_layers * (fx_bounds[ic, 1] - fx_bounds[ic, 0])
            fr = fx_bounds[ic, 1] - fx_bounds[ic, 0]
            gs = np.logspace(0, 1, self.n_layers)
            epsilon = (gs-gs[0])*fr/(gs[-1]-gs[0]) + fx_bounds[ic, 0] + 0.1*dx

            # sample
            for k in range(len(epsilon)):

                # p-epsilon bi-objective optimization problem
                op = self.op_hybrid(epsilon[k])

                # non-dominated sampler with the ic objective as constraint
                sampler = NonDominatedSampler(optimization_problem=op,
                                              algorithm=self.algorithm,
                                              n_samples=n_samples_surface[k],
                                              distance_type=1)

                # output
                o = sampler.sample()
                x = np.hstack((x, o.x))
                fx = np.hstack((fx, self.optimization_problem.objective.objectives.eval(o.x)))

        # output
        output = OptimizationResults()
        output.x = x
        output.fx = fx

        return output

    def op_hybrid(self, e):
        """ Builds a hybrid p-epsilon/lambda optimization problem.

        Args:
            e : epsilon bounds.

        Returns:
            op: optimization problem.
        """

        # copy of optimization problem
        op = deepcopy(self.optimization_problem)
        obj = deepcopy(self.optimization_problem.objective)

        # constrained objective function
        ico = self.objective_constraint_index  # index of constrained objective
        co = obj.objectives.functions[ico]

        # objective function
        if self.optimization_problem.objective.objectives.n_functions == 2:
            if not obj.objectives.is_linear():
                w = [sfunc.LinearFunction(c=np.zeros((co.dimension(), 1)), d=1.),
                     sfunc.LinearFunction(c=np.zeros((co.dimension(), 1)), d=1e-6)]
                fo = w[0] * obj.objectives.functions[1-self.objective_constraint_index] + w[1] * co
            else:
                fo = sfunc.LinearFunction(
                    c=obj.objectives.functions[1-self.objective_constraint_index].parameters['c'] +
                    1e-6 * co.parameters['c'],
                    d=obj.objectives.functions[1-self.objective_constraint_index].parameters['d'] +
                    1e-6 * co.parameters['d']
                )

            # update problem objective
            op.objective.objectives.clear()
            op.objective.objectives.add(fo)
        else:
            # remove one objective function
            op.objective.objectives.remove(idx=ico)

        # change parametric constrained objectives
        if isinstance(co, sfunc.LinearFunction) or isinstance(co, sfunc.QuadraticFunction):
            # change function
            co.parameters['d'] = co.parameters['d'] - e

            # add co to inequality constraints
            op.constraints.inequality_constraints.add(co)

        # change parametric constrained objectives
        elif isinstance(co, sfunc.PolynomialFunction):
            # change function
            co.parameters['e'].extend([0]*co.dimension())
            co.parameters['c'].extend([float(-e)])

            # add co to inequality constraints
            op.constraints.inequality_constraints.add(co)

        # nonparametric constrained functions
        else:
            g = co + sfunc.LinearFunction(c=np.zeros((co.dimension(), 1)), d=-e)

            # add to constraint
            op.constraints.inequality_constraints.add(g)

        return op
