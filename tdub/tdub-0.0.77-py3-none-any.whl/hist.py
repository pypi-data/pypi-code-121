"""A module to aid working with histograms."""

from __future__ import annotations

# stdlib
import logging
from typing import Tuple, Optional, Union, Iterable

# ext
import numpy as np

log = logging.getLogger(__name__)


class SystematicComparison:
    """Systematic template histogram comparison.

    Attributes
    ----------
    nominal : numpy.ndarray
        Nominal histogram bin counts.
    up : numpy.ndarray
        Up variation histogram bin counts.
    down : numpy.ndarray
        Down variation histogram bin counts.
    percent_diff_up : numpy.ndarray
        Percent difference between nominal and up varation.
    percent_diff_down : numpy.ndaray
        Percent difference between nominald and down variation.

    """

    def __init__(
        self,
        nominal: np.ndarray,
        up: np.ndarray,
        down: np.ndarray,
    ) -> None:
        """Class constructor."""
        self.nominal = nominal
        self.up = up
        self.down = down
        self.percent_diff_up = (up - nominal) / nominal * 100.0
        self.percent_diff_down = (down - nominal) / nominal * 100.0

    @property
    def percent_diff_min(self) -> float:
        """float: minimum for percent difference."""
        return float(np.amin([self.percent_diff_up, self.percent_diff_down]))

    @property
    def percent_diff_max(self) -> float:
        """float: maximum for percent difference."""
        return float(np.amax([self.percent_diff_up, self.percent_diff_down]))

    @property
    def template_max(self) -> float:
        """float: maximum height of a variation."""
        return float(np.amax(np.concatenate([self.up, self.down])))

    @staticmethod
    def one_sided(nominal: np.ndarray, up: np.ndarray) -> SystematicComparison:
        """Generate components of a systematic comparion plot.

        Parameters
        ----------
        nominal : numpy.ndarray
            Histogram bin counts for the nominal template.
        up : numpy.ndarray
            Histogram bin counts for the "up" variation.

        Returns
        -------
        SystematicComparison
            The complete description of the comparison

        """
        diffs = nominal - up
        down = nominal + diffs
        return SystematicComparison(nominal, up, down)


def bin_centers(bin_edges: np.ndarray) -> np.ndarray:
    """Get bin centers given bin edges.

    Parameters
    ----------
    bin_edges : numpy.ndarray
       edges defining binning

    Returns
    -------
    numpy.ndarray
       the centers associated with the edges

    Examples
    --------
    >>> import numpy as np
    >>> from tdub.hist import bin_centers
    >>> bin_edges = np.linspace(25, 225, 11)
    >>> centers = bin_centers(bin_edges)
    >>> bin_edges
    array([ 25.,  45.,  65.,  85., 105., 125., 145., 165., 185., 205., 225.])
    >>> centers
    array([ 35.,  55.,  75.,  95., 115., 135., 155., 175., 195., 215.])

    """
    return (bin_edges[1:] + bin_edges[:-1]) * 0.5


def to_uniform_bins(bin_edges: np.ndarray):
    """Convert a set of variable width bins to arbitrary uniform bins.

    This will create a set of bin edges such that the bin centers are
    at whole numbers, i.e. 5 variable width bins will return an array
    from 0.5 to 5.5: [0.5, 1.5, 2.5, 3.5, 4.5, 5.5].

    Parameters
    ----------
    bin_edges : numpy.ndarray
        Array of bin edges.

    Returns
    -------
    numpy.ndarray
        The new set of uniform bins

    Examples
    --------
    >>> import numpy as np
    >>> from tdub.hist import to_uniform_bins
    >>> var_width = [0, 1, 3, 7, 15]
    >>> to_uniform_bins(var_width)
    array([0.5, 1.5, 2.5, 3.5, 4.5])

    """
    return np.arange(0.5, len(bin_edges) + 0.5, dtype=np.float64)


def edges_and_centers(
    bins: int | Iterable, range: tuple[float, float] | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Create arrays for edges and bin centers.

    Parameters
    ----------
    bins : int or sequence of scalers
       the number of bins or sequence representing bin edges
    range : tuple(float, float), optional
       the minimum and maximum defining the bin range (used if bins is integral)

    Returns
    -------
    :py:obj:`numpy.ndarray`
       the bin edges
    :py:obj:`numpy.ndarray`
       the bin centers

    Examples
    --------
    from bin multiplicity and a range

    >>> from tdub.hist import edges_and_centers
    >>> edges, centers = edges_and_centers(bins=20, range=(25, 225))

    from pre-existing edges

    >>> edges, centers = edges_and_centers(np.linspace(0, 10, 21))

    """
    if isinstance(bins, int):
        if range is None:
            raise ValueError("for integral bins we require the range argument")
        edges = np.linspace(range[0], range[1], bins + 1)
    else:
        edges = np.asarray(bins)
        if not np.all(edges[1:] >= edges[:-1]):
            raise ValueError("bins edges must monotonically increase")
    centers = bin_centers(edges)
    return edges, centers
