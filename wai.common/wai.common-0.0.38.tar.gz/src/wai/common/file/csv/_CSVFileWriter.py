from typing import IO

from .._FileWriter import FileWriter
from ._CSVFile import CSVFile


class CSVFileWriter(FileWriter[str, CSVFile, "CSVFileWriter"]):
    """
    Writer for CSV files.
    """
    def _dump(self, obj: CSVFile, file: IO[str]):
        file.write(str(obj))
