#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Routines relating to frequency transforms and power-spectra.

Frequency Transform Routines:
  frequency_transform
  quadrature_transform
  phase_from_complex_signal
  freq_from_phase
  phase_from_freq
  phase_angle

Power Spectra:
  holospectrum
  hilberthuang
  hilberthuang_1d

Power Spectra Helpers:
  define_hist_bins
  define_hist_bins_from_data

"""

import logging

import numpy as np
import sparse
from scipy import ndimage, signal

from . import cycles, imftools
from ._sift_core import interp_envelope
from .support import ensure_2d, ensure_equal_dims, ensure_vector

# Housekeeping for logging
logger = logging.getLogger(__name__)

# Sential value for observations outside histogram range
DROP_SENTINAL = np.iinfo(np.int32).min

##


def frequency_transform(imf, sample_rate, method, smooth_freq=3,
                        smooth_phase=5):
    """Compute instantaneous phase, frequency and amplitude from a set of IMFs.

    Several approaches are implemented from [1]_ and [2]_.

    Parameters
    ----------
    imf : ndarray
        Input array of IMFs.
    sample_rate : float
        Sampling frequency of the signal in Hz
    method : {'hilbert','quad','direct_quad','nht'}
        The method for computing the frequency stats
    smooth_phase : int
         Length of window when smoothing the unwrapped phase (Default value = 31)

    Returns
    -------
    IP : ndarray
        Array of instantaneous phase estimates
    IF : ndarray
        Array of instantaneous frequency estimates
    IA : ndarray
        Array of instantaneous amplitude estimates

    References
    ----------
    .. [1] Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng,
       Q., … Liu, H. H. (1998). The empirical mode decomposition and the Hilbert
       spectrum for nonlinear and non-stationary time series analysis. Proceedings
       of the Royal Society of London. Series A: Mathematical, Physical and
       Engineering Sciences, 454(1971), 903–995.
       https://doi.org/10.1098/rspa.1998.0193
    .. [2] Huang, N. E., Wu, Z., Long, S. R., Arnold, K. C., Chen, X., & Blank,
       K. (2009). On Instantaneous Frequency. Advances in Adaptive Data Analysis,
       1(2), 177–229. https://doi.org/10.1142/s1793536909000096

    """
    logger.info('STARTED: compute frequency stats')

    imf = ensure_2d([imf], ['imf'], 'frequency_transform')
    logger.debug('computing on {0} samples over {1} imfs at sample rate {2}'.format(imf.shape[0],
                                                                                    imf.shape[1],
                                                                                    sample_rate))

    # Each case here should compute the analytic form of the imfs and the
    # instantaneous amplitude.
    if method == 'hilbert':
        logger.info('Using Hilbert transform')

        analytic_signal = signal.hilbert(imf, axis=0)

        # Estimate instantaneous amplitudes directly from analytic signal
        iamp = np.abs(analytic_signal)

    elif method == 'nht':
        logger.info('Using Amplitude-Normalised Hilbert transform')

        n_imf = imftools.amplitude_normalise(imf)
        analytic_signal = signal.hilbert(n_imf, axis=0)

        orig_dim = imf.ndim
        if imf.ndim == 2:
            imf = imf[:, :, None]

        # Estimate inst amplitudes with spline interpolation
        iamp = np.zeros_like(imf)
        for ii in range(imf.shape[1]):
            for jj in range(imf.shape[2]):
                iamp[:, ii, jj] = interp_envelope(imf[:, ii, jj],
                                                  mode='upper')
        if orig_dim == 2:
            iamp = iamp[:, :, 0]

    elif method == 'ctrl':
        logger.info('Using Control Points - CURRENTLY BROKEN')

        orig_dim = imf.ndim
        if imf.ndim == 2:
            imf = imf[:, :, None]

        # Get phase from control points
        iphase = np.zeros_like(imf)
        for ii in range(imf.shape[1]):
            for jj in range(imf.shape[2]):
                good_cycles = cycles.get_cycle_inds_from_waveform(imf[:, ii, jj], cycle_start='asc')
                ctrl = cycles.get_control_points(imf[:, ii, jj], good_cycles)
                iphase[:, ii, jj] = phase_from_control_points(ctrl, good_cycles)
                iphase[:, ii, jj] = np.unwrap(iphase[:, ii, jj])

        # Estimate inst amplitudes with spline interpolation
        iamp = np.zeros_like(imf)
        for ii in range(imf.shape[1]):
            for jj in range(imf.shape[2]):
                iamp[:, ii, jj] = interp_envelope(imf[:, ii, jj],
                                                  mode='upper')

        if orig_dim == 2:
            iamp = iamp[:, :, 0]
            iphase = iphase[:, :, 0]

    elif method == 'quad':
        logger.info('Using Quadrature transform')

        analytic_signal = quadrature_transform(imf)

        orig_dim = imf.ndim
        if imf.ndim == 2:
            imf = imf[:, :, None]

        # Estimate inst amplitudes with spline interpolation
        iamp = np.zeros_like(imf)
        for ii in range(imf.shape[1]):
            for jj in range(imf.shape[2]):
                iamp[:, ii, jj] = interp_envelope(imf[:, ii, jj],
                                                  mode='upper')

        if orig_dim == 2:
            iamp = iamp[:, :, 0]

    elif method == 'direct_quad':
        logger.info('Using Direct-Quadrature transform')
        raise ValueError('direct_quad method is broken!')

        n_imf = imftools.amplitude_normalise(imf.copy())
        iphase = np.unwrap(phase_angle(n_imf))

        iamp = np.zeros_like(imf)
        for ii in range(imf.shape[1]):
            iamp[:, ii] = interp_envelope(imf[:, ii, None], mode='combined')

    else:
        logger.error("Method '{0}' not recognised".format(method))
        raise ValueError("Method '{0}' not recognised\nPlease use one of 'hilbert','nht' or 'quad'".format(method))

    if method != 'ctrl':
        # Compute unwrapped phase for frequency estimation
        iphase = phase_from_complex_signal(analytic_signal,
                                           smoothing=smooth_phase,
                                           ret_phase='unwrapped')

    # Compute inst. freq from phase
    ifreq = freq_from_phase(iphase, sample_rate, savgol_width=smooth_freq)

    # Return wrapped phase
    iphase = imftools.wrap_phase(iphase)

    logger.info('COMPLETED: compute frequency stats. Returning {0} imfs'.format(iphase.shape[1]))
    return iphase, ifreq, iamp

#%% -----------------------------------------------------
# Frequency stat utils


def quadrature_transform(X, fix_zerocrossings=False):
    """Compute the quadrature transform on a set of time-series.

    This algorithm is defined in equation 34 of [1]_. The return is a complex
    array with the input data as the real part and the quadrature transform as
    the imaginary part.

    Parameters
    ----------
    X : ndarray
        Array containing time-series to transform

    Returns
    -------
    quad_signal : ndarray
        Complex valued array containing the quadrature transformed signal

    References
    ----------
    .. [1] Huang, N. E., Wu, Z., Long, S. R., Arnold, K. C., Chen, X., & Blank,
       K. (2009). On Instantaneous Frequency. Advances in Adaptive Data Analysis,
       1(2), 177–229. https://doi.org/10.1142/s1793536909000096

    """
    nX = imftools.amplitude_normalise(X.copy(), clip=False)
    nX = nX / (np.abs(nX).max() + 1e-8)  # Clip any remaining points outside -1 < x < 1

    # Avoid occasional 'invalid value encountered' RuntimeWarning in sqrt using
    # where argument in ufunc
    tmp = 1 - nX**2
    good_vals = (tmp != 0) & (np.isnan(tmp) == False)  # noqa: E712
    imagX = np.sqrt(tmp, out=tmp, where=good_vals)

    # Add warning here....
    if np.all(np.isreal(imagX)) == False:  # noqa: E712
        imagX = imagX.real

    mask = ((np.diff(nX, axis=0) > 0) * -2) + 1
    mask[mask == 0] = -1
    mask = np.r_[mask, mask[-1, None, :]]

    q = imagX * mask

    if fix_zerocrossings:
        q = _fix_quadrature_zero_crossings(q)

    return nX + 1j * q


def _fix_quadrature_zero_crossings(quad):
    """Numerical 'fix' for instability around zero in quadrature signals.

    EXPERIMENTAL WORK-IN-PROGRESS FUNCTION!! Use with caution.

    Replaces sample closest to zero with the average of the four surrounding
    points. This is needed as the direct quadrature method involves squaring
    the raw signal - this is normally fine but explodes when close to zero.

    """
    quad_fix = quad.copy()

    for ii in range(quad.shape[1]):
        # Find all zero crossings
        zc = np.where(np.diff(np.sign(quad[:, ii]), axis=0) != 0)[0]
        # Drop crossings we don't have surrounding samples for
        zc = zc[(zc >= 1) & (zc < quad.shape[0]-3)]
        # Delay-embedding array around zero-crossing
        zz = np.vstack((quad[zc-1, ii],
                        quad[zc, ii],
                        quad[zc+1, ii],
                        quad[zc+2, ii],
                        quad[zc+3, ii])).T

        # Take a copy for output and replace 'fixed' zero-crossing point.
        quad_fix[zc+1, ii] = zz[:, np.array((0, 4))].mean(axis=1)
        quad_fix[zc, ii] = np.average(zz[:, np.array((0, 4))], weights=[3/4, 1/4], axis=1)
        quad_fix[zc+2, ii] = np.average(zz[:, np.array((0, 4))], weights=[1/4, 3/4], axis=1)

    quad_fix = ndimage.median_filter(quad_fix, (7, 1))

    return quad_fix


def phase_from_complex_signal(complex_signal, smoothing=None,
                              ret_phase='wrapped', phase_jump='ascending'):
    """Compute the instantaneous phase from a complex signal.

    The complex input may be obtained from either the Hilbert Transform or by
    Direct Quadrature.

    Parameters
    ----------
    complex_signal : complex ndarray
        Complex valued input array
    smoothing : int
         Integer window length used in phase smoothing (Default value = None)
    ret_phase : {'wrapped','unwrapped'}
         Flag indicating whether to return the wrapped or unwrapped phase (Default value = 'wrapped')
    phase_jump : {'ascending','peak','descending','trough'}
         Flag indicating where in the cycle the phase jump should be (Default value = 'ascending')

    Returns
    -------
    IP : ndarray
        Array of instantaneous phase values

    """
    # Compute unwrapped phase
    iphase = np.unwrap(np.angle(complex_signal), axis=0)

    orig_dim = iphase.ndim
    if iphase.ndim == 2:
        iphase = iphase[:, :, None]

    # Apply smoothing if requested
    if smoothing is not None:
        for ii in range(iphase.shape[1]):
            for jj in range(iphase.shape[2]):
                iphase[:, ii, jj] = signal.medfilt(iphase[:, ii, jj], smoothing)

    if orig_dim == 2:
        iphase = iphase[:, :, 0]

    # Set phase jump point to requested part of cycle
    if phase_jump == 'ascending':
        iphase = iphase + np.pi / 2
    elif phase_jump == 'peak':
        pass  # do nothing
    elif phase_jump == 'descending':
        iphase = iphase - np.pi / 2
    elif phase_jump == 'trough':
        iphase = iphase + np.pi

    if ret_phase == 'wrapped':
        return imftools.wrap_phase(iphase)
    elif ret_phase == 'unwrapped':
        return iphase


def freq_from_phase(iphase, sample_rate, savgol_width=3):
    """Compute the instantaneous frequency from the instantaneous phase.

    A savitsky-golay filter is used to compute the derivative of the phase and
    can be smoothed by specifying a longer savgol_width (minimum value=3).

    Parameters
    ----------
    iphase : ndarray
        Input array containing the unwrapped instantaneous phase time-course
    sample_rate : float
        The sampling frequency of the data
    savgol_width : int >= 3
        The window length of the Savitsky-Golay filter window

    Returns
    -------
    IF : ndarray
        Array containing the instantaneous frequencies

    """
    # Differential of instantaneous phase
    iphase = signal.savgol_filter(iphase, savgol_width, 1, deriv=1, axis=0)

    # Convert to freq
    ifrequency = iphase / (2.0 * np.pi) * sample_rate

    return ifrequency


def phase_from_freq(ifrequency, sample_rate, phase_start=-np.pi):
    """Compute the instantaneous phase of a signal from its instantaneous frequency.

    Parameters
    ----------
    ifrequency : ndarray
        Input array containing the instantaneous frequencies of a signal
    sample_rate : float
        The sampling frequency of the data
    phase_start : float
         Start value of the phase output (Default value = -np.pi)

    Returns
    -------
    IP : ndarray
        The instantaneous phase of the signal

    """
    iphase_diff = (ifrequency / sample_rate) * (2 * np.pi)

    iphase = phase_start + np.cumsum(iphase_diff, axis=0)

    return iphase


def phase_from_control_points(ctrl, cycles):
    """Compute instantaneous phase from control points."""
    from scipy import interpolate as interp

    cycles = ensure_vector([cycles],
                           ['cycles'],
                           'phase_from_control_points')

    ip = np.zeros_like(cycles, dtype=float)
    phase_y = np.array([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])

    for jj in range(1, cycles.max() + 1):

        if np.any(np.isnan(ctrl[jj-1, :])):
            continue

        f = interp.interp1d(ctrl[jj-1, :], phase_y, kind='linear')
        ph = f(np.arange(0, ctrl[jj-1, -1] + 1))

        ip[cycles == jj] = ph

    return ip


def direct_quadrature(fm):
    """Compute the quadrature transform on a set of time-series.

    This algorithm is  defined in equation 35 of [1].

    Section 3.2 of 'on instantaneous frequency'

    THIS IS IN DEVELOPMENT

    Parameters
    ----------
    fm : ndarray
        Input signal containing a frequency-modulated signal

    References
    ----------
    .. [1] Huang, N. E., Wu, Z., Long, S. R., Arnold, K. C., Chen, X., & Blank,
       K. (2009). On Instantaneous Frequency. Advances in Adaptive Data Analysis,
       1(2), 177–229. https://doi.org/10.1142/s1793536909000096

    """
    ph = phase_angle(fm)

    # We'll have occasional nans where fm==1 or -1
    inds = np.argwhere(np.isnan(ph))

    vals = (ph[inds[:, 0] - 1, :] + ph[inds[:, 0] + 1, :]) / 2
    ph[inds[:, 0]] = vals

    return ph


def phase_angle(fm):
    """Compute the phase angle of a set of time-series.

    This algorithm is defined in equation 35 of [1]_.

    THIS IS IN DEVELOPMENT

    Parameters
    ----------
    X : ndarray
        Array containing time-series to transform

    Returns
    -------
    quad_signal : ndarray
        Complex valued array containing the quadrature transformed signal

    References
    ----------
    .. [1] Huang, N. E., Wu, Z., Long, S. R., Arnold, K. C., Chen, X., & Blank,
       K. (2009). On Instantaneous Frequency. Advances in Adaptive Data Analysis,
       1(2), 177–229. https://doi.org/10.1142/s1793536909000096

    """
    return np.arctan(fm / np.lib.scimath.sqrt(1 - np.power(fm, 2)))

#%% -----------------------------------------------------
# Time-frequency spectra


def hilberthuang(IF, IA, edges=None,
                 sum_time=True,
                 sum_imfs=True,
                 mode='power',
                 sample_rate=1,
                 scaling=None,
                 return_sparse=False,
                 return_Gb_limit=10):
    """Compute a Hilbert-Huang transform (HHT).

    The Hilbert-Huang transform takes the instataneous frequency and
    instantaneous amplitude of a time-series and represents the energy of a
    signal across time and frequency [1]_.

    The full Hilbert-Huang array is 3-dimensional [nfrequencies x ntimes x nimfs].
    By default, the returned holospectrum is summed across time and IMFs,
    returning only the frequency dimension.- this behaviour can be tuned with
    the sum_time and sum_imfs arguments. Setting return_sparse to True is
    strongly recommended returning very large arrays.

    Parameters
    ----------
    IF : ndarray
        2D first level instantaneous frequencies
    IA : ndarray
        2D first level instantaneous amplitudes
    edges : {ndarray, tuple or None}
        Definition of the frequency bins used in the spectrum. This may be:

        * array_like vector of bin edge values (as defined by
        emd.spectra.define_hist_bins)

        * a tuple of values that can be passed to emd.spectra.define_hist_bins
        (eg edges=(1,50,49) will define 49 bins between 1 and 50Hz)

        * None in which case a sensible set of bins will be defined from the
        input data (this is the default option)
    sum_time : boolean
        Flag indicating whether to sum across time dimension
    sum_imfs : boolean
        Flag indicating whether to sum across IMF dimension
    mode : {'power','amplitude'}
         Flag indicating whether to sum the power or amplitudes (Default value = 'energy')
    scaling : {'density', 'spectrum', None}
        Switch specifying the normalisation or scaling applied to the spectrum.
    sample_rate : float
        Sampling rate of the data used in 'density' scaling
    return_sparse : bool
         Flag indicating whether to return the full or sparse form(Default value = True)
    return_Gb_limit : {float, None}
        Maximum array size in Gb that will be returned if a non-sparse/dense
        array is being returned (default = 10). If the function return would
        exceed this size, the function will raise an error. If set to None,
        then no limit is imposed. Sparse arrays are always returned.

    Returns
    -------
    f : ndarray
        Vector of histogram bin centers for each frequency
    hht : ndarray
        2D array containing the Hilbert-Huang Transform

    Notes
    -----
    Run a HHT with an automatically generated set of histogram bins:

    >>> f, hht = emd.spectra.hilberthuang(IF, IA, sample_rate=512)

    Run a HHT and return the spectrum for each IMF separately

    >>> f, hht = emd.spectra.hilberthuang(IF, IA,, sample_rate=512, sum_imfs=False)

    Run a HHT with 49 bins, linearly spaced between 1 and 50Hz

    >>> f, hht = emd.spectra.hilberthuang(IF, IA, edges=(1, 50, 49), sample_rate=512)

    Run a HHT with 49 bins, logarithmically spaced between 0.001 and 50Hz

    >>> f, hht = emd.spectra.hilberthuang(IF, IA, edges=(1, 50, 49, 'log'), sample_rate=512)

    Run a HHT with an externally generated set of histogram bin edges

    >>> my_edges = np.array([0.5, 2, 5, 11, 22])
    >>> f, hht = emd.spectra.hilberthuang(IF, IA, edges=my_edges sample_rate=512)

    Run a HHT and return the full time dimension - the HHT is summed over time by default

    >>> f, hht = emd.spectra.hilberthuang(IF, IA, edges=(1, 50, 49), sample_rate=512, sum_time=False)

    Run a HHT and return a memory efficient sparse array - this is strongly
    recommended for very large HHTs

    >>> f, hht = emd.spectra.hilberthuang(IF, IA, edges=(1, 50, 49), sample_rate=512,
    >>>                                   sum_time=False, return_sparse=True)

    If return_sparse is set to True the returned array is a sparse matrix in
    COOrdinate form using sparse package (sparse.COO). This is much more memory
    efficient than the full form but may not behave as expected in all
    functions expecting full arrays.

    References
    ----------
    .. [1] Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng,
       Q., … Liu, H. H. (1998). The empirical mode decomposition and the Hilbert
       spectrum for nonlinear and non-stationary time series analysis. Proceedings
       of the Royal Society of London. Series A: Mathematical, Physical and
       Engineering Sciences, 454(1971), 903–995.
       https://doi.org/10.1098/rspa.1998.0193

    """
    # Housekeeeping
    IF, IA = ensure_2d([IF, IA], ['IF', 'IA'], 'hilberthuang')
    ensure_equal_dims((IF, IA), ('IF', 'IA'), 'hilberthuang')

    logger.info('STARTED: compute Hilbert-Huang Transform')
    logger.debug('computing on {0} samples over {1} IMFs '.format(IF.shape[0],
                                                                  IF.shape[1]))
    edges, bins = _histogram_bin_relay(edges, IF.flatten())
    logger.debug('Freq bins: {0} to {1} in {2} steps'.format(edges[0],
                                                             edges[-1],
                                                             len(edges)))

    # Begin computation
    spec = _base_spectra(IF, IA, edges)

    sum_dims = np.where([0, sum_time, sum_imfs])[0]

    spec = _post_process_spectra(spec, sum_dims=sum_dims,
                                 mode=mode, time_dim=1,
                                 sample_rate=sample_rate, scaling=scaling,
                                 return_sparse=False, return_Gb_limit=return_Gb_limit)

    logger.info('COMPLETED: Hilbert-Huang Transform - output size {0}'.format(spec.shape))
    return bins, spec


def holospectrum(IF, IF2, IA2,
                 edges=None, edges2=None,
                 sum_time=True,
                 sum_first_imfs=True,
                 sum_second_imfs=True,
                 mode='power',
                 sample_rate=1,
                 scaling=None,
                 return_sparse=False,
                 return_Gb_limit=10):
    """Compute a Holospectrum.

    Holospectra are computed from the first and second layer frequecy
    statistics of a dataset. The Holospectrum represents the energy of a signal
    across time, carrier frequency and amplitude-modulation frequency [1]_.

    The full Holospctrum is a 5-dimensional array:
    [nfrequencise x namplitude_frequencies x time x first_imfs x second_imfs]
    By default, the returned holospectrum is summed across time and IMFs,
    returning only the first two dimensions - this behaviour can be tuned with
    the sum_time, sum_first_imfs and sum_second_imfs arguments.

    WARNING: returning the full Holospectrum can create some enormous arrays!
    Setting return_sparse=True is VERY strongly recommended if you want to work
    with the raw time and IMF dimensions.

    Parameters
    ----------
    IF : ndarray
        2D first level instantaneous frequencies
    IF2 : ndarray
        3D second level instantaneous frequencies
    IA2 : ndarray
        3D second level instantaneous amplitudes
    edges : {ndarray, tuple or None}
        Definition of the frequency bins used for carrier frequencies in the
        spectrum. This may be:

        * array_like vector of bin edge values (as defined by
        emd.spectra.define_hist_bins)

        * a tuple of values that can be passed to emd.spectra.define_hist_bins
        (eg edges=(1,50,49) will define 49 bins between 1 and 50Hz)

        * None in which case a sensible set of bins will be defined from the
        input data (this is the default option)
    edges2 : {ndarray, tuple or None}
        Definition of the frequency bins used for amplitude modulation
        frequencies in the spectrum. The options are the same as for `edges`.
    sum_time : boolean
        Flag indicating whether to sum across time dimension
    sum_first_imfs : boolean
        Flag indicating whether to sum across first-layer IMF dimension
    sum_second_imfs : boolean
        Flag indicating whether to sum across the second-layer IMF dimension
    mode : {'power','amplitude'}
         Flag indicating whether to sum the power or amplitude (Default value = 'power')
    scaling : {'density', 'spectrum', None}
        Switch specifying the normalisation or scaling applied to the spectrum.
    sample_rate : float
        Sampling rate of the data used in 'density' scaling
    return_sparse : boolean
        Flag indicating whether to return a sparse or dense (normal numpy) array.
    return_Gb_limit : {float, None}
        Maximum array size in Gb that will be returned if a non-sparse/dense
        array is being returned (default = 10). If the function return would
        exceed this size, the function will raise an error. If set to None,
        then no limit is imposed. Sparse arrays are always returned.

    Returns
    -------
    f_carrier : ndarray
        Vector of histogram bin centers for each carrier (first-level) frequency
    f_am : ndarray
        Vector of histogram bin centers for each amplitude modulation
        (second-level) frequency
    holo : ndarray
        Holospectrum of input data.

    Notes
    -----
    Run a Holospectrum with an automatically generated set of histogram bins:

    >>> fcarrier, fam, holo = emd.spectra.holospectrum(IF, IA, sample_rate=512)

    Run a Holospectrum and return the spectrum for each first and second level IMF separately

    >>> fcarrier, fam, holo = emd.spectra.holospectrum(IF, IA, sample_rate=512,
    >>>                                                sum_first_imfs=False, sum_second_imfs=False)

    Run a Holospectrum with 49 carrier frequency bins linearly spaced between 1
    and 50Hz and 32 amplitude modulation frequency bins logarithmicly spaced
    between 0.1 and 20Hz

    >>> fcarrier, fam, holo = emd.spectra.holospectrum(IF, IA, sample_rate=512,
    >>>                                                edges=(1, 50, 49),
    >>>                                                edges2=(0.1, 20, 32, 'log'))

    Run a Holospectrum without summing over the time dimensions and return the
    result in a memory efficient sparse array - this is strongly recommended
    for very large HHTs

    >>> fcarrier, fam, holo = emd.spectra.holospectrum(IF, IA, sample_rate=512,
    >>>                                                edges=(1, 50, 49),
    >>>                                                edges2=(0.1, 20, 32, 'log',
    >>>                                                sum_time=False, return_sparse=True)

    If return_sparse is set to True the returned array is a sparse matrix in
    COOrdinate form using sparse package (sparse.COO). This is much more memory
    efficient than the full form but may not behave as expected in all
    functions expecting full arrays.

    References
    ----------
    .. [1] Huang, N. E., Hu, K., Yang, A. C. C., Chang, H.-C., Jia, D., Liang,
       W.-K., … Wu, Z. (2016). On Holo-Hilbert spectral analysis: a full
       informational spectral representation for nonlinear and non-stationary
       data. Philosophical Transactions of the Royal Society A: Mathematical,
       Physical and Engineering Sciences, 374(2065), 20150206.
       https://doi.org/10.1098/rsta.2015.0206

    """
    # Housekeeping
    logger.info('STARTED: compute Holospectrum')

    out = ensure_2d((IF, IF2, IA2), ('IF', 'IF2', 'IA2'), 'holospectrum')
    IF, IF2, IA2 = out
    ensure_equal_dims((IF, IF2, IA2), ('IF', 'IF2', 'IA2'), 'holospectrum', dim=0)
    ensure_equal_dims((IF, IF2, IA2), ('IF', 'IF2', 'IA2'), 'holospectrum', dim=1)

    msg = 'computing on {0} samples over {1} first-level IMFs and {2} second level IMFs'
    logger.debug(msg.format(IF2.shape[0], IF2.shape[1], IF2.shape[2]))

    edges, bins = _histogram_bin_relay(edges, IF.flatten())
    logger.debug('First level freq bins: {0} to {1} in {2} steps'.format(edges[0],
                                                                         edges[-1],
                                                                         len(edges)))
    edges2, bins2 = _histogram_bin_relay(edges2, IF2.flatten())
    logger.debug('Second level freq bins: {0} to {1} in {2} steps'.format(edges2[0],
                                                                          edges2[-1],
                                                                          len(edges2)))

    # Begin computation
    holo = _higher_order_spectra(IF, IF2, IA2, edges, edges2)

    sum_dims = np.where([0, 0, sum_time, sum_first_imfs, sum_second_imfs])[0]

    holo = _post_process_spectra(holo, sum_dims=sum_dims,
                                 mode='power', time_dim=2,
                                 sample_rate=sample_rate, scaling=scaling,
                                 return_sparse=False, return_Gb_limit=return_Gb_limit)

    logger.info('COMPLETED: Holospectrum - output size {0}'.format(holo.shape))
    return bins, bins2, holo


def hilbertmarginal(IF, IA, order=2,
                    freq_edges=None, amp_edges=None,
                    sum_time=True, sum_imfs=True,
                    sample_rate=1, scaling=None,
                    return_sparse=False,
                    return_Gb_limit=10):
    """Compute a generalised Hilbert marginal spectrum.

    This is an experimental function which probably implements the method
    introduced in Huang et al (2008) _[1]. This creates a 2D
    amplitude-frequency representation of the signal.

    Parameters
    ----------
    IF : ndarray
        2D first level instantaneous frequencies
    IA : ndarray
        2D first level instantaneous amplitudes
    order : int
        Power to which amplitude is raised before spectrum computation.
    freq_edges: {ndarray, tuple or None}
        Definition of the frequency bins used in the spectrum. This may be:

        * array_like vector of bin edge values (as defined by
        emd.spectra.define_hist_bins)

        * a tuple of values that can be passed to emd.spectra.define_hist_bins
        (eg edges=(1,50,49) will define 49 bins between 1 and 50Hz)

        * None in which case a sensible set of bins will be defined from the
        input data (this is the default option)
    amp_edges : {ndarray, tuple or None}
        Definition of amplitude bins used in spectrum. Format options are the
        same as for `freq_edges`.
    sum_time : boolean
        Flag indicating whether to sum across time dimension
    sum_imfs : boolean
        Flag indicating whether to sum across IMF dimension
    sample_rate : float
        Sampling rate of the data used in 'density' scaling
    scaling : {'density', 'spectrum', None}
        Switch specifying the normalisation or scaling applied to the spectrum.
    return_sparse : bool
         Flag indicating whether to return the full or sparse form(Default value = True)
    return_Gb_limit : {float, None}
        Maximum array size in Gb that will be returned if a non-sparse/dense
        array is being returned (default = 10). If the function return would
        exceed this size, the function will raise an error. If set to None,
        then no limit is imposed. Sparse arrays are always returned.

    Returns
    -------
    a : ndarray
        Vector of histogram bin centers for each amplitude
    f : ndarray
        Vector of histogram bin centers for each frequency
    hht : ndarray
        2D array containing the Hilbert-Huang Transform

    References
    ----------
    .. [1] Huang, Y. X., Schmitt, F. G., Lu, Z. M., & Liu, Y. L. (2008). An
       amplitude-frequency study of turbulent scaling intermittency using
       Empirical Mode Decomposition and Hilbert Spectral Analysis. In EPL
       (Europhysics Letters) (Vol. 84, Issue 4, p. 40010). IOP Publishing.
       https://doi.org/10.1209/0295-5075/84/40010

    """
    logger.info('STARTED: compute Hilbert-Marginal spectrum')

    IF, IA = ensure_2d([IF, IA], ['IF', 'IA'], 'hilberthuang')
    ensure_equal_dims((IF, IA), ('IF', 'IA'), 'hilberthuang')

    freq_edges, freq_bins = _histogram_bin_relay(freq_edges, IF.flatten())
    logger.debug('Freq bins: {0} to {1} in {2} steps'.format(freq_edges[0],
                                                             freq_edges[-1],
                                                             len(freq_edges)))

    amp_edges, amp_bins = _histogram_bin_relay(amp_edges, IA.flatten())
    logger.debug('Amp bins: {0} to {1} in {2} steps'.format(amp_edges[0],
                                                            amp_edges[-1],
                                                            len(amp_edges)))

    # Compute HOS - distribution of amplitude across amplitude, frequency,
    # time and IMF
    hima = _higher_order_spectra(IA,
                                 IF[:, :, None],
                                 IA[:, :,  None],
                                 amp_edges, freq_edges)
    # hima is a spase array of dimensions
    # [len(edges), len(edges2), num_samples, num_imfs, 1]

    # Get amplitude values in broadcastable shape
    A_values = np.reshape(IA, (1, 1, IA.shape[0], IA.shape[1], 1))**order

    # Scale hima by amplitude values and resolution
    dA = np.diff(amp_bins)[0]
    hima = hima * A_values * dA

    # Create PDF histogram
    sum_dims = np.where([0, 0, sum_time, sum_imfs, 1])[0]
    hima = hima.sum(axis=sum_dims)
    hima = hima / IF.size

    # Post-process - summing as already been done
    hima = _post_process_spectra(hima, mode=None, sample_rate=sample_rate,
                                 scaling=scaling, return_sparse=return_sparse,
                                 return_Gb_limit=return_Gb_limit)

    logger.info('COMPLETED: Hilbert-Marginal Spectrum - output size {0}'.format(hima.shape))
    return amp_bins, freq_bins, hima


def _post_process_spectra(spec, sum_dims=None,
                          mode='power',
                          scaling=None,
                          time_dim=1,
                          sample_rate=1,
                          return_sparse=False,
                          return_Gb_limit=10):
    """Apply standard processes to input spectrum.

    This function implements a set of processing options common to all
    hilbert-huang based spectra.

    Parameters
    ----------
    spec : ndarray
        2 or 3d input spectrum, usually a sparse array
    sum_dims : int or list of int
        Flag indicating whether to sum across time dimension
    mode : {'power', 'amplitude'}
        Switch specifying whether the distribution should return amplitude or
        power (amplitude squared) values.
    scaling : {'density', 'spectrum', None}
        Switch specifying the normalisation or scaling applied to the spectrum.
    time_dim : int
        Axis index of the dimension across time. This is used when applying
        some normalisations or scalings.
    return_sparse : boolean
        Flag indicating whether to return a sparse or dense (normal numpy) array.
    return_Gb_limit : {float, None}
        Maximum array size in Gb that will be returned if a non-sparse/dense
        array is being returned (default = 10). If the function return would
        exceed this size, the function will raise an error. If set to None,
        then no limit is imposed.  Sparse arrays are always returned.

    Returns
    -------
    ndarray
        processed power spectrum

    See Also
    --------
    hilberthuang, holospectrum, hilbertmarginal

    """
    # No housekeeping here - assume that inputs have been sanitised by higher level functions.
    if mode == 'power':
        logger.debug('Squaring amplitude to compute power')
        spec = spec**2

    if scaling == 'density':
        logger.debug("Applying scaling: 'density'.")
        spec = spec / (sample_rate * spec.shape[time_dim])
    elif scaling == 'spectrum':
        logger.debug("Applying scaling: 'spectrum'.")
        spec = spec / spec.shape[time_dim]
    elif scaling is None:
        pass
    else:
        logger.error('Unknown scaling: {0}'.format(scaling))
        raise ValueError('Unknown scaling: {0}'.format(scaling))

    if (sum_dims is not None) and (len(sum_dims) > 0):
        orig_dim = spec.shape
        spec = spec.sum(axis=sum_dims)
        msg = "Summing across dimensions {0}. Input dims ({1}) -> output dims ({2})"
        logger.debug(msg.format(sum_dims, orig_dim, spec.shape))

    if (return_sparse is False) and (return_Gb_limit is not None):
        byte_size = spec.size * 8  # sparse arrays don't have itemsize attr so assuming 8 for now
        if (byte_size / (1024**3)) > return_Gb_limit:
            msg = "Converting the output to dense format will create a very large array\n"
            msg += "This spectrum is about to return a {0}Gb numpy array - the limit is set to {1}Gb.\n"
            msg += "please either set 'return_sparse' to True to get a memory-efficient sparse array, or \n"
            msg += "change 'return_Gb_limit' if you really want the dense array..."
            logger.warning(msg.format(byte_size / (1024**3), return_Gb_limit))
            raise RuntimeError(msg.format(byte_size / (1024**3), return_Gb_limit))
        spec = spec.todense()
        msg = 'Converting output to dense array - size {0}Gb'
        logger.debug(msg.format(byte_size / (1024**3), return_Gb_limit))
    else:
        msg = 'Returning a sparse array - size {0}Gb'
        logger.debug(msg.format(byte_size / (1024**3), return_Gb_limit))

    return spec


def _base_spectra(X, Z,  x_edges):
    """Compute a 2-dimensional Hilbert-Huang distribution.

    This is a helper function for constructing a sparse array representation of
    a two dimensional distribution of power. This function would not normally
    be called by the user.

    Parameters
    ----------
    X : ndarray
        2d array of values defining the first dimension, usually [samples x imfs]
    Z : ndarray
        2d array of amplitude or power values matching the size of input X
    x_edges : ndarray
        Vector array containing bin edges for input X

    Returns
    -------
    sparse_array
        Sparse array representation of two dimensional distribution.

    See Also
    --------
    hilberthuang

    """
    # No housekeeping here - assume that inputs have been sanitised by higher level functions.

    # Find bin indices for first dimension
    x_inds = _digitize(X, x_edges)
    # Find bin indices for time dimension - cast to match input shape
    t_inds = np.broadcast_to(np.arange(x_inds.shape[0])[:, np.newaxis],
                             x_inds.shape)
    # Find bin indices for IMF dimension - cast to match input shape
    i_inds = np.broadcast_to(np.arange(X.shape[1])[np.newaxis, :],
                             x_inds.shape)

    # Create vectorised COO coordinate array
    coords = np.c_[x_inds.flatten(),
                   t_inds.flatten(),
                   i_inds.flatten()].T

    # Vectorise amplitude values to match coordinates
    Z = Z.flatten()

    # Drop observations which lie outside specified bin edges
    drops = np.any(coords == DROP_SENTINAL, axis=0)
    coords = np.delete(coords, drops, axis=1)
    Z = np.delete(Z, drops)

    # Compute final shape
    final_shape = (x_edges.shape[0]-1,
                   x_inds.shape[0],
                   x_inds.shape[1])

    # Create sparse spectrum
    s = sparse.COO(coords, Z, shape=final_shape)

    return s


def _higher_order_spectra(X, Y, Z, x_edges, y_edges):
    """Compute a 3-dimensional Hilbert-Huang distribution.

    This is a helper function for constructing a sparse array representation of
    a three dimensional distribution of power. This would not normally be
    called by the user.

    Parameters
    ----------
    X : ndarray
        2d array of values defining the first dimension, usually [samples x imfs]
    Y : ndarray
        3d array of values defining the second dimension, usually [samples x imfs x imfs]
    Z : ndarray
        3d array of amplitude or power values matching the size of input Y
    x_edges : ndarray
        Vector array containing bin edges for input X
    y_edges : ndarray
        Vector array containing bin edges for input Y

    Returns
    -------
    sparse_array
        Sparse array representation of three dimensional distribution.

    See Also
    --------
    holospectrum, hilbertmarginal

    """
    # No housekeeping here - assume that inputs have been sanitised by higher level functions.

    # Find bin indices for user specified dimensions
    x_inds = _digitize(X, x_edges)
    y_inds = _digitize(Y, y_edges)

    x_inds = np.broadcast_to(x_inds[:, :, np.newaxis], y_inds.shape)
    # Find bin indices for time dimension - cast to match input shape
    t_inds = np.broadcast_to(np.arange(x_inds.shape[0])[:, np.newaxis, np.newaxis],
                             y_inds.shape)
    # Find bin indices for first IMF dimension - cast to match input shape
    i_inds = np.broadcast_to(np.arange(X.shape[1])[np.newaxis, :, np.newaxis],
                             y_inds.shape)
    # Find bin indices for second IMF dimension - cast to match input shape
    j_inds = np.broadcast_to(np.arange(Y.shape[2])[np.newaxis, np.newaxis, :],
                             y_inds.shape)

    # Create vectorised COO coordinate array
    coords = np.c_[x_inds.flatten(),
                   y_inds.flatten(),
                   t_inds.flatten(),
                   i_inds.flatten(),
                   j_inds.flatten()].T

    # Vectorise amplitude values to match coordinates
    Z = Z.flatten()

    # Drop observations which lie outside specified bin edges
    drops = np.any(coords == DROP_SENTINAL, axis=0)
    Z = np.delete(Z, drops)
    coords = np.delete(coords, drops, axis=1)

    # Compute final shape
    final_shape = (x_edges.shape[0]-1,
                   y_edges.shape[0]-1,
                   x_inds.shape[0],
                   x_inds.shape[1],
                   y_inds.shape[2])

    # Create sparse spectrum
    s = sparse.COO(coords, Z, shape=final_shape)

    return s


def _digitize(vals, edges):
    """Return index of values into a set of defined bins.

    Parameters
    ----------
    vals : array_like
        Array of values to be binned
    edges : array_like
        Array containing the edges of bins. N edges define N-1 bins. Edges are
        inclusive on both the left and right.

    Returns
    -------
    ndarray
        Array containing index of each data point in vals into bins defined by edges

    Notes
    -----
    This function is a wrapper for np.digitize but has important differences.
    1. This function returns a sentinel value for observations outside the
    range of the specified bin edges
    2. This bin edges in this function are inclusive on the lower end and
    exclusive on the top.

    """
    drops = np.logical_or(vals < edges[0], vals >= edges[-1])
    inds = np.digitize(vals, edges) - 1
    inds[drops] = DROP_SENTINAL
    return inds


#%% -----------------------------------------------------
# Utilities

def define_hist_bins(data_min, data_max, nbins, scale='linear'):
    """Define the bin edges and centre values for use in a histogram.

    Parameters
    ----------
    data_min : float
        Value for minimum edge
    data_max : float
        Value for maximum edge
    nbins : int
        Number of bins to create
    scale : {'linear','log'}
         Flag indicating whether to use a linear or log spacing between bins (Default value = 'linear')

    Returns
    -------
    edges : ndarray
        1D array of bin edges
    centres : ndarray
        1D array of bin centres

    Notes
    -----
    An example creating histogram bins between 1 Hz and 5 Hz with four linearly
    spaced bins.

    >>> edges,centres = emd.spectra.define_hist_bins(1, 5, 4)
    >>> print(edges)
    [1. 2. 3. 4. 5.]
    >>> print(centres)
    [1.5 2.5 3.5 4.5]

    """
    if scale == 'log':
        p = np.log([data_min, data_max])
        edges = np.linspace(p[0], p[1], nbins + 1)
        edges = np.exp(edges)
    elif scale == 'linear':
        edges = np.linspace(data_min, data_max, nbins + 1)
    else:
        raise ValueError('scale \'{0}\' not recognised. please use \'log\' or \'linear\'.')

    # Get centre frequecy for the bins
    centres = np.array([(edges[ii] + edges[ii + 1]) / 2 for ii in range(len(edges) - 1)])

    return edges, centres


def define_hist_bins_from_data(X, nbins=None, mode='sqrt', scale='linear', tol=1e-3, max_bins=2048):
    """Find the bin edges and centre frequencies for use in a histogram.

    If nbins is defined, mode is ignored

    Parameters
    ----------
    X : ndarray
        Dataset whose summary stats will define the histogram
    nbins : int
         Number of bins to create, if undefined this is derived from the data (Default value = None)
    mode : {'sqrt'}
         Method for deriving number of bins if nbins is undefined (Default value = 'sqrt')
    scale : {'linear','log'}
         (Default value = 'linear')

    Returns
    -------
    edges : ndarray
        1D array of bin edges
    centres : ndarray
        1D array of bin centres

    """
    data_min = X.min() - tol
    data_max = X.max() + tol

    if nbins is None:
        if mode == 'sqrt':
            nbins = np.sqrt(X.shape[0]).astype(int)
        else:
            raise ValueError('mode {0} not recognised, please use \'sqrt\'')

    # Don't exceed max_bin number
    nbins = nbins if nbins < max_bins else max_bins

    return define_hist_bins(data_min, data_max, nbins, scale=scale)


def _histogram_bin_relay(params, data=None):
    """Relay function which does-the-right-thing with histogram bin inputs.

    Parameters
    ----------
    params : None or tuple(start, stop, nsteps) or np.ndarray
        Parameters given by user, if:
        None - bins automatically computed using define_hist_bins_from_data
        Tuple of length three - bins computed by passing params to define_hist_bins
        numpy.ndarray - input defines bin edges, bin centres are computed.
    data : ndarray
        Optional data used to compute bins if params=None

    Returns
    -------
    ndarray
        Array of bin edges
    ndarray
        Array of bin centres

    """
    if params is None:
        # User didn't say anything - guess bins
        edges, bins = define_hist_bins_from_data(data.flatten())
    elif isinstance(params, tuple) and len(params) in [3, 4]:
        # User specified meta bins - make actual bins
        edges, bins = define_hist_bins(*params)
    elif isinstance(params, (list, tuple, np.ndarray)):
        # User provided actual bin edges - use them
        edges = np.array(params)
        bins = _compute_centres_from_edges(edges)
    else:
        ValueError('Inputs not recognised....')

    return edges, bins


def _compute_centres_from_edges(edges, method='mean'):
    """Compute bin centres from an array of bin edges."""
    if method == 'geometric':
        bins = np.sqrt(edges[1:] * edges[:-1])
    elif method == 'mean':
        bins = (edges[1:] + edges[:-1]) / 2
    else:
        msg = 'method \'{0}\' not recognised. please use \'mean\' or \'geometric\'.'
        raise ValueError(msg)

    return bins
