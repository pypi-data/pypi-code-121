import hashlib
from typing import List

from pydmt.utils.filesystem import files_under_folders


BLOCK_SIZE = 65536
ALGORITHM_NAME = "sha1"


class Digester:
    def __init__(self):
        self.hash_object = hashlib.new(ALGORITHM_NAME)

    def add_file(self, filename: str) -> None:
        with open(filename, 'rb') as file_handle:
            buf = file_handle.read(BLOCK_SIZE)
            while len(buf) > 0:
                self.hash_object.update(buf)
                buf = file_handle.read(BLOCK_SIZE)

    def add_files(self, filenames: List[str]) -> None:
        for filename in filenames:
            self.add_file(filename)

    def add_folders(self, folders: List[str]) -> None:
        for filename in files_under_folders(folders=folders):
            self.add_file(filename)

    def add_files_folders(self, files: List[str], folders: List[str]) -> None:
        f = files
        f.extend(files_under_folders(folders=folders))
        self.add_files(f)

    def get_hexdigest(self):
        return self.hash_object.hexdigest()
