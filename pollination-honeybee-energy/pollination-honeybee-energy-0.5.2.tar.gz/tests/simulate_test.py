from pollination.honeybee_energy.simulate import SimulateModel, SimulateOsm, \
    SimulateIdf, SimulateModelRoomBypass
from queenbee.plugin.function import Function


def test_simulate_model():
    function = SimulateModel().queenbee
    assert function.name == 'simulate-model'
    assert isinstance(function, Function)


def test_simulate_osm():
    function = SimulateOsm().queenbee
    assert function.name == 'simulate-osm'
    assert isinstance(function, Function)


def test_simulate_idf():
    function = SimulateIdf().queenbee
    assert function.name == 'simulate-idf'
    assert isinstance(function, Function)


def test_simulate_model_room_bypass():
    function = SimulateModelRoomBypass().queenbee
    assert function.name == 'simulate-model-room-bypass'
    assert isinstance(function, Function)
