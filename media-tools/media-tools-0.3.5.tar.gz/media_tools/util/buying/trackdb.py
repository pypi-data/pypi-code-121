__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import pickle
from datetime import datetime
from pathlib import Path
from shutil import copy2


class TrackDB(set):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._backup_db()
        with self.bought_db.open('wb') as file:
            pickle.dump(list(self), file)

    def _backup_db(self) -> None:
        if self.bought_db.is_file():
            copy2(
                str(self.bought_db),
                str(self.bought_db.with_suffix(self.suffix_with_appended_timestamp(self.bought_db)))
            )

    @staticmethod
    def suffix_with_appended_timestamp(filepath: Path) -> str:
        return filepath.suffix + f'.{datetime.now().isoformat(timespec="minutes")}'

    def __init__(self, bought_db: Path) -> None:
        super().__init__()
        self.bought_db = bought_db
        try:
            with bought_db.open('rb') as file:
                for track in pickle.load(file):
                    self.add(track)
        except FileNotFoundError:
            pass
