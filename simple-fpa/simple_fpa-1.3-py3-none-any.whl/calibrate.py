import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sb

def calibrate_band(model, sample, u_trim, smoothing):
    sample_size = len(sample)
    std = np.std(sample)
    band = 1.06*std*np.power(sample_size, smoothing)
    delta = 1 # this is only if on [0,1]
    u_band = band/delta
    i_band = int(u_band*sample_size)
    trim = int(u_trim*sample_size)

    if trim < i_band:
        print('Warning: Not enough trimming, look out for boundary effects.')

    return sample_size, band, i_band, trim
    
def calibrate_part(model, u_grid, frec):

    M = np.max(list(frec.keys()))
    m_min = np.min(list(frec.keys()))

    A_1 = 0*u_grid
    A_1_prime = 0*u_grid
    a = 0

    for m, pm in frec.items():
        A_1 += pm*np.power(u_grid, m-1)
        A_1_prime += pm*(m-1)*np.power(u_grid, m-2)
        a += m*pm/M

    A_1[0] = A_1[1] # avoid division by zero
    A_1_prime[0] = A_1_prime[1] # avoid division by zero

    A_2 = u_grid*A_1
    A_3 = (1-u_grid)*A_1

    A_4 = A_1/A_1_prime

    return M, A_1, A_2, A_3, A_4, a