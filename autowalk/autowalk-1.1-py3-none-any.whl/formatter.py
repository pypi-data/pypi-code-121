#!/usr/bin/python

import shutil
from utils.color import C

from argparse import (
    # HelpFormatter,
    # RawDescriptionHelpFormatter,
    # ArgumentDefaultsHelpFormatter,
    # MetavarTypeHelpFormatter,
    RawTextHelpFormatter
)

class IndentHelpFormator(RawTextHelpFormatter):
    def __init__(self, *args, **kwargs):

        terminal_witdh = shutil.get_terminal_size().columns

        self.side_width = int ( (terminal_witdh - 35) / 2)

        kwargs["indent_increment"] = 0
        kwargs["width"] = 1000
        kwargs["max_help_position"] = 1000
        super().__init__(*args,**kwargs)

    def _format_usage(self, *args, **kwargs):
        ...

    def add_usage(self, *args, **kwargs):
        ...

    # overwrite to only call _indent
    def start_section(self, heading):
        self._indent()

    # overwrite to None
    def end_section(self):
        # self._dedent()
        ...

    def make_indent(self, indent_num, format_str):
        return '\n'.join( [f'{" "*indent_num}{line}' for line in format_str.split("\n")] )

    def format_help(self):
        try:             
            help = self._root_section.format_help()
            line = help.strip().split("\n")
            head = '\n'.join(line[:2]) + "\n"
            sep_  = f'│{line[2][1:]}│'
            sep = sep_+"\n"
            help = '\n'.join(map(lambda _:f'│ {_} │' if '─' not in _ else _, line[5:])) + "\n"
            tail = f'└{ (len(line[0])- 2) *"─"}┘\n'

            help = C.purple("\n" + head + sep + help + tail + "\n")
            help_list = [line for line in help.split("\n")]
            help = "\n".join(help_list)
            mid_sep = len( sep_ ) // 2

            def make_sep(title):
                title = f" {title} "
                half_title_len = len(title) // 2

                l = mid_sep-half_title_len
                r = mid_sep+half_title_len

                sep_list = list (sep_)
                sep_list[l:r] = C.purple(title)
                return ''.join(sep_list)

            ranger_sep = make_sep("Ranger")
            autojump_sep = make_sep("AutoJump")

            help_list.insert(7, ranger_sep)
            help_list.insert(12, autojump_sep)

            help = "\n".join(help_list)
            help = help.replace("    ","")
            return self.make_indent(self.side_width, help) + "\n"
        except:
            ...