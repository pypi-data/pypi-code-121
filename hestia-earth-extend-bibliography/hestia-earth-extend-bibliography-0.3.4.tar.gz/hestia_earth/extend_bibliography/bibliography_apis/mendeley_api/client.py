import requests
from hestia_earth.schema import Bibliography

from hestia_earth.extend_bibliography.bibliography_apis.utils import ORINGAL_FIELD, extend_bibliography


class ApiClient():
    def __init__(self, api_url: str):
        self.api_url = api_url

    def __enter__(self):
        return self

    def __exit__(*args):
        return False


def create_biblio(bibliography: dict, key: str, value: str):
    biblio = Bibliography()
    # save title here since closest bibliography might differ
    biblio.fields[ORINGAL_FIELD + key] = value if bibliography else None
    biblio.fields[key] = value
    authors = bibliography.get('authors', []) if bibliography else []
    (extended_biblio, actors) = extend_bibliography(authors, bibliography.get('year')) if bibliography else ({}, [])
    return (
        {**biblio.to_dict(), **bibliography, **extended_biblio},
        actors
    ) if bibliography else (biblio.to_dict(), [])


def _exec_search_by(api_url: str, key: str, value: str):
    return requests.get(f"{api_url}?limit=50&{key}={value.rstrip()}").json().get('results', [])


def _exec_search_by_title(api_url: str, value: str):
    items = _exec_search_by(api_url, 'title', value)
    # try a search with shorter value if no results found
    run_short_title_search = len(items) == 0 and len(value) > 100
    items = _exec_search_by(api_url, 'title', value[:100]) if run_short_title_search else items
    return [{'title': x.get('title'), 'item': x} for x in items if x.get('title') is not None]


def _exec_search_by_id(api_url: str, value: str):
    result = requests.get(f"{api_url}/{value}").json()
    return [] if 'message' in result else result


def _exec_search_by_documentDOI(api_url: str, value: str): return _exec_search_by(api_url, 'doi', value)[0]


def _exec_search_by_scopus(api_url: str, value: str): return _exec_search_by(api_url, 'scopus', value)[0]


SEARCH_BY_KEY = {
    'title': _exec_search_by_title,
    'mendeleyID': _exec_search_by_id,
    'documentDOI': _exec_search_by_documentDOI,
    'scopus': _exec_search_by_scopus
}


def exec_search(client: ApiClient, key: str): return lambda value: SEARCH_BY_KEY[key](client.api_url, value.rstrip())


def get_client(**kwargs): return ApiClient(kwargs.get('mendeley_api_url'))
