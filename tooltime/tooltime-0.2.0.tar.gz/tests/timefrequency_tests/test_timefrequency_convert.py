import pytest

import tooltime.spec


@pytest.mark.parametrize(
    'timefrequency_conversions',
    tooltime.spec.equivalent_sets['Timefrequency'],
)
def test_convert_timefrequencys(timefrequency_conversions):
    for (
        from_representation,
        from_timefrequency,
    ) in timefrequency_conversions.items():
        for (
            to_representation,
            to_timefrequency,
        ) in timefrequency_conversions.items():
            converted_timefrequency = tooltime.convert_timefrequency(
                timefrequency=from_timefrequency,
                from_representation=from_representation,
                to_representation=to_representation,
            )

            if to_representation != 'TimefrequencyFrequency':
                to_timefrequency = tooltime.timefrequency_to_frequency(
                    to_timefrequency
                )
                converted_timefrequency = tooltime.timefrequency_to_frequency(
                    converted_timefrequency
                )

            assert converted_timefrequency == to_timefrequency

