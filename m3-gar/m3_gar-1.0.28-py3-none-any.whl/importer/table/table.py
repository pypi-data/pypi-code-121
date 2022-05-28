from m3_gar.importer.table.consts import (
    PARAMS_SUFFIX,
)
from m3_gar.importer.table.exceptions import (
    ParentLookupError,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
)
from m3_gar.util import (
    get_model_from_table_name,
    get_table_row_filters,
)


class TableIterator:

    def __init__(self, table):
        self.table = table
        self.model = table.model

    def __iter__(self):
        if self.model is None:
            return []

        return self

    def get_context(self):
        raise NotImplementedError()

    def get_next(self):
        raise NotImplementedError()

    def format_row(self, row):
        raise NotImplementedError()

    def process_row(self, row):
        try:
            row = dict(self.format_row(row))
        except ParentLookupError as e:
            return None

        item = self.model(**row)

        if isinstance(item, RegionCodeModelMixin):
            item.region_code = self.table.region

        table_row_filters = get_table_row_filters()
        for filter_func in table_row_filters.get(self.model._meta.model_name, tuple()):
            item = filter_func(item)

            if item is None:
                break

        return item

    def __next__(self):
        return self.get_next()

    next = __next__


class Table:
    name = None
    iterator = TableIterator

    def __init__(self, *, filename, name, region, **kwargs):
        self.filename = filename
        self.region = region

        self.name = name.lower()
        self.model = get_model_from_table_name(self.name)

    def open(self, tablelist):
        return tablelist.open(self.filename)

    def rows(self, tablelist):
        raise NotImplementedError()
