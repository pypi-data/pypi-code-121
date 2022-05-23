from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.faostat2018.landTransformationFromCropland20YearAverage import (
    MODEL, run, _should_run
)

class_path = f"hestia_earth.models.{MODEL}.landTransformationFromCropland20YearAverage"
fixtures_folder = f"{fixtures_path}/{MODEL}/landTransformationFromCropland20YearAverage"


@patch(f"{class_path}.find_term_match")
def test_should_run(mock_find):
    # no indicator => no run
    mock_find.return_value = {}
    should_run, *args = _should_run({})
    assert not should_run

    # with indicator => run
    mock_find.return_value = {'value': 10}
    should_run, *args = _should_run({})
    assert should_run is True

    # with indicator value 0 => no run
    mock_find.return_value = {'value': 0}
    should_run, *args = _should_run({})
    assert not should_run


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
