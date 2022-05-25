import json
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor
from random import randrange
from hestia_earth.schema import Bibliography

from hestia_earth.extend_bibliography.log import logger
from hestia_earth.extend_bibliography.utils import current_time_ms
from .utils import (
    ORINGAL_FIELD, MAXIMUM_DISTANCE, find_closest_result, extend_bibliography, remove_empty_values,
    capitalize, update_actor_names, update_node_value
)


BASE_URL = 'https://api.unpaywall.org/v2'


def _get_email():
    # circonvent unpaywall restriction by email
    return f"community{randrange(100)}@hestia.earth"


def _author_to_actor(author):
    return update_actor_names({
        'firstName': capitalize(author.get('given')),
        'lastName': capitalize(author.get('family'))
    })


def _item_to_bibliography(item: dict):
    oa = item.get('best_oa_location', None)
    return {
        'title': capitalize(item.get('title')),
        'year': item.get('year'),
        'outlet': capitalize(item.get('journal_name')),
        'documentDOI': item.get('doi'),
        'articlePdf': oa.get('url_for_pdf') if oa else None
    }


def create_biblio(title: str, item: dict):
    biblio = Bibliography()
    # save title here since closest item might differ
    biblio.fields[ORINGAL_FIELD + 'title'] = title
    biblio.fields['title'] = title
    authors = list(map(_author_to_actor, item.get('z_authors', []) if item else []))
    bibliography = _item_to_bibliography(item) if item else {}
    (extended_biblio, actors) = extend_bibliography(authors, bibliography.get('year')) if item else ({}, [])
    return (
        {**biblio.to_dict(), **bibliography, **extended_biblio},
        actors
    ) if item else (biblio.to_dict(), [])


def exec_search(title: str):
    url = f"{BASE_URL}/search?query={title.rstrip()}&email={_get_email()}"
    items = requests.get(url).json().get('results', [])
    return list(map(lambda x: {'title': x.get('response').get('title'), 'item': x.get('response')}, items))


def search(title):
    [item, distance] = find_closest_result(title, exec_search)
    return create_biblio(title, item if distance <= MAXIMUM_DISTANCE else None)


def extend_title(bibliographies, actors):
    def extend(title: str):
        now = current_time_ms()
        (biblio, authors) = search(title)
        logger.debug('find in %sms: %s', current_time_ms() - now, title)
        logger.debug('found bibliography: %s', json.dumps(biblio, indent=2))
        bibliographies.extend([] if biblio is None else [biblio])
        actors.extend([] if authors is None else authors)
    return extend


def _search_by_documentDOI(value: str):
    try:
        return _item_to_bibliography(requests.get(f"{BASE_URL}/{value.rstrip()}?email={_get_email()}").json())
    except Exception:
        return {}


def extend_bibliography_pdf(bibliography: dict) -> dict:
    key = 'articlePdf'
    doi = bibliography.get('doi')
    run_extend = doi is not None and bibliography.get(key, None) is None
    item = _search_by_documentDOI(doi) if run_extend else {}
    return update_node_value(bibliography, key, item.get(key))


def extend_unpaywall(titles, **kwargs):
    try:
        bibliographies = []
        actors = []

        extender = extend_title(bibliographies, actors)
        with ThreadPoolExecutor() as executor:
            executor.map(extender, titles)

        return (remove_empty_values(actors), remove_empty_values(bibliographies))
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return ([], [])
