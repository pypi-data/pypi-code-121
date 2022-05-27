''' Determine the relative position of object to reference

This is basically a rewrite of cspice_spkezr without having to remember
all the options to set

Inputs:
    obj: target object name
    reference: reference object name
    et: either a single astropy Time object, a single et, a list of Time objects,
        or a numpy array of ETs.

Output:
    pos = position in km
    vel = velocity in km/s
'''
import numpy as np
import spiceypy as spice
from astropy.time import Time
import astropy.units as u
from nexoclom.solarsystem.load_kernels import load_kernels


def relative_position(obj, reference, ettemp, frame='J2000'):
    kernels = load_kernels()

    if isinstance(ettemp, Time):
        et = spice.str2et(ettemp.isot)
    elif isinstance(ettemp, float):
        et = ettemp
    else:
        et = [spice.str2et(e.isot) if type(e) == type(Time.now()) else e
              for e in ettemp]

    abcor = 'LT+S'

    if isinstance(et, float):
        posvel, lt = spice.spkezr(obj, et, frame, abcor, reference)
        pos, vel = posvel[:3], posvel[3:]
    else:
        pos = np.zeros((len(et),3))
        vel = np.zeros((len(et),3))
        for i, t in enumerate(et):
            posvel, lt = spice.spkezr(obj, t, frame, abcor, reference)
            pos[i,:] = np.array(posvel[:3])
            vel[i,:] = np.array(posvel[3:])
    pos *= u.km
    vel *= u.km/u.s

    for k in kernels:
        spice.unload(k)

    return pos, vel
