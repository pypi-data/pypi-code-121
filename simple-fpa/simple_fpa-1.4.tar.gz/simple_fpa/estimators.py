import numpy as np
from scipy.signal import fftconvolve

def q_smooth(sorted_bids, kernel, sample_size, band, i_band, trim, is_sorted = False, reflect = True, paste_ends = False):
    
    if is_sorted == False:
        sorted_bids = np.sort(sorted_bids)
    
    spacings = sorted_bids - np.roll(sorted_bids,1)
    spacings[0] = 0
    
    if reflect == False:
        mean = spacings.mean()
        out = (fftconvolve(spacings-mean, kernel, mode = 'same') + mean)*sample_size
    
    if reflect == True:
        reflected = np.concatenate((np.flip(spacings[:trim]), spacings, np.flip(spacings[-trim:])))
        out = fftconvolve(reflected, kernel, mode = 'same')[trim:-trim]*sample_size
    
    if paste_ends == True:
        out[:trim] = out[trim]
        out[-trim:] = out[-trim]
    
    return out

def f_smooth(bids, kernel, sample_size, band, i_band, trim, paste_ends = False, reflect = False):
    histogram, _ = np.histogram(bids, sample_size, range = (0,1))
    
    if reflect == False:
        mean = histogram.mean()
        out = fftconvolve(histogram - mean, kernel, mode = 'same') + mean
        
    if reflect == True:
        reflected = np.concatenate((np.flip(histogram[:trim]), histogram, np.flip(histogram[-trim:])))
        out = fftconvolve(reflected, kernel, mode = 'same')[trim:-trim]
    
    if paste_ends == True:
        out[:trim] = out[trim]
        out[-trim:] = out[-trim]
    
    return out

def v_smooth(hat_Q, hat_q, A_4):
    return hat_Q + A_4*hat_q

def d(arr):
    diff = arr - np.roll(arr, 1)
    diff[0] = diff[1]
    return diff*len(diff)
    
def int_lowbound(arr):
    return np.flip(np.cumsum(np.flip(arr)))/len(arr)

def int_uppbound(arr):
    return np.cumsum(arr)/len(arr)

def total_surplus(v, M, A_1, A_2, A_3, A_4, a):
    return int_lowbound(v*d(A_2))

def bidder_surplus(v, M, A_1, A_2, A_3, A_4, a):
    return a*int_lowbound(A_3*d(v))

def revenue(v, M, A_1, A_2, A_3, A_4, a):
    return total_surplus(v, M, A_1, A_2, A_3, A_4, a) - M*bidder_surplus(v, M, A_1, A_2, A_3, A_4, a)

def total_surplus_from_Q(Q, M, A_1, A_2, A_3, A_4, a):
    psi = d(A_2)
    chi = psi - d(A_4*psi)
    return A_4[-1]*psi[-1]*Q[-1]-A_4*psi*Q + int_lowbound(chi*Q)