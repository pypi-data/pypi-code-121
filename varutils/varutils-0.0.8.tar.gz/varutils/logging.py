from io import TextIOBase
from os import PathLike
from typing import TextIO, Union, Sequence

__all__ = (
    'Logger',
)


class Logger(TextIOBase):
    """Logger class that multiplies output across multiple files."""
    __slots__ = ('__fhandlers', '__files_to_close')
    __fhandlers: Sequence[TextIO]
    __files_to_close: Sequence[TextIO]

    def __init__(self, *fhandlers_or_fnames: Union[str, bytes, PathLike, TextIO]) -> None:
        """
        Logger class that multiplies output across multiple files.

        Args:
            *fhandlers_or_fnames:  files or filenames to write output into.
        """
        self.__fhandlers = fhandlers = []
        self.__files_to_close = files_to_close = []
        for f in fhandlers_or_fnames:
            if not isinstance(f, TextIOBase):
                f = open(f, 'w')  # type: ignore
                files_to_close.append(f)
            fhandlers.append(f)

    def __del__(self) -> None:
        for f in self.__files_to_close:
            f.close()

    def write(self, data: str) -> int:
        for f in self.__fhandlers:
            f.write(data)
        return len(data)

    def flush(self) -> None:
        for f in self.__fhandlers:
            f.flush()
