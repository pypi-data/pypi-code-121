from __future__ import division
import logging
import collections
import numpy as np
import scipy
import scipy.optimize

from . import util
from . import const
from . import waveform
from .ang_avg import ang_avg

logger = logging.getLogger('inspiral_range')

##################################################

DETECTION_SNR = 8.0

##################################################

def int73(freq, psd):
    """Return "int73" full integral value and integrand array

    The integral is over the frequency component of the closed form
    inspiral SNR calculation, e.g.:

      \int_fmin^fmax df f^(-7/3) / psd

    @returns integral value as float, and np.array of integrand

    """
    assert len(freq) == len(psd)
    f73 = freq ** (-7/3)
    integrand73 = f73 / psd
    int73 = np.trapz(integrand73, freq)
    return int73, integrand73


def sensemon_range(freq, psd, m1=1.4, m2=1.4, horizon=False, integrate=True, detection_snr=DETECTION_SNR):
    """Detector inspiral range from closed form expression

    Masses `m1` and `m2` should be specified in solar masses (default:
    m1=m2=1.4).  If the `horizon` keyword is specified the "horizon"
    range will be returned, which differs from the angle-averaged
    range by ~2.26.

    @returns distance in Mpc as a float

    """
    assert len(freq) == len(psd)
    if horizon:
        theta = 4
    else:
        theta = 1.77
    theta /= 1e6 * const.PC_SI
    M_chirp = waveform.M_chirp(m1, m2) * const.MSUN_SI
    integral, integrand = int73(freq, psd)
    if integrate:
        i73 = integral
    else:
        i73 = integrand
    val = theta / detection_snr \
        * waveform.habs_nsp_prefactor(M_chirp) \
        * np.sqrt(i73) / 2
    if integrate:
        return float(val)
    else:
        return val


def sensemon_horizon(freq, psd, **kwargs):
    """Detector inspiral range horizon from closed form expression

    See sensemon_range() function.

    @returns horizon distance in Mpc as a float

    """
    return sensemon_range(freq, psd, horizon=True, **kwargs)

##################################################


def __H_from_args(freq, psd, H, params):
    """Return waveform object from argument parameters"""
    assert len(freq) == len(psd), "Frequency and PSD arrays must be the same length."
    if H is None:
        H = waveform.CBCWaveform(freq, **params)
    else:
        assert not params, "Either H or params can be specified, not both."
    return H


def find_root_redshift(func):
    """Brentz root finding optimization on the specified function

    Returns the z value where func(z)==0.

    """
    def log_opt(z):
        if logger.getEffectiveLevel() == 10:
            logger.debug("{}({}): {}".format(
                func.__name__, z, func(z)))
    zmin = 1e-8
    log_opt(zmin)
    # steadily shift the z range if we don't find a root
    for zmax in [0.1, 1, 10, 100, 1000]:
        log_opt(zmax)
        try:
            return scipy.optimize.brentq(func, zmin, zmax)
        except ValueError:
            zmin = zmax
            continue
    else:
        raise RuntimeError(f"Could not find root of {func.__name__} inside z={zmax}.")


def horizon_redshift(freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector horizon redshift

    For the given detector noise PSD and waveform parameters return
    the redshift at which the signal SNR would equal `detection_snr`.

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns redshift as a float

    """
    H = __H_from_args(freq, psd, H, params)
    def opt_SNR_z(z):
        return H.SNR(psd, z) - detection_snr
    return find_root_redshift(opt_SNR_z)


def horizon(freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector horizon distance in Mpc

    See horizon_redshift().

    @returns distance in Mpc as a float

    """
    H = __H_from_args(freq, psd, H, params)
    zhor = horizon_redshift(freq, psd, detection_snr=detection_snr, H=H)
    return H.cosmo.luminosity_distance(zhor)


def volume(freq, psd, z_hor=None, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector redshift-corrected comoving volume

    For the given detector noise PSD and waveform parameters return
    the redshift-corrected, comoving volume in Mpc^3 within which all
    sources would have SNR greater than `detection_snr`.

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns distance in Mpc as a float

    """
    H = __H_from_args(freq, psd, H, params)

    # This volume is calculated based on the formalism described in
    # Belczynski et. al 2014:
    #
    #   https://dx.doi.org/10.1088/0004-637x/789/2/120
    #
    # The comoving sensitive volume is given by:
    #
    #   Vcbar = \Int_0^\inf dVc/dz 1/(1+z) f(z) dz
    #
    # where (dVc/dz 1/(1_z)) is the redshit-corrected "comoving
    # volumed density" and f(z) is the "detectability fraction" given
    # by a marginalization over the various orientation angles.
    #
    # We can cut off the integration at the horizon distance, z_hor,
    # since the assumption is that the SNR is below detectability
    # beyond.

    if not z_hor:
        z_hor = horizon_redshift(freq, psd, detection_snr=detection_snr, H=H)

    # create a Gauss-Legendre quadrature for the integration:
    # https://en.wikipedia.org/wiki/Gaussian_quadrature#Gauss.E2.80.93Legendre_quadrature
    # x are the roots and w are the weights
    x, w = scipy.special.orthogonal.p_roots(20)
    # older versions of p_roots return complex roots
    x = np.real(x)
    # account for the fact that the interval is [0,z_hor], not [-1,1]
    z = 0.5 * z_hor * (x + 1.0)

    # detectability fraction
    snrs = np.array([H.SNR(psd, zz) for zz in z])
    f = np.array([ang_avg(snr / detection_snr) for snr in snrs])
    # logger.debug('f = {}'.format(f))

    # comoving volume density, e.g. dVc/dz 1/(1+z)
    dVdz1pz = np.array([H.cosmo.differential_comoving_volume(zz) for zz in z])

    # compute sensitivity volume in Mpc^3
    V = 0.5 * z_hor * sum(w * dVdz1pz * f)
    # # equivalent cosmology-corrected "sensemon" range
    # V0 = 0.5 * z_hor * sum(w * dVdz1pz)

    return V


def range(freq, psd, z_hor=None, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector redshift-corrected comoving range in Mpc

    For the given detector noise PSD and waveform parameters return
    the redshift-corrected, comoving distance in Mpc at which the
    signal SNR would equal `detection_snr`, i.e. the radius of the
    Euclidean sphere given by volume().

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns distance in Mpc as a float

    """
    V = volume(freq, psd, z_hor=z_hor, detection_snr=detection_snr, H=H, **params)
    return util.v2r(V)


def response_frac_redshift(frac, freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector response fraction redshift

    For the given detector noise PSD and waveform parameters return
    the redshift at which the specified fraction of sources would be
    detected (SNR >= `detection_snr`) if they were all placed at that
    distance.  Assumes a uniform distribution of sources.

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns redshift as a float

    """
    H = __H_from_args(freq, psd, H, params)
    def opt_f_z(z):
        snr = H.SNR(psd, z)
        f = ang_avg(snr / detection_snr)
        return f - frac
    return find_root_redshift(opt_f_z)


def response_frac(frac, freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector response fraction distance in Mpc

    See reach_frac_redshift().

    @returns distance in Mpc as a float

    """
    H = __H_from_args(freq, psd, H, params)
    z = response_frac_redshift(frac, freq, psd, detection_snr=detection_snr, H=H)
    return H.cosmo.luminosity_distance(z)


def reach_frac_redshift(frac, freq, psd, cvol=None, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector detectability fraction reach redshift

    For the given detector noise PSD and waveform parameters return
    the distance at which the specified fraction of sources should be
    detected.  Assumes a uniform distribution of sources.

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns redshift as a float

    """
    H = __H_from_args(freq, psd, H, params)
    if not cvol:
        cvol = volume(freq, psd, detection_snr=detection_snr, H=H)
    def opt_V_z(z):
        V = volume(freq, psd, detection_snr=detection_snr, z_hor=z, H=H)
        return frac - V/cvol
    return find_root_redshift(opt_V_z)


def reach_frac(frac, freq, psd, cvol=None, detection_snr=DETECTION_SNR, H=None, **params):
    """Detector detectability fraction reach in Mpc

    See reach_frac_redshift().

    @returns distance in Mpc as a float

    """
    H = __H_from_args(freq, psd, H, params)
    z = reach_frac_redshift(frac, freq, psd, cvol=cvol, detection_snr=detection_snr, H=H)
    return H.cosmo.luminosity_distance(z)


def cosmological_ranges(freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Calculate various cosmology-corrected detector distance measures

    The following range values are calculated:

      horizon
      range
      response_50
      response_10
      reach_50
      reach_90

    See individual function help for more information.

    This method is faster than running all individual calculation
    methods separately, as various intermediate calculated values are
    used in the subsequent calculations to speed things up.

    Remaining keyword arguments are interpreted as waveform generation
    parameters (see waveform.gen_waveform()), or a pre-generated
    fiducial waveform `H` may be provided (see waveform.CBCWaveform).

    @returns dictionary of range values as (value, 'unit') tuples

    """
    H = __H_from_args(freq, psd, H, params)

    hor_z = horizon_redshift(freq, psd, detection_snr=detection_snr, H=H)
    hor = H.cosmo.luminosity_distance(hor_z)

    cvol = volume(freq, psd, z_hor=hor_z, detection_snr=detection_snr, H=H)
    crange = util.v2r(cvol)

    response_z_50 = response_frac_redshift(0.5, freq, psd, detection_snr=detection_snr, H=H)
    response_50 = H.cosmo.luminosity_distance(response_z_50)
    response_z_10 = response_frac_redshift(0.1, freq, psd, detection_snr=detection_snr, H=H)
    response_10 = H.cosmo.luminosity_distance(response_z_10)

    reach_z_50 = reach_frac_redshift(0.5, freq, psd, cvol=cvol, detection_snr=detection_snr, H=H)
    reach_50 = H.cosmo.luminosity_distance(reach_z_50)
    reach_z_90 = reach_frac_redshift(0.9, freq, psd, cvol=cvol, detection_snr=detection_snr, H=H)
    reach_90 = H.cosmo.luminosity_distance(reach_z_90)

    return collections.OrderedDict([
        ('range',   (crange, 'Mpc')),
        ('horizon', (hor, 'Mpc')),
        ('horizon_z',   (hor_z, None)),
        ('response_z_50', (response_z_50, None)),
        ('response_50', (response_50, 'Mpc')),
        ('response_z_10', (response_z_10, None)),
        ('response_10', (response_10, 'Mpc')),
        ('reach_z_50', (reach_z_50, None)),
        ('reach_50', (reach_50, 'Mpc')),
        ('reach_z_90', (reach_z_90, None)),
        ('reach_90', (reach_90, 'Mpc')),
        ])


def all_ranges(freq, psd, detection_snr=DETECTION_SNR, H=None, **params):
    """Calculate all ranges, cosmological and sensemon

    Returns a tuple (metrics, params) where `metrics` is a dictionary
    of all the ranges and `params` is the waveform parameters
    used.

    """
    H = __H_from_args(freq, psd, H, params)
    metrics = cosmological_ranges(freq, psd, detection_snr=detection_snr, H=H)
    metrics['sensemon_range'] = \
        (sensemon_range(freq, psd, H.params['m1'], H.params['m2'], detection_snr=detection_snr),
         'Mpc')
    metrics['sensemon_horizon'] = \
        (sensemon_range(freq, psd, H.params['m1'], H.params['m2'], detection_snr=detection_snr, horizon=True),
         'Mpc')
    return metrics, H
