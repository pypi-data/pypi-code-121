import sqlite3 as sl


def create_db(db_name):
    """
    Creates SQL DB <db_name>.

    Input:
            db_name - database name where table will be created
    """
    con = sl.connect(db_name)
    con.close()
    
    return


def create_table_in_db(db_name, table_name, values):
    """
    Creates SQL table <table_name> in DB <db_name> with the keys and types of values based on the dictionary <values>.

    Input:
            db_name - database name where table will be created
            table_name - name of the table that will be created
            values - dictionary of key="column name" and value="data type"
    """
    sql_command = f"""CREATE TABLE {table_name} (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\n"""
    c = 0
    for key in values:
        sql_command += f"            {key} {values[key]}"
        c+=1
        if c < len(values):
            sql_command += ",\n"
        else:
            sql_command += "\n"

    sql_command+=");"

    con = sl.connect(db_name)
    with con:
        con.execute(sql_command)
    
    return


def put_data_db(db_name, table_name, column_names, data):
    """
    Insert <data> on SQL table <table_name> on <db_name> DB, based on <column_names>.

    Input: 
            db_name - database name where table will be created
            table_name - name of the table that will be created
            column_names - list of "column names"
            data - list of data values (same length of column_names) 
    """
    sql_command = f'INSERT INTO {table_name} ('
    c=0
    values=''
    for item in column_names:
        if c==0:
            sql_command+=item
            values+='?'
        elif c < len(column_names):
            sql_command+=f', {item}'
            values+=f', ?'
        c+=1
    sql_command+=f') values({values})'
    con = sl.connect(db_name)
    with con:
        con.executemany(sql_command, data)
    return


def get_values_from_table(db_name, table_name):
    """
    Get row values of <table_name> from <db_name>.

    Input: 
            db_name - database name where table will be created
            table_name - name of the table that will be created
    Output:
            o - dict of indexes and list of tuples (rows/values)
    """
    values = []
    con = sl.connect(db_name)
    with con:
        data = con.execute("SELECT * FROM %s" %table_name)
    for row in data:
        values.append(row)
    indexes = [i[0] for i in data.description]
    o = {'indexes': indexes, 'values': values}
    return o


def get_indexes_from_table(db_name, table_name):
    """
    Get table indexes (headers) of <table_name> from <db_name>.

    Input: 
            db_name - database name where table will be created
            table_name - name of the table that will be created
    Output:
            indexes - list of indexes (headers as strings)
    """
    con = sl.connect(db_name)
    with con:
        data = con.execute("SELECT * FROM %s" %table_name)
        indexes = [i[0] for i in data.description]
    return indexes