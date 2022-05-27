import copy

import numpy as np
import pytest
from pytest_lazyfixture import lazy_fixture
from numpy.testing import assert_allclose

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute


@pytest.fixture(
    params=[
        {
            "attribute_id": ATTR_POSITION,
            "default_value": 8.25,
            "min_value": -10,
            "max_value": 100,
            "unit": "nm",
            "default_type": float,
            "decimals": 2,
            "readonly": False,
            "description": "Motor position",
            "tolerance": (3, 5),
            "offset": 0,
            "factor": 1,
        },
    ]
)
def attribute_params(request):
    return request.param


@pytest.fixture(params=[lazy_fixture("attribute_params")])
def attribute(request):
    yield Attribute(**request.param)


def test_attribute_creation(attribute, attribute_params):
    assert isinstance(attribute, Attribute)
    assert attribute.attribute_id == ATTR_POSITION
    assert attribute[ATTR_DESCRIPTION] == attribute_params["description"]
    unit = attribute_params["unit"]
    assert attribute.value() == units.Quantity(
        f"{attribute_params['default_value']} {unit}"
    )
    assert attribute.within_limits(attribute.value())
    assert attribute.unit() == unit
    assert attribute.negative_tolerance() == units.Quantity(
        f"{attribute_params['tolerance'][0]} {unit}"
    )
    assert attribute.positive_tolerance() == units.Quantity(
        f"{attribute_params['tolerance'][1]} {unit}"
    )
    assert attribute.minimum() == units.Quantity(
        f"{attribute_params['min_value']} {unit}"
    )
    assert attribute.maximum() == units.Quantity(
        f"{attribute_params['max_value']} {unit}"
    )


@pytest.mark.parametrize("factor", [-1, 1])
@pytest.mark.parametrize("offset", [0, 10, -15])
@pytest.mark.parametrize("value", [-10, 80, 0])
def test_offset_factor_value(attribute, attribute_params, factor, offset, value):
    _attribute = copy.deepcopy(attribute)
    _attribute[OFFSET] = offset
    _attribute[FACTOR] = factor
    unit = attribute_params["unit"]

    if _attribute.numerical:
        assert _attribute.apply_offset_factor(value) == (value + offset) * factor
        assert _attribute.apply_offset_factor(-value) == (-value + offset) * factor
        assert _attribute.remove_offset_factor(value) == (value / factor) - offset
        assert _attribute.remove_offset_factor(-value) == (-value / factor) - offset

        _attribute[VALUE] = units.Quantity(f"{value} {unit}")
        assert (
            _attribute.remove_offset_factor()
            == (_attribute.value().m / factor) - offset
        )
        assert _attribute.within_limits(_attribute.value())
