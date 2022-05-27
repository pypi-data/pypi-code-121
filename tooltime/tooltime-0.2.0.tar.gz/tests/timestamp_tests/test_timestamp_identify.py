import pytest

import tooltime.spec


examples = []
for equivalent_set in tooltime.spec.equivalent_sets['Timestamp']:
    examples.extend(equivalent_set.items())


@pytest.mark.parametrize('example', examples)
def test_detect_timestamp_type(example):
    actual_representation, value = example
    detected_representation = tooltime.detect_timestamp_representation(value)
    assert actual_representation == detected_representation

