"""
description: this module provides the class ArgumentParser.
"""

import argparse
import sys

from _pistar.utilities.exceptions import UsageError


class PistarHelpFormatter(argparse.HelpFormatter):
    def add_arguments(self, actions):
        help_action = None
        for action in actions:
            if action.option_strings == ["-h", "--help"]:
                help_action = action
                continue
            self.add_argument(action)
        if help_action:
            help_action.help = "Show help message"
            self.add_argument(help_action)


class ArgumentParser(argparse.ArgumentParser):
    """
    this class can show the types and default values of parameters,
    automatically.
    """

    def __init__(self, *args, **kwargs):
        """
        this is the constructor of the class ArgumentParser.

        parameters:
            it will pass all import arguments into
            the function __init__ of class argparse.ArgumentParser.
        """

        super().__init__(*args, formatter_class=PistarHelpFormatter, **kwargs)

    def error(self, message):
        """
        overwrite the argparse error message.
        """
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.stderr.flush()
        raise UsageError


class ArgumentTypeError(argparse.ArgumentTypeError):
    """Error creating or using custom parameters.
        The string value of this exception is the message, augmented with
        information about the argument that caused it.
    """

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return '%(message)s' % dict(message=self.message)
