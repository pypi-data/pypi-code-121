import inspect

from pypadb.table.base_table import BaseTable
from pypadb.utils.inspect_util import camel2snake


class TableConfigurer:
    __slots__ = ['tables']

    tables: dict[str, BaseTable]

    def __init__(self):
        self.tables = {}

    def __getattr__(self, item: str) -> BaseTable:
        return self.tables[item]

    def __getitem__(self, item: str) -> BaseTable:
        return self.tables[item]

    def init_tables(self, module_=None, escape_upper: bool = False, **kwargs):
        if inspect.ismodule(module_):
            module_dict: dict = {}
            module_member = inspect.getmembers(module_)
            magic_all = [i[1] for i in module_member if i[0] == '__all__'][0]
            if magic_all:
                module_member = [i for i in module_member if i[0] in magic_all]
            for i in module_member:
                member_name = camel2snake(i[0])
                module_dict[member_name] = i[1]
            self.tables = {**self.tables, **{key: BaseTable(key, module_dict[key]) for key in module_dict}}
        if kwargs:
            self.tables = {**self.tables, **{key: BaseTable(key, kwargs[key]) for key in kwargs}}


tables: TableConfigurer = TableConfigurer()
