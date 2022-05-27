import pytest

import tooltime.spec


examples = []
for equivalent_set in tooltime.spec.equivalent_sets['Timeperiod']:
    examples.extend(equivalent_set.items())


@pytest.mark.parametrize('example', examples)
def test_get_timeperiod_representation(example):
    actual_representation, value = example
    detected_representation = tooltime.detect_timeperiod_representation(value)
    assert actual_representation == detected_representation

