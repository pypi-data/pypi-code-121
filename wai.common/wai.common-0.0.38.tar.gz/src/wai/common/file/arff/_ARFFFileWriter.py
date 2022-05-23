from typing import IO

from .._FileWriter import FileWriter
from ._ARFFFile import ARFFFile


class ARFFFileWriter(FileWriter[str, ARFFFile, "ARFFFileWriter"]):
    """
    File writer for ARFF files.
    """
    def _dump(self, obj: ARFFFile, file: IO[str]):
        file.write(str(obj))
