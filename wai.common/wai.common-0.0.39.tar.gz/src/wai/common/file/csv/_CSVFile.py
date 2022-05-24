import io
from typing import List, Optional, Union, Type

import csv

# The type of the header section
HEADER_TYPE = List[str]

# The type of the column types
TYPES_TYPE = List[Union[Type[int], Type[float], Type[str]]]

# The type of the data section
VALUE_TYPE = Union[int, float, str]
ROW_TYPE = List[VALUE_TYPE]
DATA_TYPE = List[ROW_TYPE]


class CSVFile:
    """
    Class representing a CSV file loaded into memory.
    """
    def __init__(self,
                 header: Optional[HEADER_TYPE] = None,
                 types: Optional[TYPES_TYPE] = None,
                 data: Optional[DATA_TYPE] = None,
                 dialect: Optional[csv.Dialect] = None):
        # Create an empty dataset if no data is given
        if data is None:
            data = []

        # If no types are given, assume all are string
        if types is None:
            types = [str] * len(data[0]) if len(data) > 0 else []

        self.header: Optional[HEADER_TYPE] = header
        self.types: TYPES_TYPE = types
        self.data: DATA_TYPE = data
        self.dialect: Optional[csv.Dialect] = dialect

    def get_column(self, column_index):
        """
        Gets a column of data.

        :param column_index:    The column to copy.
        :return:                The column of data (as a list).
        """
        return [row[column_index] for row in self.data]

    def __str__(self) -> str:
        # Create a string buffer
        buffer: io.StringIO = io.StringIO()

        # Create a CSV writer to write to it
        writer: csv.writer = csv.writer(buffer, self.dialect)

        # Write the header
        writer.writerow(self.header)

        # Write the data rows
        for row in self.data:
            writer.writerow(row)

        # Return the buffered string
        buffer.seek(0)
        return buffer.read()
