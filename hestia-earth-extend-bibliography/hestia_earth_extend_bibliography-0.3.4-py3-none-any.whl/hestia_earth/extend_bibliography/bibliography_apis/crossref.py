import json
import traceback
from concurrent.futures import ThreadPoolExecutor
import habanero
from hestia_earth.schema import Bibliography

from hestia_earth.extend_bibliography.log import logger
from hestia_earth.extend_bibliography.utils import current_time_ms
from .utils import (
    ORINGAL_FIELD, MAXIMUM_DISTANCE, find_closest_result, extend_bibliography, remove_empty_values,
    capitalize, update_actor_names
)


def author_to_actor(author):
    return update_actor_names({
        'firstName': capitalize(author['given']),
        'lastName': capitalize(author['family'])
    })


def clean_abstract(abstract: str):
    return abstract.replace('<jats:p>', '').replace('</jats:p>', '').strip() if abstract else None


def item_to_bibliography(item):
    outlet = item.get('short-container-title')
    return {
        'title': capitalize(item.get('title')[0]),
        'year': item.get('issued').get('date-parts')[0][0],
        'outlet': capitalize(outlet[0]) if outlet and len(outlet) > 0 else None,
        'abstract': clean_abstract(item.get('abstract')),
        'documentDOI': item.get('DOI')
    }


def create_biblio(title: str, item: dict):
    biblio = Bibliography()
    # save title here since closest item might differ
    biblio.fields[ORINGAL_FIELD + 'title'] = title
    biblio.fields['title'] = title
    authors = list(map(author_to_actor, item['author'] if item else []))
    bibliography = item_to_bibliography(item) if item else {}
    (extended_biblio, actors) = extend_bibliography(authors, bibliography['year']) if item else ({}, [])
    return (
        {**biblio.to_dict(), **bibliography, **extended_biblio},
        actors
    ) if item else (biblio.to_dict(), [])


def exec_search(cr):
    def search(title: str):
        items = cr.works(query=title)['message']['items']
        return list(map(lambda x: {'title': x['title'][0], 'item': x}, items))
    return search


def search(cr, title):
    [item, distance] = find_closest_result(title, exec_search(cr))
    return create_biblio(title, item if distance <= MAXIMUM_DISTANCE else None)


def extend_title(cr, bibliographies, actors):
    def extend(title: str):
        now = current_time_ms()
        (biblio, authors) = search(cr, title)
        logger.debug('find in %sms: %s', current_time_ms() - now, title)
        logger.debug('found bibliography: %s', json.dumps(biblio, indent=2))
        bibliographies.extend([] if biblio is None else [biblio])
        actors.extend([] if authors is None else authors)
    return extend


def extend_crossref(titles, **kwargs):
    try:
        cr = habanero.Crossref()

        bibliographies = []
        actors = []

        extender = extend_title(cr, bibliographies, actors)
        with ThreadPoolExecutor() as executor:
            executor.map(extender, titles)

        return (remove_empty_values(actors), remove_empty_values(bibliographies))
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return ([], [])
