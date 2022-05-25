"""
Part of the code in this file is reproduced from https://github.com/hardmaru/estool, licensed under MIT License

MIT License

Copyright (c) 2017 David Ha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

By contributing to the hardmaru/estool repository through pull-request, comment,
or otherwise, the contributor releases their content to the license and copyright
terms herein.

"""

from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)
from .space_optim import StandardizedSpace
import numpy as np


def compute_ranks(x):
    """
    Returns ranks in [0, len(x))
    """
    assert x.ndim == 1
    ranks = np.empty(len(x), dtype=int)
    ranks[x.argsort()] = np.arange(len(x))
    return ranks


def compute_centered_ranks(x):
    y = compute_ranks(x.ravel()).reshape(x.shape).astype(np.float32)
    y /= x.size - 1
    y -= 0.5
    return y


def compute_weight_decay(weight_decay, model_param_list):
    model_param_grid = np.array(model_param_list)
    return -weight_decay * np.mean(model_param_grid * model_param_grid, axis=1)


class GradientOptimizer:
    def __init__(self, pi, epsilon=1e-08):
        self.pi = pi
        self.dim = pi.num_params
        self.epsilon = epsilon
        self.t = 0

    def update(self, globalg):
        self.t += 1
        step = self._compute_step(globalg)
        theta = self.pi.mu
        ratio = np.linalg.norm(step) / (np.linalg.norm(theta) + self.epsilon)
        self.pi.mu = theta + step
        return ratio

    def _compute_step(self, globalg):
        raise NotImplementedError


class BasicSGD(GradientOptimizer):  # pragma: no cover
    def __init__(self, pi, stepsize):
        GradientOptimizer.__init__(self, pi)
        self.stepsize = stepsize

    def _compute_step(self, globalg):
        step = -self.stepsize * globalg
        return step


class SGD(GradientOptimizer):
    def __init__(self, pi, stepsize, momentum=0.9):
        GradientOptimizer.__init__(self, pi)
        self.v = np.zeros(self.dim, dtype=np.float32)
        self.stepsize, self.momentum = stepsize, momentum

    def _compute_step(self, globalg):
        self.v = self.momentum * self.v + (1.0 - self.momentum) * globalg
        step = -self.stepsize * self.v
        return step


class Adam(GradientOptimizer):
    def __init__(self, pi, stepsize, beta1=0.99, beta2=0.999):
        GradientOptimizer.__init__(self, pi)
        self.stepsize = stepsize
        self.beta1 = beta1
        self.beta2 = beta2
        self.m = np.zeros(self.dim, dtype=np.float32)
        self.v = np.zeros(self.dim, dtype=np.float32)

    def _compute_step(self, globalg):
        a = (
            self.stepsize
            * np.sqrt(1 - self.beta2**self.t)
            / (1 - self.beta1**self.t)
        )
        self.m = self.beta1 * self.m + (1 - self.beta1) * globalg
        self.v = self.beta2 * self.v + (1 - self.beta2) * (globalg * globalg)
        step = -a * self.m / (np.sqrt(self.v) + self.epsilon)
        return step


@OptimizationAlgorithmRegistry.register_with_info(
    SupportsParallelization=True,
    RequiresMaxEvaluations=False,
    Supports1D=False,
    HasIterations=True,
)
class OpenES:
    '''Basic Version of OpenAI Evolution Strategies. Code in this class is largely reproduced from https://github.com/hardmaru/estool, MIT License, Copyright (c) 2017 David Ha.

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in one batch. Often equal to the population size.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        **algorithm_options : Additional keyword arguments passed to the algorithm. May include:

            * sigma_init (float, default 0.2): initial standard deviation
            * sigma_decay (float, default 0.999): annealing of standard deviation
            * sigma_limit (float, default 0.01): stop annealing if sigma is less than this quantity
            * learning_rate (float, default 0.01): learning rate
            * learning_rate_decay (float, default 0.9999): annealing the learning rate
            * learning_rate_limit (float, default 0.01): stop annealing learning rate
            * antithetic (bool, default False): whether to use antithetic sampling
            * forget_best (bool, default False): forget the historical best elites
            * weight_decay (float, default 0.01): weight decay coefficient
            * rank_fitness (bool, default True): use rank rather than fitness numbers

    '''

    def __init__(self, space, max_evaluations, batch_size, **algorithm_options):

        self.space = space
        self.standardized_space = StandardizedSpace(space, bounded=False)

        self.starting_point = (
            self.standardized_space.initial_value()
        )  # Numpy array of size self.standardized_space.dimension
        self.bounds = self.standardized_space.list_of_variables[
            0
        ].bounds  # [0,1] for the standardized space
        self.default_batch_size = int(
            4 + 3 * np.log(self.standardized_space.dimension)
        )  # Default batch size used in case a batch size < 3 is provided

        if 'popsize' not in algorithm_options:
            if batch_size < 3:
                batch_size = self.default_batch_size
            algorithm_options['popsize'] = batch_size

        self.num_params = self.standardized_space.dimension
        self.sigma_decay = algorithm_options.setdefault('sigma_decay', 0.999)
        self.sigma = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_init = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_limit = algorithm_options.setdefault('sigma_limit', 0.01)
        self.learning_rate = algorithm_options.setdefault('learning_rate', 0.01)
        self.learning_rate_decay = algorithm_options.setdefault(
            'learning_rate_decay', 0.9999
        )
        self.learning_rate_limit = algorithm_options.setdefault(
            'learning_rate_limit', 0.001
        )
        self.popsize = algorithm_options['popsize']
        self.antithetic = algorithm_options.setdefault('antithetic', False)
        if self.antithetic:  # pragma: no cover
            assert self.popsize % 2 == 0, "Population size must be even"
            self.half_popsize = int(self.popsize / 2)

        self.reward = np.zeros(self.popsize)
        self.mu = self.starting_point
        self.best_mu = np.zeros(self.num_params)
        self.best_reward = 0
        self.first_interation = True
        self.forget_best = algorithm_options.setdefault('forget_best', True)
        self.weight_decay = algorithm_options.setdefault('weight_decay', 0.01)
        self.rank_fitness = algorithm_options.setdefault('rank_fitness', True)

        if self.rank_fitness:
            self.forget_best = True  # always forget the best one if we rank
        # choose optimizer
        algorithm_options.setdefault('method', 'SGD')
        if algorithm_options['method'] == 'SGD':  # pragma: no cover
            self.optimizer = SGD(self, self.learning_rate)
        elif algorithm_options['method'] == 'SGD':  # pragma: no cover
            self.optimizer = BasicSGD(self, self.learning_rate)
        elif algorithm_options['method'] == 'Adam':  # pragma: no cover
            self.optimizer = Adam(self, self.learning_rate)
        else:  # pragma: no cover
            raise ValueError(
                "Unkown optimization method %r" % algorithm_options['method']
            )

        self.algorithm_options = algorithm_options

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        # antithetic sampling
        if self.antithetic:  # pragma: no cover
            self.epsilon_half = np.random.randn(self.half_popsize, self.num_params)
            self.epsilon = np.concatenate([self.epsilon_half, -self.epsilon_half])
        else:
            self.epsilon = np.random.randn(self.popsize, self.num_params)

        self.solutions = self.mu.reshape(1, self.num_params) + self.epsilon * self.sigma

        return self.standardized_space.map_to_original_space(self.solutions)

    def tell(self, list_of_samples, list_of_results):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        assert (
            len(list_of_results) == self.popsize
        ), "Inconsistent reward_table size reported."

        reward = -np.array(list_of_results)  # This algorithm always maximizes

        if self.rank_fitness:
            reward = compute_centered_ranks(reward)

        if self.weight_decay > 0:
            l2_decay = compute_weight_decay(self.weight_decay, self.solutions)
            reward += l2_decay

        idx = np.argsort(reward)[::-1]

        best_reward = reward[idx[0]]
        best_mu = self.solutions[idx[0]]

        self.curr_best_reward = best_reward
        self.curr_best_mu = best_mu

        if self.first_interation:
            self.first_interation = False
            self.best_reward = self.curr_best_reward
            self.best_mu = best_mu
        else:
            if self.forget_best or (self.curr_best_reward > self.best_reward):
                self.best_mu = best_mu
                self.best_reward = self.curr_best_reward

        # main bit:
        # standardize the rewards to have a gaussian distribution
        normalized_reward = (reward - np.mean(reward)) / np.std(reward)
        change_mu = (
            1.0
            / (self.popsize * self.sigma)
            * np.dot(self.epsilon.T, normalized_reward)
        )

        # self.mu += self.learning_rate * change_mu

        self.optimizer.stepsize = self.learning_rate
        self.optimizer.update(-change_mu)

        # adjust sigma according to the adaptive sigma calculation
        if self.sigma > self.sigma_limit:
            self.sigma *= self.sigma_decay

        if self.learning_rate > self.learning_rate_limit:
            self.learning_rate *= self.learning_rate_decay

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return self.standardized_space.map_to_original_space(self.best_mu)


@OptimizationAlgorithmRegistry.register_with_info(
    SupportsParallelization=True,
    RequiresMaxEvaluations=False,
    Supports1D=False,
    HasIterations=True,
)
class PEPG:
    '''Variant of PEPG. Code in this class is largely reproduced from https://github.com/hardmaru/estool, MIT License, Copyright (c) 2017 David Ha.

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in one batch. Often equal to the population size.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        **algorithm_options : Additional keyword arguments passed to the algorithm. May include:

            * sigma_init (float, default 0.2): initial standard deviation
            * sigma_alpha (float, default 0.2): learning rate for standard deviation
            * sigma_decay (float, default 0.999): annealing of standard deviation
            * sigma_limit (float, default 0.01): stop annealing if sigma is less than this quantity
            * sigma_max_change (float, default 0.2): clips adaptive sigma to 20%
            * learning_rate (float, default 0.01): learning rate
            * learning_rate_decay (float, default 0.9999): annealing the learning rate
            * learning_rate_limit (float, default 0.01): stop annealing learning rate
            * elite_ratio (float, default 0.2): percentage of the elites, if > 0, then ignore learning_rate
            * forget_best (bool, default False): forget the historical best elites
            * weight_decay (float, default 0.01): weight decay coefficient
            * average_baseline (bool, default True): set baseline to average of batch
            * rank_fitness (bool, default True): use rank rather than fitness numbers

    '''

    def __init__(self, space, max_evaluations, batch_size, **algorithm_options):

        self.space = space
        self.standardized_space = StandardizedSpace(space, bounded=False)

        self.starting_point = (
            self.standardized_space.initial_value()
        )  # Numpy array of size self.standardized_space.dimension
        self.bounds = self.standardized_space.list_of_variables[
            0
        ].bounds  # [0,1] for the standardized space
        self.default_batch_size = int(
            4 + 3 * np.log(self.standardized_space.dimension)
        )  # Default batch size used in case a batch size < 3 is provided

        if 'popsize' not in algorithm_options:
            if batch_size < 3:
                batch_size = self.default_batch_size
            algorithm_options['popsize'] = batch_size

        self.num_params = self.standardized_space.dimension
        self.sigma_decay = algorithm_options.setdefault('sigma_decay', 0.999)
        self.sigma = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_alpha = algorithm_options.setdefault('sigma_alpha', 0.2)
        self.sigma_init = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_max_change = algorithm_options.setdefault('sigma_max_change', 0.1)
        self.sigma_limit = algorithm_options.setdefault('sigma_limit', 0.01)
        self.learning_rate = algorithm_options.setdefault('learning_rate', 0.01)
        self.learning_rate_decay = algorithm_options.setdefault(
            'learning_rate_decay', 0.9999
        )
        self.learning_rate_limit = algorithm_options.setdefault(
            'learning_rate_limit', 0.01
        )
        self.popsize = algorithm_options['popsize']
        self.elite_ratio = algorithm_options.setdefault('elite_ratio', 0)
        self.average_baseline = algorithm_options.setdefault('average_baseline', True)
        if self.average_baseline:
            assert self.popsize % 2 == 0, "Population size must be even"
            self.batch_size = int(self.popsize / 2)
        else:  # pragma: no cover
            assert self.popsize & 1, "Population size must be odd"
            self.batch_size = int((self.popsize - 1) / 2)

        self.reward = np.zeros(self.popsize)
        self.mu = self.starting_point
        self.best_mu = np.zeros(self.num_params)
        self.best_reward = 0
        self.first_interation = True
        self.forget_best = algorithm_options.setdefault('forget_best', True)
        self.weight_decay = algorithm_options.setdefault('weight_decay', 0.01)
        self.rank_fitness = algorithm_options.setdefault('rank_fitness', True)

        # option to use greedy es method to select next mu, rather than using drift
        self.elite_popsize = int(self.popsize * self.elite_ratio)
        self.use_elite = False
        if self.elite_popsize > 0:  # pragma: no cover
            self.use_elite = True

        self.batch_reward = np.zeros(self.batch_size * 2)
        self.mu = self.starting_point
        self.sigma = np.ones(self.num_params) * self.sigma_init
        self.curr_best_mu = np.zeros(self.num_params)
        self.best_mu = np.zeros(self.num_params)
        self.best_reward = 0
        self.first_interation = True
        if self.rank_fitness:
            self.forget_best = True  # always forget the best one if we rank
        # choose optimizer
        algorithm_options.setdefault('method', 'Adam')
        if algorithm_options['method'] == 'SGD':  # pragma: no cover
            self.optimizer = SGD(self, self.learning_rate)
        elif algorithm_options['method'] == 'SGD':  # pragma: no cover
            self.optimizer = BasicSGD(self, self.learning_rate)
        elif algorithm_options['method'] == 'Adam':  # pragma: no cover
            self.optimizer = Adam(self, self.learning_rate)
        else:  # pragma: no cover
            raise ValueError(
                "Unkown optimization method %r" % algorithm_options['method']
            )

        self.algorithm_options = algorithm_options

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        # antithetic sampling
        self.epsilon = np.random.randn(
            self.batch_size, self.num_params
        ) * self.sigma.reshape(1, self.num_params)
        self.epsilon_full = np.concatenate([self.epsilon, -self.epsilon])
        if self.average_baseline:
            epsilon = self.epsilon_full
        else:  # pragma: no cover
            # first population is mu, then positive epsilon, then negative epsilon
            epsilon = np.concatenate(
                [np.zeros((1, self.num_params)), self.epsilon_full]
            )
        solutions = self.mu.reshape(1, self.num_params) + epsilon
        self.solutions = solutions

        return self.standardized_space.map_to_original_space(self.solutions)

    def tell(self, list_of_samples, list_of_results):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        assert (
            len(list_of_results) == self.popsize
        ), "Inconsistent reward_table size reported."

        reward_table = -np.array(list_of_results)  # This algorithm always maximizes

        if self.rank_fitness:
            reward_table = compute_centered_ranks(reward_table)

        if self.weight_decay > 0:
            l2_decay = compute_weight_decay(self.weight_decay, self.solutions)
            reward_table += l2_decay

        reward_offset = 1
        if self.average_baseline:
            b = np.mean(reward_table)
            reward_offset = 0
        else:  # pragma: no cover
            b = reward_table[0]  # baseline

        reward = reward_table[reward_offset:]
        if self.use_elite:  # pragma: no cover
            idx = np.argsort(reward)[::-1][0 : self.elite_popsize]
        else:
            idx = np.argsort(reward)[::-1]

        best_reward = reward[idx[0]]
        if best_reward > b or self.average_baseline:
            best_mu = self.mu + self.epsilon_full[idx[0]]
            best_reward = reward[idx[0]]
        else:  # pragma: no cover
            best_mu = self.mu
            best_reward = b

        self.curr_best_reward = best_reward
        self.curr_best_mu = best_mu

        if self.first_interation:
            self.sigma = np.ones(self.num_params) * self.sigma_init
            self.first_interation = False
            self.best_reward = self.curr_best_reward
            self.best_mu = best_mu
        else:
            if self.forget_best or (self.curr_best_reward > self.best_reward):
                self.best_mu = best_mu
                self.best_reward = self.curr_best_reward

        # short hand
        epsilon = self.epsilon
        sigma = self.sigma

        # update the mean

        # move mean to the average of the best idx means
        if self.use_elite:  # pragma: no cover
            self.mu += self.epsilon_full[idx].mean(axis=0)
        else:
            rT = reward[: self.batch_size] - reward[self.batch_size :]
            change_mu = np.dot(rT, epsilon)
            self.optimizer.stepsize = self.learning_rate
            self.optimizer.update(-change_mu)  # adam, rmsprop, momentum, etc.
            # self.mu += change_mu * self.learning_rate  # normal SGD method

        # adaptive sigma
        # normalization
        if self.sigma_alpha > 0:
            stdev_reward = 1.0
            if not self.rank_fitness:  # pragma: no cover
                stdev_reward = reward.std()
            S = (
                epsilon * epsilon - (sigma * sigma).reshape(1, self.num_params)
            ) / sigma.reshape(1, self.num_params)
            reward_avg = (reward[: self.batch_size] + reward[self.batch_size :]) / 2.0
            rS = reward_avg - b
            delta_sigma = (np.dot(rS, S)) / (2 * self.batch_size * stdev_reward)

            # adjust sigma according to the adaptive sigma calculation
            # for stability, don't let sigma move more than 10% of orig value
            change_sigma = self.sigma_alpha * delta_sigma
            change_sigma = np.minimum(change_sigma, self.sigma_max_change * self.sigma)
            change_sigma = np.maximum(change_sigma, -self.sigma_max_change * self.sigma)
            self.sigma += change_sigma

        if self.sigma_decay < 1:
            self.sigma[self.sigma > self.sigma_limit] *= self.sigma_decay

        if (
            self.learning_rate_decay < 1
            and self.learning_rate > self.learning_rate_limit
        ):  # pragma: no cover
            self.learning_rate *= self.learning_rate_decay

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return self.standardized_space.map_to_original_space(self.best_mu)


@OptimizationAlgorithmRegistry.register_with_info(
    SupportsParallelization=True,
    RequiresMaxEvaluations=False,
    Supports1D=False,
    HasIterations=True,
)
class SimpleGA:
    '''Simple Genetic Algorithm. Code in this class is largely reproduced from https://github.com/hardmaru/estool, MIT License, Copyright (c) 2017 David Ha.

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in one batch. Often equal to the population size.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        **algorithm_options : Additional keyword arguments passed to the algorithm. May include:

            * sigma_init (float, default 0.2): initial standard deviation
            * sigma_decay (float, default 0.999): annealing of standard deviation
            * sigma_limit (float, default 0.01): stop annealing if sigma is less than this quantity
            * elite_ratio (float, default 0.2): percentage of the elites
            * forget_best (bool, default False): forget the historical best elites
            * weight_decay (float, default 0.01): weight decay coefficient

    '''

    def __init__(self, space, max_evaluations, batch_size, **algorithm_options):

        self.space = space
        self.standardized_space = StandardizedSpace(space, bounded=False)

        self.starting_point = (
            self.standardized_space.initial_value()
        )  # Numpy array of size self.standardized_space.dimension
        self.bounds = self.standardized_space.list_of_variables[
            0
        ].bounds  # [0,1] for the standardized space
        self.default_batch_size = (
            10  # Default batch size used in case a batch size < 10 is provided
        )

        if 'popsize' not in algorithm_options:
            if batch_size < 10:
                batch_size = self.default_batch_size
            algorithm_options['popsize'] = batch_size

        self.num_params = self.standardized_space.dimension
        self.sigma_decay = algorithm_options.setdefault('sigma_decay', 0.999)
        self.sigma = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_init = algorithm_options.setdefault('sigma_init', 0.2)
        self.sigma_limit = algorithm_options.setdefault('sigma_limit', 0.01)

        self.popsize = algorithm_options['popsize']
        self.elite_ratio = algorithm_options.setdefault('elite_ratio', 0.2)
        self.forget_best = algorithm_options.setdefault('forget_best', True)
        self.weight_decay = algorithm_options.setdefault('weight_decay', 0.01)

        self.elite_popsize = int(self.popsize * self.elite_ratio)
        if self.elite_popsize < 2:  # pragma: no cover
            raise ValueError(
                "Elite popsize is lower than 2, increase batch size (popsize) or increase elite_ratio"
            )
        self.elite_params = np.zeros((self.elite_popsize, self.num_params))
        for i in range(self.elite_params.shape[0]):
            self.elite_params[i, :] = self.starting_point.copy()
        self.elite_rewards = np.zeros(self.elite_popsize)
        self.best_param = np.zeros(self.num_params)
        self.best_reward = 0
        self.first_iteration = True

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        self.epsilon = np.random.randn(self.popsize, self.num_params) * self.sigma
        solutions = []

        def mate(a, b):
            c = np.copy(a)
            idx = np.where(np.random.rand((c.size)) > 0.5)
            c[idx] = b[idx]
            return c

        elite_range = range(self.elite_popsize)

        for i in range(self.popsize):
            idx_a = np.random.choice(elite_range)
            idx_b = np.random.choice(elite_range)
            child_params = mate(self.elite_params[idx_a], self.elite_params[idx_b])
            solutions.append(child_params + self.epsilon[i])

        solutions = np.array(solutions)
        self.solutions = solutions

        return self.standardized_space.map_to_original_space(self.solutions)

    def tell(self, list_of_samples, list_of_results):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        assert (
            len(list_of_results) == self.popsize
        ), "Inconsistent reward_table size reported."

        reward_table = -np.array(list_of_results)  # This algorithm always maximizes

        if self.weight_decay > 0:
            l2_decay = compute_weight_decay(self.weight_decay, self.solutions)
            reward_table += l2_decay

        if self.forget_best or self.first_iteration:
            reward = reward_table
            solution = self.solutions
        else:  # pragma: no cover
            reward = np.concatenate([reward_table, self.elite_rewards])
            solution = np.concatenate([self.solutions, self.elite_params])

        idx = np.argsort(reward)[::-1][0 : self.elite_popsize]

        self.elite_rewards = reward[idx]
        self.elite_params = solution[idx]

        self.curr_best_reward = self.elite_rewards[0]

        if self.first_iteration or (self.curr_best_reward > self.best_reward):
            self.first_iteration = False
            self.best_reward = self.elite_rewards[0]
            self.best_param = np.copy(self.elite_params[0])

        if self.sigma > self.sigma_limit:
            self.sigma *= self.sigma_decay

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return self.standardized_space.map_to_original_space(self.best_param)
