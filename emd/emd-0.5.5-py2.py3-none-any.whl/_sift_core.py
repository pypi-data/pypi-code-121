#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Low level functionality for the sift algorithm.

  get_padded_extrema
  compute_parabolic_extrema
  interp_envelope
  zero_crossing_count

"""

import logging

import numpy as np
from scipy import interpolate as interp
from scipy import signal

# Housekeeping for logging
logger = logging.getLogger(__name__)


def get_padded_extrema(X, pad_width=2, mode='peaks', parabolic_extrema=False,
                       loc_pad_opts=None, mag_pad_opts=None, method='rilling'):
    """Identify and pad the extrema in a signal.

    This function returns a set of extrema from a signal including padded
    extrema at the edges of the signal. Padding is carried out using numpy.pad.

    Parameters
    ----------
    X : ndarray
        Input signal
    pad_width : int >= 0
        Number of additional extrema to add to the start and end
    mode : {'peaks', 'troughs', 'abs_peaks', 'both'}
        Switch between detecting peaks, troughs, peaks in the abs signal or
        both peaks and troughs
    method : {'rilling', 'numpypad'}
        Which padding method to use
    parabolic_extrema : bool
        Flag indicating whether extrema positions should be refined by parabolic interpolation
    loc_pad_opts : dict
        Optional dictionary of options to be passed to np.pad when padding extrema locations
    mag_pad_opts : dict
        Optional dictionary of options to be passed to np.pad when padding extrema magnitudes

    Returns
    -------
    locs : ndarray
        location of extrema in samples
    mags : ndarray
        Magnitude of each extrema

    See Also
    --------
    emd.sift.interp_envelope
    emd.sift._pad_extrema_numpy
    emd.sift._pad_extrema_rilling

    Notes
    -----
    The 'abs_peaks' mode is not compatible with the 'rilling' method as rilling
    must identify all peaks and troughs together.

    """
    if (mode == 'abs_peaks') and (method == 'rilling'):
        msg = "get_padded_extrema mode 'abs_peaks' is incompatible with method 'rilling'"
        raise ValueError(msg)

    if X.ndim == 2:
        X = X[:, 0]

    if mode == 'both' or method == 'rilling':
        max_locs, max_ext = _find_extrema(X, parabolic_extrema=parabolic_extrema)
        min_locs, min_ext = _find_extrema(-X, parabolic_extrema=parabolic_extrema)
        min_ext = -min_ext
        logger.debug('found {0} minima and {1} maxima on mode {2}'.format(len(min_locs),
                                                                          len(max_locs),
                                                                          mode))
    elif mode == 'peaks':
        max_locs, max_ext = _find_extrema(X, parabolic_extrema=parabolic_extrema)
        logger.debug('found {0} maxima on mode {1}'.format(len(max_locs),
                                                           mode))
    elif mode == 'troughs':
        max_locs, max_ext = _find_extrema(-X, parabolic_extrema=parabolic_extrema)
        max_ext = -max_ext
        logger.debug('found {0} minima on mode {1}'.format(len(max_locs),
                                                           mode))
    elif mode == 'abs_peaks':
        max_locs, max_ext = _find_extrema(np.abs(X), parabolic_extrema=parabolic_extrema)
        logger.debug('found {0} extrema on mode {1}'.format(len(max_locs),
                                                            mode))
    else:
        raise ValueError('Mode {0} not recognised by get_padded_extrema'.format(mode))

    # Return nothing if we don't have enough extrema
    if (len(max_locs) == 0) or (max_locs.size <= 1):
        logger.debug('Not enough extrema to pad.')
        return None, None
    elif (mode == 'both' or method == 'rilling') and len(min_locs) <= 1:
        logger.debug('Not enough extrema to pad 2.')
        return None, None

    # Run the padding by requested method
    if pad_width == 0:
        if mode == 'both':
            ret = (min_locs, min_ext, max_locs, max_ext)
        elif mode == 'troughs' and method == 'rilling':
            ret = (min_locs, min_ext)
        else:
            ret = (max_locs, max_ext)
    elif method == 'numpypad':
        ret = _pad_extrema_numpy(max_locs, max_ext,
                                 X.shape[0], pad_width,
                                 loc_pad_opts, mag_pad_opts)
        if mode == 'both':
            ret2 = _pad_extrema_numpy(min_locs, min_ext,
                                      X.shape[0], pad_width,
                                      loc_pad_opts, mag_pad_opts)
            ret = (ret2[0], ret2[1], ret[0], ret[1])
    elif method == 'rilling':
        ret = _pad_extrema_rilling(min_locs, max_locs, X, pad_width)
        # Inefficient to use rilling for just peaks or troughs, but handle it
        # just in case.
        if mode == 'peaks':
            ret = ret[2:]
        elif mode == 'troughs':
            ret = ret[:2]

    return ret


def _pad_extrema_numpy(locs, mags, lenx, pad_width, loc_pad_opts, mag_pad_opts):
    """Pad extrema using a direct call to np.pad.

    Extra paddings are carried out if the padded values do not span the whole
    range of the original time-series (defined by lenx)

    Parameters
    ----------
    locs : ndarray
        location of extrema in time
    mags : ndarray
        magnitude of each extrema
    lenx : int
        length of the time-series from which locs and mags were identified
    pad_width : int
        number of extra extrema to pad
    loc_pad_opts : dict
        dictionary of argumnents passed to np.pad to generate new extrema locations
    mag_pad_opts : dict
        dictionary of argumnents passed to np.pad to generate new extrema magnitudes

    Returns
    -------
    ndarray
        location of all extrema (including padded and original points) in time
    ndarray
        magnitude of each extrema (including padded and original points)

    """
    logger.verbose("Padding {0} extrema in signal X {1} using method '{2}'".format(pad_width,
                                                                                   lenx,
                                                                                   'numpypad'))

    if not loc_pad_opts:  # Empty dict evaluates to False
        loc_pad_opts = {'mode': 'reflect', 'reflect_type': 'odd'}
    else:
        loc_pad_opts = loc_pad_opts.copy()  # Don't work in place...
    loc_pad_mode = loc_pad_opts.pop('mode')

    if not mag_pad_opts:  # Empty dict evaluates to False
        mag_pad_opts = {'mode': 'median', 'stat_length': 1}
    else:
        mag_pad_opts = mag_pad_opts.copy()  # Don't work in place...
    mag_pad_mode = mag_pad_opts.pop('mode')

    # Determine how much padding to use
    if locs.size < pad_width:
        pad_width = locs.size

    # Return now if we're not padding
    if (pad_width is None) or (pad_width == 0):
        return locs, mags

    # Pad peak locations
    ret_locs = np.pad(locs, pad_width, loc_pad_mode, **loc_pad_opts)

    # Pad peak magnitudes
    ret_mag = np.pad(mags, pad_width, mag_pad_mode, **mag_pad_opts)

    # Keep padding if the locations don't stretch to the edge
    count = 0
    while np.max(ret_locs) < lenx or np.min(ret_locs) >= 0:
        logger.debug('Padding again - first ext {0}, last ext {1}'.format(np.min(ret_locs), np.max(ret_locs)))
        logger.debug(ret_locs)
        ret_locs = np.pad(ret_locs, pad_width, loc_pad_mode, **loc_pad_opts)
        ret_mag = np.pad(ret_mag, pad_width, mag_pad_mode, **mag_pad_opts)
        count += 1
        #if count > 5:
        #    raise ValueError

    return ret_locs, ret_mag


def _pad_extrema_rilling(indmin, indmax, X, pad_width):
    """Pad extrema using the method from Rilling.

    This is based on original matlab code in boundary_conditions_emd.m
    downloaded from: https://perso.ens-lyon.fr/patrick.flandrin/emd.html

    Unlike the numpypad method - this approach pads both the maxima and minima
    of the signal together.

    Parameters
    ----------
    indmin : ndarray
        location of minima in time
    indmax : ndarray
        location of maxima in time
    X : ndarray
        original time-series
    pad_width : int
        number of extra extrema to pad

    Returns
    -------
    tmin
        location of all minima (including padded and original points) in time
    xmin
        magnitude of each minima (including padded and original points)
    tmax
        location of all maxima (including padded and original points) in time
    xmax
        magnitude of each maxima (including padded and original points)

    """
    logger.debug("Padding {0} extrema in signal X {1} using method '{2}'".format(pad_width,
                                                                                 X.shape,
                                                                                 'rilling'))

    t = np.arange(len(X))

    # Pad START
    if indmax[0] < indmin[0]:
        # First maxima is before first minima
        if X[0] > X[indmin[0]]:
            # First value is larger than first minima - reflect about first MAXIMA
            logger.debug('L: max earlier than min, first val larger than first min')
            lmax = np.flipud(indmax[1:pad_width+1])
            lmin = np.flipud(indmin[:pad_width])
            lsym = indmax[0]
        else:
            # First value is smaller than first minima - reflect about first MINIMA
            logger.debug('L: max earlier than min, first val smaller than first min')
            lmax = np.flipud(indmax[:pad_width])
            lmin = np.r_[np.flipud(indmin[:pad_width-1]), 0]
            lsym = 0

    else:
        # First minima is before first maxima
        if X[0] > X[indmax[0]]:
            # First value is larger than first minima - reflect about first MINIMA
            logger.debug('L: max later than min, first val larger than first max')
            lmax = np.flipud(indmax[:pad_width])
            lmin = np.flipud(indmin[1:pad_width+1])
            lsym = indmin[0]
        else:
            # First value is smaller than first minima - reflect about first MAXIMA
            logger.debug('L: max later than min, first val smaller than first max')
            lmin = np.flipud(indmin[:pad_width])
            lmax = np.r_[np.flipud(indmax[:pad_width-1]), 0]
            lsym = 0

    # Pad STOP
    if indmax[-1] < indmin[-1]:
        # Last maxima is before last minima
        if X[-1] < X[indmax[-1]]:
            # Last value is larger than last minima - reflect about first MAXIMA
            logger.debug('R: max earlier than min, last val smaller than last max')
            rmax = np.flipud(indmax[-pad_width:])
            rmin = np.flipud(indmin[-pad_width-1:-1])
            rsym = indmin[-1]
        else:
            # First value is smaller than first minima - reflect about first MINIMA
            logger.debug('R: max earlier than min, last val larger than last max')
            rmax = np.r_[X.shape[0] - 1, np.flipud(indmax[-(pad_width-2):])]
            rmin = np.flipud(indmin[-(pad_width-1):])
            rsym = X.shape[0] - 1

    else:
        if X[-1] > X[indmin[-1]]:
            # Last value is larger than last minima - reflect about first MAXIMA
            logger.debug('R: max later than min, last val larger than last min')
            rmax = np.flipud(indmax[-pad_width-1:-1])
            rmin = np.flipud(indmin[-pad_width:])
            rsym = indmax[-1]
        else:
            # First value is smaller than first minima - reflect about first MINIMA
            logger.debug('R: max later than min, last val smaller than last min')
            rmax = np.flipud(indmax[-(pad_width-1):])
            rmin = np.r_[X.shape[0] - 1, np.flipud(indmin[-(pad_width-2):])]
            rsym = X.shape[0] - 1

    # Extrema values are ordered from largest to smallest,
    # lmin and lmax are the samples of the first {pad_width} extrema
    # rmin and rmax are the samples of the final {pad_width} extrema

    # Compute padded samples
    tlmin = 2 * lsym - lmin
    tlmax = 2 * lsym - lmax
    trmin = 2 * rsym - rmin
    trmax = 2 * rsym - rmax

    # tlmin and tlmax are the samples of the left/first padded extrema, in ascending order
    # trmin and trmax are the samples of the right/final padded extrema, in ascending order

    # Flip again if needed - don't really get what this is doing, will trust the source...
    if (tlmin[0] >= t[0]) or (tlmax[0] >= t[0]):
        msg = 'Flipping start again - first min: {0}, first max: {1}, t[0]: {2}'
        logger.debug(msg.format(tlmin[0], tlmax[0], t[0]))
        if lsym == indmax[0]:
            lmax = np.flipud(indmax[:pad_width])
        else:
            lmin = np.flipud(indmin[:pad_width])
        lsym = 0
        tlmin = 2*lsym-lmin
        tlmax = 2*lsym-lmax

        if tlmin[0] >= t[0]:
            raise ValueError('Left min not padded enough. {0} {1}'.format(tlmin[0], t[0]))
        if tlmax[0] >= t[0]:
            raise ValueError('Left max not padded enough. {0} {1}'.format(trmax[0], t[0]))

    if (trmin[-1] <= t[-1]) or (trmax[-1] <= t[-1]):
        msg = 'Flipping end again - last min: {0}, last max: {1}, t[-1]: {2}'
        logger.debug(msg.format(trmin[-1], trmax[-1], t[-1]))
        if rsym == indmax[-1]:
            rmax = np.flipud(indmax[-pad_width-1:-1])
        else:
            rmin = np.flipud(indmin[-pad_width-1:-1])
        rsym = len(X)
        trmin = 2*rsym-rmin
        trmax = 2*rsym-rmax

        if trmin[-1] <= t[-1]:
            raise ValueError('Right min not padded enough. {0} {1}'.format(trmin[-1], t[-1]))
        if trmax[-1] <= t[-1]:
            raise ValueError('Right max not padded enough. {0} {1}'.format(trmax[-1], t[-1]))

    # Stack and return padded values
    ret_tmin = np.r_[tlmin, t[indmin], trmin]
    ret_tmax = np.r_[tlmax, t[indmax], trmax]

    ret_xmin = np.r_[X[lmin], X[indmin], X[rmin]]
    ret_xmax = np.r_[X[lmax], X[indmax], X[rmax]]

    # Quick check that interpolation won't explode
    if np.all(np.diff(ret_tmin) > 0) is False:
        logger.warning('Minima locations not strictly ascending - interpolation will break')
        raise ValueError('Extrema locations not strictly ascending!!')
    if np.all(np.diff(ret_tmax) > 0) is False:
        logger.warning('Maxima locations not strictly ascending - interpolation will break')
        raise ValueError('Extrema locations not strictly ascending!!')

    return ret_tmin, ret_xmin, ret_tmax, ret_xmax


def _find_extrema(X, peak_prom_thresh=None, parabolic_extrema=False):
    """Identify extrema within a time-course.

    This function detects extrema using a scipy.signals.argrelextrema. Extrema
    locations can be refined by parabolic intpolation and optionally
    thresholded by peak prominence.

    Parameters
    ----------
    X : ndarray
       Input signal
    peak_prom_thresh : {None, float}
       Only include peaks which have prominences above this threshold or None
       for no threshold (default is no threshold)
    parabolic_extrema : bool
        Flag indicating whether peak estimation should be refined by parabolic
        interpolation (default is False)

    Returns
    -------
    locs : ndarray
        Location of extrema in samples
    extrema : ndarray
        Value of each extrema

    """
    ext_locs = signal.argrelextrema(X, np.greater, order=1)[0]

    if len(ext_locs) == 0:
        return np.array([]), np.array([])

    if peak_prom_thresh is not None:
        prom, _, _ = signal._peak_finding.peak_prominences(X, ext_locs, wlen=3)
        keeps = np.where(prom > peak_prom_thresh)[0]
        ext_locs = ext_locs[keeps]

    if parabolic_extrema:
        y = np.c_[X[ext_locs-1], X[ext_locs], X[ext_locs+1]].T
        ext_locs, max_pks = compute_parabolic_extrema(y, ext_locs)
        return ext_locs, max_pks
    else:
        return ext_locs, X[ext_locs]


def compute_parabolic_extrema(y, locs):
    """Compute a parabolic refinement extrema locations.

    Parabolic refinement is computed from in triplets of points based on the
    method described in section 3.2.1 from Rato 2008 [1]_.

    Parameters
    ----------
    y : array_like
        A [3 x nextrema] array containing the points immediately around the
        extrema in a time-series.
    locs : array_like
        A [nextrema] length vector containing x-axis positions of the extrema

    Returns
    -------
    numpy array
        The estimated y-axis values of the interpolated extrema
    numpy array
        The estimated x-axis values of the interpolated extrema

    References
    ----------
    .. [1] Rato, R. T., Ortigueira, M. D., & Batista, A. G. (2008). On the HHT,
    its problems, and some solutions. Mechanical Systems and Signal Processing,
    22(6), 1374–1394. https://doi.org/10.1016/j.ymssp.2007.11.028

    """
    # Parabola equation parameters for computing y from parameters a, b and c
    # w = np.array([[1, 1, 1], [4, 2, 1], [9, 3, 1]])
    # ... and its inverse for computing a, b and c from y
    w_inv = np.array([[.5, -1, .5], [-5/2, 4, -3/2], [3, -3, 1]])
    abc = w_inv.dot(y)

    # Find co-ordinates of extrema from parameters abc
    tp = - abc[1, :] / (2*abc[0, :])
    t = tp - 2 + locs
    y_hat = tp*abc[1, :]/2 + abc[2, :]

    return t, y_hat


def interp_envelope(X, mode='both', interp_method='splrep', extrema_opts=None,
                    ret_extrema=False, trim=True):
    """Interpolate the amplitude envelope of a signal.

    Parameters
    ----------
    X : ndarray
        Input signal
    mode : {'upper','lower','combined'}
         Flag to set which envelope should be computed (Default value = 'upper')
    interp_method : {'splrep','pchip','mono_pchip'}
         Flag to indicate which interpolation method should be used (Default value = 'splrep')

    Returns
    -------
    ndarray
        Interpolated amplitude envelope

    """
    if not extrema_opts:  # Empty dict evaluates to False
        extrema_opts = {'pad_width': 2,
                        'loc_pad_opts': None,
                        'mag_pad_opts': None}
    else:
        extrema_opts = extrema_opts.copy()  # Don't work in place...

    logger.debug("Interpolating '{0}' with method '{1}'".format(mode, interp_method))

    if interp_method not in ['splrep', 'mono_pchip', 'pchip']:
        raise ValueError("Invalid interp_method value")

    if mode == 'upper':
        extr = get_padded_extrema(X, mode='peaks', **extrema_opts)
    elif mode == 'lower':
        extr = get_padded_extrema(X, mode='troughs', **extrema_opts)
    elif (mode == 'both') or (extrema_opts.get('method', '') == 'rilling'):
        extr = get_padded_extrema(X, mode='both', **extrema_opts)
    elif mode == 'combined':
        extr = get_padded_extrema(X, mode='abs_peaks', **extrema_opts)
    else:
        raise ValueError('Mode not recognised. Use mode= \'upper\'|\'lower\'|\'combined\'')

    if extr[0] is None:
        if mode == 'both':
            return None, None
        else:
            return None

    if mode == 'both':
        lower = _run_scipy_interp(extr[0], extr[1],
                                  lenx=X.shape[0], trim=trim,
                                  interp_method=interp_method)
        upper = _run_scipy_interp(extr[2], extr[3],
                                  lenx=X.shape[0], trim=trim,
                                  interp_method=interp_method)
        env = (upper, lower)
    else:
        env = _run_scipy_interp(extr[0], extr[1], lenx=X.shape[0], interp_method=interp_method, trim=trim)

    if ret_extrema:
        return env, extr
    else:
        return env


def _run_scipy_interp(locs, pks, lenx, interp_method='splrep', trim=True):

    # Run interpolation on envelope
    t = np.arange(locs[0], locs[-1])
    if interp_method == 'splrep':
        f = interp.splrep(locs, pks)
        env = interp.splev(t, f)
    elif interp_method == 'mono_pchip':
        pchip = interp.PchipInterpolator(locs, pks)
        env = pchip(t)
    elif interp_method == 'pchip':
        pchip = interp.pchip(locs, pks)
        env = pchip(t)

    if trim:
        t_max = np.arange(locs[0], locs[-1])
        tinds = np.logical_and((t_max >= 0), (t_max < lenx))
        env = np.array(env[tinds])

        if env.shape[0] != lenx:
            msg = 'Envelope length does not match input data {0} {1}'
            raise ValueError(msg.format(env.shape[0], lenx))

    return env


def zero_crossing_count(X):
    """Count the number of zero-crossings within a time-course.

    Zero-crossings are counted through differentiation of the sign of the
    signal.

    Parameters
    ----------
    X : ndarray
        Input array

    Returns
    -------
    int
        Number of zero-crossings

    """
    if X.ndim == 2:
        X = X[:, None]

    return (np.diff(np.sign(X), axis=0) != 0).sum(axis=0)
