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

from mediadex import AudioStream
from mediadex import TextStream
from mediadex import VideoStream
from mediadex.exc import IndexerException

LOG = logging.getLogger('mediadex.item')


class Item:
    def __init__(self, data):
        gen = [t for t in data if t['track_type'] == 'General']
        if len(gen) > 1:
            raise IndexerException("More than one General track found")
        elif len(gen) == 0:
            raise IndexerException("No General track found")
        self.general = gen.pop()

        atracks = [t for t in data if t['track_type'] == 'Audio']
        self.audio_tracks = atracks
        acount = len(atracks)

        vtracks = [t for t in data if t['track_type'] == 'Video']
        self.video_tracks = vtracks
        vcount = len(vtracks)

        ttracks = [t for t in data if t['track_type'] == 'Text']
        self.text_tracks = ttracks
        tcount = len(ttracks)

        if vcount > 0 and acount > 0:
            self.dex_type = 'movie'
        elif vcount > 0:
            self.dex_type = 'image'
        elif acount == 1:
            self.dex_type = 'song'
        elif tcount == 1:
            self.dex_type = 'text'
        elif acount == 0 and vcount == 0 and tcount == 0:
            self.dex_type = 'empty'
        else:
            self.dex_type = 'unknown'

    def base_track(self, track, stream):
        if 'duration' in track:
            try:
                stream.duration = float(track['duration'])
            except ValueError as exc:
                if LOG.isEnabledFor(logging.INFO):
                    LOG.exception(exc)
                else:
                    LOG.warn(str(exc))

        if 'format' in track:
            stream.codec = track['format']
        if 'format_profile' in track:
            stream.codec_profile = track['format_profile']
        if 'language' in track:
            stream.language = track['language']
        if 'internet_media_type' in track:
            stream.mime_type = track['internet_media_type']

    def astreams(self):
        for t in self.audio_tracks:
            stream = AudioStream()

            self.base_track(t, stream)

            if 'channel_s' in t:
                stream.channels = t['channel_s']

            if 'bit_rate' in t:
                if t['bit_rate'] == 'Open':
                    continue

                try:
                    stream.bit_rate = int(t['bit_rate'])
                except ValueError as verr:
                    LOG.warn(str(verr))
                except Exception as exc:
                    LOG.exception(exc)

            if 'sampling_rate' in t:
                stream.sample_rate = t['sampling_rate']

            yield stream

    def tstreams(self):
        for t in self.text_tracks:
            stream = TextStream()

            self.base_track(t, stream)

            if 'encoding' in t:
                stream.charset = t['encoding']

            yield stream

    def vstreams(self):
        for t in self.video_tracks:
            stream = VideoStream()

            self.base_track(t, stream)

            if 'bit_rate' in t:
                if t['bit_rate'] == 'Open':
                    continue

                try:
                    stream.bit_rate = int(t['bit_rate'])
                except ValueError as verr:
                    LOG.warn(str(verr))
                except Exception as exc:
                    LOG.exception(exc)

            if 'bit_depth' in t:
                try:
                    stream.bit_depth = int(t['bit_depth'])
                except Exception as exc:
                    if LOG.isEnabledFor(logging.INFO):
                        LOG.exception(exc)
                    else:
                        LOG.warn(str(exc))

            if 'height' in t and 'width' in t:
                try:
                    stream.height = int(t['height'])
                    stream.width = int(t['width'])

                    stream.resolution = "{0}x{1}".format(
                            t['height'],
                            t['width'],
                    )
                except ValueError as exc:
                    if LOG.isEnabledFor(logging.INFO):
                        LOG.exception(exc)
                    else:
                        LOG.warn(str(exc))

            yield stream
