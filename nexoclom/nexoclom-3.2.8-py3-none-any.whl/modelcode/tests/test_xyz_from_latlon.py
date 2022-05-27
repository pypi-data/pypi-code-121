import numpy as np
import pytest
import astropy.units as u
from nexoclom.modelcode.source_distribution import xyz_from_lonlat


@pytest.mark.modelcode
def test_xyz_from_latlon():
    # Check points around the equator for planet
    lon = np.arange(0, 2*np.pi, np.pi/4)*u.rad
    lat = np.zeros_like(lon)
    exobase = 1.
    isplan = True
    xyz = xyz_from_lonlat(lon, lat, isplan, exobase)

    x = [0, np.sqrt(2)/2, 1., np.sqrt(2)/2, 0., -np.sqrt(2)/2, -1, -np.sqrt(2)/2]*u.rad
    y = [-1, -np.sqrt(2)/2, 0, np.sqrt(2)/2, 1, np.sqrt(2)/2, 0, -np.sqrt(2)/2]*u.rad
    z = np.zeros_like(x)*u.rad
    expected = np.array([x, y, z])
    
    assert xyz == pytest.approx(expected)
    
    # Check points along latitude lines
    lon = np.linspace(0, np.pi, 5)
    lat = np.linspace(-np.pi/2, np.pi/2, 5)
    exobase = 2.
    isplan = True
    xyz = xyz_from_lonlat(lon, lat, isplan, exobase)

    z = np.array([-1, -np.sqrt(2)/2, 0, np.sqrt(2)/2, 1])
    z_ = np.array([0, np.sqrt(2)/2, 1, np.sqrt(2)/2, 0])
    x = np.array([0, np.sqrt(2)/2, 1., np.sqrt(2)/2, 0]) * z_
    y = np.array([-1, -np.sqrt(2)/2, 0., np.sqrt(2)/2, 1]) * z_
    expected = np.array([x, y, z]) * exobase

    assert xyz == pytest.approx(expected)
    
    # Check points around the equator for moon
    lon = np.arange(0, 2*np.pi, np.pi/4)*u.rad
    lat = np.zeros_like(lon)
    exobase = 1.
    isplan = False
    xyz = xyz_from_lonlat(lon, lat, isplan, exobase)

    x = [0, -np.sqrt(2)/2, -1., -np.sqrt(2)/2, 0., np.sqrt(2)/2, 1, np.sqrt(2)/2]*u.rad
    y = [-1, -np.sqrt(2)/2, 0, np.sqrt(2)/2, 1, np.sqrt(2)/2, 0, -np.sqrt(2)/2]*u.rad
    z = np.zeros_like(x)*u.rad
    expected = np.array([x, y, z])
    
    assert xyz == pytest.approx(expected)
    
    # Check points along latitude lines
    lon = np.linspace(0, np.pi, 5)
    lat = np.linspace(-np.pi/2, np.pi/2, 5)
    exobase = 2.
    isplan = False
    xyz = xyz_from_lonlat(lon, lat, isplan, exobase)

    z = np.array([-1, -np.sqrt(2)/2, 0, np.sqrt(2)/2, 1])
    z_ = np.array([0, np.sqrt(2)/2, 1, np.sqrt(2)/2, 0])
    x = np.array([0, -np.sqrt(2)/2, -1., -np.sqrt(2)/2, 0]) * z_
    y = np.array([-1, -np.sqrt(2)/2, 0., np.sqrt(2)/2, 1]) * z_
    expected = np.array([x, y, z]) * exobase

    assert xyz == pytest.approx(expected)
    
    
if __name__ == '__main__':
    test_xyz_from_latlon()
