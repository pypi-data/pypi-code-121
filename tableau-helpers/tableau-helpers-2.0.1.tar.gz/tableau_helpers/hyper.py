from pathlib import Path
from typing import Optional, Union

from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    TableDefinition,
    Telemetry,
    escape_string_literal,
)


def _gen_sql_for_with_csv(
    delimiter: str = ",",
    null: str = "",
    encoding: str = "utf-8",
    on_cast_failure: str = "error",
    header: bool = False,
    quote: str = '"',
    escape: str = None,
    force_not_null: list[str] = None,
    force_null: list[str] = None,
):
    sql_with: str = "WITH ("
    sql_with += "FORMAT csv"
    sql_with += f", NULL {escape_string_literal(null)}"
    sql_with += f", DELIMITER {escape_string_literal(delimiter)}"
    sql_with += f", ENCODING {escape_string_literal(encoding)}"
    sql_with += f", ON_CAST_FAILURE {escape_string_literal(on_cast_failure)}"
    sql_with += f", HEADER {str(header).capitalize()}"
    sql_with += f", QUOTE {escape_string_literal(quote)}"
    if escape is not None:
        sql_with += f", ESCAPE {escape_string_literal(escape)}"
    if force_not_null is not None:
        sql_with += f", FORCE_NOT_NULL ({','.join(force_not_null)})"
    if force_null is not None:
        sql_with += f", FORCE_NULL ({','.join(force_null)})"
    sql_with += ")"
    return sql_with


def copy_csv_to_hyper(
    save_path: Path,
    csv: Union[Path, list[Path]],
    schema: TableDefinition,
    delimiter: str = ",",
    null: str = "",
    encoding: str = "utf-8",
    on_cast_failure: str = "error",
    header: bool = False,
    quote: str = '"',
    escape: str = None,
    force_not_null: list[str] = None,
    force_null: list[str] = None,
) -> Optional[int]:
    """
    :param save_path: where to save the resulting hyperfile
    :param csv: the csv or list of csv paths to be imported
    :param schema: the TableDefinition for the destination hyperfile
    :param delimiter: the separator character for the input csv
    :param null: the string which represents a null in the csv
    :param encoding: the encoding type of the csv { 'utf-8' | 'utf-16' | 'utf-16-le' | 'utf-16-be' }
    :param on_cast_failure: how to handle a failure to cast types { 'error' | 'set_null' }
    :param header: if a header is present in the csv
    :param quote: character used to mark quoted fields
    :param escape: Specifies the character that should appear before a data character that matches the QUOTE value. The default is the same as the QUOTE value (so that the quoting character is doubled if it appears in the data). This must be a single one-byte character.
    :param force_not_null: Do not match the specified columns' values against the null string. In the default case where the null string is empty, this means that empty values will be read as zero-length strings rather than nulls, even when they are not quoted.
    :param force_null: Match the specified columns' values against the null string, even if it has been quoted, and if a match is found set the value to NULL. In the default case where the null string is empty, this converts a quoted empty string into NULL.
    :return: the count of rows written to the hyper file, otherwise None
    """  # noqa
    sql_from: str = f"COPY {schema.table_name} "

    if isinstance(csv, Path):
        if not csv.exists():
            raise FileNotFoundError(str(csv))
        sql_from += f"FROM {escape_string_literal(str(csv))}"
    elif isinstance(csv, list):
        if len(csv) < 1:
            raise ValueError
        for x in csv:
            if not isinstance(x, Path):
                raise TypeError
            if not x.exists():
                raise FileNotFoundError(str(x))
        escaped_paths = [escape_string_literal(str(x)) for x in csv]
        sql_from += f"FROM ARRAY[{','.join(escaped_paths)}]"
    else:
        raise TypeError

    sql_with = _gen_sql_for_with_csv(
        delimiter=delimiter,
        null=null,
        encoding=encoding,
        on_cast_failure=on_cast_failure,
        header=header,
        quote=quote,
        escape=escape,
        force_not_null=force_not_null,
        force_null=force_null,
    )
    sql_command = f"{sql_from} {sql_with}"

    process_parameters = {
        "log_file_max_count": "3",
        "log_file_size_limit": "100M",
    }
    with HyperProcess(
        telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
        parameters=process_parameters,
    ) as hyper_process:
        with Connection(
            endpoint=hyper_process.endpoint,
            database=save_path,
            create_mode=CreateMode.CREATE_AND_REPLACE,
        ) as connection:
            connection.catalog.create_table(table_definition=schema)
            rowcount = connection.execute_command(sql_command)
            return rowcount
