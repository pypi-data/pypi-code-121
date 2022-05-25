import numpy as np
from science_optimization.builder import OptimizationProblem
from science_optimization.problems import Diet
from science_optimization.solvers import Optimizer
from science_optimization.algorithms.linear_programming import ScipySimplexMethod


def diet_example():
    """Diet problem example.
    """

    # minimum and maximum servings of each food
    food = ['corn', 'milk', 'white-bread']
    food_bounds = np.array([[0, 10],
                            [0, 10],
                            [0, 10]])

    # cost of each food
    cost = np.array([.18, .23, .05])

    # minimum and maximum demand of each nutrient
    demand = np.array([[2000, 2250],
                       [5000, 50000]])

    # nutrients on each food
    nutrient = np.array([[72, 121, 65],
                         [107, 500, 0]])

    # builder diet instance
    diet_problem = OptimizationProblem(builder=Diet(food=food, food_limits=food_bounds,
                                                    cost=cost, nutrient=nutrient, demand=demand))

    # results
    diet_problem.info()

    # builder optimization
    optimizer = Optimizer(opt_problem=diet_problem, algorithm=ScipySimplexMethod())
    results = optimizer.optimize()

    # result
    results.info()


if __name__ == "__main__":
    # run example
    diet_example()
