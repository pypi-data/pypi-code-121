"""
    function to generate the table.
"""


def generate_table(audit_name: str) -> str:
    """
        generates create table sql statement
    :param audit_name:
    :return: create table sql statement
    """
    return f"""
    CREATE TABLE {audit_name}
    (
        change_date timestamptz default now(),
        before      hstore,
        after       hstore
    );
    """
