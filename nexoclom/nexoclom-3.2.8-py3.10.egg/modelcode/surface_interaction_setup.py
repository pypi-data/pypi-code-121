import numpy as np
from scipy import interpolate
import astropy.units as u
import astropy.constants as const
from nexoclom.atomicdata import atomicmass
from nexoclom.modelcode.surface_temperature import surface_temperature
# from nexoclom.math.distributions import MaxwellianDist

def surface_interaction_setup(inputs):
    # Set up accommodation factor
    if inputs.surfaceinteraction.accomfactor != 0:
        longitude = np.arange(361)*np.pi/180.
        latitude = np.arange(181)*np.pi/180. - np.pi/2.
        longrid, latgrid = np.meshgrid(longitude, latitude)
        tsurf = surface_temperature(inputs.geometry, longrid.flatten(),
                                    latgrid.flatten())

        nt, nv, nprob = 201, 101, 101
        temperature = np.linspace(min(tsurf), max(tsurf), nt)*u.K
        v_temp = np.sqrt(2*temperature*const.k_B/
                         atomicmass(inputs.options.species))
        v_temp = v_temp.to(u.km/u.s)
        probability = np.linspace(0, 1, nprob)
        probgrid = np.ndarray((nt,nprob))
        for i,t in enumerate(temperature):
            vrange = np.linspace(0*u.km/u.s, np.max(v_temp[i]*3), nv)
            f_v = MaxwellianDist(vrange, t, inputs.options.species)
            cumdist = f_v.cumsum()
            cumdist -= cumdist.min()
            cumdist /= cumdist.max()
            probgrid[i,:] = np.interp(vrange.value, cumdist, probability)
            
        # v_interp = interpolate.interp2d(probability, temperature,
        #                                 probgrid)
        v_interp = interpolate.RectBivariateSpline(temperature.value,
                                                   probability, probgrid)
    else:
        v_interp = None
        
    surfaceint = {'v_accom': v_interp}
    
    return surfaceint
    