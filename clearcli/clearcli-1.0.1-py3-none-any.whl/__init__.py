"""
Copyright 2022
Author: Thomas Mahé <contact@tmahe.dev>

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import inspect
import os
import sys
import textwrap

from .commands import _populate_args_handler, ClearCliCommand


def _get_command_help(descriptor_item):
    if descriptor_item.__doc__:
        return inspect.getdoc(descriptor_item).split('\n').__getitem__(0)
    else:
        return ''
    # return inspect.getdoc(descriptor_item).split('\n')[0][:80]


def _get_command_description(descriptor_item):
    if descriptor_item.__doc__:
        return textwrap.fill(inspect.getdoc(descriptor_item), width=80)
    else:
        return ''


class _ClearCliHelpFormatter(argparse.RawTextHelpFormatter):

    def __init__(self, prog: str):
        super().__init__(prog, width=80, max_help_position=35)

    def _format_action(self, action):
        if type(action) == argparse._SubParsersAction:
            # inject new class variable for subcommand formatting
            subactions = action._get_subactions()
            invocations = [self._format_action_invocation(a) for a in subactions]
            self._subcommand_max_length = max(len(i) for i in invocations)

        if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
            # format subcommand help line
            subcommand = self._format_action_invocation(action)  # type: str
            width = self._subcommand_max_length
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)

            if len(help_text) > 0:
                first_section = "  {} {} ".format(subcommand, "." * (width + 4 - len(subcommand)))
                return "{}{}\n".format(first_section,
                                       textwrap.shorten(help_text, width=80-len(first_section), placeholder="..."),
                                       width=width)
            else:
                return "  {}\n".format(subcommand, width=width)

        elif type(action) == argparse._SubParsersAction:
            # process subcommand help section
            msg = ''
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(_ClearCliHelpFormatter, self)._format_action(action)

    def _format_action_invocation(self, action):
        # print(action)
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            # print(action.required)
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s' % option_string)
                parts[-1] += ' %s' % args_string
            return ', '.join(parts)


class ClearCli:

    def __init__(self, descriptor: dict, prog: str = os.path.basename(sys.argv[0]), description=""):
        self._description = description
        self._descriptor = descriptor
        self._cli = argparse.ArgumentParser(prog=prog, formatter_class=_ClearCliHelpFormatter)
        self._cli.description = description
        self._cli._optionals.title = 'optional arguments'

        if isinstance(descriptor, dict):
            self._from_dict_descriptor(self._descriptor, self._cli)
        else:
            raise TypeError('ClearCli descriptor must be of type <dict>')

    def big_bang(self):
        args = self._cli.parse_args().__dict__

        if len(args.keys()) == 0:
            self._cli.print_help()
            exit(0)

        callable_ = args.get('_CLEARCLI_CALLABLE')(**args)
        callable_(**callable_.filtered_args)
        sys.exit(0)

    def _from_dict_descriptor(self, descriptor, cli: argparse.ArgumentParser, depth=0):
        if isinstance(descriptor, dict):
            title = "sub-" * min(1, depth) + "command"

            if len(descriptor.keys()) > 1:
                title = title + "s"

            if len(descriptor.keys()) > 0:
                sub_parser = cli.add_subparsers(title=title)
                for command_name, sub_descriptor in descriptor.items():
                    try:
                        issubclass(sub_descriptor, ClearCliCommand)
                        parser = sub_parser.add_parser(command_name,
                                                       formatter_class=_ClearCliHelpFormatter,
                                                       help=_get_command_help(sub_descriptor),
                                                       description=_get_command_description(sub_descriptor))
                        parser._optionals.title = 'optional arguments'
                    except TypeError:
                        parser: argparse.ArgumentParser = sub_parser.add_parser(command_name, help='',
                                                                                formatter_class=_ClearCliHelpFormatter)
                        parser._optionals.title = 'optional arguments'
                    self._from_dict_descriptor(sub_descriptor, parser, depth + 1)

        elif callable(descriptor):
            cli.add_argument('--_CLEARCLI_CALLABLE', required=False, default=descriptor, help=argparse.SUPPRESS)
            _populate_args_handler(descriptor, cli)

        else:
            raise TypeError('ClearCli sub-descriptor must be of type <dict>')
