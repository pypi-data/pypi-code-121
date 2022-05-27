import pytest

import tooltime.spec


@pytest.mark.parametrize(
    'timestamp_conversions', tooltime.spec.equivalent_sets['Timestamp'],
)
def test_convert_timestamps(timestamp_conversions):
    for from_representation, from_timestamp in timestamp_conversions.items():
        for to_representation, to_timestamp in timestamp_conversions.items():
            converted_timestamp = tooltime.convert_timestamp(
                timestamp=from_timestamp,
                from_representation=from_representation,
                to_representation=to_representation,
            )
            if to_representation == 'TimestampDatetime':
                assert (
                    converted_timestamp.timestamp() == to_timestamp.timestamp()
                )
            else:
                assert converted_timestamp == to_timestamp

