from unittest.mock import patch
import json
from tests.utils import fake_new_practice, fixtures_path

from hestia_earth.models.cycle.residueRemoved import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no products => run
    cycle = {'dataCompleteness': {'products': True}}
    assert _should_run(cycle) is True

    # with crop products
    cycle['products'] = [{'term': {'termType': 'crop'}}]

    # with residue removed product => not run
    cycle['products'][0]['term']['@id'] = 'wheatStraw'
    assert not _should_run(cycle)

    # without residue removed product => run
    cycle['products'][0]['term']['@id'] = 'wheatGrain'
    assert _should_run(cycle) is True


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected
