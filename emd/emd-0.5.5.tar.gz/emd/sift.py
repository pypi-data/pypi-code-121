#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Implementations of the sift algorithm for Empirical Mode Decomposition.

Main Routines:
  sift                    - The classic sift algorithm
  ensemble_sift           - Noise-assisted sift algorithm
  complete_ensemble_sift  - Adapeted noise-assisted sift algorithm
  mask_sift               - Sift with masks to separate very sparse or nonlinear components
  iterated_mask_sift      - Sift which automatically identifies optimal masks
  sift_second_layer       - Apply sift to amplitude envlope of a set of IMFs

Sift Helper Routines:
  get_next_imf
  get_next_imf_mask
  get_mask_freqs
  energy_difference
  energy_stop
  sd_stop
  rilling_stop
  fixed_stop

Sift Config:
  get_config
  SiftConfig

"""

import collections
import functools
import inspect
import logging
import sys

import numpy as np
import yaml

from ._sift_core import (_find_extrema, get_padded_extrema, interp_envelope,
                         zero_crossing_count)
from .logger import sift_logger, wrap_verbose
from .spectra import frequency_transform
from .support import (EMDSiftCovergeError, ensure_1d_with_singleton, ensure_2d,
                      ensure_equal_dims, run_parallel)

# Housekeeping for logging
logger = logging.getLogger(__name__)


##################################################################
# Basic SIFT

# Utilities

def get_next_imf(X, env_step_size=1, max_iters=1000, energy_thresh=50,
                 stop_method='sd', sd_thresh=.1, rilling_thresh=(0.05, 0.5, 0.05),
                 envelope_opts=None, extrema_opts=None):
    """Compute the next IMF from a data set.

    This is a helper function used within the more general sifting functions.

    Parameters
    ----------
    X : ndarray [nsamples x 1]
        1D input array containing the time-series data to be decomposed
    env_step_size : float
        Scaling of envelope prior to removal at each iteration of sift. The
        average of the upper and lower envelope is muliplied by this value
        before being subtracted from the data. Values should be between
        0 > x >= 1 (Default value = 1)
    max_iters : int > 0
        Maximum number of iterations to compute before throwing an error
    energy_thresh : float > 0
        Threshold for energy difference (in decibels) between IMF and residual
        to suggest stopping overall sift. (Default is None, recommended value is 50)
    stop_method : {'sd','rilling','fixed'}
        Flag indicating which metric to use to stop sifting and return an IMF.
    sd_thresh : float
        Used if 'stop_method' is 'sd'. The threshold at which the sift of each
        IMF will be stopped. (Default value = .1)
    rilling_thresh : tuple
        Used if 'stop_method' is 'rilling', needs to contain three values (sd1, sd2, alpha).
        An evaluation function (E) is defined by dividing the residual by the
        mode amplitude. The sift continues until E < sd1 for the fraction
        (1-alpha) of the data, and E < sd2 for the remainder.
        See section 3.2 of http://perso.ens-lyon.fr/patrick.flandrin/NSIP03.pdf

    Returns
    -------
    proto_imf : ndarray
        1D vector containing the next IMF extracted from X
    continue_flag : bool
        Boolean indicating whether the sift can be continued beyond this IMF

    Other Parameters
    ----------------
    envelope_opts : dict
        Optional dictionary of keyword arguments to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema

    See Also
    --------
    emd.sift.sift
    emd.sift.interp_envelope

    """
    X = ensure_1d_with_singleton([X], ['X'], 'get_next_imf')

    if envelope_opts is None:
        envelope_opts = {}

    proto_imf = X.copy()

    continue_imf = True
    continue_flag = True
    niters = 0
    while continue_imf:

        if stop_method != 'fixed':
            if niters == 3*max_iters//4:
                logger.debug('Sift reached {0} iterations, taking a long time to coverge'.format(niters))
            elif niters > max_iters:
                msg = 'Sift failed. No covergence after {0} iterations'.format(niters)
                raise EMDSiftCovergeError(msg)
        niters += 1

        upper, lower = interp_envelope(proto_imf, mode='both',
                                       **envelope_opts, extrema_opts=extrema_opts)

        # If upper or lower are None we should stop sifting altogether
        if upper is None or lower is None:
            continue_flag = False
            continue_imf = False
            logger.debug('Finishing sift: IMF has no extrema')
            continue

        # Find local mean
        avg = np.mean([upper, lower], axis=0)[:, None]

        # Remove local mean estimate from proto imf
        x1 = proto_imf - avg

        # Stop sifting if we pass threshold
        if stop_method == 'sd':
            # Cauchy criterion
            stop, _ = sd_stop(proto_imf, x1, sd=sd_thresh, niters=niters)
        elif stop_method == 'rilling':
            # Rilling et al 2003
            stop, _ = rilling_stop(upper, lower, niters=niters,
                                   sd1=rilling_thresh[0],
                                   sd2=rilling_thresh[1],
                                   tol=rilling_thresh[2])
        elif stop_method == 'energy':
            # Rato et al 2008
            # Compare energy of signal at start of sift with energy of envelope average
            stop, _ = energy_stop(X, avg, thresh=energy_thresh, niters=niters)
        elif stop_method == 'fixed':
            stop = fixed_stop(niters, max_iters)
        else:
            raise ValueError("stop_method '{0}' not recogised".format(stop_method))

        if stop:
            proto_imf = x1.copy()
            continue_imf = False
            continue

        proto_imf = proto_imf - (env_step_size*avg)

    if proto_imf.ndim == 1:
        proto_imf = proto_imf[:, None]

    return proto_imf, continue_flag


def _energy_difference(imf, residue):
    """Compute energy change in IMF during a sift.

    Parameters
    ----------
    imf : ndarray
        IMF to be evaluated
    residue : ndarray
        Remaining signal after IMF removal

    Returns
    -------
    float
        Energy difference in decibels

    Notes
    -----
    This function is used during emd.sift.energy_stop to implement the
    energy-difference sift-stopping method defined in section 3.2.4 of
    https://doi.org/10.1016/j.ymssp.2007.11.028

    """
    sumsqr = np.sum(imf**2)
    imf_energy = 20 * np.log10(sumsqr, where=sumsqr > 0)
    sumsqr = np.sum(residue ** 2)
    resid_energy = 20 * np.log10(sumsqr, where=sumsqr > 0)
    return imf_energy-resid_energy


def energy_stop(imf, residue, thresh=50, niters=None):
    """Compute energy change in IMF during a sift.

    The energy in the IMFs are compared to the energy at the start of sifting.
    The sift terminates once this ratio reaches a predefined threshold.

    Parameters
    ----------
    imf : ndarray
        IMF to be evaluated
    residue : ndarray
        Average of the upper and lower envelopes
    thresh : float
        Energy ratio threshold (default=50)
    niters : int
        Number of sift iterations currently completed

    Returns
    -------
    bool
        A flag indicating whether to stop siftingg
    float
        Energy difference in decibels

    Notes
    -----
    This function implements the energy-difference sift-stopping method defined
    in section 3.2.4 of https://doi.org/10.1016/j.ymssp.2007.11.028

    """
    diff = _energy_difference(imf, residue)
    stop = bool(diff > thresh)

    if stop:
        logger.debug('Sift stopped by Energy Ratio in {0} iters with difference of {1}dB'.format(niters, diff))
    else:
        logger.debug('Energy Ratio evaluated at iter {0} is : {1}dB'.format(niters, diff))

    return stop, diff


def sd_stop(proto_imf, prev_imf, sd=0.2, niters=None):
    """Compute the sd sift stopping metric.

    Parameters
    ----------
    proto_imf : ndarray
        A signal which may be an IMF
    prev_imf : ndarray
        The previously identified IMF
    sd : float
        The stopping threshold
    niters : int
        Number of sift iterations currently completed
    niters : int
        Number of sift iterations currently completed

    Returns
    -------
    bool
        A flag indicating whether to stop siftingg
    float
        The SD metric value

    """
    metric = np.sum((proto_imf - prev_imf)**2) / np.sum(proto_imf**2)

    stop = metric < sd

    if stop:
        logger.verbose('Sift stopped by SD-thresh in {0} iters with sd {1}'.format(niters, metric))
    else:
        logger.debug('SD-thresh stop metric evaluated at iter {0} is : {1}'.format(niters, metric))

    return stop, metric


def rilling_stop(upper_env, lower_env, sd1=0.05, sd2=0.5, tol=0.05, niters=None):
    """Compute the Rilling et al 2003 sift stopping metric.

    This metric tries to guarantee globally small fluctuations in the IMF mean
    while taking into account locally large excursions that may occur in noisy
    signals.

    Parameters
    ----------
    upper_env : ndarray
        The upper envelope of a proto-IMF
    lower_env : ndarray
        The lower envelope of a proto-IMF
    sd1 : float
        The maximum threshold for globally small differences from zero-mean
    sd2 : float
        The maximum threshold for locally large differences from zero-mean
    tol : float (0 < tol < 1)
        (1-tol) defines the proportion of time which may contain large deviations
        from zero-mean
    niters : int
        Number of sift iterations currently completed

    Returns
    -------
    bool
        A flag indicating whether to stop siftingg
    float
        The SD metric value

    Notes
    -----
    This method is described in section 3.2 of:
    Rilling, G., Flandrin, P., & Goncalves, P. (2003, June). On empirical mode
    decomposition and its algorithms. In IEEE-EURASIP workshop on nonlinear
    signal and image processing (Vol. 3, No. 3, pp. 8-11). NSIP-03, Grado (I).
    http://perso.ens-lyon.fr/patrick.flandrin/NSIP03.pdf

    """
    avg_env = (upper_env+lower_env)/2
    amp = np.abs(upper_env-lower_env)/2

    eval_metric = np.abs(avg_env)/amp

    metric = np.mean(eval_metric > sd1)
    continue1 = metric > tol
    continue2 = np.any(eval_metric > sd2)

    stop = (continue1 or continue2) == False  # noqa: E712

    if stop:
        logger.verbose('Sift stopped by Rilling-metric in {0} iters (val={1})'.format(niters, metric))
    else:
        logger.debug('Rilling stop metric evaluated at iter {0} is : {1}'.format(niters, metric))

    return stop, metric


def fixed_stop(niters, max_iters):
    """Compute the fixed-iteraiton sift stopping metric.

    Parameters
    ----------
    niters : int
        Number of sift iterations currently completed
    max_iters : int
        Maximum number of sift iterations to be completed

    Returns
    -------
    bool
        A flag indicating whether to stop siftingg

    """
    stop = bool(niters == max_iters)

    if stop:
        logger.debug('Sift stopped at fixed number of {0} iterations'.format(niters))

    return stop


def _nsamples_warn(N, max_imfs):
    if max_imfs is None:
        return
    if N < 2**(max_imfs+1):
        msg = 'Inputs samples ({0}) is small for specified max_imfs ({1})'
        msg += ' very likely that {2} or fewer imfs are returned'
        logger.warning(msg.format(N, max_imfs, np.floor(np.log2(N)).astype(int)-1))


# SIFT implementation

@wrap_verbose
@sift_logger('sift')
def sift(X, sift_thresh=1e-8, max_imfs=None, verbose=None,
         imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Compute Intrinsic Mode Functions from an input data vector.

    This function implements the original sift algorithm [1]_.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    sift_thresh : float
         The threshold at which the overall sifting process will stop. (Default value = 1e-8)
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = None)

    Returns
    -------
    imf: ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from the decomposition of X.

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_next_imf
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema
    verbose : {None,'CRITICAL','WARNING','INFO','DEBUG'}
        Option to override the EMD logger level for a call to this function.

    See Also
    --------
    emd.sift.get_next_imf
    emd.sift.get_config

    Notes
    -----
    The classic sift is computed by passing an input vector with all options
    left to default

    >>> imf = emd.sift.sift(x)

    The sift can be customised by passing additional options, here we only
    compute the first four IMFs.

    >>> imf = emd.sift.sift(x, max_imfs=4)

    More detailed options are passed as dictionaries which are passed to the
    relevant lower-level functions. For instance `imf_opts` are passed to
    `get_next_imf`.

    >>> imf_opts = {'env_step_size': 1/3, 'stop_method': 'rilling'}
    >>> imf = emd.sift.sift(x, max_imfs=4, imf_opts=imf_opts)

    A modified dictionary of all options can be created using `get_config`.
    This can be modified and used by unpacking the options into a `sift` call.

    >>> conf = emd.sift.get_config('sift')
    >>> conf['max_imfs'] = 4
    >>> conf['imf_opts'] = imf_opts
    >>> imfs = emd.sift.sift(x, **conf)

    References
    ----------
    .. [1] Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng,
       Q., … Liu, H. H. (1998). The empirical mode decomposition and the Hilbert
       spectrum for nonlinear and non-stationary time series analysis. Proceedings
       of the Royal Society of London. Series A: Mathematical, Physical and
       Engineering Sciences, 454(1971), 903–995.
       https://doi.org/10.1098/rspa.1998.0193

    """
    if not imf_opts:
        imf_opts = {'env_step_size': 1,
                    'sd_thresh': .1}

    X = ensure_1d_with_singleton([X], ['X'], 'sift')

    _nsamples_warn(X.shape[0], max_imfs)

    continue_sift = True
    layer = 0

    proto_imf = X.copy()

    while continue_sift:

        logger.info('sifting IMF : {0}'.format(layer))

        next_imf, continue_sift = get_next_imf(proto_imf,
                                               envelope_opts=envelope_opts,
                                               extrema_opts=extrema_opts,
                                               **imf_opts)

        if layer == 0:
            imf = next_imf
        else:
            imf = np.concatenate((imf, next_imf), axis=1)

        proto_imf = X - imf.sum(axis=1)[:, None]
        layer += 1

        if max_imfs is not None and layer == max_imfs:
            logger.info('Finishing sift: reached max number of imfs ({0})'.format(layer))
            continue_sift = False

        if np.abs(next_imf).sum() < sift_thresh:
            logger.info('Finishing sift: reached threshold {0}'.format(np.abs(next_imf).sum()))
            continue_sift = False

    return imf


##################################################################
# Ensemble SIFT variants

# Utilities

def _sift_with_noise(X, noise_scaling=None, noise=None, noise_mode='single',
                     sift_thresh=1e-8, max_imfs=None, job_ind=1,
                     imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Apply white noise to a signal prior to computing a sift.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    noise_scaling : float
         Standard deviation of noise to add to each ensemble (Default value =
         None)
    noise : ndarray
         array of noise values the same size as X to add prior to sift (Default value = None)
    noise_mode : {'single','flip'}
         Flag indicating whether to compute each ensemble with noise once or
         twice with the noise and sign-flipped noise (Default value = 'single')
    sift_thresh : float
         The threshold at which the overall sifting process will stop. (Default value = 1e-8)
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = None)
    job_ind : 1
        Optional job index value for display in logger (Default value = 1)

    Returns
    -------
    imf: ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from the decomposition of X.

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of arguments to be passed to emd.get_next_imf
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema

    See Also
    --------
    emd.sift.ensemble_sift
    emd.sift.complete_ensemble_sift
    emd.sift.get_next_imf

    """
    if job_ind is not None:
        logger.info('Starting SIFT Ensemble: {0}'.format(job_ind))

    if noise is None:
        noise = np.random.randn(*X.shape)

    X = ensure_1d_with_singleton([X], ['X'], 'sift')
    ensure_equal_dims([X, noise], ['X', 'noise'], '_sift_with_noise', dim=0)

    if noise_scaling is not None:
        noise = noise * noise_scaling

    ensX = X.copy() + noise
    imf = sift(ensX, sift_thresh=sift_thresh, max_imfs=max_imfs,
               imf_opts=imf_opts, envelope_opts=envelope_opts, extrema_opts=extrema_opts)

    if noise_mode == 'single':
        return imf
    elif noise_mode == 'flip':
        ensX = X.copy() - noise
        imf += sift(ensX, sift_thresh=sift_thresh, max_imfs=max_imfs,
                    imf_opts=imf_opts, envelope_opts=envelope_opts, extrema_opts=extrema_opts)
        return imf / 2


# Implementation

@wrap_verbose
@sift_logger('ensemble_sift')
def ensemble_sift(X, nensembles=4, ensemble_noise=.2, noise_mode='single',
                  nprocesses=1, sift_thresh=1e-8, max_imfs=None, verbose=None,
                  imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Compute Intrinsic Mode Functions with the ensemble EMD.

    This function implements the ensemble empirical model decomposition
    algorithm defined in [1]_. This approach sifts an ensemble of signals with
    white-noise added and treats the mean IMFs as the result. The resulting
    IMFs from the ensemble sift resembles a dyadic filter [2]_.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    nensembles : int
        Integer number of different ensembles to compute the sift across.
    ensemble_noise : float
         Standard deviation of noise to add to each ensemble (Default value = .2)
    noise_mode : {'single','flip'}
         Flag indicating whether to compute each ensemble with noise once or
         twice with the noise and sign-flipped noise (Default value = 'single')
    nprocesses : int
         Integer number of parallel processes to compute. Each process computes
         a single realisation of the total ensemble (Default value = 1)
    sift_thresh : float
         The threshold at which the overall sifting process will stop. (Default value = 1e-8)
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = None)

    Returns
    -------
    imf : ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from the decomposition of X.

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_next_imf.
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema
    verbose : {None,'CRITICAL','WARNING','INFO','DEBUG'}
        Option to override the EMD logger level for a call to this function.

    See Also
    --------
    emd.sift.get_next_imf

    References
    ----------
    .. [1] Wu, Z., & Huang, N. E. (2009). Ensemble Empirical Mode Decomposition:
       A Noise-Assisted Data Analysis Method. Advances in Adaptive Data Analysis,
       1(1), 1–41. https://doi.org/10.1142/s1793536909000047
    .. [2] Wu, Z., & Huang, N. E. (2004). A study of the characteristics of
       white noise using the empirical mode decomposition method. Proceedings of
       the Royal Society of London. Series A: Mathematical, Physical and
       Engineering Sciences, 460(2046), 1597–1611.
       https://doi.org/10.1098/rspa.2003.1221


    """
    if noise_mode not in ['single', 'flip']:
        raise ValueError(
            'noise_mode: {0} not recognised, please use \'single\' or \'flip\''.format(noise_mode))

    X = ensure_1d_with_singleton([X], ['X'], 'sift')

    _nsamples_warn(X.shape[0], max_imfs)

    # Noise is defined with respect to variance in the data
    noise_scaling = X.std() * ensemble_noise

    # Create partial function containing everything we need to run one iteration
    pfunc = functools.partial(_sift_with_noise, X, noise_scaling=noise_scaling,
                              noise=None, noise_mode=noise_mode, sift_thresh=sift_thresh,
                              max_imfs=max_imfs, imf_opts=imf_opts, envelope_opts=envelope_opts,
                              extrema_opts=extrema_opts)

    # Run the actual sifting - in parallel if requested
    args = [[] for ii in range(nensembles)]
    res = run_parallel(pfunc, args, nprocesses=nprocesses)

    # Keep largest group of ensembles with matching number of imfs.
    nimfs = [r.shape[1] for r in res]
    uni, unic = np.unique(nimfs, return_counts=True)
    target_imfs = uni[np.argmax(unic)]

    # Adjust for max_imfs if it was defined
    if (max_imfs is not None) and (target_imfs > max_imfs):
        target_imfs = max_imfs

    msg = 'Retaining {0} ensembles ({1}%) each with {2} IMFs'
    logger.info(msg.format(np.max(unic), 100*(np.max(unic)/nensembles), target_imfs))

    # Take average across ensembles
    imfs = np.zeros((X.shape[0], target_imfs))
    for ii in range(target_imfs):
        imfs[:, ii] = np.array([r[:, ii] for r in res if r.shape[1] == target_imfs]).mean(axis=0)

    return imfs


@wrap_verbose
@sift_logger('complete_ensemble_sift')
def complete_ensemble_sift(X, nensembles=4, ensemble_noise=.2,
                           noise_mode='single', nprocesses=1,
                           sift_thresh=1e-8, max_imfs=None, verbose=None,
                           imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Compute Intrinsic Mode Functions with complete ensemble EMD.

    This function implements the complete ensemble empirical model
    decomposition algorithm defined in [1]_. This approach sifts an ensemble of
    signals with white-noise added taking a single IMF across all ensembles at
    before moving to the next IMF.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    nensembles : int
        Integer number of different ensembles to compute the sift across.
    ensemble_noise : float
         Standard deviation of noise to add to each ensemble (Default value = .2)
    noise_mode : {'single','flip'}
         Flag indicating whether to compute each ensemble with noise once or
         twice with the noise and sign-flipped noise (Default value = 'single')
    nprocesses : int
         Integer number of parallel processes to compute. Each process computes
         a single realisation of the total ensemble (Default value = 1)
    sift_thresh : float
         The threshold at which the overall sifting process will stop. (Default value = 1e-8)
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = None)

    Returns
    -------
    imf: ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from the decomposition of X.
    noise: array_like
        The Intrisic Mode Functions from the decomposition of X.

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_next_imf.
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema
    verbose : {None,'CRITICAL','WARNING','INFO','DEBUG'}
        Option to override the EMD logger level for a call to this function.

    See Also
    --------
    emd.sift.get_next_imf

    References
    ----------
    .. [1] Torres, M. E., Colominas, M. A., Schlotthauer, G., & Flandrin, P.
       (2011). A complete ensemble empirical mode decomposition with adaptive
       noise. In 2011 IEEE International Conference on Acoustics, Speech and
       Signal Processing (ICASSP). IEEE.
       https://doi.org/10.1109/icassp.2011.5947265

    """
    X = ensure_1d_with_singleton([X], ['X'], 'sift')

    _nsamples_warn(X.shape[0], max_imfs)

    # Noise is defined with respect to variance in the data
    noise_scaling = X.std() * ensemble_noise

    continue_sift = True
    layer = 0

    # Compute the noise processes - large matrix here...
    noise = np.random.random_sample((X.shape[0], nensembles)) * noise_scaling

    # Parallel environment for computing the first IMF
    logger.info('Sifting IMF-{0}'.format(layer))
    pfunc = functools.partial(_sift_with_noise, X,
                              noise_mode=noise_mode,
                              sift_thresh=sift_thresh,
                              max_imfs=1,
                              imf_opts=imf_opts,
                              envelope_opts=envelope_opts,
                              extrema_opts=extrema_opts)
    # Compute standard EEMD sift to get first IMF
    # (not using ensemble_sift here as we need to retain noise realisations)
    args = [[noise[:, ii, np.newaxis]] for ii in range(nensembles)]
    res = run_parallel(pfunc, args, nprocesses=nprocesses)
    imf = np.array([r for r in res]).mean(axis=0)

    while continue_sift:

        proto_imf = X - imf.sum(axis=1)[:, None]

        logger.info('Sifting IMF-{0}'.format(layer+1))
        # Sift off the first IMF from each noise realisation using normal EMD
        pfunc = functools.partial(sift, sift_thresh=sift_thresh,
                                  max_imfs=1,
                                  imf_opts=imf_opts,
                                  envelope_opts=envelope_opts,
                                  extrema_opts=extrema_opts)
        args = [[noise[:, ii, np.newaxis]] for ii in range(nensembles)]
        res = run_parallel(pfunc, args, nprocesses=nprocesses)
        noise = noise - np.array([r[:, 0] for r in res]).T

        # Compute next ensemble of IMFs using sifted noise ensembles
        pfunc = functools.partial(_sift_with_noise, proto_imf,
                                  noise_mode=noise_mode,
                                  sift_thresh=sift_thresh,
                                  max_imfs=1,
                                  imf_opts=imf_opts,
                                  envelope_opts=envelope_opts,
                                  extrema_opts=extrema_opts)
        args = [[noise[:, ii, np.newaxis]] for ii in range(nensembles)]
        res = run_parallel(pfunc, args, nprocesses)
        next_imf = np.array([r for r in res]).mean(axis=0)

        imf = np.concatenate((imf, next_imf), axis=1)

        pks, _ = _find_extrema(imf[:, -1])
        if len(pks) < 2:
            continue_sift = False

        if max_imfs is not None and layer == max_imfs:
            continue_sift = False

        if np.abs(next_imf).mean() < sift_thresh:
            continue_sift = False

        layer += 1

    return imf, noise


##################################################################
# Mask SIFT implementations

# Utilities


def get_next_imf_mask(X, z, amp, nphases=4, nprocesses=1,
                      imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Compute the next IMF from a data set a mask sift.

    This is a helper function used within the more general sifting functions.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    z : float
        Mask frequency as a proportion of the sampling rate, values between 0->z->.5
    amp : float
        Mask amplitude
    nphases : int > 0
        The number of separate sinusoidal masks to apply for each IMF, the
        phase of masks are uniformly spread across a 0<=p<2pi range
        (Default=4).
    nprocesses : int
         Integer number of parallel processes to compute. Each process computes
         an IMF from the signal plus a mask. nprocesses should be less than or
         equal to nphases, no additional benefit from setting nprocesses > nphases
         (Default value = 1)

    Returns
    -------
    proto_imf : ndarray
        1D vector containing the next IMF extracted from X
    continue_sift : bool
        Boolean indicating whether the sift can be continued beyond this IMF

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of keyword arguments to be passed to emd.get_next_imf
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema

    See Also
    --------
    emd.sift.mask_sift
    emd.sift.get_next_imf

    """
    X = ensure_1d_with_singleton([X], ['X'], 'get_next_imf_mask')

    if imf_opts is None:
        imf_opts = {}

    logger.info("Defining masks with freq {0} and amp {1} at {2} phases".format(z, amp, nphases))

    # Create normalised freq
    zf = z * 2 * np.pi
    # Create time matrix including mask phase-shifts
    t = np.repeat(np.arange(X.shape[0])[:, np.newaxis], nphases, axis=1)
    phases = np.linspace(0, (2*np.pi), nphases+1)[:nphases]
    # Create masks
    m = amp * np.cos(zf * t + phases)

    # Work with a partial function to make the parallel loop cleaner
    # This partial function contains all the settings which will be constant across jobs.
    pfunc = functools.partial(get_next_imf, **imf_opts,
                              envelope_opts=envelope_opts,
                              extrema_opts=extrema_opts)

    args = [[X+m[:, ii, np.newaxis]] for ii in range(nphases)]
    res = run_parallel(pfunc, args, nprocesses=nprocesses)

    # Collate results
    imfs = [r[0] for r in res]
    continue_flags = [r[1] for r in res]

    # star map should preserve the order of outputs so we can remove masks easily
    imfs = np.concatenate(imfs, axis=1) - m

    logger.verbose('Averaging across {0} proto IMFs'.format(imfs.shape[1]))

    return imfs.mean(axis=1)[:, np.newaxis], np.any(continue_flags)


def get_mask_freqs(X, first_mask_mode='zc', imf_opts=None):
    """Determine mask frequencies for a sift.

    Parameters
    ----------
    X : ndarray
        Vector time-series
    first_mask_mode : (str, float<0.5)
        Either a string denoting a method {'zc', 'if'} or a float determining
        and initial frequency. See notes for more details.
    imf_opts : dict
        Options to be passed to get_next_imf if first_mask_mode is 'zc' or 'if'.

    Returns
    -------
    float
        Frequency for the first mask in normalised units.

    """
    if imf_opts is None:
        imf_opts = {}

    if first_mask_mode in ('zc', 'if'):
        logger.info('Computing first mask frequency with method {0}'.format(first_mask_mode))
        logger.info('Getting first IMF with no mask')
        # First IMF is computed normally
        imf, _ = get_next_imf(X, **imf_opts)

    # Compute first mask frequency from first IMF
    if first_mask_mode == 'zc':
        num_zero_crossings = zero_crossing_count(imf)[0, 0]
        z = num_zero_crossings / imf.shape[0] / 2
        logger.info('Found first mask frequency of {0}'.format(z))
    elif first_mask_mode == 'if':
        _, IF, IA = frequency_transform(imf[:, 0, None], 1, 'nht',
                                        smooth_phase=3)
        z = np.average(IF, weights=IA)
        logger.info('Found first mask frequency of {0}'.format(z))
    elif isinstance(first_mask_mode, (int, float)):
        if first_mask_mode <= 0 or first_mask_mode > .5:
            raise ValueError("The frequency of the first mask must be 0 <= x < 0.5")
        logger.info('Using specified first mask frequency of {0}'.format(first_mask_mode))
        z = first_mask_mode

    return z


# Implementation

@wrap_verbose
@sift_logger('mask_sift')
def mask_sift(X, mask_amp=1, mask_amp_mode='ratio_sig', mask_freqs='zc',
              mask_step_factor=2, ret_mask_freq=False, max_imfs=9, sift_thresh=1e-8,
              nphases=4, nprocesses=1, verbose=None,
              imf_opts=None, envelope_opts=None, extrema_opts=None):
    """Compute Intrinsic Mode Functions using a mask sift.

    This function implements a masked sift from a dataset using a set of
    masking signals to reduce mixing of components between modes [1]_, multiple
    masks of different phases can be applied when isolating each IMF [2]_.

    This function can either compute the mask frequencies based on the fastest
    dynamics in the data (the properties of the first IMF from a standard sift)
    or apply a pre-specified set of masks.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    mask_amp : float or array_like
        Amplitude of mask signals as specified by mask_amp_mode. If float the
        same value is applied to all IMFs, if an array is passed each value is
        applied to each IMF in turn (Default value = 1)
    mask_amp_mode : {'abs','ratio_imf','ratio_sig'}
        Method for computing mask amplitude. Either in absolute units ('abs'),
        or as a ratio of the standard deviation of the input signal
        ('ratio_sig') or previous imf ('ratio_imf') (Default value = 'ratio_imf')
    mask_freqs : {'zc','if',float,,array_like}
        Define the set of mask frequencies to use. If 'zc' or 'if' are passed,
        the frequency of the first mask is taken from either the zero-crossings
        or instantaneous frequnecy the first IMF of a standard sift on the
        data. If a float is passed this is taken as the first mask frequency.
        Subsequent masks are defined by the mask_step_factor. If an array_like
        vector is passed, the values in the vector will specify the mask
        frequencies.
    mask_step_factor : float
        Step in frequency between successive masks (Default value = 2)
    mask_type : {'all','sine','cosine'}
        Which type of masking signal to use. 'sine' or 'cosine' options return
        the average of a +ve and -ve flipped wave. 'all' applies four masks:
        sine and cosine with +ve and -ve sign and returns the average of all
        four.
    nphases : int > 0
        The number of separate sinusoidal masks to apply for each IMF, the
        phase of masks are uniformly spread across a 0<=p<2pi range
        (Default=4).
    ret_mask_freq : bool
         Boolean flag indicating whether mask frequencies are returned (Default value = False)
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = None)
    sift_thresh : float
         The threshold at which the overall sifting process will stop. (Default value = 1e-8)

    Returns
    -------
    imf : ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from the decomposition of X.
    mask_freqs : ndarray
        1D array of mask frequencies, if ret_mask_freq is set to True.

    Other Parameters
    ----------------
    imf_opts : dict
        Optional dictionary of keyword arguments to be passed to emd.get_next_imf
    envelope_opts : dict
        Optional dictionary of keyword options to be passed to emd.interp_envelope
    extrema_opts : dict
        Optional dictionary of keyword options to be passed to emd.get_padded_extrema
    verbose : {None,'CRITICAL','WARNING','INFO','DEBUG'}
        Option to override the EMD logger level for a call to this function.

    Notes
    -----
    Here are some example mask_sift variants you can run:

    A mask sift in which the mask frequencies are determined with
    zero-crossings and mask amplitudes by a ratio with the amplitude of the
    previous IMF (note - this is also the default):

    >>> imf = emd.sift.mask_sift(X, mask_amp_mode='ratio_imf', mask_freqs='zc')

    A mask sift in which the first mask is set at .4 of the sampling rate and
    subsequent masks found by successive division of this mask_freq by 3:

    >>> imf = emd.sift.mask_sift(X, mask_freqs=.4, mask_step_factor=3)

    A mask sift using user specified frequencies and amplitudes:

    >>> mask_freqs = np.array([.4,.2,.1,.05,.025,0])
    >>> mask_amps = np.array([2,2,1,1,.5,.5])
    >>> imf = emd.sift.mask_sift(X, mask_freqs=mask_freqs, mask_amp=mask_amps, mask_amp_mode='abs')

    See Also
    --------
    emd.sift.get_next_imf
    emd.sift.get_next_imf_mask

    References
    ----------
    .. [1] Ryan Deering, & James F. Kaiser. (2005). The Use of a Masking Signal
       to Improve Empirical Mode Decomposition. In Proceedings. (ICASSP ’05). IEEE
       International Conference on Acoustics, Speech, and Signal Processing, 2005.
       IEEE. https://doi.org/10.1109/icassp.2005.1416051
    .. [2] Tsai, F.-F., Fan, S.-Z., Lin, Y.-S., Huang, N. E., & Yeh, J.-R.
       (2016). Investigating Power Density and the Degree of Nonlinearity in
       Intrinsic Components of Anesthesia EEG by the Hilbert-Huang Transform: An
       Example Using Ketamine and Alfentanil. PLOS ONE, 11(12), e0168108.
       https://doi.org/10.1371/journal.pone.0168108

    """
    X = ensure_1d_with_singleton([X], ['X'], 'sift')

    # if first mask is if or zc - compute first imf as normal and get freq
    if isinstance(mask_freqs, (list, tuple, np.ndarray)):
        logger.info('Using user specified masks')
        if len(mask_freqs) < max_imfs:
            max_imfs = len(mask_freqs)
            logger.info("Reducing max_imfs to {0} as len(mask_freqs) < max_imfs".format(max_imfs))
    elif mask_freqs in ['zc', 'if'] or isinstance(mask_freqs, float):
        z = get_mask_freqs(X, mask_freqs, imf_opts=imf_opts)
        mask_freqs = np.array([z/mask_step_factor**ii for ii in range(max_imfs)])

    _nsamples_warn(X.shape[0], max_imfs)

    # Initialise mask amplitudes
    if mask_amp_mode == 'ratio_imf':
        sd = X.std()  # Take ratio of input signal for first IMF
    elif mask_amp_mode == 'ratio_sig':
        sd = X.std()
    elif mask_amp_mode == 'abs':
        sd = 1

    continue_sift = True
    imf_layer = 0
    proto_imf = X.copy()
    imf = []
    while continue_sift:

        # Update mask amplitudes if needed
        if mask_amp_mode == 'ratio_imf' and imf_layer > 0:
            sd = imf[:, -1].std()

        if isinstance(mask_amp, (int, float)):
            amp = mask_amp * sd
        else:
            # Should be array_like if not a single number
            amp = mask_amp[imf_layer] * sd

        logger.info('Sifting IMF-{0}'.format(imf_layer))

        next_imf, continue_sift = get_next_imf_mask(proto_imf, mask_freqs[imf_layer], amp,
                                                    nphases=nphases,
                                                    nprocesses=nprocesses,
                                                    imf_opts=imf_opts,
                                                    envelope_opts=envelope_opts,
                                                    extrema_opts=extrema_opts)

        if imf_layer == 0:
            imf = next_imf
        else:
            imf = np.concatenate((imf, next_imf), axis=1)

        proto_imf = X - imf.sum(axis=1)[:, None]

        if max_imfs is not None and imf_layer == max_imfs-1:
            logger.info('Finishing sift: reached max number of imfs ({0})'.format(imf.shape[1]))
            continue_sift = False

        if np.abs(next_imf).sum() < sift_thresh:
            continue_sift = False

        imf_layer += 1

    if ret_mask_freq:
        return imf, mask_freqs
    else:
        return imf


@wrap_verbose
@sift_logger('iterated_mask_sift')
def iterated_mask_sift(X,
                       # Iterated mask sift arguments
                       mask_0='zc', w_method='power', max_iter=15, iter_th=0.1,
                       N_avg=1, exclude_edges=False, sample_rate=1.0,
                       seed=None,
                       # Standard mask sift arguments - specify a couple which need defaults.
                       max_imfs=6, ret_mask_freq=False, mask_amp_mode='ratio_imf',
                       **kwargs):
    """Compute Intrinsic Mode Functions using an iterated mask sift.

    This function implements a masked sift from a dataset using a set of
    masking signals to reduce mixing of components between modes [1]_, multiple
    masks of different phases can be applied when isolating each IMF [2]_.

    Mask frequencies are determined automatically by an iterative process [3]_.
    The iteration can be started with either a random mask, a mask based on the
    fastest dynamics (same as 'zc' in mask_sift), or a pre-specified mask.

    Parameters
    ----------
    X : ndarray
        1D input array containing the time-series data to be decomposed
    mask_0 : {array_like, 'zc', 'random'}
        Initial mask for the iteration process, can be one of:

        * 'zc' or 'if' initialises with the masks chosen by the zero-crossing
        count or instantaneous frequency method in  the standard mask sift.

        * 'random' chooses random integers between 0 and sample_rate/4 as the starting mask.
        seed=int can be optionally passed to control the random seed in numpy.

        * array-like needs to be in normalised units, i.e. divided by the sample rate.
        (Default value = 'zc')
    w_method : {'amplitude', 'power', float, None}
        Weighting method to use in the iteration process. 'amplitude' weights
        frequencies by the instantaneous amplitude, 'power' by its square.  If
        a float is passed, the amplitude is raised to that exponent before averaging.
        None performs a simple average without weighting.
        (Default value = 'power')
    max_imfs : int
         The maximum number of IMFs to compute. (Default value = 6)
    max_iter : int
        The maximum number of iterations to compute. (Default value = 15)
    iter_th : float
        Relative mask variability threshold below which iteration is stopped.
        (Default value = 0.1)
    N_avg : int
        Number of iterations to average after convergence is reached. (Default value = 1)
    exlude_edges : bool
        If True, excludes first and last 2.5% of frequency data during the iteration
        process to avoid edge effects. (Default value = False)
    sample_rate : float
        Sampling rate of the data in Hz (Default value = 1.0)
    seed : int or None
        Random seed to use for random initial mask selection when mask_0 = 'random'
    **kwargs
        Any additional arguments for the standard emd.sift.mask_sift can be
        specified - see the documentation for emd.sift.mask_sift for more
        details.

    Returns
    -------
    imf : ndarray
        2D array [samples x nimfs] containing he Intrisic Mode Functions from
        the decomposition of X.
    mask_freqs : ndarray
        1D array of mask frequencies, if ret_mask_freq is set to True.

    Notes
    -----
    Here are some example iterated_mask_sift variants you can run:

    An iterated mask sift in which the mask frequencies are determined with
    zero-crossings and iteration stop at 15 iterations or if masks
    stabilize to within 10% (note - this is also the default):

    >>> imf = emd.sift.iterated_mask_sift(X, sample_rate, mask_0='zc',
                                          max_iter=15, iter_th=0.1)

    An iterated mask sift in which a custom initial mask is used and after convergence
    5 further iterations are averaged:

    >>> imf = emd.sift.iterated_mask_sift(X, sample_rate,
                                          mask_0=[10, 5, 3, 1]/sample_rate,
                                          N_avg=5)

    An iterated mask sift weighted by instantaneous amplitude that also returns
    the automatically determined mask and excludes 5% of edge data to avoid
    edge effectd:

    >>> imf, mask = emd.sift.iterated_mask_sift(X, sample_rate, w_method='amplitude',
                                                exclude_edges=True, ret_mask_freq=True)

    See Also
    --------
    emd.sift.mask_sift
    emd.sift.get_next_imf_mask

    References
    ----------
    .. [1] Ryan Deering, & James F. Kaiser. (2005). The Use of a Masking Signal
       to Improve Empirical Mode Decomposition. In Proceedings. (ICASSP ’05). IEEE
       International Conference on Acoustics, Speech, and Signal Processing, 2005.
       IEEE. https://doi.org/10.1109/icassp.2005.1416051
    .. [2] Tsai, F.-F., Fan, S.-Z., Lin, Y.-S., Huang, N. E., & Yeh, J.-R.
       (2016). Investigating Power Density and the Degree of Nonlinearity in
       Intrinsic Components of Anesthesia EEG by the Hilbert-Huang Transform: An
       Example Using Ketamine and Alfentanil. PLOS ONE, 11(12), e0168108.
       https://doi.org/10.1371/journal.pone.0168108
    .. [3] Marco S. Fabus, Andrew J. Quinn, Catherine E. Warnaby,
       and Mark W. Woolrich (2021). Automatic decomposition of
       electrophysiological data into distinct nonsinusoidal oscillatory modes.
       Journal of Neurophysiology 2021 126:5, 1670-1684.
       https://doi.org/10.1152/jn.00315.2021

    """
    # Housekeeping
    X = ensure_1d_with_singleton([X], ['X'], 'sift')
    _nsamples_warn(X.shape[0], max_imfs)
    nsamples = X.shape[0]

    # Add explicitly specified mask_sift kwargs into full dict for use later
    kwargs['max_imfs'] = max_imfs
    kwargs['mask_amp_mode'] = mask_amp_mode

    # Main switch initialising the mask frequency set
    if isinstance(mask_0, (list, tuple, np.ndarray)):
        # User has provided a full set of masks
        logger.info('Initialising masks with user specified frequencies')
        if len(mask_0) < max_imfs:
            max_imfs = len(mask_0)
            logger.info("Reducing max_imfs to {0} as len(mask_freqs) < max_imfs".format(max_imfs))
        mask = mask_0
    elif isinstance(mask_0, (int, float)):
        logger.info('Initialising masks with user specified single frequency')
        mask = mask_0
    elif mask_0 in ('zc', 'if'):
        logger.info('Initialising masks with mask_sift default mask_freqs={0}'.format(mask_0))
        # if first mask is if or zc - compute first imf as normal and get freq
        _, mask = mask_sift(X, mask_freqs=mask_0, ret_mask_freq=True, **kwargs)
        mask = mask
    elif mask_0 == 'random':
        logger.info('Initialising masks with random values')
        if seed is not None:
            np.random.seed(seed)
        mask = np.random.randint(0, sample_rate/4, size=max_imfs) / sample_rate
    else:
        raise ValueError("'mask_0' input {0} not recognised - cannot initialise mask frequencies".format(mask_0))

    # Preallocate arrays for loop process
    mask_all = np.zeros((max_iter+N_avg, max_imfs))
    imf_all = np.zeros((max_iter+N_avg, nsamples, max_imfs))

    # Start counters
    niters = 0
    niters_c = 0
    maxiter_flag = 0
    continue_iter = True
    converged = False

    # Main loop
    while continue_iter:
        if not converged:
            logger.info('Computing iteration number ' + str(niters))
        else:
            logger.info('Converged, averaging... ' + str(niters_c) + ' / ' + str(N_avg))

        # Update masks
        mask_prev = mask.copy()
        mask_all[niters+niters_c, :len(mask)] = mask.copy()

        # Compute mask sift
        imf = mask_sift(X, mask_freqs=mask, **kwargs)
        imf_all[niters+niters_c, :, :imf.shape[1]] = imf

        # Compute IMF frequencies
        IP, IF, IA = frequency_transform(imf, sample_rate, 'nht')

        # Trim IMF edges if requested - avoids edge effects distorting IF average
        if exclude_edges:
            logger.info('Excluding 5% of edge frequencies in mask estimation.')
            ex = int(0.025*nsamples)
            samples_included = list(range(ex, nsamples-ex))  # Edge effects ignored
        else:
            samples_included = list(range(nsamples))  # All, default

        # find weighted IF average as the next mask
        if w_method == 'amplitude':
            # IF weighed by amplitude values in IA
            IF_weighted = np.average(IF[samples_included, :], 0, weights=IA[samples_included, :])
        elif w_method == 'power':
            # IF weighed by power values from IA**2
            IF_weighted = np.average(IF[samples_included, :], 0, weights=IA[samples_included, :]**2)
        elif isinstance(w_method, float):
            # IF weighed by amplitude raised to user specified power
            IF_weighted = np.average(IF[samples_included, :], 0, weights=IA[samples_included, :]**w_method)
        elif w_method == 'avg':
            # IF average not weighted
            IF_weighted = np.mean(IF[samples_included, :], axis=0)
        else:
            raise ValueError("w_method '{0}' not recognised".format(w_method))

        # Compute new mask frequencies and variances
        mask = IF_weighted/sample_rate
        l = min(len(mask), len(mask_prev))
        mask_variance = np.abs((mask[:l] - mask_prev[:l]) / mask_prev[:l])

        # Check convergence
        if np.all(mask_variance[~np.isnan(mask_variance)] < iter_th) or converged:
            converged = True
            logger.info('Finishing iteration process: convergence reached in {0} iterations '.format(niters))
            if niters_c < N_avg:
                niters_c += 1
            else:
                continue_iter = False

        if not converged:
            niters += 1

        if niters >= max_iter:
            logger.info('Finishing iteration process: reached max number of iterations: {0}'.format(max_iter))
            maxiter_flag = 1
            continue_iter = False

    # Average IMFs across iterations after convergence
    imf_final = np.nanmean(imf_all[niters:niters+N_avg, :, :], axis=0)
    IF_final = np.nanmean(mask_all[niters:niters+N_avg, :], axis=0)*sample_rate
    IF_std_final = np.nanstd(mask_all[niters:niters+N_avg, :], axis=0)*sample_rate

    if maxiter_flag:
        imf_final = imf_all[niters-1, :, :]
        IF_final = mask
        IF_std_final = mask_variance

    # If we are not averaging, output relative change from last mask instead
    if N_avg == 1:
        IF_std_final = mask_variance

    N_imf_final = int(np.sum(~np.isnan(mask_all[niters-1, :])))
    imf_final = imf_final[:, :N_imf_final]
    IF_final = IF_final[:N_imf_final]
    IF_std_final = IF_std_final[:N_imf_final]
    imf = imf_final

    logger.info('Final mask variability: %s', str(IF_std_final))
    logger.info('COMPLETED: iterated mask sift')

    if ret_mask_freq:
        return imf, IF_final
    else:
        return imf


##################################################################
# Second Layer SIFT


@sift_logger('second_layer')
def sift_second_layer(IA, sift_func=sift, sift_args=None):
    """Compute second layer intrinsic mode functions.

    This function implements a second-layer sift to be appliede to the
    amplitude envelopes of a set of first layer IMFs [1]_.

    Parameters
    ----------
    IA : ndarray
        Input array containing a set of first layer IMFs
    sift_func : function
        Sift function to apply
    sift_args : dict
        Dictionary of sift options to be passed into sift_func

    Returns
    -------
    imf2 : ndarray
        3D array [samples x first layer imfs x second layer imfs ] containing
        the second layer IMFs

    References
    ----------
    .. [1] Huang, N. E., Hu, K., Yang, A. C. C., Chang, H.-C., Jia, D., Liang,
       W.-K., … Wu, Z. (2016). On Holo-Hilbert spectral analysis: a full
       informational spectral representation for nonlinear and non-stationary
       data. Philosophical Transactions of the Royal Society A: Mathematical,
       Physical and Engineering Sciences, 374(2065), 20150206.
       https://doi.org/10.1098/rsta.2015.0206

    """
    IA = ensure_2d([IA], ['IA'], 'sift_second_layer')

    if (sift_args is None) or ('max_imfs' not in sift_args):
        max_imfs = IA.shape[1]
    elif 'max_imfs' in sift_args:
        max_imfs = sift_args['max_imfs']

    imf2 = np.zeros((IA.shape[0], IA.shape[1], max_imfs))

    for ii in range(max_imfs):
        tmp = sift_func(IA[:, ii], **sift_args)
        imf2[:, ii, :tmp.shape[1]] = tmp

    return imf2


@sift_logger('mask_sift_second_layer')
def mask_sift_second_layer(IA, mask_freqs, sift_args=None):
    """Compute second layer IMFs using a mask sift.

    Second layer IMFs are computed from the amplitude envelopes of a set of
    first layer IMFs [1]_.A single set of masks is applied across all IMFs with
    the highest frequency mask dropped for each successive first level IMF.

    Parameters
    ----------
    IA : ndarray
        Input array containing a set of first layer IMFs
    mask_freqs : function
        Sift function to apply
    sift_args : dict
        Dictionary of sift options to be passed into sift_func

    Returns
    -------
    imf2 : ndarray
        3D array [samples x first layer imfs x second layer imfs ] containing
        the second layer IMFs

    References
    ----------
    .. [1] Huang, N. E., Hu, K., Yang, A. C. C., Chang, H.-C., Jia, D., Liang,
       W.-K., … Wu, Z. (2016). On Holo-Hilbert spectral analysis: a full
       informational spectral representation for nonlinear and non-stationary
       data. Philosophical Transactions of the Royal Society A: Mathematical,
       Physical and Engineering Sciences, 374(2065), 20150206.
       https://doi.org/10.1098/rsta.2015.0206

    """
    IA = ensure_2d([IA], ['IA'], 'sift_second_layer')

    if (sift_args is None):
        sift_args = {'max_imfs': IA.shape[1]}
    elif ('max_imfs' not in sift_args):
        sift_args['max_imfs'] = IA.shape[1]

    imf2 = np.zeros((IA.shape[0], IA.shape[1], sift_args['max_imfs']))

    for ii in range(IA.shape[1]):
        sift_args['mask_freqs'] = mask_freqs[ii:]
        tmp = mask_sift(IA[:, ii], **sift_args)
        imf2[:, ii, :tmp.shape[1]] = tmp
    return imf2


##################################################################
# SIFT Estimation Utilities

##################################################################
# SIFT Config Utilities


class SiftConfig(collections.abc.MutableMapping):
    """A dictionary-like object specifying keyword arguments configuring a sift."""

    def __init__(self, name='sift', *args, **kwargs):
        """Specify keyword arguments configuring a sift."""
        self.store = dict()
        self.sift_type = name
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        """Return an item from the internal store."""
        key = self.__keytransform__(key)
        if isinstance(key, list):
            if len(key) == 2:
                return self.store[key[0]][key[1]]
            elif len(key) == 3:
                return self.store[key[0]][key[1]][key[2]]
        else:
            return self.store[key]

    def __setitem__(self, key, value):
        """Set or change the value of an item in the internal store."""
        key = self.__keytransform__(key)
        if isinstance(key, list):
            if len(key) == 2:
                self.store[key[0]][key[1]] = value
            elif len(key) == 3:
                self.store[key[0]][key[1]][key[2]] = value
        else:
            self.store[key] = value

    def __delitem__(self, key):
        """Remove an item from the internal store."""
        key = self.__keytransform__(key)
        if isinstance(key, list):
            if len(key) == 2:
                del self.store[key[0]][key[1]]
            elif len(key) == 3:
                del self.store[key[0]][key[1]][key[2]]
        else:
            del self.store[key]

    def __iter__(self):
        """Iterate through items in the internal store."""
        return iter(self.store)

    def __str__(self):
        """Print summary of internal store."""
        out = []
        lower_level = ['imf_opts', 'envelope_opts', 'extrema_opts']
        for stage in self.store.keys():
            if stage not in lower_level:
                out.append('{0} : {1}'.format(stage, self.store[stage]))
            else:
                out.append(stage + ':')
                for key in self.store[stage].keys():
                    out.append('    {0} : {1}'.format(key, self.store[stage][key]))

        return '%s %s\n%s' % (self.sift_type, self.__class__, '\n'.join(out))

    def __repr__(self):
        """Print summary of internal store."""
        return "<{0} ({1})>".format(self.__module__ + '.' + type(self).__name__, self.sift_type)

    def _repr_html_(self):
        _str_html = "<h3><b>%s %s</b></h3><hr><ul>" % (self.sift_type, self.__class__)
        lower_level = ['imf_opts', 'envelope_opts', 'extrema_opts']
        for stage in self.store.keys():
            if stage not in lower_level:
                _str_html += '<li><b>{0}</b> : {1}</li>'.format(stage, self.store[stage])
            else:
                outer_list = '<li><b>{0}</b></li>%s'.format(stage)
                inner_list = '<ul>'
                for key in self.store[stage].keys():
                    inner_list += '<li><i>{0}</i> : {1}</li>'.format(key, self.store[stage][key])
                _str_html += outer_list % (inner_list + '</ul>')
        return _str_html + '</ul>'

    def __len__(self):
        """Return number of items in internal store."""
        return len(self.store)

    def __keytransform__(self, key):
        """Split a merged dictionary key into separate levels."""
        key = key.split('/')
        if len(key) == 1:
            return key[0]
        else:
            if len(key) > 3:
                raise ValueError("Requested key is nested too deep. Should be a \
                                 maximum of three levels separated by '/'")
            return key

    def _get_yamlsafe_dict(self):
        """Return copy of internal store with values prepped for saving into yaml format."""
        conf = self.store.copy()
        conf = _array_or_tuple_to_list(conf)
        return [{'sift_type': self.sift_type}, conf]

    def to_yaml_text(self):
        """Return a copy of the internal store in yaml-text format."""
        return yaml.dump(self._get_yamlsafe_dict(), sort_keys=False)

    def to_yaml_file(self, fname):
        """Save a copy of the internal store in a specified yaml file."""
        with open(fname, 'w') as f:
            yaml.dump_all(self._get_yamlsafe_dict(), f, sort_keys=False)
        logger.info("Saved SiftConfig ({0}) to {1}".format(self, fname))

    @classmethod
    def from_yaml_file(cls, fname):
        """Create and return a new SiftConfig object with options loaded from a yaml file."""
        ret = cls()
        with open(fname, 'r') as f:
            cfg = [d for d in yaml.load_all(f, Loader=yaml.FullLoader)]
            if len(cfg) == 1:
                ret.store = cfg[0]
                ret.sift_type = 'Unknown'
            else:
                ret.sift_type = cfg[0]['sift_type']
                ret.store = cfg[1]
        logger.info("Loaded SiftConfig ({0}) from {1}".format(ret, fname))

        return ret

    @classmethod
    def from_yaml_stream(cls, stream):
        """Create and return a new SiftConfig object with options loaded from a yaml stream."""
        ret = cls()
        ret.store = yaml.load(stream, Loader=yaml.FullLoader)
        return ret

    def get_func(self):
        """Get a partial-function coded with the options from this config."""
        mod = sys.modules[__name__]
        func = getattr(mod, self.sift_type)
        return functools.partial(func, **self.store)


def get_config(siftname='sift'):
    """Return a SiftConfig with default options for a specified sift variant.

    Helper function for specifying config objects specifying parameters to be
    used in a sift. The functions used during the sift areinspected
    automatically and default values are populated into a nested dictionary
    which can be modified and used as input to one of the sift functions.

    Parameters
    ----------
    siftname : str
        Name of the sift function to find configuration from

    Returns
    -------
    SiftConfig
        A modified dictionary containing the sift specification

    Notes
    -----
    The sift config acts as a nested dictionary which can be modified to
    specify parameters for different parts of the sift. This is initialised
    using this function

    >>> config = emd.sift.get_config()

    The first level of the dictionary contains three sub-dicts configuring
    different parts of the algorithm:

    >>> config['imf_opts'] # options passed to `get_next_imf`
    >>> config['envelope_opts'] # options passed to interp_envelope
    >>> config['extrema_opts'] # options passed to get_padded_extrema

    Specific values can be modified in the dictionary

    >>> config['extrema_opts']['parabolic_extrema'] = True

    or using this shorthand

    >>> config['imf_opts/env_step_factor'] = 1/3

    Finally, the SiftConfig dictionary should be nested before being passed as
    keyword arguments to a sift function.

    >>> imfs = emd.sift.sift(X, **config)

    """
    # Extrema padding opts are hard-coded for the moment, these run through
    # np.pad which has a complex signature
    mag_pad_opts = {'mode': 'median', 'stat_length': 1}
    loc_pad_opts = {'mode': 'reflect', 'reflect_type': 'odd'}

    # Get defaults for extrema detection and padding
    extrema_opts = _get_function_opts(get_padded_extrema, ignore=['X', 'mag_pad_opts',
                                                                  'loc_pad_opts',
                                                                  'mode'])

    # Get defaults for envelope interpolation
    envelope_opts = _get_function_opts(interp_envelope, ignore=['X', 'extrema_opts', 'mode', 'ret_extrema', 'trim'])

    # Get defaults for computing IMFs
    imf_opts = _get_function_opts(get_next_imf, ignore=['X', 'envelope_opts', 'extrema_opts'])

    # Get defaults for the given sift variant
    sift_types = ['sift', 'ensemble_sift', 'complete_ensemble_sift',
                  'mask_sift', 'iterated_mask_sift']
    if siftname in sift_types:
        mod = sys.modules[__name__]
        sift_opts = _get_function_opts(getattr(mod, siftname), ignore=['X', 'imf_opts'
                                                                       'envelope_opts',
                                                                       'extrema_opts',
                                                                       'kwargs'])
        if siftname == 'iterated_mask_sift':
            # Add options for mask sift as well
            mask_opts = _get_function_opts(getattr(mod, 'mask_sift'), ignore=['X', 'imf_opts'
                                                                              'envelope_opts',
                                                                              'extrema_opts',
                                                                              'mask_freqs',
                                                                              'mask_step_factor'])
            sift_opts = {**sift_opts, **mask_opts}
    else:
        raise AttributeError('Sift siftname not recognised: please use one of {0}'.format(sift_types))

    out = SiftConfig(siftname)
    for key in sift_opts:
        out[key] = sift_opts[key]
    out['imf_opts'] = imf_opts
    out['envelope_opts'] = envelope_opts
    out['extrema_opts'] = extrema_opts
    out['extrema_opts/mag_pad_opts'] = mag_pad_opts
    out['extrema_opts/loc_pad_opts'] = loc_pad_opts

    return out


def _get_function_opts(func, ignore=None):
    """Inspect a function and extract its keyword arguments and their default values.

    Parameters
    ----------
    func : function
        handle for the function to be inspected
    ignore : {None or list}
        optional list of keyword argument names to be ignored in function
        signature

    Returns
    -------
    dict
        Dictionary of keyword arguments with keyword keys and default value
        values.

    """
    if ignore is None:
        ignore = []
    out = {}
    sig = inspect.signature(func)
    for p in sig.parameters:
        if p not in out.keys() and p not in ignore:
            out[p] = sig.parameters[p].default
    return out


def _array_or_tuple_to_list(conf):
    """Convert an input array or tuple to list (for yaml_safe dict creation."""
    for key, val in conf.items():
        if isinstance(val, np.ndarray):
            conf[key] = val.tolist()
        elif isinstance(val, dict):
            conf[key] = _array_or_tuple_to_list(conf[key])
        elif isinstance(val, tuple):
            conf[key] = list(val)
    return conf
