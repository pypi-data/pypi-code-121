import logging
from enum import Enum
from .langs.mysql import definition as mysql
from .models import *
from .docs import plantuml as erd


class Language(Enum):
    MYSQL = 'mysql'


PARSERS = {
    Language.MYSQL: mysql
}


def clean(ddl):
    return ddl.replace('`', '')


def table(result):
    """
    :param result: pyparse parseString result
    :return: paddl.Schema
    """
    columns = []
    nts = []
    cont = 0
    for x in range(len(result['columns'])):
        if cont:
            cont -= 1
            continue
        part = result['columns'][x]

        if part == '(':
            columns[-1].size = result['columns'][x+1]
            cont = 2
        else:
            nts.append(part)
        if len(nts) == 2:
            columns.append(Column(*nts))
            nts = []

    return Table(name=result['table_name'],
                 columns=columns)


def parse(ddl, engine=Language.MYSQL, strict=False):
    """
    parse SQL DDLs and return Schema objects

    :param ddl: string
    :param engine: db engine, defaults to mysql
    :param strict: should parse strictly or fail
    :return:
    """
    engine = Language(engine)
    ddl = clean(ddl)
    schema = Schema()
    results = PARSERS[engine].parseString(ddl, parseAll=strict)
    logging.debug(results)

    schema.tables = [table(result) for result in results]
    return schema
