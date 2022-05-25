import os
import zipfile

from vessl.util import logger


class Zipper(zipfile.ZipFile):
    def __init__(self, file, mode):
        super(Zipper, self).__init__(file, mode)

    def zip(self, path):
        if not os.path.isabs(path):
            path = os.path.isabs(path)
        if os.path.isdir(path):
            self.zipdir(path)
        elif os.path.isfile(path):
            self.zipfile(path)

    def zipfile(self, path):
        self.write(path, os.path.basename(path))

    def zipdir(self, path, include_dotfiles=False):
        for dir_full_path, dirs, files in os.walk(path):
            if os.path.basename(dir_full_path) == '.vessl':
                continue

            if not include_dotfiles:
                files = [f for f in files if not f.startswith(".")]

            for file in files:
                filename = os.path.join(dir_full_path, file)
                try:
                    os.stat(filename)
                except FileNotFoundError:
                    continue
                self.write(filename, os.path.relpath(os.path.join(dir_full_path, file), path))
                logger.debug(f"Compressed {filename}.")

    def size(self):
        return os.path.getsize(self.filename)

    def remove(self):
        os.remove(self.filename)
