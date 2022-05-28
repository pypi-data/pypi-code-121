import re
from pathlib import (
    PurePath,
)

from m3_gar.importer.table.exceptions import (
    BadTableError,
)
from m3_gar.importer.table.xml import (
    XMLTable,
)


table_xml_re = re.compile(
    r'as_(?P<name>[a-z_]+)_(?P<date>\d{8})_(?P<uuid>[a-z0-9-]{36}).xml',
    re.I,
)


class TableFactory:

    @staticmethod
    def parse(filename):
        path_obj = PurePath(filename)
        basename = path_obj.name

        if path_obj.parent == PurePath():
            region = None
        else:
            region = int(path_obj.parent.name)

        m = table_xml_re.match(basename)
        if m is not None:
            return XMLTable(filename=filename, region=region, **m.groupdict())

        return None
