"""Module containing the logic for describe-get-system proof of conception entry-points."""

import sys
import argparse

from dgspoc import version
from dgspoc.config import Data

from dgspoc.utils import Printer
from dgspoc.utils import Text

from dgspoc.constant import ECODE
from dgspoc.constant import FEATURE

from dgspoc.usage import validate_usage

from dgspoc.operation import OptionSelector


class ArgumentParser(argparse.ArgumentParser):

    def parse_args(self, *args, **kwargs):
        try:
            options = super().parse_args(*args, **kwargs)
        except BaseException as ex:    # noqa
            if isinstance(ex, SystemExit):
                if ex.code == ECODE.SUCCESS:
                    sys.exit(ECODE.SUCCESS)
                else:
                    self.print_help()
                    sys.exit(ECODE.BAD)
            else:
                Printer.print_message('\n{}\n', Text(ex))
                self.print_help()
                sys.exit(ECODE.BAD)

        if options.help:
            if not options.command:
                self.print_help()
                sys.exit(ECODE.SUCCESS)
            else:
                if options.command in Cli.commands:
                    command = options.command
                    feature = options.operands[0].lower() if options.operands else ''
                    if feature == FEATURE.SCRIPT:
                        name = '{}_script'.format(command)
                    else:
                        name = '{}_{}'.format(command, feature) if feature else command
                    validate_usage(name, ['usage'])
                else:
                    self.print_help()
                    sys.exit(ECODE.BAD)
        return options


class Cli:
    """describe-get-system proof of concept console CLI application."""
    prog = Data.console_cli_name
    prog_fn = Data.console_cli_fullname
    commands = Data.console_supported_commands

    def __init__(self):
        parser = ArgumentParser(
            prog=self.prog,
            usage='%(prog)s [options] command operands',
            description='{} Proof of Concept'.format(self.prog_fn.title()),
            add_help=False
        )

        parser.add_argument(
            '-h', '--help', action='store_true',
            help='show this help message and exit'
        )

        parser.add_argument(
            '-v', '--version', action='version',
            version='%(prog)s v{}'.format(version)
        )

        parser.add_argument(
            '--author', type=str, default='',
            help="author's name"
        ),

        parser.add_argument(
            '--email', type=str, default='',
            help="author's email"
        ),

        parser.add_argument(
            '--company', type=str, default='',
            help="author's company"
        ),

        parser.add_argument(
            '--save-to', type=str, dest='filename', default='',
            help="saving to file"
        ),

        parser.add_argument(
            '--template-id', type=str, dest='tmplid', default='',
            help="template ID"
        ),

        parser.add_argument(
            '--clear', type=str, dest='template_id', default='',
            help="clear template from template-storage"
        ),

        parser.add_argument(
            '--adaptor', type=str, default='',
            help="connector adaptor"
        ),

        parser.add_argument(
            '--action', type=str, default='',
            help="execution action which uses to test template or verification"
        ),

        parser.add_argument(
            '--replaced', action='store_true',
            help='overwrite template ID/file'
        )

        parser.add_argument(
            '--all', action='store_true',
            help='showing all information'
        )

        parser.add_argument(
            '--dependency', action='store_true',
            help='showing package dependency'
        )

        parser.add_argument(
            '--template-storage', action='store_true',
            help='showing template storage information'
        )

        parser.add_argument(
            '--delete', dest='filepath', type=str, default='',
            help="delete file or folder"
        ),

        parser.add_argument(
            '--detail', action='store_true',
            help='generate detail test execution script or report'
        )

        parser.add_argument(
            '--quiet', action='store_true',
            help='silent success or fail info'
        )

        parser.add_argument(
            'command', nargs='?', type=str, default='',
            help='command must be either build, '
                 'info, report, search, test, version, or usage'
        )
        parser.add_argument(
            'operands', nargs='*', type=str,
            help='operands can be template, unittest, '
                 'pytest, robotframework, script, or data such command-line, '
                 'config-lines, or filename'
        )

        self.kwargs = dict()
        self.parser = parser
        self.options = self.parser.parse_args()

    def validate_command(self):
        """Validate argparse `options.command`.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(ECODE.BAD)`` if
        command is neither build, info, report, search,
        test, version, nor usage otherwise, return True
        """
        self.options.command = self.options.command.lower()

        if self.options.command:
            if self.options.command in self.commands:
                return True
            else:
                self.parser.print_help()
                sys.exit(ECODE.BAD)
        return True

    def run(self):
        """Take CLI arguments, parse it, and process."""
        self.validate_command()

        node = OptionSelector(self.options, print_help=self.parser.print_help)
        node.process()


def execute():
    """Execute template console CLI."""
    app = Cli()
    app.run()
