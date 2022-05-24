from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.aggregation.cycle.practice import _new_practice


@patch('hestia_earth.aggregation.cycle.practice.download_hestia', return_value=TERM)
def test_new_practice(*args):
    # with a Term as string
    practice = _new_practice('term')
    assert practice == {
        '@type': 'Practice',
        'term': TERM
    }

    # with a Term as dict
    practice = _new_practice(TERM, 10)
    assert practice == {
        '@type': 'Practice',
        'term': TERM,
        'value': [10],
        'statsDefinition': 'cycles'
    }
