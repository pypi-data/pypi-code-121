from tokyo_lineage.utils.parser.parser import Parser as _Parser

class Parser:
    def __init__(self, sql) -> None:
        self.__parser = _Parser(sql)

    @property
    def tables(self):
        _all_tables = self.__parser.get_tables()
        _tables = _all_tables['tables']
        _ctes = _all_tables['cte']
        
        # Assuming real table name is always in index 0
        _tables = [_table[0] for _table in _tables]
        _ctes = [_cte[0] for _cte in _ctes]

        # Do post-cleaning
        _tables = [self.__clean(_table) for _table in _tables]
        _ctes = [self.__clean(_cte) for _cte in _ctes]

        return [table for table in _tables if table not in _ctes]

    def __clean(self, table):
        steps = [
            lambda _table: _table.replace('`', '')
        ]

        for step in steps:
            table = step(table)

        return table