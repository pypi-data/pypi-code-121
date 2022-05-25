import os
import argparse

from ._version import __version__ as __bare_version

# Version
try:
    from ._commit import __commit__, __date__
    __version__ = '%s+%s (%s)' % (__bare_version, __commit__, __date__)
except ImportError:
    __commit__ = ""
    __date__ = ""
    __version__ = __bare_version

# Global variables
pp_output_path = '{trajectory.filename}.pp.{symbol}.{tag}'
pp_trajectory_format = None

# Help formatter
os.environ['COLUMNS'] = "100"

class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog, *args, **kwargs):
        argparse.RawDescriptionHelpFormatter.__init__(self, prog,
                                                      indent_increment=2,
                                                      max_help_position=60,
                                                      width=None)

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' [default: %(default)s]'
        return help

    def __add_whitespace(self, idx, iWSpace, text):
        if idx == 0:
            return text
        return (" " * iWSpace) + text

    def _split_lines(self, text, width):
        import re
        import textwrap as _textwrap
        textRows = text.splitlines()
        for idx, line in enumerate(textRows):
            search = re.search(r'\s*[0-9\-]{0,}\.?\s*', line)
            if line.strip() == "":
                textRows[idx] = " "
            elif search:
                lWSpace = search.end()
                lines = [self.__add_whitespace(i, lWSpace, x) for i, x in enumerate(_textwrap.wrap(line, width))]
                textRows[idx] = lines

        return [item for sublist in textRows for item in sublist]
