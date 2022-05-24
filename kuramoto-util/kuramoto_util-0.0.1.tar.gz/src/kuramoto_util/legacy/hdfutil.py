import numpy as np
import h5py



def get_r(f: h5py.File, cutoff_t):
    attrs = get_attrs(f)
    t = np.array(f['t'])
    theta = np.array(f['theta'])
    N = attrs['N']
    z = np.sum(np.exp(1j*theta), axis=1)/N
    r = np.abs(z)

    
    N_t = len(t)

    rs = 0
    N_cut = 0
    r2s = 0
    for i in range(N_t):
        if t[i] > cutoff_t:
            N_cut += 1
            rs += r[i]
            r2s += r[i]**2

    r_ave = rs / N_cut
    r2_ave = r2s / N_cut
    r_stdev = np.sqrt(r2_ave - r_ave**2)
    return rs / N_cut, r_stdev


def get_attrs(f):
    d = dict()
    for key in f.attrs:
        d[key] = f.attrs[key]
    return d
