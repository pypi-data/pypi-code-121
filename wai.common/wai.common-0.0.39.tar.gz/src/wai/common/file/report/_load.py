import io
from typing import Dict, Any, IO

import javaproperties

from .._functions import get_open_func
from ._Report import Report
from . import constants
from ._DataType import DataType
from ._Field import Field


def loadf(filename: str,
          encoding: str = 'utf-8') -> Report:
    """
    Reads a report file from the file given by name.

    :param filename:    The name of the file to read.
    :param encoding:    The encoding of the file.
    :return:            The loaded report file.
    """
    # Select the open method based on the filename
    open_func, mode = get_open_func(filename)

    # Parse the file
    with open_func(filename, mode, encoding=encoding) as file:
        return load(file)


def loads(string: str) -> Report:
    """
    Loads a report from a string.

    :param string:      Text in report file format.
    :return:            The report.
    """
    return load(io.StringIO(string))


def load(file: IO[str]) -> Report:
    """
    Loads a report file from an IO stream.

    :param file:    The stream to read the report from.
    :return:        The report.
    """
    # Load the report file as a Java properties file
    properties: Dict[str, Any] = javaproperties.load(file)

    # Parse the properties into a report
    return from_properties(properties)


def from_properties(properties: Dict[str, Any]) -> Report:
    """
    Parses the properties and generates a report object from it.

    :param properties:  The properties to generate the report from.
    :return:            The report.
    """
    # Create the result object
    report: Report = Report()

    # Parse the properties
    for property_name, property_value in properties.items():
        # Data-type properties are only used for the type of their corresponding property
        if property_name.endswith(constants.DATATYPE_SUFFIX):
            continue

        # Special handling for the parent ID field
        if property_name == constants.PROPERTY_PARENTID:
            report.database_id = int(property_value)

        # Get the datatype for this property
        datatype_property_name: str = property_name + constants.DATATYPE_SUFFIX
        datatype_property_value: str = DataType.UNKNOWN.value
        if datatype_property_name in properties:
            datatype_property_value = properties[datatype_property_name]
        datatype: DataType = DataType.parse(datatype_property_value)
        if datatype is None:
            datatype = DataType.UNKNOWN

        # Convert and set the value
        report.set_value(Field(property_name, datatype), datatype.convert(property_value))

    return report
