import numpy as np
from scipy import interpolate
import astropy.units as u
import astropy.constants as const
from nexoclom.atomicdata import atomicmass
from nexoclom.modelcode.surface_temperature import surface_temperature
from nexoclom.math.distributions import MaxwellianDist


class SurfaceInteraction:
    def __init__(self, inputs, **kwargs):
        # Sticking coeffienct setup
        if inputs.surfaceinteraction.sticktype == 'temperature dependent':
            A = inputs.surfaceinteraction.A
            def stickcoef(lon, lat):
                tsurf = surface_temperature(inputs.geometry, lon, lat)
                stickcoef = A[0] * np.exp(A[1]*tsurf) + A[2]
                stickcoef[stickcoef > 1.] = 1.
                stickcoef[stickcoef < 0.] = 0.
                return stickcoef
            
            self.stickcoef = stickcoef
        elif inputs.surfaceinteraction.sticktype == 'surface map':
            assert 0
        else:
            pass

        # Surface accommodation setup
        if inputs.surfaceinteraction.accomfactor == 0:
            pass
        else:
            longitude = np.arange(361)*np.pi/180.
            latitude = np.arange(181)*np.pi/180. - np.pi/2.
            longrid, latgrid = np.meshgrid(longitude, latitude)
            tsurf = surface_temperature(inputs.geometry, longrid.flatten(),
                                        latgrid.flatten())
            
            nt = kwargs['nt'] if 'nt' in kwargs else 201
            nv = kwargs['nv'] if 'nv' in kwargs else 101
            nprob = kwargs['nprob'] if 'nprob' in kwargs else 101
            
            temperature = np.linspace(min(tsurf), max(tsurf), nt)*u.K
            v_temp = np.sqrt(2*temperature*const.k_B/
                             atomicmass(inputs.options.species))
            v_temp = v_temp.to(u.km/u.s)
            probability = np.linspace(0, 1, nprob)
            probgrid = np.ndarray((nt,nprob))
            for i,t in enumerate(temperature):
                vrange = np.linspace(0*u.km/u.s, v_temp[i]*3, nv)
                f_v = MaxwellianDist(vrange, t, inputs.options.species)
                cumdist = f_v.cumsum()
                cumdist -= cumdist.min()
                cumdist /= cumdist.max()
                probgrid[i,:] = np.interp(probability, cumdist, vrange.value)
                
            self.v_interp = interpolate.RectBivariateSpline(temperature.value,
                                                            probability,
                                                            probgrid).ev
            self.probgrid = probgrid
            self.temperature = temperature
            self.probability = probability
            
