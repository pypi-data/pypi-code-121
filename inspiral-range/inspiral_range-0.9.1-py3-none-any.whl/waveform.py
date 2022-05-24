from __future__ import division
import copy
from collections import OrderedDict
import numpy as np
import scipy.interpolate

from . import logger
from . import const
from .cosmology import Cosmology

##################################################

# default inspiral waveform parameters
# face-on 1.4/1.4 Msolar inspiral at 1 Mpc distance
DEFAULT_PARAMS = OrderedDict([
    ('approximant', 'IMRPhenomD'),
    ('distance', 1e6),
    ('m1', 1.4),
    ('m2', 1.4),
    ('S1x', 0.0),
    ('S1y', 0.0),
    ('S1z', 0.0),
    ('S2x', 0.0),
    ('S2y', 0.0),
    ('S2z', 0.0),
    ('inclination', 0.0),
    ('f_ref', 0.0),
    ('phiRef', 0.0),
    ('longAscNodes', 0.0),
    ('eccentricity', 0.0),
    ('meanPerAno', 0.0),
    # FIXME: are these limits reasonable?
    ('deltaF', 1.0),
    ('f_min', 1.0),
    ('f_max', 100000.0),
    ('LALpars', None),
    ])

# DEFAULT_APPROXIMANT_BNS = 'TaylorF2'
# DEFAULT_APPROXIMANT_BBH = 'IMRPhenomD'
# NS_MSUN_CUTOFF = 3


def _get_waveform_params(**kwargs):
    params = OrderedDict(DEFAULT_PARAMS)
    params.update(**kwargs)
    # FIXME: what the right approximant to use?
    #
    # # use waveform approximant appropriate to type
    # if not params['approximant']:
    #     if params['m1'] < NS_MSUN_CUTOFF and params['m2'] < NS_MSUN_CUTOFF:
    #         params['approximant'] = DEFAULT_APPROXIMANT_BNS
    #     else:
    #         params['approximant'] = DEFAULT_APPROXIMANT_BBH
    #
    # We will be using IMRPhenomD for all systems unless otherwise
    # specified.  We know this is not correct for BNS systems, but
    # nothing is, so we use the best available.
    return params

##################################################

def M_chirp(m1, m2):
    """Calculate chirp mass

    """
    M = m1 + m2
    eta = m1*m2/M/M
    return eta**(3.0/5.0) * M


def habs_nsp_prefactor(M_chirp):
    """Preftor for Newtonian stationary phase chirp amplitude

    Assumes M_chirp in SI units

    """
    GMc = const.G * M_chirp
    return (5.0 / 24.0 / np.pi**(4.0/3.0) * GMc**(5.0/3.0) / const.c**3)**0.5


def habs_nsp(freq, **params):
    """|h(f)| from Newtonian stationary phase chirp amplitude

    """
    # convert to SI units
    mc = M_chirp(params['m1'], params['m2']) * const.MSUN_SI
    dlum = params['distance'] * const.PC_SI
    return habs_nsp_prefactor(mc) * freq**(-7.0/6.0) / dlum

##################################################

def gen_waveform(**params):
    """Generate frequency-domain inspiral waveform

    Returns a tuple of (freq, h_plus^tilde, h_cross^tilde).

    The waveform is generated with the lalsimulation
    SimInspiralChooseFDWaveform() function.  Keyword arguments are
    used to update the default waveform parameters (see DEFAULT_PARAMS
    macro).  The mass parameters ('m1' and 'm2') should be specified
    in solar masses and the 'distance' parameter should be specified
    in parsecs**.  Waveform approximants may be given as string names
    (see `lalsimulation` documentation for more info).

    For example, to generate a 20/20 Msolar BBH waveform:

    >>> hp,hc = waveform.gen_waveform('m1'=20, 'm2'=20)

    **NOTE: The requirement that masses be specified in solar masses
    and distances in parsecs is different than that of the underlying
    lalsimulation method which expects mass and distance parameters to
    be in SI units.

    """
    import lalsimulation

    iparams = _get_waveform_params(**params)

    # convert to SI units
    iparams['distance'] *= const.PC_SI
    iparams['m1'] *= const.MSUN_SI
    iparams['m2'] *= const.MSUN_SI
    logger.info("approximant: {}".format(iparams['approximant']))
    iparams['approximant'] = lalsimulation.SimInspiralGetApproximantFromString(iparams['approximant'])

    # # calculate delta F based on frequency of inner-most stable
    # # circular orbit ("fisco")
    # m = iparams['m1'] + iparams['m2']
    # fisco = (const.c**3)/(const.G*(6**1.5)*2*np.pi*m)
    # df = 2**(np.max([np.floor(np.log(fisco/4096)/np.log(2)), -6]))
    # iparams['deltaF'] = df
    # FIXME: fisco deltaF produces all nan for M<1.9

    hp, hc = lalsimulation.SimInspiralChooseFDWaveform(**iparams)

    freq = hp.f0 + np.arange(len(hp.data.data)) * hp.deltaF

    return freq, hp.data.data, hc.data.data


def habs_lalsimulation(freq, **params):
    """|h_+(f)| from lalsimulation waveform

    Masses should be in solar masses and distances should be in
    parsecs.

    """
    logger.info("waveform generation with lalsimulation...")
    _freq, hp, hc = gen_waveform(**params)
    return scipy.interpolate.interp1d(
        _freq, np.absolute(hp),
        kind='cubic',
        bounds_error=False, fill_value=(0.0, 0.0),
    )(freq)

##################################################

# interpolation waveform interpolation algorithm provided by:
#
#   Jolien Creighton <jolien.creighton@ligo.org>
#
# Create an extrapolate-able interpolant of an R(f) function that
# transitions between the analytic stationary phase Newtonian chirp at
# low frequencies to an IMRPhenomD model at high frequencies,
# calculated for an equal mass, non-spinning binary.  This is highly
# accurate and fast for those parameters, and should only be used
# appropriately.

def compute_waveform_interp():
    params = _get_waveform_params(
        m1=1, m2=1,
        distance=1/const.PC_SI,
    )

    freq, hp, hc = gen_waveform(**params)
    habs_phenomd = np.absolute(hp)
    habs_spanewt = habs_nsp(freq, **params)

    # ratio (==1 at low frequencies)
    R = habs_phenomd / habs_spanewt
    R[freq < params['f_min']] = 1.0

    # will interpolate in logspace
    log_f = np.log10(freq[1:])
    log_R = np.log10(R[1:])
    log_R[np.isinf(log_R)] = -10.0

    # omit points at high frequency where phenomd waveform is cut off
    log_f = log_f[log_R > -2.0]
    log_R = log_R[log_R > -2.0]

    # create interpolator
    log_R_interp = scipy.interpolate.interp1d(
        log_f, log_R, kind='cubic', copy=True)

    # new frequencies to interpolate, uniform in logspace
    log_f = np.linspace(min(log_f), max(log_f), 100)

    # values at those new frequencies
    log_R = log_R_interp(log_f)

    return log_f, log_R


_log10_f_data = np.array(
      [0.        , 0.04188728, 0.08377456, 0.12566185, 0.16754913,
       0.20943641, 0.25132369, 0.29321098, 0.33509826, 0.37698554,
       0.41887282, 0.4607601 , 0.50264739, 0.54453467, 0.58642195,
       0.62830923, 0.67019651, 0.7120838 , 0.75397108, 0.79585836,
       0.83774564, 0.87963293, 0.92152021, 0.96340749, 1.00529477,
       1.04718205, 1.08906934, 1.13095662, 1.1728439 , 1.21473118,
       1.25661846, 1.29850575, 1.34039303, 1.38228031, 1.42416759,
       1.46605488, 1.50794216, 1.54982944, 1.59171672, 1.633604  ,
       1.67549129, 1.71737857, 1.75926585, 1.80115313, 1.84304042,
       1.8849277 , 1.92681498, 1.96870226, 2.01058954, 2.05247683,
       2.09436411, 2.13625139, 2.17813867, 2.22002595, 2.26191324,
       2.30380052, 2.3456878 , 2.38757508, 2.42946237, 2.47134965,
       2.51323693, 2.55512421, 2.59701149, 2.63889878, 2.68078606,
       2.72267334, 2.76456062, 2.8064479 , 2.84833519, 2.89022247,
       2.93210975, 2.97399703, 3.01588432, 3.0577716 , 3.09965888,
       3.14154616, 3.18343344, 3.22532073, 3.26720801, 3.30909529,
       3.35098257, 3.39286986, 3.43475714, 3.47664442, 3.5185317 ,
       3.56041898, 3.60230627, 3.64419355, 3.68608083, 3.72796811,
       3.76985539, 3.81174268, 3.85362996, 3.89551724, 3.93740452,
       3.97929181, 4.02117909, 4.06306637, 4.10495365, 4.14684093])

_log10_R_data = np.array(
      [-3.32032304e-04, -3.54523254e-04, -3.78330508e-04, -4.03611337e-04,
       -4.30523017e-04, -4.59222821e-04, -4.89868022e-04, -5.22615895e-04,
       -5.57623713e-04, -5.95048750e-04, -6.35048280e-04, -6.77779577e-04,
       -7.23402800e-04, -7.72119741e-04, -8.24163454e-04, -8.79769158e-04,
       -9.39191051e-04, -1.00269719e-03, -1.07057323e-03, -1.14313361e-03,
       -1.22071305e-03, -1.30367176e-03, -1.39239872e-03, -1.48731213e-03,
       -1.58886293e-03, -1.69753770e-03, -1.81386154e-03, -1.93840159e-03,
       -2.07177080e-03, -2.21463194e-03, -2.36770261e-03, -2.53175997e-03,
       -2.70764670e-03, -2.89627721e-03, -3.09864472e-03, -3.31582920e-03,
       -3.54900617e-03, -3.79945666e-03, -4.06857843e-03, -4.35789864e-03,
       -4.66908818e-03, -5.00397808e-03, -5.36457820e-03, -5.75309862e-03,
       -6.17197431e-03, -6.62389370e-03, -7.11183166e-03, -7.63908802e-03,
       -8.20933254e-03, -8.82665761e-03, -9.49564013e-03, -1.02214145e-02,
       -1.10097588e-02, -1.18671962e-02, -1.28011152e-02, -1.38199116e-02,
       -1.49331549e-02, -1.61517847e-02, -1.74883383e-02, -1.89572156e-02,
       -2.05749804e-02, -2.23607000e-02, -2.43363172e-02, -2.65270440e-02,
       -2.89617521e-02, -3.16733206e-02, -3.46988671e-02, -3.80797478e-02,
       -4.18611376e-02, -4.60908953e-02, -5.08172488e-02, -5.60845822e-02,
       -6.19262146e-02, -6.83524778e-02, -7.53315441e-02, -8.27592558e-02,
       -9.03721259e-02, -9.77949600e-02, -1.04758985e-01, -1.10928431e-01,
       -1.15885293e-01, -1.19127871e-01, -1.20080638e-01, -1.18121497e-01,
       -1.12632351e-01, -1.03076586e-01, -8.91021787e-02, -7.06630121e-02,
       -4.81471981e-02, -2.25056000e-02,  4.60804275e-03,  3.06352219e-02,
        5.17216938e-02,  6.18239625e-02,  2.03889962e-02, -1.90526410e-01,
       -5.80615950e-01, -1.04468578e+00, -1.52174078e+00, -1.99968977e+00])

_log10_R = scipy.interpolate.interp1d(
    _log10_f_data, _log10_R_data,
    kind='cubic',
    bounds_error=False, fill_value=(0.0, -np.inf),
)


def habs_cached(freq, **params):
    """|h_+(f)| from a cached IMRPhenomD waveform

    Fast waveform generation, but only works for equal mass,
    non-spinnging BBH systems.  An AssertionError will be thrown if
    the params do not coorespond to those conditions.

    Masses should be in solar masses and distances should be in
    parsecs.

    """
    assert params['approximant'] == 'IMRPhenomD', "Aprroximant must be IMRPhenomD to use cached waveform."
    assert params['m1'] == params['m2'], "System must be equal mass to use cached waveform."
    for param in ['S1x', 'S1y', 'S1z', 'S2x', 'S2y', 'S2z', 'inclination']:
        assert params[param] == 0, "System must be non-spinning to use cached waveform."
    logger.info("waveform generation with cached waveform...")

    mscale = (params['m1'] + params['m2']) / 2
    hfac = habs_nsp(freq, **params)
    return hfac * 10.0**_log10_R(np.log10(freq * mscale))

##################################################

class CBCWaveform:
    """CBC waveform class for inspiral range calculations

    Generates waveform and stores parameters for later
    cosmological transformations.

    NOTE: Only the amplitude of the plus polarization of the generated
    waveform is stored, as that's all that's needed for calculating
    SNR.

    """
    def __init__(self, freq, z0=0.1, cosmo=Cosmology(), algo=None, **params):
        """Initialize waveform

        `freq` is the frequency array to which the waveform will be
        evaluated.  The PSD for SNR() calculations must be specified
        at these frequencies.  `z0` is the reference redshift to use.
        A custom Cosmology can be supplied via the `cosmo` keyword
        argument (see Cosmology).

        The `algo` argument can be used to specify the waveform
        generation algorithm to use.  'lalsimulation' can be used to
        generate arbitrary waveforms but requires the lalsimulation
        module.  'cached' extrapolates from a cached IMRPhenomD
        waveform and is much faster, but only works for equal mass,
        non-spinnging BBH systems.  If None is specified, the 'cached'
        algo will be tried, with a fallback on 'lalsimulation'.

        Additional keyword arguments are used to override the default
        waveform parameters.

        """
        self.freq = freq
        self.z0 = z0
        self.cosmo = cosmo
        self.params = _get_waveform_params(**params)
        self.d0 = self.cosmo.luminosity_distance(self.z0) * 1e6
        iparams = copy.deepcopy(self.params)
        iparams['distance'] = self.d0
        iparams['m1'] *= 1.0 + self.z0
        iparams['m2'] *= 1.0 + self.z0

        if algo:
            self.habs = eval('habs_{}'.format(algo))(freq, **iparams)
        else:
            try:
                self.habs = habs_cached(freq, **iparams)
            except AssertionError as e:
                logger.info(e)
                self.habs = habs_lalsimulation(freq, **iparams)

    def __repr__(self):
        return '<{}: {}>'.format(
            type(self).__name__,
            ', '.join(['{}={}'.format(*p) for p in self.params.items()]),
        )

    def z_scale(self, z):
        """Scale/shift waveform amplitude and frequency arrays for a given redshift

        Returns transformed (freq, habs) tuple.

        """
        d = self.cosmo.luminosity_distance(z) * 1e6
        fscale = (1+self.z0)/(1+z)
        hscale = self.d0/d * fscale**-2
        return self.freq*fscale, self.habs*hscale


    def SNR(self, psd, z=0):
        """Calculate waveform SNR against given PSD

        If redshift z provided, SNR will be calculated for a waveform
        transformed to that redshift.

        PSD must be specified at the same frequency points as
        used/generated at initialization.

        """
        if z != 0:
            f, h = self.z_scale(z)
            h = scipy.interpolate.interp1d(f, h, bounds_error=False, fill_value=(h[0], 0))(self.freq)
        else:
            h = self.habs
        return np.sqrt(4*np.trapz((h**2)/psd, self.freq))

####################

if __name__ == '__main__':
    _log10_f_data, _log10_R_data = compute_waveform_interp()
    print('_log10_f_data =', repr(_log10_f_data))
    print('_log10_R_data =', repr(_log10_R_data))
