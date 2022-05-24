import re

import pytest

from polidoro_argument import Command, Argument, PolidoroArgumentParser

parser = None


@pytest.fixture(scope="module", autouse=True)
def setup():
    global parser
    parser = PolidoroArgumentParser(prog='testManual', version='0')


class TestCLI(object):
    help = 'cli help'
    description = 'description'

    @staticmethod
    @Command(
        help='inner help',
        aliases=['ic'],
        arguments_help={'arg1': 'Arg1 help', 'kwarg1': 'Kwarg1 Help'},
        arguments_aliases={'kwarg1': ['kw', 'k'], 'arg1': 'a'}
    )
    def inner_command(arg1, arg2, kwarg1=None):  # pragma: no cover
        print('command!')

    @staticmethod
    @Argument
    def argument():  # pragma: no cover
        print('argument!')

    @staticmethod
    @Command
    def command_with_remainders(*_remainder):
        print(f'Remainders: {_remainder}')


def test_description(capsys):
    with pytest.raises(SystemExit) as exit_info:
        # noinspection PyUnresolvedReferences
        parser.parse_args('testcli --help'.split())
    assert exit_info.value.code == 0

    output = capsys.readouterr().out
    assert re.search(r'usage: testManual testcli.*\n\ndescription\n\n', output, flags=re.DOTALL), output


def test_help_command_alias(capsys):
    with pytest.raises(SystemExit) as exit_info:
        # noinspection PyUnresolvedReferences
        parser.parse_args('testcli --help'.split())
    assert exit_info.value.code == 0

    output = capsys.readouterr().out
    assert 'inner_command (ic)' in output


def test_help_command_help_alias(capsys):
    with pytest.raises(SystemExit) as exit_info:
        # noinspection PyUnresolvedReferences
        parser.parse_args('testcli ic --help'.split())
    assert exit_info.value.code == 0

    output = capsys.readouterr().out
    assert re.search(r'--kwarg1.*--kw', output, flags=re.DOTALL), output


def test_remainders(capsys):
    import sys
    remainders = ['re',  'ma in de',  'r s', '']
    sys.argv = ['discard', 'testcli', 'command_with_remainders'] + remainders

    # noinspection PyUnresolvedReferences
    parser.parse_args()
    output = capsys.readouterr().out
    assert f'Remainders: (\'re\', "\'ma in de\'", "\'r s\'", "\'\'")\n' == output
