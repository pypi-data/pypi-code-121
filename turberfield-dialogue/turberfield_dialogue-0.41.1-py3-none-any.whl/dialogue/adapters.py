#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import os
import platform
import re

from turberfield.utils.logger import LogAdapter


class ColourAdapter(LogAdapter):

    patterns = [
        (re.compile("NOTE"), (234, 0, 255)),
        (re.compile("INFO"), (0, 255, 255)),
        (re.compile("ERROR"), (234, 255, 0)),
        (re.compile("WARNING"), (255, 106, 0)),
        (re.compile("CRITICAL"), (255, 0, 106)),
    ]

    def __init__(self):
        if platform.system().lower() == "windows":
            os.system("color")

    def colour_field(self, n, field, word):
        if "level" in field:
            r, g, b = next(
                (c for r, c in self.patterns if r.search(word)),
                (200, 200, 200)
            )
            return f"\033[38;2;{r};{g};{b}m{word}\033[0m"
        elif "line" in field:
            return f"\033[1m{word}\033[0m"
        elif "{0}" in field:
            return f"\033[3m{word}\033[0m"
        else:
            return word

    def render(self, entry):
        frame = entry.origin.frame
        return " ".join(
            self.colour_field(n, f, w)
            for n, f, w in zip(itertools.count(len(frame)), frame, entry.tokens)
            if f not in ("{now}", "{logger.name}")
        )
