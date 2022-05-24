import io
import os
from multiprocessing.pool import Pool
from typing import List, Any, IO, Callable

from ._error import ARFFError
from .._functions import get_open_func
from ._Attribute import Attribute
from ._ARFFFile import ARFFFile, DATA_TYPE, ROW_TYPE
from . import constants
from ._load_helper import read_till_found, line_starts_with, is_comment_line, is_whitespace_only, remove_keyword, \
    consume, NAME_PATTERN, UnrecognisedContentError, remove_quotes, QUOTES

# The number of rows to process as a batch in parallel mode
PARALLEL_BATCH_SIZE = 64


def loadf(filename: str,
          encoding: str = 'utf-8',
          parallel: bool = True,
          use_csv: bool = True) -> ARFFFile:
    """
    Reads an ARFF file from the file given by name.

    :param filename:    The name of the file to read.
    :param encoding:    The encoding of the file.
    :param parallel:    Whether to process the data section using multiprocessing.
    :param use_csv:     Whether to process the data section using the csv package.
    :return:            The loaded ARFF file.
    """
    # Select the open method based on the filename
    open_func, mode = get_open_func(filename)

    # Parse the file
    with open_func(filename, mode, encoding=encoding) as file:
        return load(file, parallel, use_csv)


def loads(string: str,
          parallel: bool = True,
          use_csv: bool = True) -> ARFFFile:
    """
    Reads an ARFF file from the given string in ARFF file format.

    :param string:      Text in ARFF file format.
    :param parallel:    Whether to process the data section using multiprocessing.
    :param use_csv:     Whether to process the data section using the csv package.
    :return:            The loaded ARFF file.
    """
    return load(io.StringIO(string), parallel, use_csv)


def load(file: IO[str],
         parallel: bool = True,
         use_csv: bool = True) -> ARFFFile:
    """
    Reads an ARFF file from the given file-like handle.

    :param file:        Any stream of text in ARFF file format.
    :param parallel:    Whether to process the data section using multiprocessing.
    :param use_csv:     Whether to process the data section using the csv package.
    :return:            The loaded ARFF file.
    """
    # Get the relation and attributes
    relation = get_relation_section(file)
    attributes = get_attribute_section(file)

    # Select the data-reading method (serial or parallel, csv or not)
    data_section_method: Callable[[IO[str], List[Attribute]], DATA_TYPE] = \
        get_data_section_parallel_csv if parallel and use_csv else \
        get_data_section_parallel if parallel else \
        get_data_section_csv if use_csv else \
        get_data_section

    # Get the data
    data = data_section_method(file, attributes)

    # Return the ARFF file
    return ARFFFile(relation, attributes, data)


def get_relation_section(file: IO[str]) -> str:
    """
    Gets the relation name from the ARFF file.

    :param file:    The file we are processing.
    :return:        The relation name.
    """
    # Get the line starting with the @relation keyword
    line = read_till_found(file, {constants.RELATION_SECTION_KEYWORD})

    # Parse the line
    relation = parse_relation_line(line)

    # Return the header
    return relation


def get_attribute_section(file: IO[str]) -> List[Attribute]:
    """
    Gets the list of attributes in the ARFF file.

    :param file:            The ARFF file being processed.
    :return:                The list of attributes in the file.
    """
    # Create the empty list of attributes
    attributes: List[Attribute] = []

    # Process attribute and stop on data keywords
    stopwords = {constants.ATTRIBUTE_SECTION_KEYWORD, constants.DATA_SECTION_KEYWORD}

    # Keep reading attributes until we find the @data keyword
    line = read_till_found(file, stopwords)
    while not line_starts_with(line, constants.DATA_SECTION_KEYWORD):
        # Parse the @attribute line
        attribute: Attribute = Attribute.from_string(line)

        # Add it to the list
        attributes.append(attribute)

        # Read the next attribute or data line
        line = read_till_found(file, stopwords)

    # Return the attributes
    return attributes


def get_data_section(file: IO[str], attributes: List[Attribute]) -> List[List[Any]]:
    """
    Gets the data from the data section of the ARFF file.

    :param file:        The ARFF file we are processing.
    :param attributes:  The attributes of the ARFF file.
    :return:            The list of data rows.
    """
    # Create the empty data list
    data = []

    # Keep reading lines until we run out of file
    line = None
    while line != '':
        # Read the next line
        line = file.readline()

        # If it was just whitespace/comments, skip it
        if is_whitespace_only(line) or is_comment_line(line):
            continue

        # Parse the data row
        row = parse_data_row_line(line, attributes)

        # Append the row to the data
        data.append(row)

    # Return the data
    return data


def get_data_section_parallel(file: IO[str], attributes: List[Attribute]) -> DATA_TYPE:
    """
    Gets the data from the data section of the ARFF file.

    :param file:        The ARFF file we are processing.
    :param attributes:  The attributes of the ARFF file.
    :return:            The list of data rows.
    """
    # Keep reading lines until we run out of file
    lines = [line for line in file if not (is_whitespace_only(line) or is_comment_line(line))]

    # Parse the lines in parallel
    with Pool(initializer=pool_initialiser_parallel, initargs=(attributes,)) as pool:
        return pool.map(parse_data_row_line_parallel, lines, PARALLEL_BATCH_SIZE)


def get_data_section_parallel_csv(file: IO[str], attributes: List[Attribute]) -> DATA_TYPE:
    """
    Gets the data from the data section of the ARFF file.
    Operates in a parallel manner and uses csv to split
    the lines of the file.

    :param file:        The ARFF file we are processing.
    :param attributes:  The attributes of the ARFF file.
    :return:            The list of data rows.
    """
    # Keep reading lines until we run out of file
    lines = [line for line in file if not (is_whitespace_only(line) or is_comment_line(line))]

    # Get the number of sub-processes we can employ
    pool_size: int = os.cpu_count()

    # Calculate the number of lines each sub-process should handle
    work_unit_size = len(lines) // pool_size

    # Divide the lines into the unit of work for each sub-process
    work_units: List[List[str]] = [lines[i * work_unit_size: (i+1) * work_unit_size] for i in range(pool_size - 1)]
    work_units.append(lines[(pool_size - 1) * work_unit_size:])

    # Process the lines in parallel
    import itertools
    with Pool(processes=pool_size, initializer=pool_initialiser_parallel, initargs=(attributes,)) as pool:
        return [row for row in itertools.chain(*pool.imap(parse_data_rows_csv_parallel, work_units))]


def get_data_section_csv(file: IO[str], attributes: List[Attribute]) -> DATA_TYPE:
    """
    Gets the data from the data section of the ARFF file.
    Uses csv to split the data lines.

    :param file:        The ARFF file we are processing.
    :param attributes:  The attributes of the ARFF file.
    :return:            The list of data rows.
    """
    # Keep reading lines until we run out of file
    lines = [line for line in file if not (is_whitespace_only(line) or is_comment_line(line))]

    # Parse the lines with csv and return the data
    return parse_data_rows_csv(lines, attributes)


def parse_data_rows_csv(lines: List[str], attributes: List[Attribute]) -> DATA_TYPE:
    """
    Parses a list of lines from the data section using csv.

    :param lines:           The lines to parse.
    :param attributes:      The attributes of the ARFF file.
    :return:                The parsed data.
    """
    # Create a CSV reader to split the lines
    import csv
    csv_reader = csv.reader(lines, doublequote=False, escapechar='\\', skipinitialspace=True, strict=True)

    # Calculate the number of elements that should be in each row
    num_attributes = len(attributes)

    # Initialise the output data to the correct size
    output = [[None] * num_attributes for _ in range(len(lines))]

    # Process each row
    for j, row in enumerate(csv_reader):
        # Make sure the line wasn't too long or too short
        if len(row) != num_attributes:
            raise DataSizeMismatchError(num_attributes, lines[j])

        # Convert each value
        for i in range(num_attributes):
            # Add the value to the row
            output[j][i] = attributes[i].parse_string(row[i])

    return output


def pool_initialiser_parallel(attributes: List[Attribute]):
    """
    Pool initialisation method for when using parallel data reading.

    :param attributes:  The attributes of the ARFF file.
    :return:            Nothing.
    """
    # Make the attributes global so parse_data_row_line_parallel can access them.
    global attributes_global
    attributes_global = attributes


def parse_data_row_line_parallel(line: str) -> ROW_TYPE:
    """
    Parallel implementation of parse_data_row_line.

    :param line:        The line of data to parse.
    :return:            A list of data values.
    """
    # Defers to normal implementation by accessing attributes from global
    return parse_data_row_line(line, attributes_global)


def parse_data_rows_csv_parallel(lines: List[str]) -> DATA_TYPE:
    """
    Parallel implementation of parse_data_rows_csv.

    :param lines:       The lines of data to parse.
    :return:            A list of data values.
    """
    # Defers to normal implementation by accessing attributes from global
    return parse_data_rows_csv(lines, attributes_global)


def parse_relation_line(line: str) -> str:
    """
    Gets the name of the relation from the line of the ARFF file
    beginning with the @relation keyword.

    :param line:    The line beginning with the @relation keyword.
    :return:        The name of the relation.
    """
    # Save the original line for error messages
    original_line = line

    # Remove the keyword and any following whitespace
    line = remove_keyword(line, constants.RELATION_SECTION_KEYWORD).lstrip()

    # Extract the relation name
    relation, line = consume(line, NAME_PATTERN)

    # Make sure we got a name back
    if relation is None:
        raise RelationNameNotFoundError(original_line)

    # Make sure the entire line has been consumed
    if not is_whitespace_only(line):
        raise UnrecognisedContentError(line, original_line)

    # Return the relation name
    return remove_quotes(relation)


def parse_data_row_line(line: str, attributes: List[Attribute]) -> ROW_TYPE:
    """
    Parses a line of data from the @data section of the ARFF file.

    :param line:            The line of data to parse.
    :param attributes:      The attributes of the ARFF file.
    :return:                A list of data values.
    """
    # Save the original line for error messages
    original_line = line

    # Get the number of expected values
    num_attributes = len(attributes)

    # Create the data row with all missing values
    row = [None] * num_attributes

    # Keep extracting values until we have enough
    i = 0
    j = 0
    line_length = len(line)
    while i < num_attributes:
        # Make sure there is string left to consume
        if j == line_length:
            break

        # Advance through any leading spaces
        while line[j] == ' ':
            j += 1

        # Advance through any quoted section
        if line[j] in QUOTES:
            # Advance till the next matching quote
            quote = line[j]
            j += 1
            start = j
            while line[j] != quote:
                j += 1
            end = j
            j += 2
        else:
            # Advance to the next delimiter
            start = j
            while line[j] not in {'\t', ',', '\n'}:
                j += 1
            end = j
            j += 1

        value = line[start:end]

        # Convert the value and add it to the output row
        row[i] = attributes[i].parse_string(value)

        # Increment the index
        i += 1

    # Make sure the line wasn't too long or too short
    if j != line_length or i != num_attributes:
        raise DataSizeMismatchError(num_attributes, original_line)

    return row


def parse_date_format(string: str) -> str:
    """
    Parses the date-format string for date-type attributes.
    TODO: Implement. csterling

    :param string:      The date-format string to parse.
    :return:            Currently, just the input.
    """
    return string


class RelationNameNotFoundError(ARFFError):
    """
    Exception for when the name of the relation cannot be found.
    """
    def __init__(self, line: str):
        super().__init__("Couldn't parse relation name from: " + line)


class DataSizeMismatchError(ARFFError):
    """
    Exception when there are too many or too few values in a given data row.
    """
    def __init__(self, num_attributes: int, line: str):
        super().__init__("Wrong number of values (require " + str(num_attributes) + ") in: " + line)
