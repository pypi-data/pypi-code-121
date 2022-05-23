from unittest.mock import patch
import json

from tests.utils import fixtures_path, fake_new_property
from hestia_earth.models.cycle.energyContentLowerHeatingValue import TERM_ID, PROPERTY_KEY, run, _should_run_input

class_path = f"hestia_earth.models.cycle.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/cycle/{TERM_ID}"


def test_should_run_input():
    input = {}

    # without dryMatter property => no run
    assert not _should_run_input(input)

    # with min and max and value => NO run
    input = {
        'properties': [{
            'term': {'@id': PROPERTY_KEY},
            'value': 50
        }]
    }
    assert _should_run_input(input) is True


@patch(f"{class_path}.get_wood_fuel_terms", return_value=['woodPellets', 'woodFuel'])
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
