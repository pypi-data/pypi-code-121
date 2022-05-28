"""
    generate functions
"""
from typing import Optional, List

from django_auditmatic.utils.generate.extension import generate_install_hstore
from django_auditmatic.utils.generate.function import generate_function
from django_auditmatic.utils.generate.table import generate_table
from django_auditmatic.utils.generate.trigger import generate_trigger


def generate_sql(
    app_name: str,
    model_name: str,
    schema: str,
    table_name: Optional[str] = None,
    debug: Optional[bool] = True,
    verbs: Optional[List[str]] = None
):
    """
        generates the sql
    :param app_name:
    :param model_name:
    :param schema:
    :param table_name:
    :param debug:
    :param verbs:
    :return:
    """
    if verbs is None:
        verbs = ["INSERT", "UPDATE", "DELETE"]
    table_name, audit_name = get_table_and_audit_name(
        app_name,
        model_name,
        schema,
        table_name
    )
    table_statement = generate_table(audit_name)
    function_statement = generate_function(audit_name)
    triggers = '\n'.join([
        generate_trigger(audit_name, table_name, verb) for verb in verbs
    ])
    statement = combine_statements(table_statement, function_statement, triggers)

    if debug:
        log_generated(statement, model_name, table_name, schema)
    return statement


def get_table_and_audit_name(app_name, model_name, schema, table_name):
    """

    :param app_name:
    :param model_name:
    :param schema:
    :param table_name:
    :return:
    """
    table_name = table_name or f"{app_name}_{model_name}"
    audit_name = f"{schema}.audit_{table_name}"
    table_name = f"{schema}.{table_name}"
    return table_name, audit_name


def combine_statements(table_stmt: str, function_stmt: str, triggers: str) -> str:
    """

    :param table_stmt:
    :param function_stmt:
    :param triggers:
    :return:
    """
    return f"""
    {table_stmt}
    {function_stmt}
    {triggers}
    """


def log_generated(
    statement: str,
    model_name: str,
    table_name: str,
    schema: str
) -> None:
    """

    :param statement:
    :param model_name:
    :param table_name:
    :param schema:
    :return:
    """
    print("Statement generated: ", statement)
    print("Model Name:", model_name)
    print("Table Name:", table_name)
    print("Schema: ", schema)


__all__ = [
    "generate_function",
    "generate_install_hstore",
    "generate_sql",
    "generate_table",
    "generate_trigger",
]
