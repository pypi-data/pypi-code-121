#!/usr/bin/env python3
"""
ATAC peaks file related tools

author: jy, nkmtmsys
"""

import ageas.tool as tool

class Reader(tool.Reader_Template):
    """
    Load in ATAC peaks from files
    """

    def __init__(self, arg):
        super(Reader, self).__init__()
        self.arg = arg
