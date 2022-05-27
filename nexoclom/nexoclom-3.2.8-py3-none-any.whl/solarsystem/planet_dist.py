"""Determine distance and radial velocity relative to Sun."""
import numpy as np
from scipy.misc import derivative
import astropy.units as u
# from astroquery.jplhorizons import Horizons
from nexoclom.solarsystem.SSObject import SSObject


def planet_dist(planet_, taa=None, time=None):
    if isinstance(planet_, str):
        planet = SSObject(planet_)
        
        if planet.object is None:
            return None
    elif isinstance(planet_, SSObject):
        planet = planet_
    else:
        raise TypeError('solarsystemMB.planet_dist',
                        'Must give a SSObject or a object name.')

    if time is not None:
        raise NotImplementedError
        # et = spice.str2et(time.isot)
        # posvel, lt = spice.spkezr(planet.object, et, 'J2000',
        #                           'LT+S', 'Sun')
        #
        # position = np.array(posvel[0:3])*u.km
        # r = np.sqrt(np.sum(position**2))
        #
        # velocity = np.array(posvel[3:])*u.km/u.s
        # v_r = np.sum(position*velocity)/r
        # r = r.to(u.au)
    elif taa is not None:
        a = planet.a
        eps = planet.e

        # make sure taa is in radians. If not a quantity, assume it is.
        if isinstance(taa, type(1*u.s)):
            taa_ = taa.to(u.rad).value
        elif type(taa) in (int, float):
            taa_ = taa
        else:
            raise TypeError('taa must be a number or angle quantity')

        if eps > 0:
            # determine r
            r = a * (1-eps**2)/(1+eps*np.cos(taa_))
            P = np.sqrt(a**3/(1*u.au)**3) * u.yr

            # determine v_r = dr/dt
            def trueanom(time):
                # Mean anomally
                M = 2*np.pi*time/P.value

                # Determine eccentric anomaly from M = E-e*sin(E)
                EEtemp = np.linspace(0, 2*np.pi, 1001)
                mm = EEtemp - eps*np.sin(EEtemp)
                EE = np.array([np.interp(x, mm, EEtemp) for x in M])

                # True anomaly
                phi = (2*np.arctan(np.sqrt((1+eps)/(1-eps)) * np.tan(EE/2)) +
                       (2*np.pi)) % (2*np.pi)
                return phi

            def radius(time):
                phi = trueanom(time)
                r = a * (1-eps**2)/(1+eps*np.cos(phi))
                return r.value

            time = np.linspace(-1, 1, 2001)*P.value
            radvel = derivative(radius, time, dx=1e-3)
            radvel = radvel.astype(np.float64)
            ttt = trueanom(time)
            v_r = np.interp(taa_, ttt, radvel, period=2*np.pi)
            v_r *= a.unit/P.unit
            v_r = v_r.to(u.km/u.s)
        else:
            r, v_r = a, 0.*u.km/u.s
    else:
        print('Neither a time nor a true anomaly was given.')
        return None

    return r, v_r
