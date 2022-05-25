from __future__ import annotations

from typing import List, Union, Set, Dict

from bigeye_sdk.generated.com.torodata.models.generated import Table, TableColumn
from bigeye_sdk.log import get_logger
from fuzzywuzzy import process

log = get_logger(__file__)


def table_has_column(table: Table, column_name: str) -> bool:
    """
    Returns True if table contains column_name (case insensitive)
    :param table: Table object
    :param column_name: column name
    :return: boolean
    """
    for c in table.columns:
        if c.name.lower() == column_name.lower():
            return True

    return False


def get_matching_table_columns(table: Table, column_names: List[str]) -> List[TableColumn]:
    """

    :param table: a Table object.
    :param column_names: ordered priority first list of string column names
    :return: Dict of TableColumns matching and ordered by column_names as ix.  {ix: TableColumn}
    """
    tcd = {c.name.lower(): c for c in table.columns}
    return [tcd[cn.lower()] for cn in column_names
            if cn.lower() in tcd]


def get_table_column_priority_first(table: Table, column_names: List[str]) -> Union[TableColumn, None]:
    tcs = get_matching_table_columns(table, column_names)
    if tcs:
        return tcs[0]
    else:
        return None


def table_contains_any_column(table: Table, column_names: List[str]) -> bool:
    return any(get_matching_table_columns(table, column_names))


def get_table_column_id(table: Table, column_name: str) -> Union[int, None]:
    """
    Returns the column id if table contains the column_name (case insensitive)
    :param table: Table object
    :param column_name: column name
    :return: column id
    """
    for c in table.columns:
        if c.name.lower() == column_name.lower():
            return c.id

    return None


def get_table_column_names(table: Table) -> List[str]:
    return [c.name for c in table.columns]


def transform_table_list_to_dict(tables: List[dict]) -> dict:
    return {t['datasetName'].lower(): _transform_table_field_list_to_dict(t) for t in tables}


def _transform_table_field_list_to_dict(table: dict) -> dict:
    """
    Converts the table['fields'] list to a dictionary of { <tableName.lower>: <field_entry> } for quick, easy,
    case-insensitive keying
    :param table: a dictionary representing a dataset in Bigeye derived from the dataset/tables endpoint.
    :return: the modified table entry
    """
    table['fields'] = {f['fieldName'].lower(): f for f in table['fields']}
    return table


def create_table_name_pairs(table1: List[str], table2: List[str]):
    return list(zip(table1, [process.extract(t, table2, limit=1)[0][0] for t in table1]))


def table_has_metric_time(table: Table) -> bool:
    """
    Logic to determine whether a particular table has a metric time.
    :param table: Table object
    :return: Boolean
    """
    if table.metric_time_column.id != 0:
        return True
    else:
        return False
