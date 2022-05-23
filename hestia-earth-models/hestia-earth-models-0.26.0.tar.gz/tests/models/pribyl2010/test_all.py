from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.pribyl2010._all import MODEL, run

class_path = f"hestia_earth.models.{MODEL}"
fixtures_folder = f"{fixtures_path}/{MODEL}/all"


@patch(f"hestia_earth.models.{MODEL}.utils._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected
