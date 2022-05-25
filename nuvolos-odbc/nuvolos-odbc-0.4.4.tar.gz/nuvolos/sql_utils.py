"""
Utility functions to load Pandas DataFrames to Nuvolos/Snowflake.
"""
import logging
import os
import random
import re
import string
from tempfile import TemporaryDirectory
from typing import TypeVar, Iterator, Tuple, Sequence

import pandas._libs.lib as lib
from pandas.core.api import (
    DataFrame,
    Series,
)
from pyodbc import ProgrammingError, Connection

logger = logging.getLogger(__name__)
RESERVED_WORDS = frozenset(
    [
        "ALL",  # ANSI Reserved words
        "ALTER",
        "AND",
        "ANY",
        "AS",
        "BETWEEN",
        "BY",
        "CHECK",
        "COLUMN",
        "CONNECT",
        "COPY",
        "CREATE",
        "CURRENT",
        "DELETE",
        "DISTINCT",
        "DROP",
        "ELSE",
        "EXISTS",
        "FOR",
        "FROM",
        "GRANT",
        "GROUP",
        "HAVING",
        "IN",
        "INSERT",
        "INTERSECT",
        "INTO",
        "IS",
        "LIKE",
        "NOT",
        "NULL",
        "OF",
        "ON",
        "OR",
        "ORDER",
        "REVOKE",
        "ROW",
        "ROWS",
        "SAMPLE",
        "SELECT",
        "SET",
        "START",
        "TABLE",
        "THEN",
        "TO",
        "TRIGGER",
        "UNION",
        "UNIQUE",
        "UPDATE",
        "VALUES",
        "WHENEVER",
        "WHERE",
        "WITH",
        "REGEXP",
        "RLIKE",
        "SOME",  # Snowflake Reserved words
        "MINUS",
        "INCREMENT",  # Oracle reserved words
    ]
)
UNQUOTED_RE = re.compile(r"""^[a-z_]+[a-z0-9_\$]*$""")


def _quote_name(name):
    """
    Quotes a Snowflake name if required:
     - The name starts with a non-alpha character,
     - The name contains a special character,
     - The name is a reserved name.
    :param name: Name to quote.
    :return: The quoted name, if quoting is required.
    """
    if name.upper() in RESERVED_WORDS:
        return f'"{name}"'
    elif not UNQUOTED_RE.match(name):
        name = name.replace('"', "")
        return f'"{name}"'
    else:
        return name


def _get_col_db_type(col):
    """
    Returns the Snowflake type for the DataFrame column type.
    See https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#basics-dtypes
    Based on https://github.com/pandas-dev/pandas/blob/d01561fb7b9ad337611fa38a3cfb7e8c2faec608/pandas/io/sql.py#L1142:9
    :param col: The Pandas DataFrame column.
    :return: The Snowflake SQL type matching the dtype
    """
    col_type = lib.infer_dtype(col, skipna=True)

    if col_type == "datetime64" or col_type == "datetime":
        # GH 9086: TIMESTAMP is the suggested type if the column contains
        # timezone information
        try:
            if col.dt.tz is not None:
                return "TIMESTAMPT_TZ"
        except AttributeError:
            # The column is actually a DatetimeIndex
            # GH 26761 or an Index with date-like data e.g. 9999-01-01
            if getattr(col, "tz", None) is not None:
                return "TIMESTAMPT_TZ"
        return "TIMESTAMP_NTZ"
    if col_type == "timedelta64":
        logger.warning(
            "the 'timedelta' type is not supported, and will be "
            "written as integer values (ns frequency) to the database.",
        )
        return "INT"
    elif col_type == "floating":
        return "FLOAT"
    elif col_type == "integer":
        return "INT"
    elif col_type == "boolean":
        return "BOOLEAN"
    elif col_type == "date":
        return "DATE"
    elif col_type == "time":
        return "TIME"
    elif col_type == "complex":
        raise ValueError("Complex datatypes not supported")
    return "TEXT"


def _index_name(frame, index, index_label):
    # for writing: index=True to include index in sql table
    if index is True:
        nlevels = frame.index.nlevels
        # if index_label is specified, set this as index name(s)
        if index_label is not None:
            if not isinstance(index_label, list):
                index_label = [index_label]
            if len(index_label) != nlevels:
                raise ValueError(
                    "Length of 'index_label' should match number of "
                    f"levels, which is {nlevels}"
                )
            else:
                return index_label
        # return the used column labels for the index columns
        if nlevels == 1 and "index" not in frame.columns and frame.index.name is None:
            return ["index"]
        else:
            return [
                l if l is not None else f"level_{i}"
                for i, l in enumerate(frame.index.names)
            ]

    # for reading: index=(list of) string to specify column to set as index
    elif isinstance(index, str):
        return [index]
    elif isinstance(index, list):
        return index
    else:
        return None


def _get_column_names_and_types(index, frame, dtype_mapper):
    column_names_and_types = []
    if index is not None:
        for i, idx_label in enumerate(index):
            idx_type = dtype_mapper(frame.index._get_level_values(i))
            column_names_and_types.append((str(idx_label), idx_type, True))

    column_names_and_types += [
        (str(frame.columns[i]), dtype_mapper(frame.iloc[:, i]), False)
        for i in range(len(frame.columns))
    ]
    logger.debug(f"Snowflake types assigned to pandas dtypes: {column_names_and_types}")
    return column_names_and_types


def _get_create_table_statement(table, index, frame, database=None, schema=None):
    """
    Returns a CREATE TABLE statement for the table to which the DataFrame will be loaded.
    :param table: The name of the table which will be created.
    :param index: DataFrame indexes which will be created as DataFrame columns
    :param frame: The DataFrame to load.
    :param database: The name of the database to which data will be inserted.
    :param schema: The name of the schema to which data will be inserted.
    :return: The CREATE TABLE statement.
    """
    column_names_and_types = _get_column_names_and_types(
        index=index, frame=frame, dtype_mapper=_get_col_db_type
    )
    col_defs = []
    for col_name, col_type, is_index in column_names_and_types:
        col_defs.append(f"  {_quote_name(col_name)} {col_type}")
    qualified_name = _qualify_name(database, schema, table)
    return (
        f"CREATE OR REPLACE TABLE {qualified_name} (\n" + ",\n".join(col_defs) + "\n);"
    )


def _qualify_name(database, schema, table):
    if database is not None and schema is None:
        raise ValueError(
            f"Schema is not specified for database [{database}] to create table [{_quote_name(table)}] in."
        )
    qualified_name = _quote_name(table)
    if schema is not None:
        qualified_name = f"{_quote_name(schema)}.{qualified_name}"
    if database is not None:
        qualified_name = f"{_quote_name(database)}.{qualified_name}"
    return qualified_name


def _ensure_table_exists(
    con, table, index, frame, if_exists="fail", database=None, schema=None
):
    """
    Checks if the table exists in the current/given schema and creates it based on the DataFrame/indices if necessary.
    :param con: The pre-opened database Connection to use.
    :param table: The name of the database table. It will be quoted and case sensitive if it contains keywords, lower case or special chars.
    :param index: DataFrame indexes which will be created as DataFrame columns
    :param frame: The DataFrame to load.
    :param if_exists: How to behave if the table already exists. {‘fail’, ‘replace’, ‘append’}, default ‘fail’
             * fail: Raise a ValueError.
             * replace: Drop the table before inserting new values.
             * append: Insert new values to the existing table.
    :param database: The name of the database to which data will be inserted.
    :param schema: The name of the schema to which data will be inserted.
    :return: None
    """
    if database is not None and schema is None:
        raise ValueError(
            f"Schema is not specified for database [{database}] to check if table [{_quote_name(table)}] exists."
        )
    qualified_name = ""
    if schema is not None:
        qualified_name = f" IN SCHEMA {_quote_name(schema)}"
    if database is not None:
        qualified_name = f" IN SCHEMA {_quote_name(database)}.{_quote_name(schema)}"

    name_to_search = _quote_name(table).replace('"', "")
    if _quote_name(table) == table:
        name_to_search = table.upper()

    table_exists = False
    logger.info(f"Checking if table [{table}] exists in [{database}].[{schema}]")
    cursor = con.cursor()
    cursor.execute(f"SHOW TERSE TABLES{qualified_name};")
    for row in cursor.fetchall():
        if name_to_search == row[1]:
            logger.info(f"Table [{table}] already exists in [{database}].[{schema}]")
            table_exists = True
    if not table_exists or "replace" == if_exists:
        logger.info(
            f"Table [{table}] doesn't exist yet in [{database}].[{schema}], creating..."
        )
        create_statement = _get_create_table_statement(
            table=table, index=index, frame=frame, database=database, schema=schema
        )
        logger.debug(f"Table will be created as:\n{create_statement}")
        cursor.execute(create_statement)
        logger.info(f"Table [{table}] created successfully.")
    elif if_exists == "fail":
        raise ValueError(f"Table [{table}] already exists in [{database}].[{schema}]")


T = TypeVar("T", bound=Sequence)


def _chunk_helper(lst: T, n: int) -> Iterator[Tuple[int, T]]:
    """Helper generator to chunk a sequence efficiently with current index like if enumerate was called on sequence."""
    for i in range(0, len(lst), n):
        yield int(i / n), lst[i : i + n]


def to_sql(
    df,
    name,
    con,
    database=None,
    schema=None,
    if_exists="fail",
    index=True,
    index_label=None,
    nanoseconds=False,
):
    """
    Load a DataFrame to the specified table in the database.
    Creates the table if it doesn't yet exist, with TEXT/FLOAT/DATE/TIMESTAMP columns as required.
    The name will be case sensitive (quoted) if it contains lowercase or special characters or is a reserved keyword.
    Based on the write_pandas function of snowflake-connector-python:
    https://docs.snowflake.com/en/user-guide/python-connector-api.html#write_pandas
    :param df: The Pandas DataFrame to insert/stage as a table.
    :param name: The name of the database table. It will only be quoted and case sensitive if it contains keywords or special chars.
    :param con: The pre-opened database Connection to use.
    :param database: The name of the database to which data will be inserted.
    :param schema: The name of the schema to which data will be inserted.
    :param if_exists: How to behave if the table already exists. {‘fail’, ‘replace’, ‘append’}, default ‘fail’
             * fail: Raise a ValueError.
             * replace: Drop the table before inserting new values.
             * append: Insert new values to the existing table.
    :param index: bool, default True: Write DataFrame index as a column. Uses index_label as the column name in the table.
    :param index_label: Column label for index column(s). If None is given (default) and index is True, then the index names are used. A sequence should be given if the DataFrame uses MultiIndex.
    :param nanoseconds: If True, nanosecond timestamps will be used to upload the data. Limits timestamp range from 1677-09-21 00:12:43.145224192 to 2262-04-11 23:47:16.854775807.
    :return: Returns the COPY INTO command's results to verify ingestion in the form of a tuple of whether all chunks were
        ingested correctly, # of chunks, # of ingested rows, and ingest's output.
    """
    if not isinstance(con, Connection):
        raise ValueError(f"Provided con object is not an pyodbc.Connection instance.")
    prev_autocommit = con.autocommit
    con.autocommit = False
    if if_exists not in ("fail", "replace", "append"):
        raise ValueError(f"'{if_exists}' is not valid for if_exists")

    if isinstance(df, Series):
        df = df.to_frame()
    elif not isinstance(df, DataFrame):
        raise NotImplementedError(
            "'df' argument should be either a Series or a DataFrame"
        )

    indices = _index_name(df, index, index_label)
    _ensure_table_exists(
        con=con,
        table=name,
        index=indices,
        frame=df,
        if_exists=if_exists,
        database=database,
        schema=schema,
    )

    # Create a temporary stage where the DataFrame will be uploaded as a Parquet file.
    cursor = con.cursor()
    stage_name = None  # Forward declaration
    while True:
        try:
            stage_name = "".join(
                random.choice(string.ascii_lowercase) for _ in range(5)
            )
            create_stage_sql = (
                "CREATE TEMPORARY STAGE /* Python:nuvolos.to_sql() */ " '"{stage_name}"'
            ).format(stage_name=stage_name)
            logger.debug("Creating temporary stage with '{}'".format(create_stage_sql))
            cursor.execute(create_stage_sql)
            break
        except ProgrammingError as pe:
            if str(pe).endswith("already exists."):
                logger.debug(
                    f"Temporary stage {stage_name} already exists, choosing a different name."
                )
                continue
            raise

    with TemporaryDirectory() as tmp_folder:
        for i, chunk in _chunk_helper(df, 10000000):
            chunk_path = os.path.join(tmp_folder, "file{}.txt".format(i))
            # Dump chunk into parquet file
            if nanoseconds:
                chunk.to_parquet(
                    chunk_path,
                    engine="pyarrow",
                    compression="snappy",
                    index=index,
                    version="2.6",
                )
            else:
                chunk.to_parquet(
                    chunk_path, engine="pyarrow", compression="snappy", index=index
                )
            # Upload parquet file
            upload_sql = (
                "PUT /* Python:nuvolos.to_sql() */ "
                "'file://{path}' @\"{stage_name}\" PARALLEL={parallel}"
            ).format(
                path=chunk_path.replace("\\", "\\\\").replace("'", "\\'"),
                stage_name=stage_name,
                parallel=4,
            )
            logger.debug("Uploading Parquet files with '{}'".format(upload_sql))
            cursor.execute(upload_sql)
            # Remove chunk file
            os.remove(chunk_path)

    db_columns = []
    parquet_columns = []
    column_names_and_types = _get_column_names_and_types(
        index=indices, frame=df, dtype_mapper=_get_col_db_type
    )
    scale = 6
    if nanoseconds:
        scale = 9
    for col_name, col_type, is_index in column_names_and_types:
        if is_index and indices is not None:
            db_columns.append(_quote_name(col_name))
            if col_type.startswith("TIMESTAMP"):
                parquet_columns.append(
                    f"TO_TIMESTAMP($1:{_quote_name(col_name)}::INT,{scale})"
                )
            else:
                parquet_columns.append(f"$1:{_quote_name(col_name)}")
        else:
            db_columns.append(_quote_name(col_name))
            if col_type.startswith("TIMESTAMP"):
                parquet_columns.append(
                    f"TO_TIMESTAMP($1:{_quote_name(col_name)}::INT,{scale})"
                )
            else:
                parquet_columns.append(f"$1:{_quote_name(col_name)}")
    db_columns = ",".join(db_columns)
    parquet_columns = ",".join(parquet_columns)

    # in Snowflake, all parquet data is stored in a single column, $1, so we must select columns explicitly
    # see (https://docs.snowflake.com/en/user-guide/script-data-load-transform-parquet.html)
    copy_into_sql = (
        "COPY INTO {location} /* Python:nuvolos.to_sql() */ "
        "({columns}) "
        'FROM (SELECT {parquet_columns} FROM @"{stage_name}") '
        "FILE_FORMAT=(TYPE=PARQUET COMPRESSION={compression}) "
        "PURGE=TRUE ON_ERROR={on_error}"
    ).format(
        location=_qualify_name(database=database, schema=schema, table=name),
        columns=db_columns,
        parquet_columns=parquet_columns,
        stage_name=stage_name,
        compression="Snappy",
        on_error="ABORT_STATEMENT",
    )
    logger.debug("Copying into table with '{}'".format(copy_into_sql))
    copy_results = cursor.execute(copy_into_sql).fetchall()
    con.commit()
    cursor.close()
    con.autocommit = prev_autocommit
    return (
        all(e[1] == "LOADED" for e in copy_results),
        len(copy_results),
        sum(e[3] for e in copy_results),
        copy_results,
    )
