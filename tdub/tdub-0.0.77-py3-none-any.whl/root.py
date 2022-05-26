"""Module to work with ROOT-like objects."""

from __future__ import annotations

# external
from uproot.model import Model as ROOTModel
from uproot.behaviors.TH1 import Histogram as ROOTHistogram
import numpy as np

# tdub
from tdub.hist import bin_centers


class TGraphAsymmErrors:
    """Wrapper around uproot's interpretation of ROOT's TGraphAsymmErrors.

    Parameters
    ----------
    root_object : uproot.model.Model
        Object from reading ROOT file with uproot.

    """

    def __init__(self, root_object: ROOTModel) -> None:
        """Initialize from the ROOT object."""
        self._root_object = root_object
        self._xlo = self._root_object.member("fEXlow")
        self._xhi = self._root_object.member("fEXhigh")
        self._ylo = self._root_object.member("fEYlow")
        self._yhi = self._root_object.member("fEYhigh")

    @property
    def xlo(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: X-axis low errors."""
        return self._xlo

    @property
    def xhi(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: X-axis high errors."""
        return self._xhi

    @property
    def ylo(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Y-axis low errors."""
        return self._ylo

    @property
    def yhi(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Y-axis high errors."""
        return self._yhi


class TH1:
    """Wrapper around uproot's interpretation of ROOT's TH1.

    This class interprets the histogram in a way that *ignores* under
    and overflow bins. We expect the treatment of those values to
    already be accounted for.

    Parameters
    ----------
    root_object : uproot.behaviors.TH1.Histogram
        Object from reading ROOT file with uproot.

    """

    def __init__(self, root_object: ROOTHistogram) -> None:
        """Initialize from the ROOT object."""
        self._root_object = root_object
        self._counts = self._root_object.values(flow=False)
        self._errors = self._root_object.errors(flow=False)
        self._edges = self._root_object.axis(0).edges(flow=False)

    @property
    def counts(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Histogram bin counts."""
        return self._counts

    @property
    def errors(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Histogram bin errors."""
        return self._errors

    @property
    def edges(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Histogram bin edges."""
        return self._edges

    @property
    def centers(self) -> np.ndarray:
        """:py:obj:`numpy.ndarray`: Histogram bin centers."""
        return bin_centers(self.edges)

    @property
    def bin_width(self) -> float:
        """float: Width of a bin."""
        return self._edges[1] - self._edges[0]
