from unittest.mock import patch
import json

from tests.utils import fixtures_path, get_citations, clean_actors, clean_bibliography
from hestia_earth.extend_bibliography.bibliography_apis.wos_soap.client import (
    get_client, exec_search, search_query, create_biblio
)


def fake_parse():
    with open(f"{fixtures_path}/wos-soap/response.json", 'r') as f:
        return json.load(f)


@patch('hestia_earth.extend_bibliography.bibliography_apis.wos_soap.client.WosClient.__enter__', return_value=())
def test_get_client(mock_client):
    with get_client() as client:
        mock_client.assert_called_once()
        assert client is not None


@patch('wos.utils.query', return_value=())
@patch('xmltodict.parse', return_value=fake_parse())
def test_exec_search(*args):
    title = get_citations()[0]
    items = exec_search('client')(title)
    assert items[0]['title'] == title


def test_search_query():
    assert search_query('test (with parenthesis)') == 'TI=(test)'
    assert search_query('test : with semi-colon') == 'TI=(test)'
    assert search_query('t' * 100) == f"TI=({'t' * 50})"


def test_create_biblio():
    with open(f"{fixtures_path}/wos-soap/bibliography.json", 'r') as f:
        expected_biblio = json.load(f)
    with open(f"{fixtures_path}/wos-soap/actors.json", 'r') as f:
        expected_actors = json.load(f)
    data = fake_parse().get('return').get('records')
    title = get_citations()[0]
    (biblio, actors) = create_biblio(title, data)
    # actor ids are all random, so update result to make sure tests are passing
    assert clean_bibliography(biblio) == expected_biblio
    assert list(map(clean_actors(expected_actors), actors)) == expected_actors
