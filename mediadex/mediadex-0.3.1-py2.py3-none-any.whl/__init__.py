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

from opensearch_dsl import Document
from opensearch_dsl import Float
from opensearch_dsl import InnerDoc
from opensearch_dsl import Integer
from opensearch_dsl import Keyword
from opensearch_dsl import Long
from opensearch_dsl import Object
from opensearch_dsl import Text


class _Index:
    settings = {
        'number_of_shards': 1,
        'number_of_replicas': 0,
    }


class StreamCounts(InnerDoc):
    audio_stream_count: Integer()
    text_stream_count: Integer()
    video_stream_count: Integer()


class Media(Document):
    title = Text()
    year = Keyword()
    genre = Keyword(multi=True)
    stream_counts = Object(StreamCounts)
    container = Keyword()
    dirname = Keyword()
    filename = Keyword()
    filesize = Long()
    fingerprint = Text()


class Stream(InnerDoc):
    codec = Keyword()
    codec_profile = Keyword()
    duration = Float()
    language = Keyword()
    mime_type = Keyword()


class TextStream(Stream):
    charset = Keyword()


class BitStream(Stream):
    bit_rate = Long()
    bit_depth = Integer()
    sample_rate = Integer()


class AudioStream(BitStream):
    channels = Keyword()


class VideoStream(BitStream):
    resolution = Keyword()
    height = Integer()
    width = Integer()


class ID(InnerDoc):
    acoustid_fingerprint = Keyword()
    acoustid_id = Keyword()

    musicip_fingerprint = Keyword()
    musicip_puid = Keyword()


class Song(Media):
    audio_stream = Object(AudioStream)
    id_info = Object(ID)

    album = Text()
    albumartist = Text()
    arranger = Keyword()
    artist = Text()
    bpm = Float()
    compilation = Keyword()
    composer = Text()
    conductor = Text()
    discnumber = Keyword()
    mood = Keyword()
    performer = Text()
    tracknumber = Keyword()

    class Index(_Index):
        name = 'music'


class Cinema(Media):
    cast = Text(multi=True)
    director = Text(multi=True)
    writer = Text(multi=True)

    audio_streams = Object(AudioStream, multi=True)
    text_streams = Object(TextStream, multi=True)
    video_streams = Object(VideoStream, multi=True)


class Movie(Cinema):
    class Index(_Index):
        name = 'movies'


class Show(Cinema):
    season = Integer()

    class Index(_Index):
        name = 'series'
