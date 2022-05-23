import os
from inspect import getmembers, isfunction
import json
from hestia_earth.models.utils import term

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(CURRENT_DIR, 'search-results.json')
IGNORE_FUNC = ['get_lookup_value', 'get_table_value']


def _create_search_result(data: tuple):
    search_query = {}
    original_search = term.search

    def new_search(query: dict, *_a, **_b):
        nonlocal search_query
        search_query = query
        return original_search(query, *_a, **_b)
    term.search = new_search
    original_find_node = term.find_node

    def new_find_node(_n, query: dict, *_a, **_b):
        nonlocal search_query
        search_query = query
        return original_find_node(_n, query, *_a, **_b)
    term.find_node = new_find_node
    function_name, func = data
    res = func()
    results = [res['@id']] if isinstance(res, dict) else res
    return {'name': function_name, 'query': search_query, 'results': results}


def create_search_results():
    funcs = list(filter(lambda v: v[0].startswith('get_') and not v[0] in IGNORE_FUNC, getmembers(term, isfunction)))
    return list(map(_create_search_result, funcs))


def _load_results():
    with open(RESULTS_PATH) as f:
        return json.load(f)


def _find_search_result(query: dict):
    search_results = _load_results()
    res = next((n for n in search_results if n['query'] == query), {})
    print('mocking search result', res)
    return list(map(lambda id: {'@type': 'Term', '@id': id}, res.get('results', [])))


def _fake_search(query: dict, *_a, **_b): return _find_search_result(query)


def _fake_find_node(_n, query: dict, *_a, **_b): return _find_search_result(query)


def mock():
    term.search = _fake_search
    term.find_node = _fake_find_node
