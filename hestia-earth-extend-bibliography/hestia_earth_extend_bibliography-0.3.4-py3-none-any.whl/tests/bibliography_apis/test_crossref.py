from unittest.mock import patch
import json

from tests.utils import fixtures_path, get_citations, clean_actors, clean_bibliography, order_lists
from hestia_earth.extend_bibliography.bibliography_apis.crossref import extend_crossref


def get_works():
    with open(f"{fixtures_path}/crossref/response.json", 'r') as f:
        return json.load(f)


def get_exception(): raise Exception('error')


@patch('habanero.Crossref.works', return_value=get_works())
def test_extend_crossref(*args):
    with open(f"{fixtures_path}/crossref/results.json", 'r') as f:
        expected = json.load(f).get('results')
    (actors, bibliographies) = extend_crossref(get_citations())
    # actor ids are all random, so update result to make sure tests are passing
    result = list(map(clean_actors(expected), actors)) + list(map(clean_bibliography, bibliographies))
    assert order_lists(result) == order_lists(expected)


@patch('habanero.Crossref', side_effect=get_exception)
def test_extend_crossref_exception(*args):
    assert extend_crossref(['title']) == ([], [])
