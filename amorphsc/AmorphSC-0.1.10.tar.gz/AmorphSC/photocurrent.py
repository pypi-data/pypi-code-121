import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def calculate_PC(amplitude: list, sensitivity: float, gain: list, change_positions: list) -> np.ndarray:
    """
    Function that given input data returns the photocurrent spectra calculated
    with each 

    Parameters
    ----------
    amplitude : list of float
        input data of photocurrent
    gain : list of float
        vector with gains used
    sensitivity : float
        sensitivity of lockin
    change_positions : list of float
        vector with positions at which the gain has been changed

    Returns
    -------
    Amp: numpy array
        calculated amplitude photocurrent

    """
    
    Amp = []#vector of amplitudes
    sens = sensitivity #sensitivity 
    p = 0 # counter for initial position
    for i, j in enumerate(change_positions):
        amp = amplitude[p:j+1] #take that part of spectrum
        amp = amp*sens*1e-4 /gain[i] #adjust with gain and sens
        p = j+1
        Amp = np.concatenate((Amp, amp))
    return Amp

def lamp_spec(amplitude: list, wavelength: list, sensitivity: float, gain: list, change:list , diode_area: float) -> np.ndarray:
    """
    Function that takes into account a set of lamp data and returns the adjustment
    of the set with the sensitivity of photodiode

    Parameters
    ----------
    
    amplitude : list of float
        values of lamp amplitude   
    wavelength : list of float
        values of acquired wavelength
    sensitivity : float
        lockin sensitivity
    gain : list of float
        vector with gains used
    change : list of float
        vector with positions at which the gain has been changed
    
    Returns
    -------
    L1/A : numpy array
        vector with data adjusted with sensitivity

    """
    A = diode_area
    L1=[]
    
    #import photodiode sensitivities
    try:
        pdc = pd.read_csv("SensitivityPhotodiode.dat", sep="\t", names=["WL", "S"])
    except:
        print("You must have the file with diode sensitivity in the folder!")
        exit()
    #perform and interpolation to smooth conversion
    pdc_int = interp1d(pdc.WL, pdc.S)
    sens_new_WL = np.linspace(200,1000, 1000 )
    sens_new = pdc_int(sens_new_WL)
    #calculate spectrum of lamp
    PC = calculate_PC(amplitude, sensitivity, gain, change)
    #now multiply sensitivity
    for i in range(len(wavelength)):
        for j in range(len(sens_new_WL)):
            if (wavelength[i] >= sens_new_WL[j] and wavelength[i] < sens_new_WL[j+1]):
                L1.append(PC[i] /( 1e-3 * sens_new[j]))
                break
            else: continue
    L1 = np.asarray(L1)
    #return adjusted values in W/cm^2
    return L1/A