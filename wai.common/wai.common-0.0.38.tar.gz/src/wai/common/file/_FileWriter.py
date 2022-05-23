from abc import abstractmethod
from typing import IO, TypeVar

from ._FileIOBase import FileIOBase, ObjectType, DiskType

SelfType = TypeVar("SelfType", bound="FileWriter")


class FileWriter(FileIOBase[DiskType, ObjectType, SelfType]):
    """
    Base class for classes which write objects to disk.
    """
    def dump(self, obj: ObjectType):
        """
        Serialises an object to the file.

        :param obj:     The object to serialise.
        """
        # If writing fails, ensure the file position remains unchanged
        pre_dump_position = self._file.tell()
        try:
            return self._dump(obj, self._file)
        except Exception:
            self._file.seek(pre_dump_position)
            self._file.truncate()
            raise

    def dumpf(self, filename: str, *objects: ObjectType, append: bool = False):
        """
        Dumps the given objects to a disk file.

        :param filename:    The file to write to.
        :param objects:     The objects to write.
        :param append:      Whether to append the objects.
        """
        with self.set_file(self.open(filename, append)) as writer:
            for obj in objects:
                writer.dump(obj)

    def dumps(self, *objects: ObjectType) -> DiskType:
        """
        Serialises objects to a string.

        :param objects:     The objects to serialise.
        :return:            A string/bytes.
        """
        # Create a new memory file
        memory_file: IO[DiskType] = self.get_memory_file()

        # Write the objects to the memory file
        with self.set_file(memory_file) as writer:
            for obj in objects:
                writer.dump(obj)

        # Return the memory file contents
        memory_file.seek(0)
        return memory_file.read()

    @classmethod
    def open(cls, filename: str, append: bool = False) -> IO[DiskType]:
        """
        Opens the given file for writing using this writer type.

        :param filename:    The file to open.
        :param append:      Whether to append to the end of the file.
        :return:            The file writer.
        """
        return cls._open(filename, 'a' if append else 'w')

    @abstractmethod
    def _dump(self, obj: ObjectType, file: IO[DiskType]):
        """
        Implementation to write the given object to the given file.
        Assumes the file is valid (writable).

        :param obj:     The object to write.
        :param file:    The file to write to.
        """
        pass

    @classmethod
    def _check_file(cls, file: IO[DiskType]):
        if not file.writable():
            raise ValueError("File not writable")
