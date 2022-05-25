import re
from random import randint
import Levenshtein
from hestia_earth.schema import Actor


MAXIMUM_DISTANCE = 10
ORINGAL_FIELD = 'original'


def int_value(x): return int(x) if x and int(x) > 0 else None


def has_key(key: str, **kwargs): return kwargs.get(key, None) is not None


def is_enabled(key: str, **kwargs): return kwargs.get(key, False) is True


def join_list_string(values): return ' '.join(list(filter(non_empty_value, values))).strip()


def non_empty_value(value): return value != '' and value is not None and value != []


def remove_empty_values(values): return list(map(lambda x: {k: v for k, v in x.items() if non_empty_value(v)}, values))


def unique_values(values: list, key='id'): return list({v[key]: v for v in values}.values())


def update_node_value(node: dict, key: str, value: str):
    if value and len(value) > 0:
        node[key] = value
    return node


def actor_id(author):
    return author.get('scopusID') if 'scopusID' in author and author.get('scopusID') \
        else f"H-{str(randint(10**9, 10**10-1))}"


def actor_name(actor: dict):
    first_name = actor.get('firstName')
    last_name = actor.get('lastName')
    return join_list_string([
        first_name[0] if first_name else None, last_name, actor.get('primaryInstitution')
    ]) if last_name else ''


def update_actor_names(actor: dict):
    # last name pattern
    pattern = re.compile(r'^([A-Z]{1}[\.]\s?)*$')
    first_name = actor.get('firstName')
    last_name = actor.get('lastName')
    inverted = first_name is not None and last_name is not None and \
        pattern.match(last_name) and not pattern.match(first_name)
    update_node_value(actor, 'firstName', last_name if inverted else first_name)
    update_node_value(actor, 'lastName', first_name if inverted else last_name)
    update_node_value(actor, 'name', actor_name(actor))
    return actor


def capitalize(title: str):
    return title.title() if title is not None and title.isupper() and len(title) > 4 else title


def _first_author(authors: list): return authors[0] if authors and len(authors) > 0 else None


def _author_suffix(authors: list):
    if len(authors) == 2 and authors[1].get('lastName'):
        return f"& {authors[1].get('lastName')}"
    elif len(authors) >= 3:
        return 'et al'
    return ''


def _parse_author_names(authors: list):
    def parse_author(author: dict):
        pattern = re.compile(r'^([A-Z]{1})\s(.*)$')
        match = pattern.match(author.get('name', ''))
        (first, last) = match.groups() if match else (None, None)
        return {
            'name': author.get('name'),
            'firstName': author.get('firstName', first),
            'lastName': author.get('lastName', last)
        }

    return list(map(parse_author, authors))


def biblio_name(authors: list, year=None):
    updated_authors = _parse_author_names(authors)
    first_author = _first_author(updated_authors)
    if first_author:
        author_name = join_list_string([
            first_author.get('lastName'),
            _author_suffix(updated_authors)
        ]) if first_author.get('lastName') else first_author.get('name')

        return join_list_string([author_name, f"({str(year)})" if year else None]) if author_name else None
    return ''


def create_actors(actors):
    def create_actor(author):
        actor = Actor()
        actor.fields = {**actor.fields, **author}
        actor.fields['id'] = actor_id(author)
        actors.append(update_actor_names(actor.to_dict()))

        author = Actor()
        author.fields['id'] = actor.fields.get('id')
        return remove_empty_values([author.to_dict()])[0]
    return create_actor


def extend_bibliography(authors=[], year=None):
    biblio = {}
    actors = []
    biblio['authors'] = list(map(create_actors(actors), authors))
    biblio['name'] = biblio_name(authors, year)
    return (biblio, actors)


def get_distance(str1: str, str2: str):
    return Levenshtein.distance(str1.rstrip().lower(), str2.rstrip().lower())


def find_closest_result(title: str, fetch_items):
    items = fetch_items(title)
    distances = list(map(lambda i: get_distance(title, i['title']), items))
    distance = min(distances) if len(distances) else 1000
    closest_title = items[distances.index(distance)]['item'] if len(distances) else None
    return [closest_title, distance]
