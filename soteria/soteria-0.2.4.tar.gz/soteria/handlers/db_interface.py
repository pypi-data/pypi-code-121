import pyodbc

from database_lookup import db_connections


def build_connection(database_lookup=None, auth_override=None, username=None, password=None):

    conn_details = db_connections[database_lookup.lower()]

    if auth_override:
        connection = pyodbc.connect('DRIVER={' + conn_details["driver"] + '}; SERVER=' + conn_details["server"] +
                                    '; DATABASE=' + database_lookup + ';UID=' + username + '; PWD=' + password)
    else:
        if conn_details["auth"] == "windows":
            # print(conn_details['driver'])
            connection = f"DRIVER={conn_details['driver']}; SERVER={conn_details['server']}; DATABASE={ database_lookup };Trusted_Connection=yes;"
        if conn_details["auth"] == "azure":
            connection = f"DRIVER={conn_details['driver']}; SERVER={conn_details['server']}; DATABASE={ database_lookup }; UID={ username }; PWD={ password }"
            # connection = 'DRIVER={' + conn_details["driver"] + '}; SERVER=' + conn_details["server"] + '; DATABASE=' + database_lookup + ';UID=' + encrypted["idm_username"] + '; PWD=' + encrypted["decrypted"]["idm_password"])

    return connection


def run_query(query, database, auth_override=None, params=[], return_single_value=None, username=None, password=None):
    params = tuple(params)
    conn_details = build_connection(
        database_lookup=database, auth_override=auth_override, username=username, password=password)
    connection = pyodbc.connect(conn_details)

    # add parameter placeholders to query
    param_input = []
    if len(params) > 0:
        param_placeholders = '?,'*len(params)
        param_placeholders = param_placeholders[:-1]  # remove trailing comma
        param_input = f'({param_placeholders})'

        query = query.replace('()', param_input)
    else:
        if 'IN ()' in query:
            return [[]]

    cursor = connection.cursor()
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    connection.commit()

    if return_single_value:
        results = results[0][0]

    return results
