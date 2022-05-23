import csv
from typing import IO, Optional, Tuple, List, Type, Union

from .._FileReader import FileReader
from ._CSVFile import CSVFile, DATA_TYPE, VALUE_TYPE, TYPES_TYPE

# Number of lines to sample to try and determine CSV format
SAMPLE_SIZE = 4


class CSVFileReader(FileReader[str, CSVFile, "CSVFileReader"]):
    """
    Reader for CSV files.
    """
    def __init__(self, has_header: Optional[bool] = None, **fmtparams):
        super().__init__()

        self.has_header: Optional[bool] = has_header
        self.fmtparams = fmtparams

    def _load(self, file: IO[str]) -> CSVFile:
        # Sniff the possible dialect
        dialect, has_header = sniff_dialect(file, self.has_header)

        # Get the reader
        reader = csv.reader(file, dialect, **self.fmtparams)

        # Read in all the data
        data = [row for row in reader]

        # Take the header from the data if there is one
        if has_header:
            header = data.pop(0)
        else:
            header = None

        # Get the column types
        types = estimate_types(data[:SAMPLE_SIZE])

        # Convert the data to the given types
        convert_columns(data, types)

        # Create and return the CSV file object
        return CSVFile(header, types, data, dialect)


def sniff_dialect(file: IO[str], has_header: Optional[bool]) -> Tuple[csv.Dialect, bool]:
    """
    Uses the csv Sniffer class to try and auto-detect the dialect of
    the CSV file. Also determines if the file has a header row.

    :param file:        The CSV file to sniff.
    :param has_header:  Whether the file has a header, or None to auto-detect.
    :return:            The detected dialect of the file, and whether it has a header.
    """
    # Peek a small sample of lines from the file
    sample = ''.join([file.readline() for _ in range(SAMPLE_SIZE)])
    file.seek(0)

    # Create the sniffer
    sniffer: csv.Sniffer = csv.Sniffer()

    # Sniff the dialect
    dialect: csv.Dialect = sniffer.sniff(sample)

    # Sniff the header if it isn't already determined
    if has_header is None:
        has_header = sniffer.has_header(sample)

    return dialect, has_header


def estimate_types(sample: DATA_TYPE) -> List[Type[VALUE_TYPE]]:
    """
    Attempts to guess which columns of the provided sample contain numeric data.

    :param sample:          A sample of the data from the CSV file.
    :return:                A list of indices of columns which are thought to contain numeric data.
    """
    # Initialise the list
    types = []

    # Test each column in turn
    for column_index in range(len(sample[0])):
        # Assume the column is integers
        column_type = int

        # Test the value in each row of this column
        for row_index in range(len(sample)):
            # Get the value
            value = sample[row_index][column_index]

            # Test if it converts to an int
            try:
                int(value)
            except Exception:
                # If not, test float
                column_type = float
                try:
                    float(value)
                except Exception:
                    # If not, leave as string
                    column_type = str

        # If all values converted, assume it is a numeric column
        types.append(column_type)

    return types


def convert_columns(data: DATA_TYPE, types: TYPES_TYPE):
    """
    Converts the values in each of the specified columns into the given types.

    :param data:                The data from the CSV file.
    :param types:               The types to convert the data to.
    :return:                    Nothing, the data is converted in place.
    """
    # Convert each row in turn
    for row in data:
        # Convert only those columns that are marked numeric
        for column_index in range(len(row)):
            # Convert the value in place
            row[column_index] = types[column_index](row[column_index])
