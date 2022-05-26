#!/usr/bin/env python3

# Copyright © 2022 erzo <erzo@posteo.de>
# This work is free. You can use, copy, modify, and/or distribute it
# under the terms of the BSD Zero Clause License, see LICENSE.

"""
usage: gitd [<options>] [<commit> [<commit>]] [--] [<path>...]

This is a wrapper around `git diff` using the details view from gitl.
It takes the following command line arguments:

{doc_common_options}

All other command line arguments are passed through to git diff.
You can use that for example to:

- show unstaged changes:
      $ gitd
- show staged changes:
      $ gitd --cached
- compare two branches:
      $ gitd master origin/otherbranch

For more information see `git diff --help`.
"""

from . import main
from . import check

main.DetailsView.max_lines_per_file = 2000


def run():
	import sys

	args = sys.argv[1:]
	kw = main.parse_common_args(args, doc=__doc__)

	diff_args = args

	a = main.App(diff=diff_args, **kw)
	while a.continue_running:
		a.run()
		a.run_external_if_requested()


if __name__ == '__main__':
	run()
