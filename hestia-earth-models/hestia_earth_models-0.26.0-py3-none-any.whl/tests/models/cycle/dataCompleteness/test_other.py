from unittest.mock import patch

from hestia_earth.models.cycle.dataCompleteness.other import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.dataCompleteness.{MODEL_KEY}"


@patch(f"{class_path}.find_term_match", return_value=None)
def test_run_seed(mock_find_term):
    cycle = {}

    # on cropland => not complete
    cycle['site'] = {'siteType': 'cropland'}
    assert not run(cycle)

    # with input => complete
    mock_find_term.return_value = {'value': [10]}
    assert run(cycle) is True


@patch(f"{class_path}.is_orchard", return_value=False)
@patch(f"{class_path}.find_term_match", return_value=None)
def test_run_saplings(mock_find_term, mock_is_orchard):
    cycle = {}

    # on cropland => not complete
    cycle['site'] = {'siteType': 'cropland'}
    assert not run(cycle)

    # with orchard crop => not complete
    mock_is_orchard.return_value = True
    assert not run(cycle)

    # with input => complete
    mock_find_term.return_value = {'value': [10]}
    assert run(cycle) is True
