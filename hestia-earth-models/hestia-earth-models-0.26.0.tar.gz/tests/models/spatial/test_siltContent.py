from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.spatial.siltContent import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    site = {'measurements': []}

    # without other measurements
    should_run, *_ = _should_run(site)
    assert not should_run

    # with measumrents => run
    site['measurements'] = [
        {'term': {'@id': 'clayContent'}, 'value': [10]},
        {'term': {'@id': 'sandContent'}, 'value': [20]}
    ]
    should_run, *_ = _should_run(site)
    assert should_run is True


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected
