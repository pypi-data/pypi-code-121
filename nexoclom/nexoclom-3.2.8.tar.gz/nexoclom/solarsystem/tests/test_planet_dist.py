import os
import numpy as np
import pandas as pd
import astropy.units as u
from nexoclom.solarsystem import SSObject, planet_dist
import pytest


table = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                 'perihelion_aphelion.csv'))

planet = table.planet.values
perihelion = table.perihelion.apply(lambda x: (x*u.km).to(u.au).value).values
aphelion = table.aphelion.apply(lambda x: (x*u.km).to(u.au).value).values

ind = [0, 5, 7]
args_dist = [(planet[ind[0]], 0, (perihelion[ind[0]], 0)),
             (planet[ind[1]], np.pi*u.rad, (aphelion[ind[1]], 0)),
             (SSObject(planet[ind[2]]), 0*u.deg, (perihelion[ind[2]], 0))]

@pytest.mark.solarsystem
@pytest.mark.parametrize('planet, taa, result', args_dist)
def test_planet_dist(planet, taa, result):
    r, v_r = planet_dist(planet, taa)
    
    assert r.value == pytest.approx(result[0], rel=0.01)
    assert v_r.value == pytest.approx(result[1], rel=0.01)
    assert (r.unit, v_r.unit) == (u.au, u.km/u.s)

@pytest.mark.solarsystem
def test_not_real_object():
    assert planet_dist('Fake') is None
    
@pytest.mark.solarsystem
def test_planet_dist_bad_input():
    with pytest.raises(TypeError):
        planet_dist(4)

    with pytest.raises(TypeError):
        planet_dist('Jupiter', 'bad')

@pytest.mark.solarsystem
@pytest.mark.xfail
def test_planet_dist_with_time():
    # Not setup to work with times yet
    r, v_r = planet_dist('Mercury', time='2021-10-20T12:00:00')
    assert r.value == pytest.approx(4, rel=0.01)
    assert v_r.value == pytest.approx(4, rel=0.01)
    assert (r.unit, v_r.unit) == (u.au, u.km/u.s)

@pytest.mark.solarsystem
def test_planet_dist_no_inputs():
    assert planet_dist('Mercury') is None
    