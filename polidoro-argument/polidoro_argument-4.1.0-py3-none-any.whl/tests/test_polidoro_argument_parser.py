from argparse import SUPPRESS

from polidoro_argument.polidoro_argument_parser import _get_action_name


class GetActionNameTest:
    def __init__(self, option_strings=None, metavar=None, dest=None):
        self.option_strings = option_strings
        self.metavar = metavar
        self.dest = dest


def test_get_action_name():
    assert _get_action_name(None) is None

    argument = GetActionNameTest(option_strings=['os1', 'os2'])
    assert _get_action_name(argument) == 'os1/os2'

    argument = GetActionNameTest(metavar='metavar')
    assert _get_action_name(argument) == 'metavar'

    argument = GetActionNameTest(dest='dest')
    assert _get_action_name(argument) == 'dest'

    argument = GetActionNameTest(dest='dest', metavar=SUPPRESS)
    assert _get_action_name(argument) == 'dest'

    argument = GetActionNameTest()
    assert _get_action_name(argument) is None

    argument = GetActionNameTest(dest=SUPPRESS, metavar=SUPPRESS)
    assert _get_action_name(argument) is None

    argument = GetActionNameTest(dest=SUPPRESS)
    assert _get_action_name(argument) is None

    argument = GetActionNameTest(metavar=SUPPRESS)
    assert _get_action_name(argument) is None
