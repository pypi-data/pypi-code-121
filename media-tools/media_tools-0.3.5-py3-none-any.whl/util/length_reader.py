__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
from pathlib import Path
from typing import Optional

import audioread
import eyed3
import soundfile
from audioread.exceptions import NoBackendError
from mutagen import File, MutagenError


class LengthReader:  # pylint: disable=too-few-public-methods
    def __init__(self, track: Path):
        self.track = track

    def get_duration(self) -> Optional[float]:
        raise NotImplementedError


class MutagenLengthReader(LengthReader):
    def get_duration(self) -> Optional[float]:
        try:
            audio = File(self.track)
            if audio and audio.info:
                return audio.info.length
        except MutagenError:
            pass
        return None


class Eyed3LengthReader(LengthReader):
    def get_duration(self) -> Optional[float]:
        log_level = logging.getLogger().getEffectiveLevel()
        try:
            logging.getLogger().setLevel(logging.ERROR)
            mp3file = eyed3.load(self.track)
            if mp3file is not None and mp3file.info is not None:
                duration = mp3file.info.time_secs
                return duration
        except IOError:
            pass
        finally:
            logging.getLogger().setLevel(log_level)
        return None


class SoundfileLengthReader(LengthReader):
    def get_duration(self) -> Optional[float]:
        try:
            with soundfile.SoundFile(self.track) as mp3file:
                return mp3file.frames / mp3file.samplerate
        except RuntimeError:
            pass
        return None


class AudioreadLengthReader(LengthReader):
    def get_duration(self) -> Optional[float]:
        try:
            with audioread.audio_open(self.track) as mp3file:
                return mp3file.duration
        except (NoBackendError, EOFError, UnicodeEncodeError):
            pass
        return None
