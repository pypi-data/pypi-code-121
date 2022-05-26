"""Class defining a triangular distribution."""
import numbers
from typing import Any, Dict, Optional

import numpy
import scipy.stats
import scipy.optimize

from .distribution import Distribution


class Triangular(Distribution):
    """A class to define a triangular distribution.

    Parameters
    ----------
    worst : float
        The parameter absolute worst value.
    likely : float
        The parameter absolute likely value (i.e. corresponding to the peak probability).
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
        likely: float,
        best: float,
        pworst: Optional[float] = 0.15,
        pbest: Optional[float] = 0.15,
    ):
        self._rv = None  # type: scipy.stats.triang
        # Dummy init
        self._likely = 0.5 * (best + worst)  # type: numbers.Number
        super().__init__(worst, best, pworst, pbest)

        self.likely = likely  # Trigger likely validation

    def __json__(self) -> Dict[str, Any]:
        """Serialize the distribution object.

        Returns
        -------
        Dict[str, Any]
            JSONable dictionary describing the distribution.
        """
        base = super().__json__()
        base.update({"likely": self.likely})
        return base

    @property
    def likely(self) -> float:
        """float : The parameter absolute likely value
        
        It corresponds to the peak probability.
        """
        return self._likely

    @likely.setter
    def likely(self, value: float):
        params = self._rv.kwds
        lower = params["loc"]
        upper = lower + params["scale"]
        if not (lower <= value <= upper):
            raise ValueError(
                f"Likely value not within distribution bounds: {lower} <= {value} <= {upper}."
            )
        self._likely = value
        self._set_distribution()

    def _set_distribution(self) -> None:
        """Set the probability distribution according the parameters."""
        if self.pworst + self.pbest > 1.0:
            raise ValueError(
                f"Best and worst probabilities are incompatible: {self.__json__()!s}."
            )

        pts = [self.worst, self.best]
        if self.worst > self.best:
            ppts = [1 - self.pworst, self.pbest]
        else:
            ppts = [self.pworst, 1 - self.pbest]

        if self._rv is None:
            x0 = [min(0, self.likely), 2 * abs(self.likely)]
        else:
            params = self._rv.kwds  # return {"c": #, "loc": #, "scale": #}
            x0 = [params["loc"], params["scale"]]

        def make_triang(x):
            # likely = loc + c * scale
            if any(numpy.isnan(x)):
                raise ValueError(f"invalid distribution parameters {x}")
            c = (self.likely - x[0]) / x[1]
            return scipy.stats.triang(c=c, loc=x[0], scale=x[1])

        def f(x):
            t = make_triang(x)
            return t.ppf(ppts) - pts

        res = scipy.optimize.root(f, x0)
        if not res.success or any(numpy.isnan(res.x)):
            raise ValueError(
                f"Unable to fit triangular distribution on {self.__json__()!s}."
            )
        self._rv = make_triang(res.x)

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
