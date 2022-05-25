from pkgutil import extend_path
from functools import reduce
from hestia_earth.schema import SchemaType, Bibliography

from .log import logger
from .utils import current_time_ms
from .bibliography_apis.utils import (
    ORINGAL_FIELD, has_key, is_enabled, unique_values, biblio_name, update_node_value, update_actor_names
)
from .bibliography_apis.crossref import extend_crossref
from .bibliography_apis.mendeley import get_client as mendeley_client, extend_mendeley
from .bibliography_apis.unpaywall import extend_unpaywall, extend_bibliography_pdf
from .bibliography_apis.wos import extend_wos


__path__ = extend_path(__path__, __name__)

DEFAULT_KEY = 'title'


def is_node_of(node_type: SchemaType): return lambda node: node.get('type') == node_type.value


def source_name_from_biblio(biblio: dict):
    name = biblio.get('name', '')
    return name if name is not None and len(name) > 0 else biblio.get('title', '')


def update_source_from_biblios(source: dict, bibliographies: list, nkey=DEFAULT_KEY):
    def update_key(key: str):
        value = source.get(key)
        biblio = next((x for x in bibliographies if value and value.get(nkey, '') == x.get(ORINGAL_FIELD + nkey)), None)
        if biblio:
            source[key] = {**source[key], **biblio}
            del source[key][ORINGAL_FIELD + nkey]

            name = source_name_from_biblio(biblio)
            if key == 'bibliography':
                update_node_value(source, 'name', name)

    update_key('bibliography')
    return source


def need_update_source(node: dict, nkey=DEFAULT_KEY):
    def has_nkey(key: str): return key in node and nkey in node.get(key)

    return has_nkey('bibliography')


def update_sources(bibliographies: list, key=DEFAULT_KEY):
    def update(source: dict):
        return update_source_from_biblios(source, bibliographies, key) if need_update_source(source, key) else source
    return update


def update_author_privacy(actors: list, dataPrivate: bool, author: dict):
    # try to find the actor in the list of top-level actors
    actor = next((a for a in actors if a.get('id') == author.get('id')), None)
    # if the actor is found, update its privacy from source
    if actor:
        # remove privacy from author as not needed
        author.pop('dataPrivate', None)
        actor['dataPrivate'] = dataPrivate
    elif 'dataPrivate' in author:
        author['dataPrivate'] = dataPrivate
    return author


def update_authors_privacy(actors: list):
    def update(source: dict):
        authors = source.get('bibliography', {}).get('authors', [])
        [
            update_author_privacy(actors, source.get('dataPrivate', False), v) for v in authors if 'id' in v
        ]
        return source
    return update


def map_author_from_nodes(authors: list):
    def map_author(actor: dict):
        actor_name = actor.get('firstName')
        return actor if actor_name else next((x for x in authors if x.get('id', '-1') == actor.get('id', '0')), actor)
    return map_author


def update_biblio(node: dict, authors: list):
    # authors might be in bibliography or in top-level authors
    authors = list(map(map_author_from_nodes(authors), node.get('authors', [])))
    name = biblio_name(authors, node.get('year'))
    return extend_bibliography_pdf({**node, **{'name': name if name else node.get('name')}})


def update_actor(node: dict, *args): return update_actor_names(node)


def update_source(node: dict, *args):
    biblio = node.get('bibliography')
    if biblio:
        name = source_name_from_biblio(biblio)
        update_node_value(node, 'name', name)
    return node


UPDATE_NODE_TYPE = {
    SchemaType.ACTOR.value: update_actor,
    SchemaType.BIBLIOGRAPHY.value: update_biblio,
    SchemaType.SOURCE.value: update_source,
}


def update_node_list(authors, node: list): return list(reduce(lambda p, x: p + [update_node(authors)(x)], node, []))


def update_node_dict(authors: list, node: dict):
    node_type = node.get('type')
    node = UPDATE_NODE_TYPE[node_type](node, authors) if node_type in UPDATE_NODE_TYPE else node
    for key, value in node.items():
        node[key] = update_node(authors)(value)
    return node


def update_node(authors: list):
    def update(node):
        if isinstance(node, list):
            return update_node_list(authors, node)
        elif isinstance(node, dict):
            return update_node_dict(authors, node)
        return node
    return update


def has_node_value(node: dict):
    def has_value(key: str):
        value = node.get(key)
        if isinstance(value, str) or isinstance(value, list):
            return len(value) > 0
        if isinstance(value, int):
            return value > 0
        return value is not None
    return has_value


def _bibliography_missing_required_values(biblio: dict):
    def can_compute_name():
        name = biblio.get('name', None)
        # name can be created from authors, therefore if authors not empty name can be skipped
        return name and len(name) > 0 or len(biblio.get('authors', [])) > 0

    required = Bibliography().required
    values = list(filter(has_node_value(biblio), required))
    values.extend(['name'] if 'name' not in values and can_compute_name() else [])
    return len(values) != len(required)


def get_biblio_value(node: dict, key: str):
    has_missing_values = _bibliography_missing_required_values(node)
    value = node.get(key, '')
    return value if len(value) > 0 and has_missing_values else None


def get_values_from_node(node: dict, key: str):
    value = get_biblio_value(node, key) if is_node_of(SchemaType.BIBLIOGRAPHY)(node) else None
    return list(set(reduce(lambda x, y: x + get_node_values(y, key), node.values(), [] if value is None else [value])))


def get_node_values(nodes, key=DEFAULT_KEY):
    if isinstance(nodes, list):
        return list(set(reduce(lambda p, x: p + get_node_values(x, key), nodes, [])))
    elif isinstance(nodes, dict):
        return get_values_from_node(nodes, key)
    else:
        return []


def _extend_mendeley_by(field: str, actors: list, sources: list, **kwargs):
    # number of titles to search for will decide which client to use
    values = sorted(get_node_values(sources, field))
    (functions, client) = mendeley_client(len(values), **kwargs)
    (authors, bibliographies) = extend_mendeley(functions, client, values, field)
    actors.extend([] if authors is None else authors)
    list(map(update_sources(bibliographies, field), sources)) if len(bibliographies) > 0 else []


def _extend_mendeley(actors: list, sources: list, **kwargs):
    if has_key('mendeley_api_url', **kwargs) or has_key('mendeley_username', **kwargs):
        _extend_mendeley_by('mendeleyID', actors, sources, **kwargs)
        _extend_mendeley_by('documentDOI', actors, sources, **kwargs)
        _extend_mendeley_by('scopus', actors, sources, **kwargs)
        _extend_mendeley_by(DEFAULT_KEY, actors, sources, **kwargs)


def _extend_wos(actors, sources, **kwargs):
    if has_key('wos_api_key', **kwargs) or (has_key('wos_api_user', **kwargs) and has_key('wos_api_pwd', **kwargs)):
        (authors, bibliographies) = extend_wos(sorted(get_node_values(sources)), **kwargs)
        actors.extend([] if authors is None else authors)
        list(map(update_sources(bibliographies), sources)) if len(bibliographies) > 0 else []


def _extend_unpaywall(actors, sources, **kwargs):
    if is_enabled('enable_unpaywall', **kwargs):
        (authors, bibliographies) = extend_unpaywall(sorted(get_node_values(sources)), **kwargs)
        actors.extend([] if authors is None else authors)
        list(map(update_sources(bibliographies), sources)) if len(bibliographies) > 0 else []


def _extend_crossref(actors, sources, **kwargs):
    if is_enabled('enable_crossref', **kwargs):
        (authors, bibliographies) = extend_crossref(sorted(get_node_values(sources)), **kwargs)
        actors.extend([] if authors is None else authors)
        list(map(update_sources(bibliographies), sources)) if len(bibliographies) > 0 else []


def missing_bibliographies(nodes: list):
    key = 'bibliography'
    return [
        [{
            'level': 'error',
            'dataPath': f".{key}",
            'message': 'is missing required bibliographic information'
        }] if is_node_of(SchemaType.SOURCE)(node) and
        _bibliography_missing_required_values(node.get(key, {})) else []
        for node in nodes
    ]


def extend(content, **kwargs):
    now = current_time_ms()
    nodes = content.get('nodes', [])

    actors = []
    sources = list(filter(is_node_of(SchemaType.SOURCE), nodes))

    _extend_mendeley(actors, sources, **kwargs)
    _extend_wos(actors, sources, **kwargs)
    _extend_unpaywall(actors, sources, **kwargs)
    _extend_crossref(actors, sources, **kwargs)

    list(map(update_authors_privacy(actors), sources))

    authors = list(filter(is_node_of(SchemaType.ACTOR), nodes))
    # update all nodes except sources
    nodes = list(map(update_node(authors), nodes))
    # TODO: find a better way, because of children we need to run twice for parents to have correct values
    nodes = list(map(update_node(authors), nodes))

    # return errors if any, otherwise return updated content
    errors = missing_bibliographies(nodes)
    has_errors = next((True for x in errors if len(x) > 0), False)

    results = {'errors': errors} if has_errors else {**content, 'nodes': unique_values(actors) + nodes}
    logger.info('time=%s, unit=ms', current_time_ms() - now)
    return results
