import os
from abc import abstractmethod
from typing import IO, Callable, Iterator, Tuple, Union, TypeVar
from io import SEEK_END

from ._FileIOBase import FileIOBase, DiskType, ObjectType

SelfType = TypeVar("SelfType", bound="FileReader")


class FileReader(FileIOBase[DiskType, ObjectType, SelfType]):
    """
    Base class for classes which read files from files. Ensures that
    the file is seekable (e.g. so you can read past the end of a valid
    object in the file and then return the stream position to the start
    of the next object).
    """
    def __init__(self):
        super().__init__()

        self._eof: int = -1
        self._checkpoint: int = -1

    def set_file(self, file: Union[DiskType, IO[DiskType]]) -> SelfType:
        super().set_file(file)

        # Calculate the EOF position
        position: int = self._file.tell()
        self._file.seek(0, SEEK_END)
        self._eof: int = self._file.tell()
        self._file.seek(position)

        return self

    def eof_reached(self) -> bool:
        """
        Returns true if the end-of-file has been reached.
        """
        self.ensure_file()
        return self._file.tell() == self._eof

    def checkpoint(self):
        """
        Sets a checkpoint at the current read position of the file.
        """
        self.ensure_file()
        self._checkpoint = self._file.tell()

    def restore_checkpoint(self):
        """
        Restores the previous checkpoint.
        """
        self.ensure_file()
        self._file.seek(self._checkpoint)

    def load(self) -> ObjectType:
        """
        Loads an object from the file.

        :return:        The loaded object.
        """
        # Make sure we have a file
        self.ensure_file()

        # If reading fails, ensure the file position remains unchanged
        pre_load_position = self._file.tell()
        try:
            return self._load(self._file)
        except Exception:
            self._file.seek(pre_load_position)
            raise

    def loadf(self, filename: str) -> Iterator[ObjectType]:
        """
        Loads all the objects from a file.

        :param filename:    The file to load objects from.
        :return:            The objects.
        """
        with self.set_file(self.open(filename)) as reader:
            while not reader.eof_reached():
                yield reader.load()

    def loads(self, string: DiskType) -> Iterator[ObjectType]:
        """
        Loads all the objects from a string.

        :param string:      The string to load objects from.
        :return:            The objects.
        """
        with self.set_file(string) as reader:
            while not reader.eof_reached():
                yield reader.load()

    def loadd(self,
              path: str,
              filename_predicate: Callable[[str], bool],
              recurse: bool = False) -> Iterator[Tuple[str, int, ObjectType]]:
        """
        Loads all files from the given path that match the filename predicate.

        :param path:                The directory to load from.
        :param filename_predicate:  A function which takes a filename and
                                    returns True if the file should be loaded.
        :param recurse:             Whether sub-directories should be loaded as well.
        :return:                    An iterator over the objects loaded from the files,
                                    along with the filename and the position of the object
                                    in the file.
        """
        # Make sure a valid path was provided
        if not os.path.isdir(path):
            raise ValueError(f"'{path}' is not a directory")

        # Loop through all files/directories in the given directory
        for name in os.listdir(path):
            # Get the full name
            full_name: str = os.path.join(path, name)

            # If we are recursing through directories, do that
            if os.path.isdir(full_name):
                if recurse:
                    for filename, position, obj in self.loadd(full_name, filename_predicate, recurse):
                        yield filename, position, obj

            # Otherwise load the file if the name matches the predicate
            elif os.path.isfile(full_name) and filename_predicate(full_name) is True:
                for position, obj in enumerate(self.loadf(full_name)):
                    yield full_name, position, obj

    @classmethod
    def open(cls, filename: str) -> IO[DiskType]:
        """
        Opens the given file for reading.

        :param filename:    The file to open.
        :return:            The file object.
        """
        return cls._open(filename, 'r')

    @abstractmethod
    def _load(self, file: IO[DiskType]) -> ObjectType:
        """
        Loads a single object from the given file, starting at the current
        file position and leaving the file position at the start of the
        next object (just after the end of the loaded object).

        :param file:    The file to read from. Assumed to be a valid file
                        (readable, seekable).
        :return:        The loaded object.
        """
        pass

    @classmethod
    def _check_file(cls, file: IO[DiskType]):
        super()._check_file(file)

        if not file.readable():
            raise ValueError("File not readable")

        if not file.seekable():
            raise ValueError("File not seekable")
