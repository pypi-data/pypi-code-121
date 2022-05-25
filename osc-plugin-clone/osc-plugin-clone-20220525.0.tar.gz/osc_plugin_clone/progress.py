# progress.py
#
# Copyright 2017 Collabora Limited
# Copyright 2017 Andrej Shadura <andrew.shadura@collabora.co.uk>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# SPDX-License-Identifier: GPL-2.0+

import contextlib
import sys

stdout = sys.stdout

last_desc = None

try:
    from tqdm import tqdm

    tqdm.monitor_interval = 0

    def progress(iterable, desc=None, unit='package'):
        global last_desc
        last_desc = desc
        return tqdm(iterable, desc=desc, unit=unit, file=stdout, dynamic_ncols=True, leave=(len(iterable) > 0))

    def find_bar():
        bar = None
        for inst in getattr(tqdm, '_instances', []):
            bar = inst
            break
        return bar

    def print_status(s):
        """Print the status in the progressbar, if there's one. Print it normally, if there isn't.

        The status is appended to the last progressbar's description text.
        """
        bar = find_bar()
        if bar:
            bar.set_description("%s (%s)" % (last_desc, s))
            bar.refresh()
        else:
            print(s)

    def print_progress(fmt, s):
        """
        Print the progress status, such as the package name currently being processed

        fmt: format string (ignored when the progressbar is in use)
        s: item name
        """
        print_status(s)

    class DummyTqdmFile:
        """Dummy file-like that will write to tqdm"""

        file = None

        def __init__(self, file):
            self.file = file

        def write(self, x):
            pass
            # To print messages, uncomment this:
            #
            # # Avoid print() second call (useless \n)
            # if len(x.rstrip()) > 0:
            #     tqdm.write(x, file=self.file)

    @contextlib.contextmanager
    def wrap_output():
        save_stdout = sys.stdout
        try:
            sys.stdout = DummyTqdmFile(sys.stdout)
            yield save_stdout
        # Always restore sys.stdout if necessary
        finally:
            sys.stdout = save_stdout

except ImportError:
    def progress(iterable, desc=None, unit=None):
        print(desc)
        return iterable

    def print_status(s):
        """Print a status update"""
        print(s)

    def print_progress(f, s):
        """
        Print the progress status, such as the package name currently being processed

        fmt: format string
        s: item name
        """
        print(f % s)

    @contextlib.contextmanager
    def wrap_output():
        yield sys.stdout
