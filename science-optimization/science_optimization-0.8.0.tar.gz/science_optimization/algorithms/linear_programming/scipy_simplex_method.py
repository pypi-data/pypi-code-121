"""
Simplex algorithm
"""
from .scipy_base_linear import ScipyBaseLinear


class ScipySimplexMethod(ScipyBaseLinear):
    """Scipy simplex method.

    """

    def __init__(self, n_max: int=None):
        """Constructor of simplex optimization.

            Args:
                n_max: (int) maximum number of iterations.

        """

        super().__init__(method='simplex', n_max=n_max)

