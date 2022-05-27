#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Simulation functions.

Routines:

"""

import logging

import numpy as np
from scipy import signal

from .support import ensure_equal_dims

# Housekeeping for logging
logger = logging.getLogger(__name__)


# Joint Instantaneous Frequency Functions

def compute_joint_if(freq, amp, phase, sample_rate=128, seconds=2):
    """Compute joint instantaneous frequency from a set of oscillations.

    This function implements a signal simulator based on the methods in Fabus
    et al (2021) [1]_. freq, amp and phase inputs should be tuples/lists of
    user defined values.

    Parameters
    ----------
    freq, amp, phase : {tuple, list, np.ndarray}
        Frequency, Amplitude and Phase values for each component.

        These are lists or tuples containing a single value per component.
        sample_rate and seconds must then also be defined.

    sample_rate : {None, float}
        Sampling frequency of the data used if user defined harmonic values are passed in
    seconds : {None, float}
        Amount of seconds to generate if user defined harmonic values are passed in

    Returns
    -------
    joint_if : ndarray
        Vector containing the joint instantaneous frequency signal
    joint_sig : ndarray
        Array containing the time-domain signal for each harmonic component

    Notes
    -----
    Example usage - compute joint instantaneous frequency from user defined harmonic values

    >>> f = (5, 10, 15)
    >>> a = (1, 1/3, 1/9)
    >>> p = (0, 0, 0)
    >>> joint_if, joint_sig =  compute_joint_if(f, a, p, 128, 10)

    References
    ----------
    .. [1] Fabus, M., Woolrich, M., Warnaby, C. and Quinn, A., 2021. Understanding
       Harmonic Structures Through Instantaneous Frequency. BiorXiv
       https://doi.org/10.1101/2021.12.21.473676

    """
    time_vect = np.linspace(0, seconds, int(seconds*sample_rate))

    # Work with numpy arrays internally
    freq = 2*np.pi*np.array(freq)
    amp = np.array(amp)
    phase = np.array(phase)

    ensure_equal_dims([freq, amp, phase], ['freq', 'amp', 'phase'], 'compute_joint_if')
    num_comps = freq.shape[0]

    num = np.zeros((num_comps, num_comps, time_vect.shape[0]))
    denom_sin = np.zeros((num_comps, time_vect.shape[0]))
    denom_cos = np.zeros((num_comps, time_vect.shape[0]))
    sig = np.zeros((num_comps, time_vect.shape[0]))
    for n in range(num_comps):
        denom_cos[n, :] = amp[n] * np.cos(freq[n] * time_vect + phase[n])
        denom_sin[n, :] = amp[n] * np.sin(freq[n] * time_vect + phase[n])
        sig[n, :] = amp[n] * np.cos(freq[n] * time_vect + phase[n])
        for m in range(num_comps):
            fd = freq[n] - freq[m]
            pd = phase[n] - phase[m]
            num[n, m, :] = freq[m] * amp[n] * amp[m] * np.cos(fd * time_vect + pd)

    joint_if = np.sum(num, axis=(0, 1)) / ((np.sum(denom_cos, axis=0)**2) + (np.sum(denom_sin, axis=0)**2))
    joint_if = joint_if / (2*np.pi)

    return joint_if, sig


def abreu2010(f, nonlin_deg, nonlin_phi, sample_rate, seconds):
    r"""Simulate a non-linear waveform using equation 7 in [1]_.

    Parameters
    ----------
    f : float
        Fundamental frequency of generated signal
    nonlin_deg : float
        Degree of non-linearity in generated signal
    nonlin_phi : float
        Skew in non-linearity of generated signal
    sample_rate : float
        The sampling frequency of the generated signal
    seconds : float
        The number of seconds of data to generate

    Returns
    -------
    ndarray
        Simulated signal containing non-linear wave

    Notes
    -----
    This function implements equation 7 in [1]_.

    .. math::
        u(t) = U_wf \frac{ sin(\omega t) + \frac{r sin \phi}{1+\sqrt{1-r^2}} } {1-r cos(\omega t+ \phi)}

    Where :math:`\phi` is nonlin_phi - a waveform parameter :math:`(-\pi/2 \leq \phi \leq \pi/2)`
    related to the biphase and :math:`r` is nonlin_deg - an
    index of skewness or nonlinearity :math:`(-1 \leq r \leq 1)`.

    This equation is a generalisation of equation 14 in [2]_. This paper highlights 3 cases for :math:`\phi`.

    * :math:`\phi = 0`, resulting in an accelerated skewed wave (sawtooth wave profile);

    * :math:`\phi = - \pi/2`, a velocity-skewed wave (with a velocity shape similar to a 1st-order cnoidal wave);

    * :math:`\phi = - \pi/4`, corresponding to a wave with both velocity and acceleration skewnesses


    References
    ----------
    .. [1] Abreu, T., Silva, P. A., Sancho, F., & Temperville, A. (2010).
       Analytical approximate wave form for asymmetric waves. Coastal Engineering,
       57(7), 656-667. https://doi.org/10.1016/j.coastaleng.2010.02.005
    .. [2] Drake, T. G., & Calantoni, J. (2001). Discrete particle model for
       sheet flow sediment transport in the nearshore. In Journal of Geophysical
       Research: Oceans (Vol. 106, Issue C9, pp. 19859-19868). American
       Geophysical Union (AGU). https://doi.org/10.1029/2000jc000611

    """
    time_vect = np.linspace(0, seconds, int(seconds * sample_rate))

    factor = np.sqrt(1 - nonlin_deg**2)
    num = nonlin_deg * np.sin(nonlin_phi) / (1 + factor)
    num = num + np.sin(2 * np.pi * f * time_vect)

    denom = 1 - nonlin_deg * np.cos(2 * np.pi * f * time_vect + nonlin_phi)

    return factor * (num / denom)


def ar_oscillator(freq, sample_rate, seconds, r=.95, noise_std=None, random_seed=None):
    """Create a simulated oscillation using an autoregressive filter.

    A simple filter is defined by direct pole placement and applied to white
    noise to generate a random signal with a defined oscillatory peak frequency
    that exhibits random variability frequency, amplitude and waveform.

    Parameters
    ----------
    freq : float
        Peak resonant frequency of the simulated filter.
    sample_rate : float
        Sampling frequency for the simulation
    seconds : float
        Number of seconds of data to simulate
    r : float (0 < r < 1)
        Pole magnitude of simulated autoregressive resonance.
    noise_std : float
        Scaling of optional noise to add to simulation. Scaling is relative to
        standard-deviation of the simulated data.
    random_seed : int
        Optional random seed generation

    Returns
    -------
    ndarray
        A simulated time course.

    """
    if random_seed is not None:
        np.random.seed(random_seed)

    if freq > 0:
        freq_rads = (2 * np.pi * freq) / sample_rate
        a1 = np.array([1, -2*r*np.cos(freq_rads), (r**2)])
    else:
        a1 = np.poly(r)

    num_samples = int(sample_rate * seconds)

    x = signal.filtfilt(1, a1, np.random.randn(1, num_samples)).T

    if noise_std is not None:
        noise = np.std(x)*noise_std*np.random.randn(1, num_samples).T
        x = x + noise

    if random_seed is not None:
        np.random.seed()  # restore defaults

    return x
