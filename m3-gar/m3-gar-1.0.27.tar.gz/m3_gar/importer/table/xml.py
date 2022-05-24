from datetime import (
    date,
)

from django.db import (
    models,
)
from django.db.models import (
    UUIDField,
)
from lxml import (
    etree,
)

from m3_gar.importer.table import (
    BadTableError,
)
from m3_gar.importer.table.table import (
    Table,
    TableIterator,
)


class XMLIterator(TableIterator):

    def __init__(self, table, fd):
        super().__init__(table)
        self._fd = fd
        self._context = etree.iterparse(self._fd)

    def format_row(self, row):
        for key, value in row.items():
            key = key.lower()
            field = self.model._meta.get_field(key)

            if isinstance(field, UUIDField):
                value = value or None
            elif isinstance(field, models.DateField):
                value = date.fromisoformat(value) if value else None
            elif field.one_to_one or field.many_to_one:
                key = field.get_attname()
                if isinstance(field.target_field, models.IntegerField):
                    value = int(value) if value else None
                if field.null and (not value or value == '0'):
                    value = None
            elif isinstance(field, models.BooleanField):
                value = value in ['1', 'true', True]
            elif isinstance(field, models.IntegerField):
                value = int(value) if value else None
            else:
                value = value.strip().replace('\n', '').replace('\r', '')

            yield key, value

    def get_next(self):
        event, row = next(self._context)

        if row.getparent() is None:
            raise StopIteration

        item = self.process_row(row)
        row.clear()
        while row.getprevious() is not None:
            del row.getparent()[0]

        return item


class XMLTable(Table):
    iterator = XMLIterator

    def rows(self, tablelist):
        xml = self.open(tablelist=tablelist)

        try:
            return self.iterator(self, xml)
        except etree.XMLSyntaxError as e:
            raise BadTableError(
                f'Error occured during opening table `{self.name}`: {e}'
            )
