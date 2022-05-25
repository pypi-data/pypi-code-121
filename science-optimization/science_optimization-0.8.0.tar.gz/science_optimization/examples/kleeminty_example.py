from science_optimization.builder import OptimizationProblem
from science_optimization.problems import KleeMinty
from science_optimization.solvers import Optimizer
from science_optimization.algorithms.linear_programming import Glop


def kleeminty_example():
    """Klee-Minty problem example.
    """

    # builder klee-minty
    km_n3 = OptimizationProblem(builder=KleeMinty(dimension=5))

    # printing info
    km_n3.info()

    # builder optimization
    optimizer = Optimizer(opt_problem=km_n3, algorithm=Glop())
    results = optimizer.optimize()

    # result
    results.info()


if __name__ == "__main__":
    # run example
    kleeminty_example()
