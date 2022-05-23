import javaproperties

from ._Report import Report
from . import constants


def save(report: Report, filename: str, encoding: str = "utf-8"):
    """
    Saves a report to disk.

    :param report:      The report to save.
    :param filename:    The filename to save the report under.
    :param encoding:    The encoding to use.
    """
    # Create a Java properties dictionary
    properties = {constants.PROPERTY_PARENTID: str(report.database_id)}

    # Add the fields and their types as properties
    for field in report:
        name = str(field)
        properties[name] = str(report.get_value(field))
        properties[name + constants.DATATYPE_SUFFIX] = field.datatype.to_display()

    # Write the properties to disk
    with open(filename, 'w', encoding=encoding) as file:
        print(javaproperties.to_comment(javaproperties.java_timestamp()), file=file)
        print(javaproperties.to_comment("Simple report format (= Java properties file format)"), file=file)
        javaproperties.dump(properties, file, timestamp=False, sort_keys=True)
