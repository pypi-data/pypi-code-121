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

import bisect
from collections.abc import Mapping
import numbers


class Matcher:

    @staticmethod
    def flatten_mapping(obj, path=[]):
        leaves = {k: v for k, v in obj.items() if not isinstance(v, Mapping)}
        children = {k: v for k, v in obj.items() if k not in leaves}
        for k, v in children.items():
            yield from Matcher.flatten_mapping(v, path=path[:] + [k])

        yield from (
            (tuple(path + [k]), Matcher.simplify(getattr(v, "value", v)))
            for k, v in leaves.items()
        )

    @staticmethod
    def mapping_key(obj):
        """ A keying function which allows nested objects to be sorted.

        """
        obj = obj or {}
        return sorted(list(Matcher.flatten_mapping(obj)))

    @staticmethod
    def simplify(val):
        if val is None:
            return ""
        elif isinstance(val, numbers.Complex):
            return str(abs(val))
        elif isinstance(val, numbers.Number):
            return str(val)
        else:
            return val

    def __init__(self, folders=None):
        """Match Turberfield Folders by their metadata.

        This class has methods to normalise arbitrary dictionaries.
        It provides a search API, so you can discover which folders are a metadata
        match.

        :param folders: A sequence of
            :py:class:`turberfield.dialogue.model.SceneScript.Folder` objects.
        """
        self.folders = sorted(folders or [], key=lambda x: self.mapping_key(x.metadata))
        self.keys = sorted([self.mapping_key(i.metadata) for i in self.folders])

    def options(self, data):
        """Generate folders to best match metadata.

        The results will be a single, perfectly matched folder, or the two nearest
        neighbours of an imperfect match.

        :param dict data: metadata matching criteria.

        This method is a generator. It yields
        :py:class:`turberfield.dialogue.model.SceneScript.Folder` objects.

        """
        if self.mapping_key(data) in self.keys:
            yield next(i for i in self.folders if i.metadata == data)
        else:
            index = bisect.bisect_left(self.keys, self.mapping_key(data))
            posns = sorted(set([max(0, index - 1), index]))
            yield from (self.folders[i] for i in posns)
