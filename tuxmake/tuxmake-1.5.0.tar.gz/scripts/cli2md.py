from argparse import RawTextHelpFormatter
import os
import sys

__dir__ = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(os.path.join(__dir__, "..")))
from tuxmake.cli import build_parser  # noqa: E402


class MyFormatter(RawTextHelpFormatter):
    def __init__(self, **kwargs):
        kwargs["max_help_position"] = 0
        kwargs["indent_increment"] = 2
        super().__init__(**kwargs)


parser = build_parser(formatter_class=MyFormatter)
print(parser.format_help())
