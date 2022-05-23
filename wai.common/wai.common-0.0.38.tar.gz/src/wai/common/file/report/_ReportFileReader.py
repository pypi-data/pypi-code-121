from typing import IO, Dict, Any

import javaproperties

from wai.common.file._FileIOBase import DiskType, ObjectType
from .._FileReader import FileReader
from ._Report import Report
from . import constants
from ._DataType import DataType
from ._Field import Field


class ReportFileReader(FileReader[str, Report, "ReportFileReader"]):
    """
    Reader for report files.
    """
    def _load(self, file: IO[DiskType]) -> ObjectType:
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
