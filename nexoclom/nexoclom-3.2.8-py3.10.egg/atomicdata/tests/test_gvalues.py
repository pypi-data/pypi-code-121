import os
import pickle
import astropy.units as u
from nexoclom.atomicdata import gValue, RadPresConst
from pytest import approx
import pytest
# pylint: disable=no-member


with open(os.path.join(os.path.dirname(__file__),
                       'g_value_test_data.pkl'), 'rb') as f:
    gvalue_test_data, radpres_test_data = pickle.load(f)
 
args_gval = [('Na', 5891, 1.5, gvalue_test_data[0]),
             ('Ca', 4227*u.AA, 0.3, gvalue_test_data[1]),
             ('X', 3333*u.AA, 1.0*u.au, gvalue_test_data[2])]
args_rp = [('Na', 1.5, radpres_test_data[0]),
           ('Ca', 0.3*u.au, radpres_test_data[1]),
           ('X', 1.0*u.au, radpres_test_data[2])]

@pytest.mark.atomicdata
@pytest.mark.parametrize('species, wavelength, aplanet, result', args_gval)
def test_gValue(species, wavelength, aplanet, result):
    g = gValue(species, wavelength, aplanet)
    assert g.species == result['species'], 'Species Failure'
    assert g.wavelength == result['wavelength'], 'Wavelength failure'
    assert g.aplanet == result['aplanet'], 'aplanet failure'
    assert g.velocity.value == approx(result['velocity'].value), 'velocity failure'
    assert g.g.value == approx(result['g'].value), 'g-values failure'

@pytest.mark.atomicdata
def test_gvalue_bad_input():
    with pytest.raises(ValueError):
        gValue('Fk', 9999, 1)

@pytest.mark.atomicdata
@pytest.mark.parametrize('species, aplanet, result', args_rp)
def test_radpresconst(species, aplanet, result):
    rp_const = RadPresConst(species, aplanet)
    assert rp_const.species == result['species'], 'Species Failure'
    assert rp_const.aplanet == result['aplanet'], 'aplanet Failure'
    assert rp_const.velocity.value == approx(result['velocity'].value), 'velocity failure'
    assert rp_const.accel.value == approx(result['accel'].value), 'accel failure'

@pytest.mark.atomicdata
def test_radpres_bad_input():
    with pytest.raises(ValueError):
        RadPresConst('Fk', 1)