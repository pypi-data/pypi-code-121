from typing import List, Tuple, Optional, Dict

from .._functions import get_open_func
from ._Field import Field, DATATYPE_UNKNOWN, DATATYPE_NUMERIC
from ._Report import Report, FIELD_PARENT_ID
from ._Spectrum import Spectrum
from ._SpectrumPoint import SpectrumPoint

# The file extension for spectra files
FILE_EXTENSION = '.spec'

# Symbol for comments in the file
COMMENT_SYMBOL = '#'

# Separator between name and value of field
NAME_VALUE_SEPARATOR = '='

# Suffix for datatype field lines
DATATYPE_SUFFIX = '\tDataType'

# The separator for multiple spectra in a single file
SEPARATOR = '---'

# The header of the data section
DATA_HEADER = 'waveno,amplitude'


def read_all(filename: str, encoding: str = 'utf-8') -> List[Spectrum]:
    """
    Reads all spectra from the given file.

    :param filename:    The name of the file to read.
    :param encoding:    The encoding of the file (defaults to UTF-8).
    :return:            The spectra read from the file.
    """
    return [spectrum for spectrum in reader(filename, encoding)]


def reader(filename: str, encoding: str = 'utf-8') -> Spectrum:
    """
    Creates a generator that reads a .spec or .spec.gz file into memory.
    Each iteration of the generator returns a single spectrum from the file.

    :param filename:    The name of the file to read.
    :param encoding:    The encoding of the file (defaults to UTF-8).
    :return:            The spectrum generator.
    """

    # Make sure they've provided the correct file-type
    if not filename.endswith(FILE_EXTENSION) and not filename.endswith(FILE_EXTENSION + '.gz'):
        raise ValueError('Unknown file type for: ' + filename)

    # Get the correct file reader for the file type
    open_func, mode = get_open_func(filename)

    # Read the file
    with open_func(filename, mode, encoding=encoding) as file:
        # Keep reading spectra until we run out
        while True:
            # Read the next spectrum from the file
            sample_data = read_report(file)
            points, more = read_points(file)

            # Format and return the next spectrum
            spectrum = Spectrum()
            if sample_data is not None:
                spectrum.id = sample_data.get_id()
                spectrum.database_id = sample_data.get_parameter(FIELD_PARENT_ID)
            spectrum.report = sample_data
            spectrum.points = points
            yield spectrum

            # Finish once all spectra are read from the file
            if not more:
                return


def read_report(file) -> Optional[Report]:
    """
    Reads the report meta-data section of the file.

    :param file:    The file being read from.
    :return:        The report section of the file.
    """

    # Use a peeker so we don't read beyond the end of the header section
    peeker = line_peeker(file)

    # Read each line as a property
    properties = {}
    while True:
        line = next(peeker)

        # Finish when we reach a non-report line
        if not is_report_line(line):
            break

        # Skip comment lines
        if is_comment_line(line):
            continue

        # Extract the property name and value from the line
        name, value = split_field_line(line)
        properties[name] = value

    # Return the report (if there was one)
    if len(properties) == 0:
        return None
    else:
        return properties_to_report(properties)


def is_report_line(line: str) -> bool:
    """
    Checks if the given line is a line from the report section.

    :param line:    The line to check.
    :return:        True if it's a report line, False if not.
    """
    return line.startswith(COMMENT_SYMBOL)


def is_comment_line(line: str) -> bool:
    """
    Checks if the given line is a comment.

    :param line:    The line to check.
    :return:        True if the line is a comment,
                    False if not.
    """
    return line[1:].lstrip().startswith(COMMENT_SYMBOL)


def properties_to_report(properties: Dict[str, str]) -> Report:
    """
    Composes the properties read from the file into a report.

    :param properties:  The properties read from the file.
    :return:            The report.
    """
    report = Report()

    for name in properties:
        # Datatype properties are only additional to other properties
        if is_datatype_name(name):
            continue

        # Get the expected name of the datatype property
        datatype_name = name + DATATYPE_SUFFIX

        # Determine the datatype of the property
        if datatype_name in properties:
            datatype = properties[datatype_name]
        elif name == FIELD_PARENT_ID:
            datatype = DATATYPE_NUMERIC
        else:
            datatype = DATATYPE_UNKNOWN

        # Determine the value of the property
        value = properties[name]

        # Add the property as a field to the report
        report.add_field(Field(name, datatype))
        report.add_parameter(name, value)

    return report


def is_datatype_name(name: str) -> bool:
    """
    Checks if the given name is the name of a datatype property.

    :param name:    The name to check.
    :return:        True if the name is a datatype property name,
                    False if not.
    """
    return name.endswith(DATATYPE_SUFFIX)


def split_field_line(line: str) -> Tuple[str, str]:
    """
    Splits a header line into a name/value pair.

    :param line:    The line to split.
    :return:        The name/value pair as a tuple.
    """

    # Remove the leading comment symbol and space,
    # and split around the = character
    parts = line[2:].split(NAME_VALUE_SEPARATOR, 1)

    # Return the name/value pair
    name = fix_string(parts[0])
    value = fix_string(parts[1])
    return name, value


def fix_string(string: str) -> str:
    """
    Fixes the escape formatting of the given string.

    :param string:  The string to fix.
    :return:        The fixed string
    """
    string = string.replace('\\t', '\t')
    string = string.replace('\\', '')
    return string


def read_points(file) -> Tuple[List[SpectrumPoint], bool]:
    """
    Reads the data points section of the file.

    :param file:    The file to read from.
    :return:        The list of points read, and if there is more file to read.
    """
    points = []
    more = False

    # Ignore the header
    line = file.readline()[:-1]
    if line != DATA_HEADER:
        raise ValueError('Missing data header')

    while True:
        line = file.readline()[:-1]

        if line == '':
            break
        elif line == SEPARATOR:
            more = True
            break

        split = line.split(',')

        wave_number = float(split[0])
        amplitude = float(split[1])

        points.append(SpectrumPoint(wave_number, amplitude))

    return points, more


def line_peeker(file) -> str:
    """
    Creates a generator that reads lines from the file,
    but leaves the read position at the beginning of the
    last line read.

    :param file:    The file to read from.
    :return:        The line generator.
    """
    while True:
        pre = file.tell()
        line = file.readline()[:-1]
        post = file.tell()

        file.seek(pre)

        yield line

        file.seek(post)
