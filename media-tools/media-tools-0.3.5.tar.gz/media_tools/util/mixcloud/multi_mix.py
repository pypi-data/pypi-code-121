__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
from math import ceil
from pathlib import Path
from typing import List

from media_tools.util.mixcloud.constants import (
    DEFAULT_CROSSFADE_MS, MIXCLOUD_MAX_FILESIZE, DEFAULT_MAX_RETRY, MP3_KBIT_RATE
)
from media_tools.util.mixcloud.mix import Mix
from media_tools.util.mixcloud.mix_path import MixPath


def bytes_per_second(mp3_kbit_rate: int = MP3_KBIT_RATE) -> int:
    return mp3_kbit_rate // 8 * 1024 * 2


# noinspection PyMissingConstructor
class MultiMix(Mix):

    def __init__(  # pylint: disable=super-init-not-called, too-many-arguments
            self, mix_path: MixPath, access_token: str, total_length: int,
            strict: bool = False, crossfade_ms: int = DEFAULT_CROSSFADE_MS
    ) -> None:
        self._mix_path = mix_path
        self._mix_parts: List[Mix] = []
        self._part_paths: List[Path] = []
        self._incomplete = False
        oversize_factor = ceil(total_length * bytes_per_second() / MIXCLOUD_MAX_FILESIZE)
        chunk_size = len(self._mix_path.audio_files) // oversize_factor
        for i in range(oversize_factor):
            part_files = tuple(self._mix_path.audio_files[i * chunk_size:(i + 1) * chunk_size])
            part_name = f"{self.title} Part {i + 1}"
            logging.info(part_name)
            mix_part = Mix(
                self._mix_path.from_files(part_files), strict=strict, crossfade_ms=crossfade_ms
            ).with_access_token(access_token).with_title(part_name)
            self._mix_parts.append(mix_part)
        self._incomplete = any(part._incomplete for part in self._mix_parts)

    @property
    def parts(self):
        return self._mix_parts

    @property
    def title(self) -> str:
        title = self._mix_path.title
        return f"Test - don't bother playing ({title})" if self._incomplete else title

    def upload(self, name: Path = Path('mix.mp3'), max_retry: int = DEFAULT_MAX_RETRY) -> None:
        for mix_part, part_path in zip(self._mix_parts, self._part_paths):
            mix_part.upload(part_path, max_retry)

    def export(self, name: Path = Path('mix.mp3')) -> None:
        for i, mix_part in enumerate(self._mix_parts):
            part_path = Path(f"{name.stem}_{i + 1}{name.suffix}")
            mix_part.export(part_path)
            self._part_paths.append(part_path)
