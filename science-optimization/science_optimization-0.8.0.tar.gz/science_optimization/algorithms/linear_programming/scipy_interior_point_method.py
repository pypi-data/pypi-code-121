"""
Interior point algorithm
"""
from .scipy_base_linear import ScipyBaseLinear


class ScipyInteriorPointMethod(ScipyBaseLinear):
    """Scipy interior-point method.

    """

    def __init__(self, n_max: int=None):
        """Constructor of interior-point optimization.

            Args:
                n_max: (int) maximum number of iterations.

        """

        super().__init__(method='interior-point', n_max=n_max)

