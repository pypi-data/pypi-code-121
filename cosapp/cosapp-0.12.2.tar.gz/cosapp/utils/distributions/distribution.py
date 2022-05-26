"""Basic class to define a variable distribution."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import scipy
import numpy

EPS = 1e-12


class Distribution(ABC):
    """Abstract class to define a variable distribution.

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

    # TODO should we forbid worst > best

    __slots__ = ("__wearkref__", "_best", "_pbest", "_pworst", "_worst")

    def __init__(
        self,
        worst: float,
        best: float,
        pworst: Optional[float] = 0.15,
        pbest: Optional[float] = 0.15,
    ):
        self._worst = worst
        self._best = best
        # Need to initiate with EPS to be sure to fulfill pworst + pbest < 1.
        # We don't initialise to 0. otherwise fitting distribution for unbounded
        # one will fail (like the normal distribution)
        self._pworst = EPS
        self._pbest = EPS

        self.pworst = pworst
        self.pbest = pbest

    def __json__(self) -> Dict[str, Any]:
        """Serialize the distribution object.

        Returns
        -------
        Dict[str, Any]
            JSONable dictionary describing the distribution.
        """
        return {
            "worst": self.worst,
            "pworst": self.pworst,
            "best": self.best,
            "pbest": self.pbest,
        }

    @abstractmethod
    def _set_distribution(self) -> None:
        """Set the probability distribution according the parameters."""
        pass

    @property
    def worst(self) -> float:
        """float: The worst possible value of the variable.
        
        It is defined as an absolute value. It has a physical meaning, i.e. it
        can be numerically higher than the best value.
        The probability to meet the worst value is given by the `pworst` property.
        """
        return self._worst

    @worst.setter
    def worst(self, value):
        self._worst = value
        self._set_distribution()

    @property
    def pworst(self) -> float:
        """float: The worst value probability.
        
        It is the probability that the variable will be lower (if worst<best) or higher
        (if worst>best) than the worst value.
        """
        return self._pworst

    @pworst.setter
    def pworst(self, value: float):
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"Worst probability does not verify 0 <= {value} <= 1."
            )
        self._pworst = value
        self._set_distribution()

    @property
    def best(self) -> float:
        """float : The best possible value of the variable.
        
        It is defined as an absolute value. It has a physical meaning, i.e. it can
        be numerically lower than the worst value.
        The probability to meet the best value is given by the `pbest` property.
        """
        return self._best

    @best.setter
    def best(self, value: float):
        self._best = value
        self._set_distribution()

    @property
    def pbest(self) -> float:
        """float: The best value probability.
        
        It is the probability that the variable will be higher (if worst<best) or lower
        (if worst>best) than the best value.
        """
        return self._pbest

    @pbest.setter
    def pbest(self, value: float):
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"Best probability does not verify 0 <= {value} <= 1."
            )
        self._pbest = value
        self._set_distribution()

    @abstractmethod
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
        pass
