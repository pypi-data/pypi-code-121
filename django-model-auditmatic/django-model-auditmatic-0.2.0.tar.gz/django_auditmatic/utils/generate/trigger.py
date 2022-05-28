"""
    function to generate sql trigger
"""


def generate_trigger(audit_name, table_name, action):
    """
        generates create trigger sql statement
    :param audit_name:
    :param table_name:
    :param action:
    :return: create trigger statement
    """
    trigger_audit_name = audit_name.replace(".", "_")
    trigger_audit_name = f"{trigger_audit_name}_{action}"
    return f"""
    CREATE TRIGGER {trigger_audit_name}
        AFTER {action} ON {table_name}
            FOR EACH ROW
    EXECUTE PROCEDURE {audit_name}();
    """
