#!/usr/bin/env python3

# Copyright © 2022 erzo <erzo@posteo.de>
# This work is free. You can use, copy, modify, and/or distribute it
# under the terms of the BSD Zero Clause License, see LICENSE.

"""
usage: gits [<options>] [<commit>]

This is a wrapper around `git show` using the details view from gitl.
It takes the following command line arguments:

{doc_common_options}

All other command line arguments are passed through to git show.
You can use that for example in your vimrc:

    map <c-c> :!gits <C-r><C-w><cr><cr>

With that line pressing control + c opens the commit whose hash id is under the cursor.
This is useful while writing a commit message if you want to verify that you have copied
the correct hash or when doing an interactive rebase.

For more information see `git show --help`.
"""

from . import main
from . import check

main.DetailsView.max_lines_per_file = 2000


def run():
	import sys

	args = sys.argv[1:]
	kw = main.parse_common_args(args, doc=__doc__)

	if not args:
		diff_args = []
		hash_id = "HEAD"
	else:
		diff_args = args[:-1]
		hash_id = args[-1]

	a = main.App(show=hash_id, diff_args=diff_args, **kw)

	while a.continue_running:
		a.run()
		a.run_external_if_requested()


if __name__ == '__main__':
	run()
