from chtoolset import query as chquery
from collections import defaultdict
from toposort import toposort
from typing import List, Tuple, Any
from tinybird.ch_utils.constants import ENABLED_TABLE_FUNCTIONS

VALID_REMOTE = 'VALID_REMOTE'


class InvalidFunction(ValueError):
    def __init__(self, msg=None, table_function_names=None):
        if table_function_names:
            self.msg = f"The query uses disabled table functions: '{table_function_names}'"
        else:
            self.msg = msg
        super().__init__(self.msg)


class InvalidResource(ValueError):
    def __init__(self, database, table):
        self.msg = f"{database}.{table}" if database else table
        self.msg = f"Resource '{self.msg}' not found"
        super().__init__(self.msg)
        self.database = database
        self.table = table


def format_sql(sql: str) -> str:
    return chquery.format(sql)


def format_where_for_mutation_command(where_clause: str) -> str:
    """
    >>> format_where_for_mutation_command("numnights = 99")
    'DELETE WHERE numnights = 99'
    >>> format_where_for_mutation_command("\\nnumnights = 99")
    'DELETE WHERE numnights = 99'
    >>> format_where_for_mutation_command("reservationid = 'foo'")
    "DELETE WHERE reservationid = \\\\'foo\\\\'"
    >>> format_where_for_mutation_command("reservationid = '''foo'")
    "DELETE WHERE reservationid = \\\\'\\\\\\\\\\\\'foo\\\\'"
    >>> format_where_for_mutation_command("reservationid = '\\\\'foo'")
    "DELETE WHERE reservationid = \\\\'\\\\\\\\\\\\'foo\\\\'"
    """
    formatted_condition = chquery.format(f"""SELECT {where_clause}""").split('SELECT ')[1]
    formatted_condition = formatted_condition.replace("\\", "\\\\").replace("'", "''")
    quoted_condition = chquery.format(f"SELECT '{formatted_condition}'").split('SELECT ')[1]
    return f"DELETE WHERE {quoted_condition[1:-1]}"


def sql_get_used_tables(sql: str, raising: bool = False, default_database: str = '',
                        table_functions: bool = True) -> List[Any]:
    """
    >>> sql_get_used_tables("SELECT 1 FROM the_table")
    [('', 'the_table', '')]
    >>> sql_get_used_tables("SELECT 1 FROM the_database.the_table")
    [('the_database', 'the_table', '')]
    >>> sql_get_used_tables("SELECT * from numbers(100)")
    [('', '', 'numbers')]
    >>> sql_get_used_tables("SELECT * FROM table1, table2")
    [('', 'table1', ''), ('', 'table2', '')]
    """
    try:
        tables: List[Tuple[str, str, str]] = chquery.tables(sql, default_database=default_database)
        if not table_functions:
            return [(t[0], t[1]) for t in tables if t[0] or t[1]]
        return tables
    except ValueError as e:
        if raising:
            msg = str(e)
            if msg.endswith('is restricted'):
                raise InvalidFunction(msg=msg) from e
            raise
        return [(default_database, sql, '')]


class ReplacementsDict(dict):
    def __getitem__(self, key):
        v = super().__getitem__(key)
        if isinstance(v, tuple):
            k, r = v
            if callable(r):
                r = r()
                super().__setitem__(key, (k, r))
            return k, r
        if callable(v):
            v = v()
            super().__setitem__(key, v)
        return v


def tables_or_sql(replacement: dict, table_functions=False) -> set:
    try:
        return set(sql_get_used_tables(replacement[1], default_database=replacement[0],
                                       raising=True, table_functions=table_functions))
    except Exception as e:
        if replacement[1][0] == '(':
            raise e
        return {replacement}


def _separate_as_tuple_if_contains_database_and_table(definition: str) -> Any:
    if "." in definition:
        database_and_table_separated = definition.split(".")
        return database_and_table_separated[0], database_and_table_separated[1]
    return definition


def replacements_to_tuples(replacements: dict) -> dict:
    parsed_replacements = {}
    for k, v in replacements.items():
        parsed_replacements[_separate_as_tuple_if_contains_database_and_table(k)] \
            = _separate_as_tuple_if_contains_database_and_table(v)
    return parsed_replacements


def replace_tables(sql: str, replacements: dict, default_database: str = '', check_functions: bool = False, only_replacements: bool = False) -> str:
    """Given a query and a list of table replacements, returns the query after applying the table replacements.
    It takes into account dependencies between replacement subqueries (if any)
    It also replaces any sleep/sleepEachRow call with a call to sleep(0)/sleepEachRow(0)
    """
    if not replacements:
        # Always call replace_tables so it applies other transformations too (remove sleeps and format the query)
        return chquery.replace_tables(sql, {})

    _replaced_with = set()
    _replacements = ReplacementsDict()
    for k, r in replacements.items():
        rk = k if isinstance(k, tuple) else (default_database, k)
        _replacements[rk] = r if isinstance(r, tuple) else (default_database, r)
        _replaced_with.add(r)

    deps: defaultdict = defaultdict(set)
    _tables = sql_get_used_tables(sql, default_database=default_database, raising=True, table_functions=check_functions)
    seen_tables = set()
    while _tables:
        table = _tables.pop()
        if len(table) == 3:
            if table[2] and table[2] not in ENABLED_TABLE_FUNCTIONS:
                raise InvalidFunction(table_function_names=table[2])
            if table[0] and table[1]:
                table = (table[0], table[1])
            else:
                continue
        seen_tables.add(table)
        if table in _replacements:
            replacement = _replacements[table]
            dependent_tables = tables_or_sql(replacement, table_functions=check_functions)
            deps[table] |= {(d[0], d[1]) for d in dependent_tables}
            for dependent_table in list(dependent_tables):
                if len(dependent_table) == 3:
                    if dependent_table[2] and dependent_table[2] not in ENABLED_TABLE_FUNCTIONS and not(dependent_table[2] in ['remote', 'cluster'] and replacement[0] == VALID_REMOTE):
                        raise InvalidFunction(table_function_names=dependent_table[2])
                    if dependent_table[0] and dependent_table[1]:
                        dependent_table = (dependent_table[0], dependent_table[1])
                    else:
                        continue
                if dependent_table not in seen_tables:
                    _tables.append(dependent_table)
        else:
            deps[table] |= set()
    deps_sorted = list(reversed(list(toposort(deps))))

    if not deps_sorted:
        return chquery.replace_tables(sql, {})

    for current_deps in deps_sorted:
        current_replacements = {}
        for r in current_deps:
            if r in _replacements:
                replacement = _replacements[r]
                current_replacements[r] = replacement
            else:
                if only_replacements:
                    continue
                database, table_name = r
                if (table_name and default_database != '' and database not in [default_database, 'tinybird', VALID_REMOTE] and r not in _replaced_with):
                    raise InvalidResource(database, table_name)

        if current_replacements:
            sql = chquery.replace_tables(sql, current_replacements, default_database=default_database)
        else:
            sql = chquery.replace_tables(sql, {})

    return sql
