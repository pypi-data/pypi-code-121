import pytest

import tooltime.spec


@pytest.mark.parametrize(
    'timeperiod_conversions', tooltime.spec.equivalent_sets['Timeperiod'],
)
def test_convert_timeperiods(timeperiod_conversions):
    for from_representation, from_timeperiod in timeperiod_conversions.items():
        for to_representation, to_timeperiod in timeperiod_conversions.items():
            converted_timeperiod = tooltime.convert_timeperiod(
                timeperiod=from_timeperiod,
                from_representation=from_representation,
                to_representation=to_representation,
            )
            assert converted_timeperiod == to_timeperiod


