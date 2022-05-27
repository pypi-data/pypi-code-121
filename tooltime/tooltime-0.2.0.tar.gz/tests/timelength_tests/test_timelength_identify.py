import pytest

import tooltime.spec


examples = []
for equivalent_set in tooltime.spec.equivalent_sets['Timelength']:
    examples.extend(equivalent_set.items())


@pytest.mark.parametrize('example', examples)
def test_get_timelength_representation(example):
    actual_representation, value = example
    detected_representation = tooltime.detect_timelength_representation(value)

    if actual_representation == 'TimelengthClockPhrase':
        assert detected_representation in [
            'TimelengthClock',
            'TimelengthClockPhrase',
        ]
    else:
        assert actual_representation == detected_representation

