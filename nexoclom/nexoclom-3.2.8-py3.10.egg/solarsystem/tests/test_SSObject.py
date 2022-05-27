from nexoclom.solarsystem import SSObject
import pytest


@pytest.mark.solarsystem
def test_SSObject():
    p0 = SSObject('Mercury')
    assert p0.object == 'Mercury'
    assert p0.type == 'Planet'
    assert p0.moons is None
    assert len(p0) == 1

    p1 = SSObject('Jupiter')
    assert p1.object == 'Jupiter'
    assert p1.type == 'Planet'
    assert len(p1.moons) == 4
    assert len(p1) == 5
    
    p2 = SSObject('Io')
    assert p2.object == 'Io'
    assert p2.type == 'Moon'
    assert p2.orbits == 'Jupiter'
    
    p3 = SSObject('Fake')
    assert p3.object is None
    
    p4 = SSObject('Sun')
    assert p4.object == 'Sun'
    assert p4.type == 'Star'
    assert p4.orbits == 'Milky Way'

    p5 = SSObject('Sun')
    assert p4 == p5
    assert p1 != p5
