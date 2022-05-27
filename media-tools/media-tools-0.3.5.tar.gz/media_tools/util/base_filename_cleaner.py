from pathlib import Path
from typing import List


class BaseFilenameCleaner:

    MUSIC_EXTENSIONS = ('mp3', 'flac', 'ogg', 'm4a')

    def __init__(self, basedir: Path) -> None:
        self._base_directory = basedir

    def get_music_files(self) -> List[Path]:
        return sorted(
            [
                f for f in Path(self._base_directory).iterdir()
                if f.is_file() and self.is_music_file(f)
            ]
        )

    @staticmethod
    def is_music_file(filename: Path) -> bool:
        return any(
            filename.name.upper().endswith(e.upper()) for e in BaseFilenameCleaner.MUSIC_EXTENSIONS
        )

    @staticmethod
    def filename_base(file: Path) -> str:
        return file.stem
