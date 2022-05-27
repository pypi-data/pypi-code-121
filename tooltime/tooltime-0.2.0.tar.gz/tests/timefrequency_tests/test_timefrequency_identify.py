import pytest

import tooltime.spec


examples = []
for equivalent_set in tooltime.spec.equivalent_sets['Timefrequency']:
    examples.extend(equivalent_set.items())


@pytest.mark.parametrize('example', examples)
def test_get_timefrequency_representation(example):
    actual_representation, value = example
    detected_representation = tooltime.detect_timefrequency_representation(
        value
    )
    assert actual_representation == detected_representation

