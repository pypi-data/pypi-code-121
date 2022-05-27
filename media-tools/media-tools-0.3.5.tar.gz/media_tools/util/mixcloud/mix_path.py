__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import re
from pathlib import Path
from typing import Tuple, List, Optional

from tinytag import TinyTag


class MixPath:

    def __init__(self, basedir: Path, patterns: Tuple[str, ...]) -> None:
        self.basedir = basedir
        self.audio_files = sorted([f for p in patterns for f in self.basedir.glob(p)])

    def from_files(self, files: Tuple[Path, ...]):
        return MixPath(self.basedir, tuple(file.name for file in files))

    def file(self, filename: Path) -> Path:
        return self.basedir / filename

    def scan(self) -> Tuple[List[str], int]:
        length = sum([TinyTag.get(str(audio_file)).duration for audio_file in self.audio_files])
        return [f.name for f in self.audio_files], int(length)

    @property
    def tags(self) -> List[str]:
        if (self.basedir / 'tags.txt').exists():
            with (self.basedir / 'tags.txt').open() as file:
                return list(line for line in (line.strip() for line in file) if line)
        return []

    @property
    def title(self) -> str:
        return re.sub(r'^\d+ - ', '', self.basedir.resolve().name)

    @property
    def description(self) -> str:
        if (self.basedir / 'description.txt').exists():
            with (self.basedir / 'description.txt').open() as file:
                return file.read().strip()
        return ''

    @property
    def picture(self) -> Optional[Path]:
        """Currently just returns the first JPEG or PNG. Raises StopIteration if there is none."""
        return next(self.basedir.glob('*.*p*g'))
