import pytest
import astropy.units as u
from nexoclom.atomicdata import PhotoRate
from pytest import approx


args = [('Na', 1.5, 3.2266666666666665e-06),
        ('Ca', 0.3*u.au, 0.0007777777777777777),
        ('X', 1.0*u.au, 1e-30)]

@pytest.mark.atomicdata
@pytest.mark.parametrize('species, aplanet, result', args)
def test_PhotoRate(species, aplanet, result, capsys):
    rate = PhotoRate(species, aplanet)
    assert rate.species == species
    if isinstance(aplanet, type(1*u.au)):
        assert rate.aplanet.value == aplanet.value
    else:
        assert rate.aplanet.value == aplanet
    assert rate.rate.value == approx(result)
    assert rate.rate.unit == 1./u.s
    _ = capsys.readouterr()

    print(rate)
    captured = capsys.readouterr()
    assert captured[0] == (f'Species = {rate.species}\n'
                           f'Distance = {rate.aplanet}\n'
                           f'Rate = {rate.rate}\n')
    assert captured[1] == ''

    
    