import os
import numpy as np
from scipy import interpolate
import pandas as pd
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom.solarsystem import SSObject
from nexoclom import Input, __file__ as basefile
from nexoclom.modelcode.source_distribution import surface_distribution
from nexoclom.modelcode.input_classes import SpatialDist
import nexoclom.math as mathMB

import matplotlib.pyplot as plt


# import warnings
# warnings.filterwarnings("error")

basepath = os.path.dirname(basefile)
if __name__ == '__main__':
    inputpath = os.path.join('test_data', 'inputfiles')
else:
    inputpath = os.path.join(basepath, 'modelcode', 'tests', 'test_data', 'inputfiles')


NPACKETS = 100000

def Q_ks(z):
    # Numerical Recipes (3rd edition), Chapter 6.14.12
    j = np.arange(100000) + 1
    # return 2*np.sum((-1.)**(j-1) * np.exp(-2*j**2 * z**2))
    return 1 - np.sqrt(2*np.pi)/z * np.sum(np.exp(-(2*j-1)**2*np.pi**2/(8*z**2)))

class Output_:
    def __init__(self, inputs):
        self.inputs = inputs
        self.npackets = NPACKETS
        self.randgen = np.random.default_rng()
        self.X0 = pd.DataFrame()


spatial_inputs = [{'type': 'surface spot',
                   'longitude': '4.712388',
                   'latitude': '0',
                   'sigma': '0.87266'},
                  {'type': 'uniform'},
                  {'type': 'uniform',
                   'exobase': 1.0,
                   'longitude': '1, 2',
                   'latitude': '0, 1'},
                  {'type': 'uniform',
                   'exobase': 1.0,
                   'longitude': '0, 0',
                   'latitude': '0, 0'}]


def spotmap(lon0, lat0, sigma0):
    spot0 = ((np.sin(lon0)*np.cos(lat0)).value,
             (-np.cos(lon0)*np.cos(lat0)).value,
             (np.sin(lat0)).value)
    longitude = np.linspace(0, 2*np.pi, 361)*u.rad
    latitude = np.linspace(-np.pi/2, np.pi/2, 181)*u.rad
    
    ptsx = np.outer(np.sin(longitude.value), np.cos(latitude.value))
    ptsy = -np.outer(np.cos(longitude.value), np.cos(latitude.value))
    ptsz = -np.outer(np.ones_like(longitude.value), np.sin(latitude.value))
    
    cosphi = ptsx*spot0[0]+ptsy*spot0[1]+ptsz*spot0[2]
    cosphi[cosphi > 1] = 1
    cosphi[cosphi < -1] = -1
    phi = np.arccos(cosphi)
    sourcemap_ = np.exp(-phi/sigma0.value)
    sourcemap = {'longitude': longitude,
                 'latitude': latitude,
                 'map': sourcemap_}
    
    return sourcemap


def ks_test(data, expected):
    p_x = np.sqrt(NPACKETS) + 0.12 + 0.11/np.sqrt(NPACKETS)
    cum_data = mathMB.CumDist(data)
    cum_expect = mathMB.CumDist(data, expected)
    
    D = np.max(np.abs(cum_data.sum - cum_expect.sum))
    p = Q_ks(p_x * D)
    
    if not np.isclose(p, 1):
        plt.plot(cum_data.x, cum_data.sum)
        plt.plot(cum_expect.x, cum_expect.sum)
        plt.show()
        from IPython import embed; embed()
    
    return D, p


@pytest.mark.modelcode
@pytest.mark.parametrize('sparams', spatial_inputs)
def test_surface_distribution(sparams):
    # Full surface uniform distribution
    inputfile = os.path.join(inputpath, 'Spatial.01.input')
    inputs = Input(inputfile)
    inputs.spatialdist = SpatialDist(sparams)
    outputs = Output_(inputs)
    
    surface_distribution(outputs)
    X0 = outputs.X0
    assert X0.shape == (NPACKETS, 6)
    
    longitude, latitude = X0.longitude.values, X0.latitude.values

    if sparams['type'] == 'uniform':
        # longitude
        lon = tuple(map(lambda x:x.value, inputs.spatialdist.longitude))
        expect_lon = np.ones_like(longitude)
        
        if lon[0] < lon[1]:
            expect_lon[(longitude < lon[0]) | (longitude > lon[1])] = 0
        else:
            expect_lon[(longitude > lon[1]) & (longitude < lon[0])] = 0

        # Latitude
        lat = tuple(map(lambda x:np.sin(x.value), inputs.spatialdist.latitude))
        expect_lat = np.ones_like(latitude)
        expect_lat[(np.sin(latitude) < lat[0]) | (np.sin(latitude) > lat[1])] = 0
    elif sparams['type'] == 'surface spot':
        sourcemap = spotmap(inputs.spatialdist.longitude,
                            inputs.spatialdist.latitude,
                            inputs.spatialdist.sigma)
        lon = sourcemap['longitude'].value
        lat = sourcemap['latitude'].value
        
        weight = sourcemap['map'] * np.sin(sourcemap['latitude'])
        expect_lon = np.interp(longitude, lon, np.sum(weight, axis=1))
        expect_lat = np.interp(np.sin(latitude), np.sin(lat),
                               np.sum(sourcemap['map'], axis=0))
        
    else:
        assert False
        
    from IPython import embed; embed()
    import sys; sys.exit()
    

    _, p_lon = ks_test(longitude, expect_lon)
    assert p_lon == pytest.approx(1)

    _, p_lat = ks_test(np.sin(latitude), expect_lat)
    assert p_lat == pytest.approx(1)


if __name__ == '__main__':
    for sparams in spatial_inputs:
        print(sparams)
        test_surface_distribution(sparams)
