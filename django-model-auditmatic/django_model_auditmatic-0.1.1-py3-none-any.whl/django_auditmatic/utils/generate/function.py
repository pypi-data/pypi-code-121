"""
    function to generate the sql function.
"""


def generate_function(audit_name: str) -> str:
    """
        generates sql function for the audit_name
    :param audit_name:
    :return: create function statement
    """
    return f"""
    CREATE OR REPLACE FUNCTION {audit_name}()
        RETURNS TRIGGER
        LANGUAGE plpgsql
    AS $$
    BEGIN
        INSERT INTO {audit_name}(before, after)
            SELECT hstore(old), hstore(new);
        RETURN new;
    END;
    $$;
    """
