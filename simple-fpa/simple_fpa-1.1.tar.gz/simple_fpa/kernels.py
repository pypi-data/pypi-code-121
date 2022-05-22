import numpy as np
import scipy as sp

def tri(u):
    return np.maximum(35*np.power(1 - np.power(u, 2), 3)/32, 0)

def epa(u):
    return np.maximum(3*(1 - np.power(u, 2))/4, 0)

def rec(u):
    return (np.sign(1/2 - np.abs(u)) + 1)/2

def make_kernel(u_grid, i_band, kernel = tri):
    return np.array([kernel(j/i_band)/i_band for j in range(-i_band+1, i_band)]), 2*np.square(kernel(u_grid)).mean()