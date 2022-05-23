import pandas as pd
from scipy.integrate import cumtrapz
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def calculate_capacitance(current: list, frequency: float, V_out: float, W: float, L: float, n_tft=500) -> list:
    """
    Function that calculates capacitance from I-V data recorded. Since data are
    acquired as AC signal then C = I/(2*pi*f*V_out)

    Parameters
    ----------
    current : list of float
        Current value registered from lock-in amplifier
    frequency : float
        DFrequency of acquisition
    V_out : float
        RMS of peak-to-peak value of base voltage in lock-in amplifier
    W : float
        Width of the transistor's channel in meters
    L : float
        Length of the transistor's channel in meters
    n_tft : int, optional
        Numer of trasistors in the sample. The default is 500.

    Returns
    -------
    C : float
        Values of capacitance

    """
    C = current /(2*3.1415*frequency*V_out)
    C = C-min(C) #remove parasite capacitance
    return C

def calculate_DOS(capacitance: list, oxide_capacitance: float, W: float, L: float, t: float) -> list:
    """
    Function that calculated density of states from capacitance data

    Parameters
    ----------
    capacitance : list of float
        Capacitance data
    oxide_capacitance : float
        Specific capacitance of oxide dielectric
    W : float
        Width of transistor channel in meters
    L : float
        Length of transistor channel in meteres
    t : float
        Thickness of dielectric

    Returns
    -------
    list of float
        Values of density of states

    """
    q0 = 1.6e-19 #electron charge
    CD = (capacitance*oxide_capacitance) / (oxide_capacitance-capacitance)
    return (CD /(q0*W*L*t))

def calculate_energy_range(capacitance: list, oxide_capacitance: float, voltage: list, correction=0, init = 0) -> list:
    """
    Function that calculates energy (or surface potential) from data

    Parameters
    ----------
    capacitance : list of float
        Values of measured capacitance
    oxide_capacitance : float
        Specific capacitance of oxide layer
    voltage : list of float
        Values of voltage offset used in CV measure
    correction : float, optional
        Optional correction to energy scale (account for flat band
                                             voltage). The default is 0.
    init : float, optional
        Initial value for integration. The default is 0.

    Returns
    -------
    E : list of float
        Values of energy range.

    """
    E = cumtrapz(1-capacitance/oxide_capacitance,voltage, initial = init)+correction
    return E

def find_fit_interval(E: list, g: list , FitLeft: float, FitRight: float ):
    """
    Function that finds intervals for fitting of DOS vs Energy

    Parameters
    ----------
    E : list of float
        Energy values
    g : list of float
        DOS values
    FitLeft : float
        Left margin to fit data
    FitRight : float
        DRight margin to fit data

    Returns
    -------
    E : list of float
        Energy range between Left and Right
    g : list of float
        DOS range between Left and Right

    """
    fit_interval = np.where((E>=FitLeft) & (E<=FitRight))
    fit_interval = fit_interval[0]
    g = g[fit_interval]
    E = E[fit_interval]
    return E, g

def c_thick_func(phi, k, omega, delta):
    """
    Analytical function used to fit CV data in function of surface potential.
    Paramters are k, omega and delta while phi is the variable.
    """
    epsilon_0 = 8.85e-12
    epsilon=10
    output = []
    for x in range(len(phi)):
        num = np.exp(omega*(phi[x]-delta)) -1
        den = np.sqrt(2*(np.exp(omega*(phi[x]-delta))-omega*(phi[x]-delta)-1))
        if phi[x]-delta >=  0:
            p1 = epsilon*epsilon_0 * np.sqrt(k/omega)
        elif phi[x]-delta < 0 :
            p1 = -epsilon*epsilon_0 * np.sqrt(k/omega)
        output.append(p1*num/den)   

    return output
