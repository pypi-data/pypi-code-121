#!/usr/bin/env python3

"""
Handling of data outside the database and for preparation for import into the
database.

--------

Copyright (C) 2011, 2012 Ian Donaldson <ian.donaldson@biotek.uio.no>
Original author: Paul Boddie <paul.boddie@biotek.uio.no>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import codecs
import os
import time


class Reader:

    "Provide properly unbuffered stream reading."

    def __init__(self, stream, encoding="utf-8"):
        self.stream = stream
        self.encoding = encoding

    def __iter__(self):
        return self

    def __next__(self):
        s = self.stream.readline()
        if not s:
            raise StopIteration
        return self._decode(s)

    def read(self, size=-1):
        return self._decode(self.stream.read(size))

    def close(self):
        self.stream.close()

    def _decode(self, s):
        return str(s, encoding=self.encoding)


def rewrite(stream, encoding="utf-8"):

    "Re-open the given 'stream' for writing, applying the specified 'encoding'."

    writer = codecs.getwriter(encoding)
    return writer(stream)


def reread(stream, encoding="utf-8"):

    "Re-open the given 'stream' for reading, applying the specified 'encoding'."

    return Reader(stream, encoding)


# Basic value handling.


def bulkstr(x):

    "Perform PostgreSQL import file encoding on the string value 'x'."

    if x is None:
        return r"\N"
    else:
        x = str(x)
        if "\\" in x:
            return x.replace(
                "\\", r"\\"
            )  # replace single backslash with double backslash
        else:
            return x


def tab_to_space(x):
    if x is None:
        return None
    else:
        return x.replace("\t", " ")


# Utility classes.


class RawImportFile:

    """
    A tab-separated import file writer which does not observe the PostgreSQL
    encoding conventions.
    """

    def __init__(self, filename_or_stream, encoding="utf-8", delimiter="\t"):
        self.delimiter = delimiter
        if hasattr(filename_or_stream, "write"):
            self.file = filename_or_stream
        else:
            self.file = codecs.open(filename_or_stream, "w+", encoding=encoding)
        self.last_write = ""

    def append(self, values):
        # Convert None to the empty string, since there is no sensible
        # distinction between the two values in this format.
        self.last_write = (
            self.delimiter.join(
                [(value is not None and str(value) or u"") for value in values]
            )
            + "\n"
        )
        self.file.write(self.last_write)

    def remove_last(self):
        self.file.seek(-len(self.last_write), 1)
        self.last_write = ""

    def close(self):
        self.file.close()

    def time_now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


class RawImportFileReader:

    """
    A tab-separated import file reader which does not observe the PostgreSQL
    encoding conventions.
    """

    def __init__(self, filename_or_stream, encoding="utf-8", delimiter="\t"):
        self.delimiter = delimiter
        if hasattr(filename_or_stream, "read"):
            self.file = filename_or_stream
        else:
            self.file = codecs.open(filename_or_stream, encoding=encoding)
        self.iterator = None

    def __iter__(self):
        self.iterator = iter(self.file)
        return self

    def __next__(self):
        return next(self.iterator).rstrip("\n").split(self.delimiter)

    def close(self):
        self.file.close()


class Writer:

    "A simple writer of tabular data."

    def __init__(self, directory, filenames):
        self.directory = directory
        self.filenames = filenames
        self.files = {}
        self.filename = None

    def get_filename(self, key):
        return os.path.join(self.directory, "%s%stxt" % (key, os.path.extsep))

    def reset(self):
        for key in self.filenames:
            try:
                os.remove(self.get_filename(key))
            except OSError:
                pass

    def start(self, filename):
        self.filename = filename

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        for key in self.filenames:
            self.files[key] = codecs.open(self.get_filename(key), "a", encoding="utf-8")

    def close(self):
        for f in self.files.values():
            f.close()
        self.files = {}


# Miscellaneous conversion functions.


def index_for_int(x):

    "Convert 'x' from a 1-based index to a 0-based index."

    if x is not None:
        return max(0, int(x) - 1)
    else:
        return None


def partition(l, start=None, end=None):

    """
    Partition 'l' using the index positions 'start' and 'end', returning the
    preceding slice, the slice described by 'start' and 'end', and the following
    slice.
    """

    if start is not None:
        preceding = l[:start]
    else:
        preceding = []

    if end is not None:
        following = l[end:]
    else:
        following = []

    return preceding, l[start:end], following


def int_or_none(x):
    if x is not None:
        return int(x)
    else:
        return None


# vim: tabstop=4 expandtab shiftwidth=4
