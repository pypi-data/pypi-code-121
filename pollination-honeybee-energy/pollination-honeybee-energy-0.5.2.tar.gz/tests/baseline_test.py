from pollination.honeybee_energy.baseline import Geometry2004, Constructions2004, \
    Lighting2004, Hvac2004, RemoveEcms
from queenbee.plugin.function import Function


def test_geometry2004():
    function = Geometry2004().queenbee
    assert function.name == 'geometry2004'
    assert isinstance(function, Function)


def test_constructions2004():
    function = Constructions2004().queenbee
    assert function.name == 'constructions2004'
    assert isinstance(function, Function)


def test_lighting2004():
    function = Lighting2004().queenbee
    assert function.name == 'lighting2004'
    assert isinstance(function, Function)


def test_hvac2004():
    function = Hvac2004().queenbee
    assert function.name == 'hvac2004'
    assert isinstance(function, Function)


def test_remove_ecms():
    function = RemoveEcms().queenbee
    assert function.name == 'remove-ecms'
    assert isinstance(function, Function)
