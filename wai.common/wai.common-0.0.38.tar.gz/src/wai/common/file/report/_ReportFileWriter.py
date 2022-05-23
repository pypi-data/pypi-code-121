from typing import IO

import javaproperties

from .._FileWriter import FileWriter
from ._Report import Report
from . import constants


class ReportFileWriter(FileWriter[str, Report, "ReportFileWriter"]):
    """
    Writer for report files.
    """
    def _dump(self, obj: Report, file: IO[str]):
        # Create a Java properties dictionary
        properties = {constants.PROPERTY_PARENTID: str(obj.database_id)}

        # Add the fields and their types as properties
        for field in obj:
            name = str(field)
            properties[name] = str(obj.get_value(field))
            properties[name + constants.DATATYPE_SUFFIX] = field.datatype.to_display()

        print(javaproperties.to_comment(javaproperties.java_timestamp()), file=file)
        print(javaproperties.to_comment("Simple report format (= Java properties file format)"), file=file)
        javaproperties.dump(properties, file, timestamp=False, sort_keys=True)
