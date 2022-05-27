import numpy as np
import astropy.units as u
from nexoclom.math import interpu
import pytest


def fn(x):
    return (x**np.random.random()*3 +
            (10*np.random.random()-5)*x**np.random.random()*3 +
            (10*np.random.random()-5))

@pytest.mark.math
def test_interpu():
    xp = np.arange(20)
    fp = fn(xp)
    
    points = np.random.rand(30)*20-5
    result = np.interp(points, xp, fp)
    test = interpu(points*u.km, xp*u.km, fp*u.km**3)

    assert test.value == pytest.approx(result)
    assert test.unit == u.km**3
    
    test = interpu((points*u.km).to(u.imperial.mi), xp*u.km, fp*u.km**3)
    assert test.value == pytest.approx(result)

    with pytest.raises(TypeError):
        interpu(points, xp*u.km, fp*u.km**3)

    with pytest.raises(TypeError):
        interpu(points*u.km, xp, fp*u.km**3)

    with pytest.raises(TypeError):
        interpu(points*u.km, xp*u.km, fp)

    with pytest.raises(u.UnitConversionError):
        interpu(points*u.s, xp*u.km, fp*u.km**3)
