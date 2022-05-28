# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentParser, Action

import inspect
import sys

from .application import Application, OperationError
from .baseobject import BaseObject

##############################################################################


class CommandApplication (Application):

    subcommands = []

    def __init__(self, **kw):
        kw['argparse_kwargs'] = {'add_help': False}
        super(CommandApplication, self).__init__(**kw)
        self.command = None

    def build_cmdline_parser(self):
        parser = super(CommandApplication, self).build_cmdline_parser()
        parser.add_argument('-h', '--help',
                            dest='deferred_help',
                            action='store_true',
                            help='Show help message and exit.')
        return parser

    def setup(self, subcommand_arguments):
        self.setup_help(subcommand_arguments)
        self.setup_subcommand(subcommand_arguments)

    def setup_help(self, arguments):
        if self.cmdline_arguments.deferred_help and arguments:
            self.cmdline_arguments.deferred_help = False
            arguments.insert(0, "help")

        self.subcommands.append(HelpCommand)

        if self.cmdline_arguments.deferred_help:
            action = HelpAction(None, None, default=self)
            action(self.cmdline_parser, self.cmdline_arguments, None, None)

    def setup_subcommand(self, arguments):
        if not arguments:
            action = HelpAction(None, None, default=self)
            action(self.cmdline_parser, self.cmdline_arguments, None, None)

        command = arguments[0]
        command_args = arguments[1:]

        self.command = self._find_subcommand(command)

        cmd_parser = self.command.get_cmdline_parser()
        self.arguments = cmd_parser.parse_args(command_args)

    def _find_subcommand(self, command):
        for cmdclass in self.subcommands:
            if cmdclass.name is None:
                continue
            if command == cmdclass.name:
                return cmdclass(self)
        else:
            raise OperationError('unknown command: %s' % command)

    def run(self):
        self.command.run(self.arguments)

##############################################################################


class HelpAction (Action):

    def __call__(self, parser, namespace, values, option_string=None):
        app = self.default
        parser.print_help(sys.stdout)
        sys.stdout.write('\nCommands:\n')

        for cmdclass in app.subcommands:
            if cmdclass.name is None:
                continue

            cmd = cmdclass(app)
            cmdname = cmd.name
            cmddesc = cmd.get_description().split('\n')[0]

            sys.stdout.write('  %-19s  %s\n' % (cmdname, cmddesc))

        sys.exit(0)

##############################################################################


class Subcommand (BaseObject):

    name = None
    description = None

    def __init__(self, app, **kw):
        super(Subcommand, self).__init__(**kw)
        self.app = app
        self.setup()

    def setup(self):
        self.config = self.app.config

    def get_description(self):
        if self.description is None:
            return inspect.getdoc(self.__class__) or ''
        return self.description

    def get_cmdline_parser(self):
        parser = ArgumentParser(description=self.get_description(),
                                prog='%s %s' % (self.app.app_name, self.name))
        return parser

    def run(self, arguments):
        self.setup_command(arguments)
        self.run_command(arguments)

    def setup_command(self, arguments):
        pass

    def run_command(self, arguments):
        pass

##############################################################################


class HelpCommand (Subcommand):
    """
    Print detailed help for another command
    """

    name = 'help'

    def get_cmdline_parser(self):
        parser = super(HelpCommand, self).get_cmdline_parser()
        parser.add_argument('cmd',
                            help='name of the command')
        return parser

    def run_command(self, arguments):
        if arguments.cmd:
            thecmd = self.app._find_subcommand(arguments.cmd)
            parser = thecmd.get_cmdline_parser()
            parser.print_help(sys.stdout)
        else:
            action = HelpAction(None, None, default=self.app)
            action(self.cmdline_parser, self.cmdline_arguments, None, None)

##############################################################################
# THE END
