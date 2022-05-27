import numpy as np

from lhcb_ftcalib.printing import info, raise_error, raise_warning


class ResolutionModel:
    """ Resolution model base type. Used for including the effects of a
        per-event specific decay time resolutions on the time dependent
        mixing asymmetry if numerical convolution is needed.
        Determines appropriate binning given a chosen binning of the
        decay time. Derived classes implement resolution lineshape on this
        discretisation. Initialized by Tagger object.
    """

    def __init__(self):
        self.DM = None
        self.DG = None
        self.a  = None
        self.res_range = None
        self._ready = False

    def init_resolution_range(self, decay_time_range, n_samples, res_max = 0.5):
        """ Determines a good range for sampling the decay time resolution model.
            For FFT convolution to make sense, time and resolution sampling need to be binned equally

            :param decay_time_range: two component list of lower and upper decay time sampling range
            :type decay_time_range:  list or tuple
            :param n_samples: Number of bins used for decay time
            :type n_samples: int
            :param res_max: Maximum absolute sampling range for decay time resolution in picoseconds. By default, it is assumed that time resolutions > 500 fs do not occur
            :type res_max: float
        """
        assert decay_time_range[1] > decay_time_range[0]
        assert res_max > 0 and n_samples > 0

        rangesize = (decay_time_range[1] - decay_time_range[0])
        nres = 2 * res_max / (rangesize / n_samples)
        raise_error(nres > 80, f"Number of resolution sampling points is too low: {nres}")
        info(f"FFT: Sampling decay time resolution with {int(nres)} points")
        self.res_range = np.linspace(-res_max, res_max, int(nres))

        self._ready = True


class GaussianResolution(ResolutionModel):
    """ Single gaussian resolution model (default choice).  """

    def __init__(self):
        pass

    def get(self, tauerr):
        """ Samples the decay time resolution on a set range given
            a resolution width "tauerr"

            :param tauerr: Resolution width
            :type tauerr: list
            :return: Discrete decay time resolution model lineshape on predefined range
            :return type: numpy.array
        """
        assert self._ready
        return np.exp(-0.5 * (self.res_range / tauerr)**2) / (np.sqrt(2 * np.pi) * tauerr)


def convolution_at(arr1, arr2, at):
    """ Performs FFT convolution of two discretely samples functions at the index "at".
        Behaves as scipy.signal.convolve(arr1, arr2, mode="same")[at] but only
        computes a single value

        :param arr1: Values of first function
        :type arr1: numpy.array
        :param arr2: Values of second function
        :type arr2: numpy.array
        :param at: Lookup index
        :type at: int
    """
    arr2 = np.flip(arr2)
    N1 = len(arr1)
    N2 = len(arr2)

    # Flip lookup index because of convolution
    at = N1 + N2 - at

    # Shift by offset given by minimum array size (scipy.signal.convolve mode "same")
    at -= int((N2 + 1) / 2)

    return np.sum(arr1[max(0, N1 - at): 1 + min(N1 - 1, N1 + N2 - 1 - at)] * arr2[max(0, at - N1): 1 + min(at - 1, N2 - 1)])


def mixing_asymmetry(tau, DM, DG, tauerr=None, a=0, res=None, nosc=1, n_samples=10000):
    r"""
    Computes the mixing asymmetry given an oscillation frequency and a delta gamma value

    :param tau: decay time data
    :type tau: numpy.array
    :param DM: :math:`\Delta m`
    :type DM: float
    :param DG: :math:`\Delta\Gamma`
    :type DG: float
    :param tauerr: decay time uncertainty data
    :type tauerr: numpy.array
    :param a: :math:`1-|q/p|^2`
    :type a: float
    :param res: Resolution model. By default single gaussian model is used
    :type res: ResolutionModel
    :param nosc: How many oscillations to sample (Relevant for numerical computation). For Bd modes osc=1 should be sufficient.
    :type nosc: int
    :param n_samples: Number of discrete time samples to use in case of numerical convolution.
    :type n_samples: int
    """
    Amix = np.cos(DM * tau) / np.cosh(0.5 * DG * tau)
    if a != 0:
        Amix += a / 2 * (1 - Amix**2)
    if tauerr is None:
        raise_warning(res is None, "You specified a resolution model but no decay time uncertainty -> Ignoring resolution model.")
        return Amix

    # Perform convolution
    if DG == 0 and a == 0:
        # Analytical solution exists if resolution is single gaussian
        return Amix * np.exp(-0.5 * DM**2 * tauerr**2)

    # Numerical convolution is required
    # Set / check resolution model
    if res is None:
        res = GaussianResolution()

    raise_error(isinstance(res, ResolutionModel), f"{res} is not a resolution model")

    # Sample mixing asymmetry and resolution model. The latter needs
    # to be re-sampled for each event
    # Negative decay times are sampled to maximize precision around t = 0
    maxosc = nosc * 2 * np.pi / DM
    tau_lin_range = [-maxosc, maxosc]
    tau_lin = np.linspace(*tau_lin_range, n_samples)

    Amix = np.cos(DM * tau_lin) / np.cosh(0.5 * DG * tau_lin)
    if a != 0:
        Amix += a / 2 * (1 - Amix**2)

    # Initialize resolution model
    resmax = 0.2  # Assume "no" events have > 200fs resolution
    res.init_resolution_range([-maxosc, maxosc], n_samples, resmax)

    # For each decay time value, compute lookup index for convolution result which is on same time range as Amix
    lookup = np.array((n_samples / 2) * tau / maxosc, dtype=np.int32) + len(Amix) // 2
    lookup %= len(Amix) // 2

    Amix_fftconv = []
    for look, sigma in zip(lookup, tauerr):
        resolution = res.get(sigma)

        Amix_fftconv.append(convolution_at(Amix, resolution, look))

    # Normalize
    norm = 2 * resmax / n_samples
    range_ratio = 2 * resmax / (tau_lin_range[1] - tau_lin_range[0])
    norm /= range_ratio

    # import matplotlib.pyplot as plt
    # plt.subplot(1, 2, 1)
    # plt.plot(res.res_range, res.get(0.02))
    # plt.subplot(1, 2, 2)
    # plt.plot(tau_lin, Amix)
    # plt.plot(tau, norm * np.array(Amix_fftconv), ',')
    # plt.show()

    return norm * np.array(Amix_fftconv)
