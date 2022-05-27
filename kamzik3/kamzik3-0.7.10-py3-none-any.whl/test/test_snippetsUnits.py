import pytest

from kamzik3 import DeviceError, DeviceUnitError, units
from kamzik3.devices.dummy.deviceDummy import DeviceDummy
from kamzik3.snippets.snippetsUnits import convert_to_unit, device_units


@pytest.fixture
def device():
    yield DeviceDummy(
        device_id="BladeRunner",
        config=None,
    )


def test_convert_to_unit_all_units():
    output = convert_to_unit("hertz", units.Quantity("10 kHz"))
    assert output == units.Quantity(10000, "hertz")


def test_convert_to_unit_value_unitless():
    output = convert_to_unit("hertz", units.Quantity("10"))
    assert output == units.Quantity(10, "hertz")


def test_convert_to_unit_target_unitless_value_unitless():
    output = convert_to_unit("", units.Quantity("2"))
    assert output == units.Quantity(2)


def test_convert_to_unit_target_unitless_value_with_unit():
    output = convert_to_unit("", units.Quantity("2 m"))
    assert output is None
