import re

from hestia_earth.extend_bibliography.bibliography_apis.utils import (
    actor_id, actor_name, update_actor_names, capitalize, biblio_name, _parse_author_names
)


class FakeAuthor():
    def __init__(self):
        self.scopus_author_id = ''


def test_biblio_name():
    authors = [{
        'lastName': 'lastName'
    }]
    year = 2010
    assert biblio_name(authors, year) == 'lastName (2010)'

    authors = [{
        'name': 'name'
    }]
    year = 2010
    assert biblio_name(authors, year) == 'name (2010)'


def test_actor_id():
    actor = {'scopusID': 'scopus_author_id'}
    assert actor_id(actor) == actor.get('scopusID')

    # no scopus, generate random value
    actor = {'scopusID': None}
    assert re.match(r'H-\d{10}$', actor_id(actor)) is not None


def test_actor_name():
    actor = {'lastName': 'Last Name'}
    assert actor_name(actor) == 'Last Name'
    actor['firstName'] = 'First'
    assert actor_name(actor) == 'F Last Name'
    # override name
    actor['name'] = 'Full Name'
    assert actor_name(actor) == 'F Last Name'


def test_update_actor_names():
    first_name = 'L. N. R.'
    last_name = 'Last Name'
    actor = {'firstName': first_name, 'lastName': last_name}
    assert update_actor_names(actor) == {
        'firstName': first_name, 'lastName': last_name, 'name': 'L Last Name'
    }
    # invert first/last, should sort them out
    actor = {'firstName': last_name, 'lastName': first_name}
    assert update_actor_names(actor) == {
        'firstName': first_name, 'lastName': last_name, 'name': 'L Last Name'
    }


def test_capitalize():
    assert not capitalize(None)
    assert capitalize('A random title') == 'A random title'
    assert capitalize('A RANDOM TITLE') == 'A Random Title'


def test_parse_author_names():
    authors = [{
        'name': 'W Wang'
    }, {
        'name': 'J Poore',
        'firstName': 'Joseph',
        'lastName': 'Poore'
    }]
    assert _parse_author_names(authors) == [{
        'name': 'W Wang',
        'firstName': 'W',
        'lastName': 'Wang'
    }, {
        'name': 'J Poore',
        'firstName': 'Joseph',
        'lastName': 'Poore'
    }]
