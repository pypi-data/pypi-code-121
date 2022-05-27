#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Functions for handling and assessing IMFs.

Supporting tools for IMFs estimated using the emd.sift submodule.

"""

import logging

import dcor
import numpy as np
import pandas as pd
from scipy import signal, stats
from tabulate import tabulate

from ._sift_core import (get_padded_extrema, interp_envelope,
                         zero_crossing_count)
from .support import ensure_2d, ensure_equal_dims

# Housekeeping for logging
logger = logging.getLogger(__name__)


def amplitude_normalise(X, thresh=1e-10, clip=False, interp_method='pchip',
                        max_iters=3):
    """Normalise the amplitude envelope of an IMF to be 1.

    Multiple runs of normalisation are carried out until the desired threshold
    is reached. This uses the method described as part of the AM-FM transform
    [1]_

    Parameters
    ----------
    X : ndarray
        Input array of IMFs to be normalised
    thresh : float
         Threshold for stopping normalisation (Default value = 1e-10)
    clip : bool
         Whether to clip the output between -1 and 1 (Default value = False)
    interp_method : {'pchip','mono_pchip','splrep'}
         Method used to interpolate envelopes (Default value = 'pchip')
    max_iters : int
        Maximum number of iterations of normalisation to perform

    Returns
    -------
    ndarray
        Amplitude normalised IMFs

    References
    ----------
    .. [1] Huang, N. E., Wu, Z., Long, S. R., Arnold, K. C., Chen, X., & Blank,
       K. (2009). On Instantaneous Frequency. Advances in Adaptive Data Analysis,
       1(2), 177–229. https://doi.org/10.1142/s1793536909000096

    """
    logger.info('STARTED: Amplitude-Normalise')

    if X.ndim == 2:
        logger.debug('Normalising {0} samples across {1} IMFs'.format(*X.shape))
    else:
        logger.debug('Normalising {0} samples across {1} first-level and {2} second-level IMFs'.format(*X.shape))
    logger.debug('Using {0} interpolation with threshold of {1} and max_iters {2}'.format(interp_method,
                                                                                          thresh,
                                                                                          max_iters))

    # Don't normalise in place
    X = X.copy()

    orig_dim = X.ndim
    if X.ndim == 2:
        X = X[:, :, None]

    extrema_opts = {'method': 'numpypad'}  # Rilling doesn't make sense for combined extrema
    for iimf in range(X.shape[1]):
        for jimf in range(X.shape[2]):

            env = interp_envelope(X[:, iimf, jimf], mode='combined',
                                  interp_method=interp_method,
                                  extrema_opts=extrema_opts)

            if env is None:
                continue_norm = False
            else:
                continue_norm = True

            iters = 0
            while continue_norm and (iters < max_iters):
                iters += 1

                X[:, iimf, jimf] = X[:, iimf, jimf] / env
                env = interp_envelope(X[:, iimf, jimf], mode='combined',
                                      interp_method=interp_method,
                                      extrema_opts=extrema_opts)

                if env is None:
                    continue_norm = False
                else:
                    continue_norm = True

                    iter_val = np.abs(env.sum() - env.shape[0])
                    if iter_val < thresh:
                        continue_norm = False

                        logger.info('Normalise of IMF-{0}-{1} complete in {2} iters (val={3})'.format(iimf,
                                                                                                      jimf,
                                                                                                      iters,
                                                                                                      iter_val))

    if clip:
        logger.debug('Clipping signal to -1:1 range')
        # Make absolutely sure nothing daft is happening
        X = np.clip(X, -1, 1)

    if orig_dim == 2:
        X = X[:, :, 0]

    logger.info('COMPLETED: Amplitude-Normalise')
    return X


def wrap_phase(IP, ncycles=1, mode='2pi'):
    """Wrap a phase time-course.

    Parameters
    ----------
    IP : ndarray
        Input array of unwrapped phase values
    ncycles : int
         Number of cycles per wrap (Default value = 1)
    mode : {'2pi','-pi2pi'}
         Flag to indicate the values to wrap phase within (Default value = '2pi')

    Returns
    -------
    ndarray
        Wrapped phase time-course

    Notes
    -----
    Non-finite phase values are not changed by this operation. eg np.nans in
    the input will be present and unchanged in the output.

    """
    if (ncycles < 1) or (np.can_cast(ncycles, int) is False):
        raise ValueError("'ncycles' must be a positive integer value - input was '{0}'".format(ncycles))

    if mode not in ['2pi', '-pi2pi']:
        raise ValueError("Invalid mode value")

    # Wrapping length
    phase_len = ncycles * 2 * np.pi

    # Compute wrapped phases using np.ufunc where and out to avoid processing non-finite values.
    if mode == '2pi':
        phases = np.remainder(IP, phase_len, where=np.isfinite(IP), out=IP)
    elif mode == '-pi2pi':
        phases = np.remainder(IP + np.pi * ncycles, phase_len - np.pi * ncycles, where=np.isfinite(IP), out=IP)

    return phases

# --------------------------
# Assess IMF 'quality'


def is_imf(imf, avg_tol=5e-2, envelope_opts=None, extrema_opts=None):
    """Determine whether a signal is a 'true IMF'.

    Two criteria are tested. Firstly, the number of extrema and number of
    zero-crossings must differ by zero or one. Secondly,the mean of the upper
    and lower envelopes must be within a tolerance of zero.

    Parameters
    ----------
    imf : 2d array
        Array of signals to check [nsamples x nimfs]
    avg_tol : float
        Tolerance of acceptance for criterion two. The sum-square of the mean
        of the upper and lower envelope must be below avg_tol of the sum-square
        of the signal being checked.
    envelope_opts : dict
        Dictionary of envelope estimation options, must be identical to options
        used when estimating IMFs.
    extrema_opts : dict
        Dictionary of extrema estimation options, must be identical to options
        used when estimating IMFs.

    Returns
    -------
    array [2 x nimfs]
        Boolean array indicating whether each IMF passed each test.

    Notes
    -----
    These are VERY strict criteria to apply to real data. The tests may
    indicate a fail if the sift doesn't coverge well in a short segment of the
    signal when the majority of the IMF is well behaved.

    The tests are only valid if called with identical envelope_opts and
    extrema_opts as were used in the sift estimation.

    """
    imf = ensure_2d([imf], ['imf'], 'is_imf')

    if envelope_opts is None:
        envelope_opts = {}

    checks = np.zeros((imf.shape[1], 2), dtype=bool)

    for ii in range(imf.shape[1]):

        # Extrema and zero-crossings differ by <=1
        num_zc = zero_crossing_count(imf[:, ii])
        num_ext = signal.find_peaks(imf[:, ii])[0].shape[0] + signal.find_peaks(-imf[:, ii])[0].shape[0]

        # Mean of envelopes should be zero
        upper = interp_envelope(imf[:, ii], mode='upper',
                                **envelope_opts, extrema_opts=extrema_opts)
        lower = interp_envelope(imf[:, ii], mode='lower',
                                **envelope_opts, extrema_opts=extrema_opts)

        # If upper or lower are None we should stop sifting altogether
        if upper is None or lower is None:
            logger.debug('IMF-{0} False - no peaks detected')
            continue

        # Find local mean
        avg = np.mean([upper, lower], axis=0)[:, None]
        avg_sum = np.sum(np.abs(avg))
        imf_sum = np.sum(np.abs(imf[:, ii]))
        diff = avg_sum / imf_sum

        # TODO: Could probably add a Rilling-like criterion here. ie - is_imf
        # is true if (1-alpha)% of time is within some thresh
        checks[ii, 0] = np.abs(np.diff((num_zc, num_ext))) <= 1
        checks[ii, 1] = diff < avg_tol

        msg = 'IMF-{0} {1} - {2} extrema and {3} zero-crossings. Avg of envelopes is {4:.4}/{5:.4} ({6:.4}%)'
        msg = msg.format(ii, np.alltrue(checks[ii, :]), num_ext, num_zc, avg_sum, imf_sum, 100*diff)
        logger.debug(msg)

    return checks


def check_decreasing_freq(IF, mode='proportion'):
    """Similar to method 1 in http://dx.doi.org/10.11601/ijates.v5i1.139.

    Parameters
    ----------
    IF : ndarray
        nsamples x nimfs array of instantaneous frequency values
    mode : {'proportion', 'sum', 'full'}
        Flag indicating whether the proportion of overlapping samples
        ('proportion', default), the total number of overlapping samples
        ('sum') or the full nsamples x nimfs-1 array ('full') will be returned

    Returns
    -------
    metric : ndarray
        nimfs-1 length vector containing the proportion of samples in which the
        IF of adjacent pairs of IMFs overlapped. This is returned per-sample if
        input squash_time is None.

    """
    # Find frequency differences
    dIF = np.diff(IF, axis=1)

    metric = dIF > 0

    if mode == 'sum' or mode == 'proportion':
        metric = np.nansum(dIF > 0, axis=0)

    if mode == 'proportion':
        metric = metric / dIF.shape[0]

    return metric


def est_orthogonality(imf):
    """Compute the index of orthogonality from a set of IMFs.

    Method is described in equation 6.5 of Huang et al (1998) [1]_.

    Parameters
    ----------
    imf : ndarray
        Input array of IMFs

    Returns
    -------
    ndarray
        Matrix of orthogonality values [nimfs x nimfs]

    References
    ----------
    .. [1] Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng,
       Q., … Liu, H. H. (1998). The empirical mode decomposition and the Hilbert
       spectrum for nonlinear and non-stationary time series analysis. Proceedings
       of the Royal Society of London. Series A: Mathematical, Physical and
       Engineering Sciences, 454(1971), 903–995.
       https://doi.org/10.1098/rspa.1998.0193

    """
    ortho = np.ones((imf.shape[1], imf.shape[1])) * np.nan

    for ii in range(imf.shape[1]):
        for jj in range(imf.shape[1]):
            ortho[ii, jj] = np.abs(np.sum(imf[:, ii] * imf[:, jj])) \
                / (np.sqrt(np.sum(imf[:, jj] * imf[:, jj])) * np.sqrt(np.sum(imf[:, ii] * imf[:, ii])))

    return ortho


def pseudo_mode_mixing_index(imf):
    """Compute the Pseudo Mode Mixing Index from a set of IMFs.

    Section VI in Wang et al (2018) _[1]

    Parameters
    ----------
    imf : ndarray
        Input array of IMFs

    Returns
    -------
    ndarray
        Vector of PSMI [nimfs,]

    References
    ----------
    .. [1] Wang, Y.-H., Hu, K., & Lo, M.-T. (2018). Uniform Phase Empirical
       Mode Decomposition: An Optimal Hybridization of Masking Signal and Ensemble
       Approaches. IEEE Access, 6, 34819–34833.
       https://doi.org/10.1109/access.2018.2847634

    """
    psmi = np.zeros((imf.shape[1],))

    for ii in range(imf.shape[1]-1):

        num = np.dot(imf[:, ii], imf[:, ii+1])
        denom = np.linalg.norm(imf[:, ii])**2 + np.linalg.norm(imf[:, ii+1])**2 + 1e-8

        psmi[ii] = np.max([num / denom, 0])

    return psmi


def assess_harmonic_criteria(IP, IF, IA, num_segments=None, base_imf=None, print_result=True):
    """Assess IMFs for potential harmonic relationships.

    This function implements tests for the criteria defining when signals can
    be considered 'harmonically related' as introduced in [1]_. Broadly,
    harmonically related signals are defined as having an integer frequency
    ratio, constant phase relationship, and a well-defined joint instantaneous
    frequency

    Three criteria are assessed by splitting the time-series into approximately
    equally sized segments and computing metrics within each segment.

    Parameters
    ----------
    IP, IF, IA : ndarray of equal shape
        Instantaneous Phase, Frequency and Amplitude estimates for a set of
        IMFs. These are typically the outputs from emd.spectra.frequency_transform.
    num_segments : int
        Number of segments to split the time series into to enable statistical assessment.
    base_inf : int
        Index of IMF to be considered the potential 'fundamental' oscillation.
    print_result : bool
        Flag indicating whether to print a summary table of results.

    Returns
    -------
    df
        Pandas DataFrame containing a range of summary and comparison metrics.

    Notes
    -----
    In detail, this function compares each IMF to a 'base' IMF to see if it can
    be considered a potential harmonic. Each pair of IMFs are assessed for:

    1) An integer frequency ratio. The distribution of frequency ratios across
    segments is compared to its closest integer value with a 1-sample t-test

    2) Consistent phase relationship. The instantaneous phase time-courses are
    assessed for temporal dependence using a Distance Correlation t-statistic.

    3) The af ratio is less than 1. The product of the amplitude ratio and
    frequency ratio of the two IMFs should be less than 1 according to a
    1-sided 1-sample t-test.

    References
    ----------
    .. [1] Fabus, M. S., Woolrich, M. W., Warnaby, C. W., & Quinn, A. J.
           (2021). Understanding Harmonic Structures Through Instantaneous Frequency.
           Cold Spring Harbor Laboratory. https://doi.org/10.1101/2021.12.21.473676

    """
    # Housekeeping
    IP, IF, IA = ensure_2d([IP, IF, IA], ['IP', 'IF', 'IA'], 'assess_harmonic_criteria')
    ensure_equal_dims((IP, IF, IA), ('IP', 'IF', 'IA'), 'assess_harmonic_criteria')

    if base_imf is None:
        base_imf = IP.shape[1] - 1

    if num_segments is None:
        num_segments = 20

    IPs = np.array_split(IP, num_segments, axis=0)
    IPs = np.concatenate([xx[np.newaxis, ...] for xx in IPs], axis=0)
    IFs = np.array_split(IF, num_segments, axis=0)
    IFs = np.concatenate([xx[np.newaxis, ...] for xx in IFs], axis=0)
    IAs = np.array_split(IA, num_segments, axis=0)
    IAs = np.concatenate([xx[np.newaxis, ...] for xx in IAs], axis=0)

    IFms = np.mean(IFs, 1)
    IAms = np.mean(IAs, 1)

    fratios = np.zeros((base_imf, num_segments))
    a_s = np.zeros((base_imf, num_segments))
    afs = np.zeros((base_imf, num_segments))
    dcorrs = np.zeros((base_imf, num_segments))
    dcor_pvals = np.zeros((base_imf, 2))
    fratio_pvals = np.zeros(base_imf)
    af_pvals = np.zeros(base_imf)

    for ii in range(base_imf):
        # Freq ratios
        fratios[ii, :] = IFms[:, ii] / IFms[:, base_imf]
        # Amp ratio
        a_s[ii, :] = IAms[:, ii] / IAms[:, base_imf]
        # af value
        afs[ii, :] = a_s[ii, :] * fratios[ii, :]

        # Test 1: significant Phase-Phase Correlation
        dcorr = dcor.distance_correlation(IP[:, ii], IP[:, base_imf])
        p_dcor, _ = dcor.independence.distance_correlation_t_test(IP[:, ii], IP[:, base_imf])
        dcor_pvals[ii, :] = dcorr, p_dcor
        for jj in range(num_segments):
            dcorrs[ii, jj] = dcor.distance_correlation(IPs[jj, :, ii], IPs[jj, :, base_imf])

        # Test 2: frequency ratio not different from nearest integer
        ftarget = np.round(fratios[ii, :].mean())
        _, fratio_pvals[ii] = stats.ttest_1samp(fratios[ii, :], ftarget)
        # Test 3: af < 1
        _, af_pvals[ii] = stats.ttest_1samp(afs[ii, :], 1, alternative='less')

    info = {'InstFreq Mean': IFms.mean(axis=0)[:base_imf],
            'InstFreq StDev': IFms.std(axis=0)[:base_imf],
            'InstFreq Ratio': fratios.mean(axis=1),
            'Integer IF p-value': fratio_pvals,
            'InstAmp Mean': IAms.mean(axis=0)[:base_imf],
            'InstAmp StDev': IAms.std(axis=0)[:base_imf],
            'InstAmp Ratio': a_s.mean(axis=1),
            'af Value': afs.mean(axis=1),
            'af < 1 p-value': af_pvals,
            'DistCorr': dcor_pvals[:, 0],
            'DistCorr p-value': dcor_pvals[:, 1]}

    df = pd.DataFrame.from_dict(info)

    if print_result:
        tabs = []
        for ii in range(base_imf):
            tabs.append([f'IMF-{ii}',
                         df['DistCorr'][ii],
                         df['DistCorr p-value'][ii],
                         df['InstFreq Ratio'][ii],
                         df['Integer IF p-value'][ii],
                         df['af Value'][ii],
                         df['af < 1 p-value'][ii]])
        heads = ['IMF', 'Phase DistCorr', 'p-value', 'InstFreq Ratio', 'p-value', 'af Ratio', 'p-value']

        print(tabulate(tabs, headers=heads, tablefmt='orgtbl'))

    return df


def assess_joint_if(imf, freq_transform_args=None, return_mode='full'):
    """Assess whether two signals have a well formed joint instantaneous frequency.

    Parameters
    ----------
    imf : ndarray
        Array of intrinsic mode functions.
    freq_transform_args : {None, dict}
        Optional dictionary of keyword arguments to be passed to
        emd.spectra.frequency_transform
    return_mode : {'binary', 'full'}
        Whether to return the full joint instantaneous frequency or a binarised
        vector indicating samples that have positive joint instantaneous
        frequency.

    Returns
    -------
    joint_if : ndarray
        Array of joint instantaneous frequency values or binary values
        indicating whether the joint instantaneous frequency was less than
        zero.

    References
    ----------
    .. [1] Fabus, M. S., Woolrich, M. W., Warnaby, C. W., & Quinn, A. J.
           (2021). Understanding Harmonic Structures Through Instantaneous Frequency.
           Cold Spring Harbor Laboratory. https://doi.org/10.1101/2021.12.21.473676

    """
    # Import from spectra inside function to avoid circular imports. Strictly,
    # emd.spectra depends on emd.imftools but not the other way around
    from .spectra import frequency_transform

    # Housekeeping
    imf = ensure_2d([imf], ['imf'], 'assess_joint_if')

    inds = np.arange(1, imf.shape[1])
    step = -1

    freq_transform_args = {} if freq_transform_args is None else freq_transform_args

    joint_if = np.zeros_like(imf[:, :-1])

    for ii in range(len(inds)):

        jif = imf[:, inds[ii]] + imf[:, inds[ii]+step]
        IP, IF, IA = frequency_transform(jif, 1, 'hilbert', **freq_transform_args)

        joint_if[:, ii] = IF[:, 0]

    if return_mode == 'binary':
        joint_if = joint_if < 0

    return joint_if


# --------------------------
# Epoching


def find_extrema_locked_epochs(X, winsize, lock_to='peaks', percentile=None):
    """Define epochs around peaks or troughs within the data.

    Parameters
    ----------
    X : ndarray
        Input time-series
    winsize : int
        Width of window to extract around each extrema
    lock_to : {'max','min'}
         Flag to select peak or trough locking (Default value = 'max')
    percentile : float
         Optional flag to selection only the upper percentile of extrema by
         magnitude (Default value = None)

    Returns
    -------
    ndarray
        Array of start and end indices for epochs around extrema.

    """
    if lock_to not in ['peaks', 'troughs', 'combined']:
        raise ValueError("Invalid lock_to value")

    locs, pks = get_padded_extrema(X, pad_width=0, mode=lock_to)

    if percentile is not None:
        thresh = np.percentile(pks, percentile)
        locs = locs[pks > thresh]
        pks = pks[pks > thresh]

    winstep = int(winsize / 2)

    # Get all trials
    trls = np.r_[np.atleast_2d(locs - winstep), np.atleast_2d(locs + winstep)].T

    # Reject trials which start before 0
    inds = trls[:, 0] < 0
    trls = trls[inds == False, :]  # noqa: E712

    # Reject trials which end after X.shape[0]
    inds = trls[:, 1] > X.shape[0]
    trls = trls[inds == False, :]  # noqa: E712

    return trls


def apply_epochs(X, trls):
    """Apply a set of epochs to a continuous dataset.

    Parameters
    ----------
    X : ndarray
        Input dataset to be epoched
    trls : ndarray
        2D array of start and end indices for each epoch. The second dimension
        should be of len==2 and contain start and end indices in order.

    Returns
    -------
    ndarray
        Epoched time-series

    """
    Y = np.zeros((trls[0, 1] - trls[0, 0], X.shape[1], trls.shape[0]))
    for ii in np.arange(trls.shape[0]):

        Y[:, :, ii] = X[trls[ii, 0]:trls[ii, 1], :]

    return Y


# Circular statistics
#
# These functions are a work in progress and not currently tested.
# Mostly based on equations from wikipedia.
# https://en.wikipedia.org/wiki/Circular_mean
#
# Everything works in radians to match the instantaneous phase estimates.


def _radians_to_complex(IP, IA=None):
    """Convert phase in radians to circular/complex coordinates."""
    if IA is None:
        IA = np.ones_like(IP)
    ensure_equal_dims([IP, IA], ['IP', 'IA'], 'ip_to_complex')

    # Actual computation using exponential formula - could equivalently use the
    # sine/cosine form - computation time nearly identical
    # phi = np.cos(IP) + 1j * np.sin(IP)
    phi = IA * np.exp(1j * IP)

    return phi


def ip_mean_resultant_vector(IP, IA=None, axis=0):
    """Compute the mean resultant vector of a set of phase values."""
    if IA is None:
        IA = np.ones_like(IP)

    phi = _radians_to_complex(IP, IA=IA)

    return phi.mean(axis=axis)


def ip_circular_mean(IP, IA=None, axis=0):
    """Compute the circular mean of a set of phase values."""
    phi = ip_mean_resultant_vector(IP, IA=IA, axis=axis)

    return np.angle(phi)


def ip_circular_variance(IP, IA=None, axis=0):
    """Compute the circular variance of a set of phase values."""
    # https://en.wikipedia.org/wiki/Directional_statistics#Standard_deviation

    phi = ip_mean_resultant_vector(IP, IA=IA, axis=axis)

    return 1 - np.abs(phi)
