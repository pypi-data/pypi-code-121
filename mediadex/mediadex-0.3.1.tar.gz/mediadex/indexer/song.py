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

from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.id3._util import ID3NoHeaderError

from mediadex import ID
from mediadex import Song
from mediadex import StreamCounts

LOG = logging.getLogger('mediadex.indexer.song')


class SongIndexer:
    def __init__(self):
        pass

    def index(self, item, song=None):
        if song is None:
            song = Song()
        orig_dict = song.to_dict()

        song.audio_stream = next(item.astreams())
        song.dirname = item.dirname
        song.filename = item.filename
        song.filesize = item.general['file_size']
        song.fingerprint = item.fingerprint

        try:
            info = EasyID3(song.filename)
            id_doc = ID()

            if 'date' in info:
                song.year = info['date']

            for tag in ['album', 'albumartist', 'arranger', 'artist', 'bpm',
                        'compilation', 'composer', 'conductor', 'tracknumber',
                        'title', 'mood', 'genre', 'performer']:
                if tag in info:
                    setattr(song, tag, info[tag])

            for tag in ['musicip_puid', 'musicip_fingerprint',
                        'acoustid_fingerprint', 'acoustid_id']:
                if tag in info:
                    setattr(id_doc, tag, info[tag])
            song.id_info = id_doc

        except ID3NoHeaderError:
            pass
        except MutagenError as exc:
            if LOG.isEnabledFor(logging.INFO):
                LOG.exception(exc)
            else:
                LOG.warn(str(exc))

        stream_counts = StreamCounts()
        stream_counts.audio_stream_count = 1
        stream_counts.video_stream_count = 0
        stream_counts.text_stream_count = 0
        song.stream_counts = stream_counts

        if song.to_dict() != orig_dict:
            try:
                song.save()
            except Exception as exc:
                if LOG.isEnabledFor(logging.INFO):
                    LOG.exception(exc)
                else:
                    LOG.warn(str(exc))
            LOG.info("Song updated")
        else:
            LOG.debug("Song unchanged")
