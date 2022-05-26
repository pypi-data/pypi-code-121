"""Class defining an uniform distribution."""
from typing import Optional

import numpy
import scipy.stats

from .distribution import Distribution


class Uniform(Distribution):
    """A class to define an uniform distribution.

    Parameters
    ----------
    worst : float
        The parameter absolute worst value.
    best : float
        The parameter absolute best value.
    pworst : float, optional
        The worst value probability is the probability that the variable will be lower (if worst<best) or higher
        (if worst>best) than the worst value; default 0.15 (i.e. 15%).
    pbest : float, optional
        The best value probability is the probability that the variable will be higher (if worst<best) or lower
        (if worst>best) than the best value; default 0.15 (i.e. 15%).
   """

    def __init__(
        self,
        worst: float,
        best: float,
        pworst: Optional[float] = 0.15,
        pbest: Optional[float] = 0.15,
    ):
        self._rv = None  # type: scipy.stats.uniform

        super().__init__(worst, best, pworst, pbest)

    def _set_distribution(self):
        """Set the probability distribution according the parameters."""
        if self.pworst + self.pbest > 1:
            raise ValueError(
                f"Best and worst probabilities are incompatible: {self.__json__()!s}."
            )

        scale = numpy.abs(self.worst - self.best) / (1 - self.pworst - self.pbest)
        if self.worst < self.best:
            loc = self.worst - scale * self.pworst
        else:
            loc = self.best - scale * self.pbest

        self._rv = scipy.stats.uniform(loc=loc, scale=scale)

    def draw(self, quantile: Optional[float] = None) -> float:
        """Generate a random number.

        If a quantile is given, generate the perturbation for that quantile.

        Parameters
        ----------
        quantile : Optional[float], optional
            Quantile for which the perturbation must be set; default None (i.e. random perturbation)
        
        Returns
        -------
        float
            The random number
        """
        return self._rv.rvs() if quantile is None else self._rv.ppf(quantile)
