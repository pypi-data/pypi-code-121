from ..DIR.DIR import DIR
from .Extensions import Extensions
from os import listdir, remove
from json import load


def test_json_file_creation():
    remove_json_file()

    Extensions('./arrange.json', 'abc', ['abc', 'cba', 'bac'])

    assert 'arrange.json' in listdir('.')
    remove_json_file()


def test_extension_addition():
    remove_json_file()

    ext = Extensions('./arrange.json', 'abc', ['abc', 'cba'])
    ext.add_extensions(DIR('abc'), {'bbc', 'ccb', 'bca'})
    ext.write_json_file()

    with open('arrange.json') as arrange:
        extensions = load(arrange)
        extensions = {dir_: set(ext) for dir_, ext in extensions.items()}

        assert extensions == {DIR('abc').dir_path: {'abc', 'cba', 'bbc', 'ccb', 'bca'}}
    remove_json_file()


def test_extension_removal():
    remove_json_file()

    ext = Extensions('./arrange.json', 'abc', ['abc', 'cba'])
    ext.remove_extensions(DIR('abc'), {'cba'})
    ext.write_json_file()

    with open('arrange.json') as arrange:
        extensions = load(arrange)
        assert extensions == {DIR('abc').dir_path: ['abc']}
    remove_json_file()


def test_same_ext_in_dir():
    Extensions('./arrange.json', 'abc', ['abc', 'abc', 'abc'])

    with open('arrange.json') as arrange:
        extensions = load(arrange)
        assert extensions == {DIR('abc').dir_path: ['abc']}
    remove_json_file()


def test_dir_removal():
    ext = Extensions('./arrange.json', 'abc', ['abc', 'asdf'])
    ext.remove_directory(DIR('abc'))
    ext.write_json_file()

    with open('arrange.json') as arrange:
        json_file = load(arrange)
        assert json_file == {}
    remove_json_file()


def test_extension_duplication_in_child_dirs():
    remove_json_file()
    ext = Extensions('./arrange.json', 'abc', {'alpha', 'beta', 'gama'})
    ext.add_extensions(DIR('abc/b'), {'beta'})
    ext.write_json_file()

    with open('./arrange.json') as json_file:
        x = load(json_file)
        assert x[DIR('abc/b').dir_path] == ['beta'] \
               and \
               set(x[DIR('abc').dir_path]) == {'alpha', 'gama'}
    remove_json_file()


def test_removing_the_only_extension():
    """testing the removal of the only extension in an extension list."""
    remove_json_file()
    ext = Extensions('./arrange.json', 'abc', {'abc'})
    ext.remove_extensions(DIR('abc'), {'abc'})
    ext.write_json_file()

    with open('./arrange.json') as json_file:
        file = load(json_file)
        assert file == {}
    remove_json_file()


def test_extension_duplication_in_separate_dirs():
    """testing the addition of an already-existing extension in a separate directory
    ie: not a child to the directory that already has the extension"""
    remove_json_file()
    abc = DIR('abc').dir_path
    _def = DIR('def')
    ext = Extensions('./arrange.json', 'abc', {'a', 'b'})
    ext.add_extensions(_def, {'a'})
    ext.write_json_file()

    with open('./arrange.json') as json_file:
        file = load(json_file)
        assert file[abc] == ['b'] and 'a' not in file[abc]
        assert file[_def.dir_path] == ['a']

def remove_json_file():
    if 'arrange.json' in listdir('.'):
        remove('arrange.json')
