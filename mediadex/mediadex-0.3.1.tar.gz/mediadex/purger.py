#!/usr/bin/python3

# Mediadex: Index media metadata into opensearch
# Copyright (C) 2019-2022  K Jonathan Harker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os.path

from mediadex import Movie
from mediadex import Song

LOG = logging.getLogger('mediadex.purger')


class Purger:
    baseQ = None

    def purge(self):
        retval = 0

        for h in self.baseQ.scan():
            fullpath = os.path.join(h.dirname, h.filename)
            if not os.path.exists(fullpath):
                try:
                    _id = h.meta._d_['id']
                    LOG.warn('Purging {} for {}'.format(_id, fullpath))
                    h.delete()
                except Exception as exc:
                    LOG.exception(exc)
                    retval += 1

        return retval


class MoviePurger(Purger):
    def __init__(self):
        self.baseQ = Movie.search().filter('exists', field='filename')


class SongPurger(Purger):
    def __init__(self):
        self.baseQ = Song.search().filter('exists', field='filename')
