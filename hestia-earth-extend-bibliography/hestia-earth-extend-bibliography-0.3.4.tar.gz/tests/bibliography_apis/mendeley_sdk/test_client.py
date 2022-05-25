from unittest.mock import patch
import json
import pickle

from tests.utils import fixtures_path, get_citations, clean_bibliography
from hestia_earth.extend_bibliography.bibliography_apis.mendeley_sdk.client import get_client, exec_search, \
    create_biblio

file_content = b"{}"


class FakeMendeleySearch():
    def list(self, *args):
        with open(f"{fixtures_path}/mendeley-sdk/result.pickle", 'rb') as f:
            values = pickle.load(f)
        return values


class FakeCatalog():
    def search(self, value, **args): return FakeMendeleySearch()


class FakeSession():
    def __init__(self):
        self.catalog = FakeCatalog()


class FakeAuth():
    def authenticate(self): return FakeSession()


@patch('mendeley.Mendeley.start_client_credentials_flow', return_value=FakeAuth())
def test_extend_mendeley(*args):
    title = get_citations()[0]
    client = get_client(mendeley_username=1, mendeley_password='pwd')
    items = exec_search(client, 'title')(title)
    assert items[0]['title'] == title


def test_create_biblio():
    with open(f"{fixtures_path}/mendeley-sdk/bibliography.json", 'r') as f:
        expected_biblio = json.load(f)
    with open(f"{fixtures_path}/mendeley-sdk/actors.json", 'r') as f:
        expected_actors = json.load(f)
    data = FakeMendeleySearch().list().items[0]
    title = get_citations()[0]
    (biblio, actors) = create_biblio(data, 'title', title)
    assert clean_bibliography(biblio) == expected_biblio
    assert actors == expected_actors
