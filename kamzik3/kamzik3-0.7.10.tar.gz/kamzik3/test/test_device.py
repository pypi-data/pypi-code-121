import pytest

import kamzik3
from kamzik3 import DeviceError, DeviceUnitError, units
from kamzik3.constants import *
from kamzik3.devices.device import Device


@pytest.fixture
def device():
    yield Device(device_id="BladeRunner", config=None)


def test_device_creation(device):
    assert device.device_id == "BladeRunner"
    assert device.session is kamzik3.session
    assert device.get_value(ATTR_ID) == "BladeRunner"


@pytest.mark.parametrize("status", STATUSES_PRIORITY)
def test_device_status(device, status):
    device.set_status(status)
    assert device.get_value(ATTR_STATUS) == status


def test_device_units_attribute_with_units(device):
    device.create_attribute(
        "Frame rate",
        default_value=1,
        default_type=int,
        unit="Hz",
        min_value=1,
        max_value=10e6,
    )
    output = device.to_device_unit("Frame rate", "10 kHz")
    assert output == units.Quantity(10000, "hertz")


def test_device_units_value_none(device):
    device.create_attribute(
        "Frame rate",
        default_value=1,
        default_type=int,
        unit="Hz",
        min_value=1,
        max_value=10e6,
    )
    with pytest.raises(DeviceUnitError):
        device.to_device_unit("Frame rate", None)


def test_device_units_value_numerical(device):
    device.create_attribute(
        "Frame rate",
        default_value=1,
        default_type=int,
        unit="Hz",
        min_value=1,
        max_value=10e6,
    )
    output = device.to_device_unit("Frame rate", 2.33)
    assert output == units.Quantity(2.33, "hertz")


def test_device_units_value_zero(device):
    device.create_attribute(
        "Frame rate",
        default_value=1,
        default_type=int,
        unit="Hz",
        min_value=1,
        max_value=10e6,
    )
    output = device.to_device_unit("Frame rate", 0.0)
    assert output == units.Quantity(0, "hertz")


def test_device_units_value_bool(device):
    device.create_attribute(
        "Doit",
        default_value=True,
        default_type=bool,
    )
    with pytest.raises(DeviceUnitError):
        device.to_device_unit("Doit", False)


def test_device_units_attribute_with_units_value_no_unit(device):
    device.create_attribute(
        "Frame rate",
        default_value=1,
        default_type=int,
        unit="Hz",
        min_value=1,
        max_value=10e6,
    )
    output = device.to_device_unit("Frame rate", "10")
    assert output == units.Quantity(10, "hertz")


def test_device_units_attribute_without_units(device):
    device.create_attribute(
        "Run number",
        default_value=1,
        default_type=int,
        min_value=1,
    )
    output = device.to_device_unit("Run number", "2")
    assert output == units.Quantity(2, "")


def test_device_units_attribute_without_units_value_with_unit(device):
    device.create_attribute(
        "Run number",
        default_value=1,
        default_type=int,
        min_value=1,
    )
    with pytest.raises(DeviceUnitError):
        device.to_device_unit("Run number", "2 m")


def test_device_units_mismatch(device):
    device.create_attribute(
        "Length",
        default_value=1.56,
        default_type=float,
        unit="mm",
        min_value=1,
    )
    with pytest.raises(DeviceUnitError):
        device.to_device_unit("Length", "2 kg")


def test_device_units_attribute_without_units_value_percentage(device):
    device.create_attribute(
        "Used percentage",
        default_value=1,
        default_type=float,
        min_value=0,
        max_value=100,
    )
    output = device.to_device_unit("Used percentage", "2 %")
    assert output == units.Quantity(2, "")


def test_device_units_attribute_not_existing(device):
    device.create_attribute(
        "Used percentage",
        default_value=1,
        default_type=float,
        min_value=0,
        max_value=100,
    )
    with pytest.raises(DeviceError):
        device.to_device_unit("Frog", "2 %")
