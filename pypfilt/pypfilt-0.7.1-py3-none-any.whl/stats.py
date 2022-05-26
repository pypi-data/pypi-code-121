"""Weighted quantiles, credible intervals, and other statistics."""

import numpy as np


def cov_wt(x, wt, cor=False):
    r"""Estimate the weighted covariance or correlation matrix.

    Equivalent to ``cov.wt(x, wt, cor, center=TRUE, method="unbiased")`` as
    provided by the ``stats`` package for R.

    :param x: A 2-D array; columns represent variables and rows represent
        observations.
    :param wt: A 1-D array of observation weights.
    :param cor: Whether to return a correlation matrix instead of a covariance
        matrix.

    :return: The covariance matrix (if ``cor=False``) or the correlation
        matrix (if ``cor=True``).
    """

    if x.ndim != 2:
        raise ValueError("x has dimension {} != 2".format(x.ndim))

    if wt.ndim != 1:
        raise ValueError("weights have dimension {} != 1".format(wt.ndim))

    if wt.shape[0] != x.shape[0]:
        raise ValueError("{} observations but {} weights".format(x.shape[0],
                                                                 wt.shape[0]))

    if any(wt < 0):
        raise ValueError("negative weight(s) found")

    with np.errstate(divide='raise'):
        cov = np.cov(x.T, aweights=wt)

    if cor:
        # Convert the covariance matrix into a correlation matrix.
        sd = np.array([np.sqrt(np.diag(cov))])
        sd_t = np.transpose(sd)
        return np.atleast_2d(cov / sd / sd_t)
    else:
        return np.atleast_2d(cov)


def avg_var_wt(x, weights, biased=True):
    """
    Return the weighted average and variance (based on a Stack Overflow
    `answer <http://stackoverflow.com/a/2415343>`_).

    :param x: A 1-D array of values.
    :param weights: A 1-D array of **normalised** weights.
    :param biased: Use a biased variance estimator.

    :return: A tuple that contains the weighted average and weighted variance.

    :raises ValueError: if ``x`` or ``weights`` are not one-dimensional, or if
        ``x`` and ``weights`` have different dimensions.
    """
    if len(x.shape) != 1:
        message = 'x is not 1D and has shape {}'
        raise ValueError(message.format(x.shape))
    if len(weights.shape) != 1:
        message = 'weights is not 1D and has shape {}'
        raise ValueError(message.format(weights.shape))
    if x.shape != weights.shape:
        message = 'x and weights have different shapes {} and {}'
        raise ValueError(message.format(x.shape, weights.shape))

    average = np.average(x, weights=weights)
    # Fast and numerically precise biased estimator.
    variance = np.average((x - average) ** 2, weights=weights)
    if not biased:
        # Use an unbiased estimator for the population variance.
        variance /= (1 - np.sum(weights ** 2))
    return (average, variance)


def qtl_wt(x, weights, probs):
    """Equivalent to ``wtd.quantile(x, weights, probs, normwt=TRUE)`` as
    provided by the `Hmisc <http://cran.r-project.org/web/packages/Hmisc/>`_
    package for `R <http://www.r-project.org/>`_.

    :param x: A 1-D array of values.
    :param weights: A 1-D array of weights.
    :param probs: The quantile(s) to compute.

    :return: The array of weighted quantiles.

    :raises ValueError: if ``x`` or ``weights`` are not one-dimensional, or if
        ``x`` and ``weights`` have different dimensions.
    """

    if len(x.shape) != 1:
        message = 'x is not 1D and has shape {}'
        raise ValueError(message.format(x.shape))
    if len(weights.shape) != 1:
        message = 'weights is not 1D and has shape {}'
        raise ValueError(message.format(weights.shape))
    if x.shape != weights.shape:
        message = 'x and weights have different shapes {} and {}'
        raise ValueError(message.format(x.shape, weights.shape))

    if any(weights == 0):
        # Note: weights of zero can arise if a particle is deemed sufficiently
        # unlikely given the recent observations and resampling has not (yet)
        # been performed.
        mask = weights > 0
        weights = weights[mask]
        x = x[mask]

    # Normalise the weights.
    n = len(x)
    weights = weights * float(n) / np.sum(weights)

    # Sort x and the weights.
    i = np.argsort(x)
    x = x[i]
    weights = weights[i]

    # Check for duplicates, which must be summed together.
    if any(np.diff(x) == 0):
        unique_xs = np.unique(x)
        weights = [sum(weights[v == x]) for v in unique_xs]
        x = unique_xs

    # Locate the probabilities over the *continuous* interval [0, n - 1].
    locns = probs * np.array(n - 1)
    cum_wts = np.cumsum(weights) - 1

    def qtl_of(ix, locn):
        low = max(np.floor(locn), 0)
        high = min(low + 1, n - 1)
        frac = locn % 1
        ix_low = next((ix for ix, x in enumerate(cum_wts) if x >= low), -1)
        ix_high = next((ix for ix, x in enumerate(cum_wts) if x >= high), -1)
        return (1 - frac) * x[ix_low] + frac * x[ix_high]

    return [qtl_of(ix, locn) for (ix, locn) in enumerate(locns)]


def cred_wt(x, weights, creds):
    """Calculate weighted credible intervals.

    :param x: A 1-D array of values.
    :param weights: A 1-D array of weights.
    :param creds: The credible interval(s) to compute (``0..100``, where ``0``
        represents the median and ``100`` the entire range).
    :type creds: List(int)

    :return: A dictionary that maps credible intervals to the lower and upper
        interval bounds.

    :raises ValueError: if ``x`` or ``weights`` are not one-dimensional, or if
        ``x`` and ``weights`` have different dimensions.
    """
    if len(x.shape) != 1:
        message = 'x is not 1D and has shape {}'
        raise ValueError(message.format(x.shape))
    if len(weights.shape) != 1:
        message = 'weights is not 1D and has shape {}'
        raise ValueError(message.format(weights.shape))
    if x.shape != weights.shape:
        message = 'x and weights have different shapes {} and {}'
        raise ValueError(message.format(x.shape, weights.shape))

    creds = sorted(creds)
    median = creds[0] == 0
    if median:
        creds = creds[1:]
    probs = [[0.5 - cred / 200.0, 0.5 + cred / 200.0] for cred in creds]
    probs = [pr for pr_list in probs for pr in pr_list]
    if median:
        probs = [0.5] + probs
    qtls = qtl_wt(x, weights, probs)
    intervals = {}
    if median:
        intervals[0] = (qtls[0], qtls[0])
        qtls = qtls[1:]
    for cred in creds:
        intervals[cred] = (qtls[0], qtls[1])
        qtls = qtls[2:]
    return intervals
