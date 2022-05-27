import numpy as np


def surface_temperature(geometry, longitude, latitude,
                        t0=100., t1=None, n=.25):
    if geometry.startpoint == 'Mercury':
        if t1 is None:
            t1 = 600. + 125*(np.cos(geometry.taa) - 1)/2.
            t1 = t1.value
        else:
            pass
        
        t_surf = np.zeros_like(longitude) + t0
        mask = (longitude <= np.pi/2) | (longitude >= 3*np.pi/2)
        t_surf[mask] = t0 + t1*np.abs(np.cos(longitude[mask]) *
                                      np.cos(latitude[mask]))**n
        
        return t_surf