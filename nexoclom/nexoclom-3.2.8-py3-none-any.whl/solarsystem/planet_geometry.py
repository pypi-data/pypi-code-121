''' Determine some basic geometry info from the SPICE kernels

For planets:
  * r in AU
  * drdt in km/s
  * TAA in radians
  * Sub-solar longitude and latitude in radians  -- not implemented
  * Sub-earth longitude and latitude in radians  -- not implemented
'''
import numpy as np
import astropy.units as u
import astropy.constants as const
from nexoclom.solarsystem.relative_position import relative_position
from nexoclom.solarsystem.SSObject import SSObject

def planet_geometry(time, planet):
    ## Determine planet location relative to sun
    # if planet.lower() == 'mercury':
    #     frame0 = 'MSGR_MSO'
    #     frame1 = 'IAU_MERCURY'
    # elif planet.lower() == 'jupiter':
    #     frame0 = 'Jupiter_Equatorial_Frame'
    #     frame1 = 'IAU_JUPITER'
    # elif planet.lower() == 'saturn':
    #     frame0 = 'Saturn_Equatorial_Frame'
    #     frame1 = 'IAU_SATURN'
    # else:
    #     print('Proper refrerence frames not defined for %s.' % planet)
    #     return -1

    # x0, v0 = relative_position(planet, 'Sun', time, frame=frame0)
    # x1, v1 = relative_position(planet, 'Sun', time, frame=frame1)
    x2, v2 = relative_position(planet, 'Sun', time, frame='J2000')
    #
    # e0, ve0 = relative_position(planet, 'Earth', time, frame=frame0)
    # e1, ve1 = relative_position(planet, 'Earth', time, frame=frame1)

    ## Compute TAA
    mu = const.M_sun * const.G
    x2, v2, mu = x2.value, v2.value, mu.to(u.km**3/u.s**2).value

    ## r and drdt from sun
    r2 = np.sqrt(np.sum(x2**2))
    drdt = np.sum(x2*v2)/r2

    ## Eccentricity vector
    e = np.sum(v2**2)*x2/mu - np.sum(x2*v2)*v2/mu - x2/r2
    ee = np.sqrt(np.sum(e**2))
    taa = np.arccos(np.sum(e*x2)/ee/r2)
    if np.sum(x2*v2) < 0:
        taa = 2*np.pi - taa

    return {'r':r2*u.km, 'drdt':drdt*u.km/u.s, 'taa':taa*u.rad}
