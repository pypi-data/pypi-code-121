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
import re

from imdb import Cinemagoer

from mediadex import Movie
from mediadex import StreamCounts

LOG = logging.getLogger('mediadex.indexer.movie')


class MovieIndexer:
    def __init__(self):
        self.imdb = Cinemagoer()

    def index(self, item, existing=None):
        movie = Movie()

        # basic stream info
        stream_counts = StreamCounts()

        vstreams = [x for x in item.vstreams()]
        tstreams = [x for x in item.tstreams()]
        astreams = [x for x in item.astreams()]

        movie.video_streams = vstreams
        movie.text_streams = tstreams
        movie.audio_streams = astreams

        stream_counts.video_stream_count = len(vstreams)
        LOG.debug("Processed {} video streams".format(len(vstreams)))
        stream_counts.text_stream_count = len(tstreams)
        LOG.debug("Processed {} text streams".format(len(tstreams)))
        stream_counts.audio_stream_count = len(astreams)
        LOG.debug("Processed {} audio streams".format(len(astreams)))

        movie.stream_counts = stream_counts
        movie.dirname = item.dirname
        movie.filename = item.filename
        movie.filesize = item.general['file_size']
        movie.fingerprint = item.fingerprint

        if existing:
            # Assume imdb hasn't changed anything
            movie.cast = existing.cast or None
            movie.director = existing.director or None
            movie.writer = existing.writer or None
            movie.title = existing.title or None
            movie.year = existing.year or None
            movie.genre = existing.genre or None

        else:
            # build a list of potential movie names
            # order matters
            #   title + subtitle (no year)
            #   title
            #   filename
            #   subtitle
            #   container movie_name
            #   container title
            search_strings = []

            file_name = item.general['file_name']
            file_sanitized = file_name.replace('.', ' ')

            file_title = None
            file_year = None
            file_subtitle = None
            file_re = re.compile(r'([^.]+ )+(\d{4})( [^.]*)*')
            file_match = file_re.match(file_sanitized)

            # check container metadata
            if 'movie_name' in item.general:
                search_strings.append(item.general['movie_name'])

            if 'title' in item.general:
                search_strings.append(item.general['title'])

            # parse re results
            if file_match:
                LOG.debug('filename parts: {}'.format(file_match.groups()))

                file_title = file_match.group(1).strip()
                file_year = file_match.group(2)
                if file_match.group(3):
                    file_subtitle = file_match.group(3).strip()

                LOG.debug("RE Match: {} {} {}".format(
                    file_title,
                    file_year,
                    file_subtitle)
                )

                if file_subtitle:
                    full_title = '{} {}'.format(file_title, file_subtitle)
                    search_strings.append(full_title)

                search_strings.append(file_title)

                if file_subtitle:
                    search_strings.append(file_subtitle)

            search_strings.append(file_sanitized)

            # collate search string results

            imdb_results = {}
            best_title = ''
            best_imdb = []
            imdb_info = {}

            LOG.debug(search_strings)
            for imdb_search in search_strings:
                LOG.debug("IMDB search: {}".format(imdb_search))
                if not imdb_search:
                    continue
                _imdb = self.imdb.search_movie(imdb_search)
                if _imdb:
                    imdb_results[imdb_search] = _imdb

            title_list = imdb_results.keys()
            for title in title_list:
                if not best_imdb:
                    best_title = title
                    best_imdb = imdb_results[title]

            found_count = len(title_list)
            if found_count == 0:
                LOG.warn("No IMDB match: {}".format(search_strings))
                LOG.debug(item.general)
                return
            elif found_count == 1:
                LOG.debug("One IMDB match: {}".format(best_title))
                imdb_info = best_imdb[0]
                LOG.debug(item.general)
            else:
                LOG.info("Best IMDB match: {}".format(best_title))
                imdb_info = best_imdb[0]
                LOG.debug(item.general)

            LOG.info("IMDB Title: {}".format(imdb_info['title']))
            self.imdb.update(imdb_info)

            try:
                if 'cast' in imdb_info:
                    movie.cast = [
                        x['name'] for x in imdb_info['cast'] if 'name' in x
                    ]
                if 'director' in imdb_info:
                    movie.director = [
                        x['name'] for x in imdb_info['director'] if 'name' in x
                    ]
                if 'writer' in imdb_info:
                    movie.writer = [
                        x['name'] for x in imdb_info['writer'] if 'name' in x
                    ]
                if 'title' in imdb_info:
                    movie.title = imdb_info['title']
                if 'year' in imdb_info:
                    movie.year = imdb_info['year']
                if 'genres' in imdb_info:
                    movie.genre = imdb_info['genres']
            except KeyError as exc:
                LOG.debug(imdb_info.__dict__)
                LOG.exception(exc)

        try:
            if existing is None:
                movie.save()
                LOG.info("Movie added")
            elif existing.to_dict() == movie.to_dict():
                LOG.debug("Movie unchanged")
            else:
                existing.delete()
                movie.save()
                LOG.info("Movie updated")

        except Exception as exc:
            if LOG.isEnabledFor(logging.INFO):
                LOG.exception(exc)
            else:
                LOG.warn(str(exc))
