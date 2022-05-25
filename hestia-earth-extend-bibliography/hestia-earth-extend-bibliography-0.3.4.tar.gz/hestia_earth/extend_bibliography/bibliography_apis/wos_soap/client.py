from wos import WosClient
import wos.utils
import xmltodict
import re
from hestia_earth.schema import Bibliography

from hestia_earth.extend_bibliography.bibliography_apis.utils import ORINGAL_FIELD, extend_bibliography, int_value, \
    capitalize, update_actor_names


def _item_title(item: dict): return capitalize(item.get('title', {'value': None}).get('value'))


def _author_to_actor(author: str):
    [last, first] = author.split(', ')
    return update_actor_names({
        'firstName': capitalize(first),
        'lastName': capitalize(last)
    })


def _item_to_bibliography(item: dict):
    values = item.get('source', []) + item.get('other', [])

    def label_value(label: str, default=None):
        return next((x.get('value') for x in values if x.get('label') == label), default)

    return {
        'title': _item_title(item),
        'year': int_value(label_value('Published.BiblioYear', 0)),
        'documentDOI': label_value('Identifier.Doi'),
        'volume': int_value(label_value('Volume')),
        'issue': label_value('Issue', '0').split('-')[0],
        'pages': label_value('Pages'),
        'outlet': capitalize(label_value('SourceTitle'))
    }


def create_biblio(title: str, item: dict):
    biblio = Bibliography()
    # save title here since closest item might differ
    biblio.fields[ORINGAL_FIELD + 'title'] = title
    biblio.fields['title'] = title
    authors = list(map(_author_to_actor, item.get('authors', {}).get('value', []) if item else []))
    bibliography = _item_to_bibliography(item) if item else {}
    (extended_biblio, actors) = extend_bibliography(authors, bibliography.get('year')) if item else ({}, [])
    return (
        {**biblio.to_dict(), **bibliography, **extended_biblio},
        actors
    ) if item else (biblio.to_dict(), [])


def search_query(title: str): return f"TI=({re.sub(r'[(:]{1}.*', '', title)[:50].rstrip()})"


def exec_search(client: WosClient):
    def search(title: str):
        try:
            result = xmltodict.parse(wos.utils.query(client, search_query(title)))['return']
            items = result['records'] if 'records' in result else []
            items = [items] if isinstance(items, dict) else items
            return list(map(lambda x: {'title': _item_title(x), 'item': x}, items))
        except Exception:
            return []
    return search


def get_client(**kwargs):
    api_user = kwargs.get('wos_api_user')
    api_password = kwargs.get('wos_api_pwd')
    return WosClient(user=api_user, password=api_password, lite=True)
