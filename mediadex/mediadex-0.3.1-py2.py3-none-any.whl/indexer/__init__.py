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

from opensearch_dsl import FacetedSearch
from opensearch_dsl import TermsFacet

from mediadex import Movie
from mediadex import Song
from mediadex.exc import IndexerException
from mediadex.indexer.movie import MovieIndexer
from mediadex.indexer.song import SongIndexer
from mediadex.item import Item

LOG = logging.getLogger('mediadex.indexer')


class FileListFacet(FacetedSearch):
    fields = ['filename', ]
    facets = {'filenames': TermsFacet(field='filename')}

    def params(self, **kwargs):
        s = self._s._clone()
        r = s.params(**kwargs)
        self._s = r
        return r

    def execute(self):
        """
        Execute the search and return the response.
        """
        r = self._s.execute(ignore_cache=True)
        r._faceted_search = self
        return r

    def scan(self):
        for hit in self._s.scan():
            yield hit


class MovieListFacet(FileListFacet):
    doc_types = [Movie, ]

    def search(self):
        r = super().search().doc_type(Movie)
        return r.filter('exists', field='filename')


class SongListFacet(FileListFacet):
    doc_types = [Song, ]

    def search(self):
        r = super().search().doc_type(Song)
        return r.filter('exists', field='filename')


class Indexer:
    def __init__(self):
        Movie.init()
        Song.init()
        self.mi = MovieIndexer()
        self.si = SongIndexer()

    def index(self, info):
        LOG.debug('Hashing file')
        info.hashFile()

        LOG.debug('Calling mediainfo')
        info.parseMediaInfo()

        data = info.dumpData()
        item = Item(data['mediainfo']['tracks'])

        dirname = data['basepath'].rstrip('/')
        item.dirname = dirname

        filename = data['fullpath'].replace(dirname, '').lstrip('/')
        item.filename = filename

        item.fingerprint = data['fingerprint']

        if item.dex_type == 'empty':
            LOG.warn("No streams detected for {}".format(filename))
            return

        elif item.dex_type == 'unknown':
            LOG.warning('Unknown format ({}, {}, {}), '
                        'skipping {}'.format(len(item.video_tracks),
                                             len(item.audio_tracks),
                                             len(item.text_tracks),
                                             filename))

        elif item.dex_type == 'song':
            s = Song.search()
            LOG.info("Processing Song for {}".format(filename))
            r = s.filter('term', fingerprint=item.fingerprint).execute()

            if r.hits.total.value == 0:
                LOG.debug("Indexing new Song for {}".format(filename))
                self.index_song(item)
            elif r.hits.total.value == 1:
                LOG.debug("Updating existing Song for {}".format(filename))
                song = r.hits[0]
                self.index_song(item, song)
            else:
                LOG.error("Found {} existing Songs for {}".format(
                        r.hits.total.value, filename))
                for h in r.hits:
                    LOG.debug("{}/{}".format(h.dirname, h.filename))
                raise IndexerException("Multiple filename matches")

        elif item.dex_type == 'movie':
            s = Movie.search()
            LOG.info(f"Processing Movie for {filename} ({item.fingerprint})")
            r = s.filter('term', fingerprint=item.fingerprint).execute()

            if r.hits.total.value == 0:
                LOG.debug("Indexing new Movie for {}".format(filename))
                self.index_movie(item)
            elif r.hits.total.value == 1:
                LOG.debug("Updating existing Movie for {}".format(filename))
                movie = r.hits[0]
                self.index_movie(item, movie)
            else:
                LOG.error("Found {} existing Movies for {}".format(
                        r.hits.total.value, filename))
                for h in r.hits:
                    LOG.debug("{}/{}".format(h.dirname, h.filename))
                raise IndexerException("Multiple filename matches")

    def index_song(self, item, song=None):
        self.si.index(item, song)

    def index_movie(self, item, movie=None):
        self.mi.index(item, movie)
