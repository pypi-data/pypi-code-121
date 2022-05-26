"""Module with some mathematical utilities."""

from __future__ import annotations

# stdlib
from typing import Tuple
import math

# external
import numpy as np
import scipy.special


def kolmogorov_prob(z: float) -> float:
    """Calculate the Kolmogorov distribution function.

    See ROOT's implementation in TMath_ (TMath::KolmogorovProb).

    .. _TMath: https://root.cern.ch/doc/master/namespaceTMath.html

    Parameters
    ----------
    z : float
       the value to test

    Returns
    -------
    float
       the probability that the test statistic exceeds :math:`z`
       (assuming the null hypothesis).

    Examples
    --------
    >>> from tdub.math import kolmogorov_prob
    >>> kolmogorov_prob(1.13)
    0.15549781841748692

    """
    w = 2.50662827
    # c1 - -pi**2/8, c2 = 9*c1, c3 = 25*c1
    c1 = -1.2337005501361697
    c2 = -11.103304951225528
    c3 = -30.842513753404244
    u = abs(z)
    if u < 0.2:
        return 1.0
    elif u < 0.755:
        v = 1.0 / (u * u)
        return float(
            1 - w * (math.exp(c1 * v) + math.exp(c2 * v) + math.exp(c3 * v)) / u
        )
    elif u < 6.8116:
        fj = np.array([-2, -8, -18, -32], dtype=np.float64)
        r = np.zeros((4,), dtype=np.float64)
        v = u * u
        maxj = max(1.0, round(3.0 / u))
        for j in range(int(maxj)):
            r[j] = math.exp(fj[j] * v)
        return float(2 * (r[0] - r[1] + r[2] - r[3]))
    else:
        return float(0.0)


def ks_twosample_binned(
    hist1: np.ndarray, hist2: np.ndarray, err1: np.ndarray, err2: np.ndarray
) -> tuple[float, float]:
    """Calculate KS statistic and p-value for two binned distributions.

    See ROOT's implementation in TH1_ (TH1::KolmogorovTest).

    .. _TH1: https://root.cern.ch/doc/master/classTH1.html

    Parameters
    ----------
    hist1 : numpy.ndarray
       the histogram counts for the first distribution
    hist2 : numpy.ndarray
       the histogram counts for the second distribution
    err1 : numpy.ndarray
       the error on the histogram counts for the first distribution
    err2 : numpy.ndarray
       the error on the histogram counts for the second distribution

    Returns
    -------
    (float, float)
       first: the test-statistic; second: the probability of the test
       (much less than 1 means distributions are incompatible)

    Examples
    --------
    >>> import pygram11
    >>> from tdub.math import ks_twosample_binned
    >>> data1, data2, w1, w2 = some_function_to_get_data()
    >>> h1, err1 = pygram11.histogram(data1, weights=w1, bins=40, range=(-3, 3))
    >>> h2, err2 = pygram11.histogram(data2, weights=w2, bins=40, range=(-3, 3))
    >>> kst, ksp = ks_twosample_binned(h1, h2, err1, err2)

    """
    sum1 = np.sum(hist1)
    sum2 = np.sum(hist2)
    w1 = np.sum(err1 * err1)
    w2 = np.sum(err2 * err2)
    esum1 = sum1 * sum1 / w1
    esum2 = sum2 * sum2 / w2
    s1 = 1 / sum1
    s2 = 1 / sum2
    rsum1 = s1 * hist1
    rsum2 = s2 * hist2
    dfmax = float(np.max(np.abs(rsum1 - rsum2)))
    z = float(dfmax * math.sqrt(esum1 * esum2 / (esum1 + esum2)))
    return dfmax, kolmogorov_prob(z)


def chisquared_cdf_c(chi2: float, ndf: float) -> float:
    r"""Calculate :math:`\chi^2` probability from the value and NDF.

    See ROOT's ``TMath::Prob`` & ``ROOT::Math::chisquared_cdf_c``.
    Quoting the ROOT documentation:

    Computation of the probability for a certain :math:`\chi^2` and
    number of degrees of freedom (ndf). Calculations are based on the
    incomplete gamma function :math:`P(a,x)`, where
    :math:`a=\mathrm{ndf}/2` and :math:`x=\chi^2/2`.

    :math:`P(a,x)` represents the probability that the observed
    :math:`\chi^2` for a correct model should be less than the value
    :math:`\chi^2`. The returned probability corresponds to
    :math:`1-P(a,x)`, which denotes the probability that an observed
    :math:`\chi^2` exceeds the value :math:`\chi^2` by chance, even
    for a correct model.

    Parameters
    ----------
    chi2 : float
       the :math:`\chi^2` value
    ndf : float
       the degrees of freedom

    Returns
    -------
    float
       the :math:`\chi^2` probability

    """
    return scipy.special.gammaincc(0.5 * ndf, 0.5 * chi2)


def chisquared_test(
    h1: np.ndarray,
    err1: np.ndarray,
    h2: np.ndarray,
    err2: np.ndarray,
) -> tuple[float, float, float]:
    r"""Perform :math:`\chi^2` test on two histograms.

    Parameters
    ----------
    h1 : :py:obj:`numpy.ndarray`
       the first histogram bin contents
    h2 : :py:obj:`numpy.ndarray`
       the second histogram bin contents
    err1 : :py:obj:`numpy.ndarray`
       the first histogram bin errors
    err2 : :py:obj:`numpy.ndarray`
       the second histogram bin errors

    Returns
    -------
    (float, int, float)
       the :math:`\chi^2` test value, the degrees of freedom, and the probability

    """
    # remove 0 bin heights
    badh1 = h1 * h1 == 0
    badh2 = h2 * h2 == 0
    good_bins = np.invert(np.logical_or(badh1, badh2))
    histo1 = h1[good_bins]
    histo2 = h2[good_bins]
    error1 = err1[good_bins]
    error2 = err2[good_bins]

    # degrees of freedom
    nbins = histo1.shape[0]
    ndf = nbins - 1

    # sums
    sum1 = np.sum(histo1)
    sum2 = np.sum(histo2)
    sumw1 = np.sum(error1 * error1)
    sumw2 = np.sum(error2 * error2)

    # chi2 calculation
    error1sq = error1 * error1
    error2sq = error2 * error2
    sigma = sum1 * sum2 * error2sq + sum2 * sum2 * error1sq
    delta = sum2 * histo1 - sum1 * histo2
    chi2 = np.sum(delta * delta / sigma)

    return (chi2, ndf, chisquared_cdf_c(chi2, ndf))
