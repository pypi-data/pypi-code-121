""" Tests Input.__init__() and classes in input_classes.py
Note that this is more of a regression test than a unit test.
Compares with previously computed results."""
import os
import numpy as np
import pytest
import astropy.units as u
from astropy.time import Time
from nexoclom.solarsystem import SSObject
from nexoclom import Input, __file__ as basefile

basepath = os.path.dirname(basefile)
if __name__ == '__main__':
    inputpath = os.path.join('test_data', 'inputfiles')
else:
    inputpath = os.path.join(basepath, 'modelcode', 'tests', 'test_data', 'inputfiles')


@pytest.mark.modelcode
def test_geometry():
    inputfile01 = os.path.join(inputpath, 'Geometry.01.input')
    geometry01 = Input(inputfile01).geometry
    result = {'planet': SSObject('Jupiter'),
              'startpoint': 'Io',
              'objects': {SSObject('Jupiter'), SSObject('Io'), SSObject('Europa')},
              'type': 'geometry without starttime',
              'phi': (1*u.rad, 2*u.rad),
              'subsolarpoint': (3.14*u.rad, 0*u.rad),
              'taa': 1.57*u.rad}
    assert geometry01.__dict__ == result
    
    inputfile02 = os.path.join(inputpath, 'Geometry.02.input')
    geometry02 = Input(inputfile02).geometry
    result = {'planet': SSObject('Jupiter'),
              'startpoint': 'Io',
              'objects': {SSObject('Jupiter'), SSObject('Io')},
              'type': 'geometry with starttime',
              'time': Time('2022-03-08T19:53:21')}
    assert geometry02.__dict__ == result

    inputfile03 = os.path.join(inputpath, 'Geometry.03.input')
    geometry03 = Input(inputfile03).geometry
    result = {'planet':SSObject('Mercury'),
              'startpoint': 'Mercury',
              'objects': {SSObject('Mercury')},
              'type': 'geometry without starttime',
              'subsolarpoint': (0 * u.rad, 0 * u.rad),
              'phi': None,
              'taa': 3.14 * u.rad}
    assert geometry03.__dict__ == result
    
    assert geometry01 == geometry01
    assert geometry01 != geometry02
    assert geometry01 != geometry03

@pytest.mark.modelcode
def test_SurfaceInteraction():
    # sticktype = 'constant'
    inputfile01 = os.path.join(inputpath, 'SurfaceInteraction.01.input')
    interaction01 = Input(inputfile01).surfaceinteraction
    result = {'sticktype': 'constant',
              'stickcoef': 1.,
              'accomfactor': None}
    assert interaction01.__dict__ == result

    inputfile02 = os.path.join(inputpath, 'SurfaceInteraction.02.input')
    interaction02 = Input(inputfile02).surfaceinteraction
    result = {'sticktype': 'constant',
              'stickcoef': 0.5,
              'accomfactor': 0.2}
    assert interaction02.__dict__ == result

    assert interaction01 == interaction01
    assert interaction01 != interaction02

    # sticktype = 'temperature dependent
    inputfile03 = os.path.join(inputpath, 'SurfaceInteraction.03.input')
    interaction03 = Input(inputfile03).surfaceinteraction
    result = {'sticktype': 'temperature dependent',
              'accomfactor': 0.2,
              'A': (1.57014, -0.006262, 0.1614157)}
    assert interaction03.__dict__ == result

    inputfile04 = os.path.join(inputpath, 'SurfaceInteraction.04.input')
    interaction04 = Input(inputfile04).surfaceinteraction
    result = {'sticktype':'temperature dependent',
              'accomfactor':0.5,
              'A': (1., 0.001, 0.2)}
    assert interaction04.__dict__ == result

    inputfile05 = os.path.join(inputpath, 'SurfaceInteraction.05.input')
    interaction05 = Input(inputfile05).surfaceinteraction
    result = {'sticktype':'surface map',
              'stick_mapfile': 'default',
              'coordinate_system': 'solar-fixed',
              'subsolarlon': None,
              'accomfactor':0.5}
    assert interaction05.__dict__ == result

    inputfile06 = os.path.join(inputpath, 'SurfaceInteraction.06.input')
    interaction06 = Input(inputfile06).surfaceinteraction
    result = {'sticktype':'surface map',
              'stick_mapfile': 'Orbit3576.Ca.pkl',
              'coordinate_system': 'solar-fixed',
              'subsolarlon': None,
              'accomfactor':0.5}
    assert interaction06.__dict__ == result

@pytest.mark.modelcode
def test_Forces():
    inputfile01 = os.path.join(inputpath, 'Forces.01.input')
    forces01 = Input(inputfile01).forces
    result = {'gravity': True,
              'radpres': True}
    assert forces01.__dict__ == result

    inputfile02 = os.path.join(inputpath, 'Forces.02.input')
    forces02 = Input(inputfile02).forces
    result = {'gravity': False,
              'radpres': True}
    assert forces02.__dict__ == result

    inputfile03 = os.path.join(inputpath, 'Forces.03.input')
    forces03 = Input(inputfile03).forces
    result = {'gravity': True,
              'radpres': False}
    assert forces03.__dict__ == result

@pytest.mark.modelcode
def test_SpatialDist():
    inputfile01 = os.path.join(inputpath, 'Spatial.01.input')
    spatial01 = Input(inputfile01).spatialdist
    result = {'type': 'uniform',
              'longitude': (0*u.rad, 2*np.pi*u.rad),
              'latitude': (-np.pi/2*u.rad, np.pi/2*u.rad),
              'exobase': 1.}
    assert spatial01.__dict__ == pytest.approx(result)

    inputfile02 = os.path.join(inputpath, 'Spatial.02.input')
    spatial02 = Input(inputfile02).spatialdist
    result = {'type':'uniform',
              'longitude':(0*u.rad, 3.14*u.rad),
              'latitude':(0*u.rad, 0.79*u.rad),
              'exobase':2.1}
    assert spatial02.__dict__ == pytest.approx(result)
    
if __name__ == '__main__':
    # test_geometry()
    # test_SurfaceInteraction()
    # test_Forces()
    test_SpatialDist()
