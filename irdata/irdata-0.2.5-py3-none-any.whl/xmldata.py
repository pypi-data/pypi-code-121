#!/usr/bin/env python3

"""
XML parsing utilities.

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

from typing import Union

from xml.sax.handler import ContentHandler
import os
import io
import gzip
from pathlib import Path
from defusedxml import sax


class Parser(ContentHandler):

    "A generic parser."

    def __init__(self):
        ContentHandler.__init__(self)
        self.current_path = []
        self.current_attrs = []
        self.path_to_attrs = {}

    def startElement(self, name, attrs):
        self.current_path.append(name)
        self.current_attrs.append(attrs)
        self.path_to_attrs[name] = attrs

    def endElement(self, name):
        name = self.current_path.pop()
        self.current_attrs.pop()
        del self.path_to_attrs[name]

    def parse(self, source: Union[io.BufferedIOBase, str, os.PathLike]):

        """
        Parse XML from `source` which should be an
        open file in binary mode or a filename.
        """

        if isinstance(source, io.BufferedIOBase):
            return sax.parse(source, handler=self)

        opener = gzip.open if Path(source).suffix == ".gz" else open

        with opener(source, "rb") as _source:
            return sax.parse(_source, handler=self)


class EmptyElementParser(Parser):

    """
    A parser which calls the handleElement method with an empty string for empty
    elements.
    """

    def __init__(self):
        Parser.__init__(self)
        self.current_chars = {}

    def endElement(self, name):
        current_path = tuple(self.current_path)
        if current_path not in self.current_chars:
            self.handleElement("")
        else:
            self.handleElement(self.current_chars[current_path])
            del self.current_chars[current_path]
        Parser.endElement(self, name)

    def characters(self, content):
        current_path = tuple(self.current_path)
        if current_path not in self.current_chars:
            self.current_chars[current_path] = content
        else:
            self.current_chars[current_path] += content

    def handleElement(self, content):
        "Handle a completed element with the given 'content'."


# vim: tabstop=4 expandtab shiftwidth=4
