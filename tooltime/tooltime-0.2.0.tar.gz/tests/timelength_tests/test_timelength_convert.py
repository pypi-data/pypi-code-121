import pytest

import tooltime.spec


@pytest.mark.parametrize(
    'timelength_conversions', tooltime.spec.equivalent_sets['Timelength'],
)
def test_convert_timelengths(timelength_conversions):
    for from_representation, from_timelength in timelength_conversions.items():
        for to_representation, to_timelength in timelength_conversions.items():
            converted_timelength = tooltime.convert_timelength(
                timelength=from_timelength,
                from_representation=from_representation,
                to_representation=to_representation,
            )
            assert converted_timelength == to_timelength

