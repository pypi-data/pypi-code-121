"""
A wrapper over argparse.ArgumentParser
"""
# noinspection PyProtectedMember
import inspect
from argparse import SUPPRESS, ArgumentParser, ArgumentError, Namespace
from string import Template

import sys as _sys

from polidoro_argument.action import _Action
from polidoro_argument.help_formatter import ArgumentHelpFormatter

_UNRECOGNIZED_ARGS_ATTR = '_unrecognized_args'
METHOD_TO_RUN = '==METHODS_TO_RUN=='

try:
    from gettext import gettext, ngettext
except ImportError:  # pragma: no cover
    def gettext(message):
        return message


    def ngettext(singular, plural, n):
        if n == 1:
            return singular
        else:
            return plural


def _get_action_name(argument):
    if argument is None:
        return None
    elif argument.option_strings:
        return '/'.join(argument.option_strings)
    elif argument.metavar not in (None, SUPPRESS):
        return argument.metavar
    elif argument.dest not in (None, SUPPRESS):
        return argument.dest
    else:
        return None


super_signature = inspect.signature(ArgumentParser.__init__).parameters.keys()


# noinspection PyProtectedMember
class PolidoroArgumentParser(ArgumentParser):
    def __init__(self, *args, version=None, prefix_chars='-', add_help=True, raise_argument_error=False, **kwargs):
        for kw in list(kwargs.keys()):
            if kw not in super_signature:
                kwargs.pop(kw)
        super(PolidoroArgumentParser, self).__init__(*args, formatter_class=ArgumentHelpFormatter, add_help=False,
                                                     prefix_chars=prefix_chars, **kwargs)
        self.add_help = add_help
        default_prefix = '-' if '-' in prefix_chars else prefix_chars[0]
        if self.add_help:
            from polidoro_argument.help_action import HelpAction
            self.add_argument(
                default_prefix + 'h', default_prefix * 2 + 'help',
                action=HelpAction, default=SUPPRESS,
                help=gettext('show this help message and exit'))
        self.subparsers = None
        self.raise_argument_error = raise_argument_error

        if version:
            self.add_argument(
                '-v',
                '--version',
                action='version',
                version='%(prog)s ' + version
            )

    def parse_args(self, args=None, namespace=None):
        # Add arguments and commands to the parser
        namespace, argv = self.parse_known_args(args, namespace)

        if argv:
            msg = gettext('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))

        return namespace

    @staticmethod
    def run_method(argv, **kwargs):
        from polidoro_argument import Command

        # Ignore 'positional' values
        kwargs.pop('positional')
        method_info = kwargs.pop(METHOD_TO_RUN)
        command = Command.get_command(method_info['method'])
        for arg in argv[:]:
            # If there is args left but the method has a var_keyword,
            # parse the keyword args left and set in namespace
            if command.var_keyword and arg.startswith('--') and '=' in arg:
                key, _, value = arg.partition('=')
                kwargs[key[2:]] = value
                argv.remove(arg)

            # If there is args left but the method has a remainder,
            # add the remainders args in method args
            elif command.remainder:
                if arg == '':
                    method_info['args'].append('\'\'')
                elif arg.count(' ') > 0:
                    method_info['args'].append('\'%s\'' % arg)
                else:
                    method_info['args'].append(arg)
                argv.remove(arg)
        # Run Command method
        resp = method_info['method'](*method_info['args'], **kwargs)
        if resp is not None:
            print(resp)

    def add_subparsers(self, **kwargs):
        self.subparsers = super(PolidoroArgumentParser, self).add_subparsers(**kwargs)
        return self.subparsers

    def _add_arguments(self):
        from polidoro_argument.argument import Argument

        for argument in Argument._arguments:
            if not argument.added:
                argument.add_argument(self)
                argument.added = True

    def _add_commands(self):
        from polidoro_argument.command import Command

        for command in Command._commands.values():
            if not command.added:
                command.add_command(self)
                command.added = True

    def _get_nargs_pattern(self, action):
        # Override to enable keyword arguments as K
        if isinstance(action, _Action) and isinstance(action.nargs, str):
            pattern = ''

            if action.positional:
                pattern += '-*'.join('A' * len(action.positional))

            if action.var_positional:
                pattern += '[A-]*'

            if action.var_keyword:
                pattern += '[K-]*'
            elif action.keyword:
                pattern += '[K-]{0,%d}' % len(action.keyword)

            nargs_pattern = Template('(-*${pattern}-*)').substitute(pattern=pattern)

            # if this is an optional action, -- is not allowed
            if nargs_pattern and action.option_strings:
                nargs_pattern = nargs_pattern.replace('-*', '')
                nargs_pattern = nargs_pattern.replace('-', '')

            # return the pattern
            return nargs_pattern
        else:
            return super(PolidoroArgumentParser, self)._get_nargs_pattern(action)

    def _match_argument(self, action, arg_strings_pattern):
        # Override to show a better error message
        try:
            return super(PolidoroArgumentParser, self)._match_argument(action, arg_strings_pattern)
        except ArgumentError:
            if isinstance(action, _Action) and isinstance(action.nargs, str) and '+' in action.nargs:
                raise ArgumentError(action, 'expected at least %s arguments' % action.nargs[:-1])
            raise

    def parse_known_args(self, args=None, namespace=None):  # noqa: C901
        self._add_arguments()
        self._add_commands()
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)

        # default Namespace built from parser defaults
        if namespace is None:
            namespace = Namespace()

        # add any action defaults that aren't present
        for action in self._actions:
            if action.dest is not SUPPRESS:
                if not hasattr(namespace, action.dest):
                    if action.default is not SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # add any parser defaults that aren't present
        for dest in self._defaults:  # pragma: no cover
            if not hasattr(namespace, dest):
                setattr(namespace, dest, self._defaults[dest])

        # parse the arguments and exit if there are any errors
        try:
            namespace, new_args = self._parse_known_args(args, namespace)
            if hasattr(namespace, METHOD_TO_RUN):
                self.run_method(new_args, **vars(namespace))
                delattr(namespace, METHOD_TO_RUN)

            if hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                new_args = getattr(namespace, _UNRECOGNIZED_ARGS_ATTR) + new_args
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)

            return namespace, new_args
        except ArgumentError as err:
            if self.raise_argument_error:
                raise
            self.error(str(err))

    def _parse_known_args(self, arg_strings, namespace):  # noqa: C901
        # Override to parse the K pattern
        # replace arg strings that are file references
        if self.fromfile_prefix_chars is not None:  # pragma: no cover
            arg_strings = self._read_args_from_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        for mutex_group in self._mutually_exclusive_groups:  # pragma: no cover
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

        # find all option indices, and determine the arg_string_pattern
        # which has an 'O' if there is an option at an index,
        # an 'A' if there is an argument, or a '-' if there is a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        for i, arg_string in enumerate(arg_strings_iter):

            # all args after -- are non-options
            if arg_string == '--':  # pragma: no cover
                arg_string_pattern_parts.append('-')
                # noinspection PyUnusedLocal,PyAssignmentToLoopOrWithParameter
                for arg_string in arg_strings_iter:
                    arg_string_pattern_parts.append('A')

            # otherwise, add the arg to the arg strings
            # and note the index if it was an option
            else:
                option_tuple = self._parse_optional(arg_string)
                if option_tuple is None:
                    if '=' in arg_string:
                        pattern = 'K'
                        option_string_indices[i] = None, arg_string, None
                    else:
                        pattern = 'A'
                else:
                    pattern = 'O'
                    option_string_indices[i] = option_tuple
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = ''.join(arg_string_pattern_parts)

        # converts arg strings to the appropriate and then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        # noinspection PyShadowingNames
        def take_action(action, argument_strings, option_string=None):  # pragma: no cover
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error if this argument is not allowed with other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count as "present"
            if argument_values is not action.default:
                seen_non_default_actions.add(action)
                for conflict_action in action_conflicts.get(action, []):
                    if conflict_action in seen_non_default_actions:
                        msg = gettext('not allowed with argument %s')
                        action_name = _get_action_name(conflict_action)
                        raise ArgumentError(action, msg % action_name)

            # take the action if we didn't receive a SUPPRESS value
            # (e.g. from a default)
            if argument_values is not SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        # noinspection PyShadowingNames
        def consume_optional(start_index):  # pragma: no cover

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals in the same arg string
            # (e.g. -xyz is the same as -x -y -z if no args are required)
            match_argument = self._match_argument
            action_tuples = []
            while True:

                # if we found no optional action, skip it
                if action is None:
                    extras.append(arg_strings[start_index])
                    return start_index + 1

                # if there is an explicit argument, try to match the
                # optional's string arguments to only this
                if explicit_arg is not None:
                    arg_count = match_argument(action, 'A')

                    # if the action is a single-dash option and takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    if arg_count == 0 and option_string[1] not in chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] or None
                        optionals_map = self._option_string_actions
                        if option_string in optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        else:
                            msg = gettext('ignored explicit argument %r')
                            raise ArgumentError(action, msg % explicit_arg)

                    # if the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    elif arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        break

                    # error if a double-dash option did not use the
                    # explicit argument
                    else:
                        msg = gettext('ignored explicit argument %r')
                        raise ArgumentError(action, msg % explicit_arg)

                # if there is no explicit argument, try to match the
                # optional's string arguments with the following strings
                # if successful, exit the loop
                else:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    break

            # add the Optional to the list and return the index at which
            # the Optional's string args stopped
            assert action_tuples
            for action, args, option_string in action_tuples:
                take_action(action, args, option_string)
            return stop

        # the list of Positionals left to be parsed; this is modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        # noinspection PyShadowingNames
        def consume_positionals(start_index):  # pragma: no cover
            # match as many Positionals as possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings for each Positional
            # and add the Positional and its args to the list
            for action, arg_count in zip(positionals, arg_counts):
                args = arg_strings[start_index: start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed and return the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts):]
            return start_index

        # consume Positionals and Optionals alternately, until we have
        # passed the last option string
        extras = []
        start_index = 0
        if option_string_indices:
            max_option_string_index = max(option_string_indices)
        else:
            max_option_string_index = -1
        while start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min([
                index
                for index in option_string_indices
                if index >= start_index])
            if start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional if we didn't consume
                # the option string during the positionals parsing
                if positionals_end_index > start_index:
                    start_index = positionals_end_index
                    continue
                else:
                    start_index = positionals_end_index

            # if we consumed all the positionals we could and we're not
            # at the index of an option string, there were extra arguments
            if start_index not in option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional and any arguments for it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # if we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # make sure all required actions were present and also convert
        # action defaults which were not given as arguments
        required_actions = []
        for action in self._actions:
            if action not in seen_actions:
                if action.required:
                    required_actions.append(_get_action_name(action))
                else:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) if the argument was given, but
                    # only if it was defined already in the namespace
                    if (action.default is not None and
                            isinstance(action.default, str) and
                            hasattr(namespace, action.dest) and
                            action.default is getattr(namespace, action.dest)):
                        setattr(namespace, action.dest,
                                self._get_value(action, action.default))

        if required_actions:
            self.error(gettext('the following arguments are required: %s') %
                       ', '.join(required_actions))

        # make sure all required groups had one option present
        for group in self._mutually_exclusive_groups:  # pragma: no cover
            if group.required:
                for action in group._group_actions:
                    if action in seen_non_default_actions:
                        break

                # if no actions were used, report the error
                else:
                    names = [_get_action_name(action)
                             for action in group._group_actions
                             if action.help is not SUPPRESS]
                    msg = gettext('one of the arguments %s is required')
                    self.error(msg % ' '.join(names))

        # return the updated namespace and the extra arguments
        return namespace, extras
