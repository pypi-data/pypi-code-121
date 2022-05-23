import gzip
from io import StringIO, BytesIO
from typing import TypeVar, Generic, Union, Type, Optional, IO, Tuple, Callable

from ..meta.typing import TypeVarProperty

# The type of object that is read/written
ObjectType = TypeVar("ObjectType")

# The type of data the file contains (text/binary)
DiskType = TypeVar("DiskType", bytes, str)

# The type of cls (for self-referential methods)
SelfType = TypeVar("SelfType", bound="FileIOBase")

# The type of the open() function
OpenFunc = Callable[[str, str], IO[DiskType]]


class FileIOBase(Generic[DiskType, ObjectType, SelfType]):
    """
    Base class for FileReader and FileWriter.
    """
    # TypeVar properties
    _disk_type = TypeVarProperty(DiskType)
    _object_type = TypeVarProperty(ObjectType)

    def __init__(self):
        self._file: Optional[IO[DiskType]] = None

    def set_file(self, file: Union[DiskType, IO[DiskType]]) -> SelfType:
        """
        Sets the file for this reader/writer to operate on.

        :param file:    The file.
        :return:        Itself (chainable).
        """
        # Convert raw strings/bytes into in-memory files
        if isinstance(file, self._disk_type):
            file = self.get_memory_file(file)

        # Make sure the file is valid
        self._check_file(file)

        # Set the file
        self._file = file

        return self

    def has_file(self) -> bool:
        """
        Checks if the reader/writer has a file to operate on.
        """
        return self._file is not None

    def ensure_file(self):
        """
        Ensures that the reader/writer has a file to operate on.
        """
        if not self.has_file():
            raise AttributeError("No file set")

    @classmethod
    def get_memory_file(cls, initial_value: Optional[DiskType] = None) -> Union[StringIO, BytesIO]:
        """
        Gets an instance of the memory file class for the disk type.

        :param initial_value:   The initial contents for the file.
        :return:                A new memory file.
        """
        return cls._get_memory_file_class()(initial_value)

    @classmethod
    def _open(cls, filename: str, mode: str) -> IO[DiskType]:
        """
        Opens the given file is the given mode.

        :param filename:    The file to open.
        :param mode:        The base open mode (r/w).
        :return:            The file stream.
        """
        # Make sure a valid mode is given
        if mode not in ('r', 'w', 'a'):
            raise ValueError(f"Mode must be 'r', 'w' or 'a', not '{mode}'")

        # Get the open function to use
        open_func, mode = cls._get_open_func(filename, mode)

        # Open and return the file
        return open_func(filename, mode)

    @classmethod
    def _get_memory_file_class(cls) -> Union[Type[StringIO], Type[BytesIO]]:
        """
        Gets the IO class to use for the disk type that the reader class
        supports.

        :return:    Either StringIO or BytesIO.
        """
        return cls._map_disk_type(StringIO, BytesIO)

    @classmethod
    def _get_open_func(cls, filename: str, mode: str) -> Tuple[OpenFunc, str]:
        """
        Gets the open function to use to open the given filename.

        :param filename:    The file to open.
        :param mode:        The base open mode (r/w).
        :return:            The open function, and the read-mode flag to use.
        """
        if filename.endswith('.gz'):
            return gzip.open, cls._map_disk_type('{}t', '{}').format(mode)
        else:
            return open, cls._map_disk_type('{}', '{}b').format(mode)

    @classmethod
    def _map_disk_type(cls, str_, bytes_):
        """
        Returns str_ if DiskType is str and bytes_ if DiskType is bytes.
        Raises an error if it's neither.

        :param str_:    The return value when DiskType is str.
        :param bytes_:  The return type when DiskType is bytes.
        :return:        Either str_ or bytes_.
        """
        if cls._disk_type is str:
            return str_
        elif cls._disk_type is bytes:
            return bytes_
        else:
            raise TypeError(f"DiskType must be str or bytes, not {cls._disk_type}")

    @classmethod
    def _check_file(cls, file: IO[DiskType]):
        """
        Utility method that checks if the file is valid. Raises an error if it's not.

        :param file:  The file.
        """
        if file.closed:
            raise ValueError(f"File is closed")

    def __enter__(self):
        self.ensure_file()
        self._file.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ensure_file()
        return self._file.__exit__(exc_type, exc_val, exc_tb)
