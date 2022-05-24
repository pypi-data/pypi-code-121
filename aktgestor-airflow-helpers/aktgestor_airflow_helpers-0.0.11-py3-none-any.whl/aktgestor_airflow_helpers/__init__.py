from jinjasql import JinjaSql
jinja = JinjaSql(param_style='pyformat')

def read_sql_file(file_path,params = None):
    with open(file_path, 'r') as f:
        sql = f.read()
        if params == None:
            return {'sql':sql}
        query, bind_params = jinja.prepare_query(sql, params)
        return {'sql' : query, 'parameters' : bind_params}

def get_table_updated_at(hook, control_table, table_name):
    sql = f"SELECT updated_at FROM {control_table} where tablename = '{table_name}'; \n"
    datetime_str = (hook.get_first(sql))[0].strftime('%Y-%m-%d %H:%M:%S')
    return datetime_str

def set_table_updated_at(hook,control_table, table_name, datetime_str):
    sql = f"UPDATE {control_table} SET updated_at = '{datetime_str}' WHERE tablename = '{table_name}'; \n"
    hook.run(sql)

def get_new_data_from_df(df):
    df_new = df[df['updated_at'] == df['created_at']]
    return df_new

def get_updated_data_from_df(df):
    df_updated = df[df['updated_at'] != df['created_at']]
    return df_updated
    
def get_dbtime_now(hook):
    sql = "SELECT NOW() - INTERVAL 3 HOUR as timenow FROM DUAL"
    return (hook.get_first(sql))[0].strftime('%Y-%m-%d %H:%M:%S')

def get_etl_definitions(hook,control_table, table_name):
    sql = f"select tablename,updated_at,type,primary_keys,active from {control_table} where tablename = '{table_name}';"
    data = hook.get_first(sql)
    table_name = data[0]
    updated_at = data[1].strftime('%Y-%m-%d %H:%M:%S')
    type = data[2]
    primary_keys = data[3].split(',')
    active = data[4]
    return {'table_name':table_name, 'updated_at':updated_at, 'type':type, 'primary_keys':primary_keys, 'active':active}

def update_rows(hook, table, data, primary_keys):
    for index, row in data.iterrows():
        where_clause = ' AND '.join([f'{key} = %%({key})s' for key in primary_keys])
        where_params = {key: row[key] for key in primary_keys}
        set_clause = ', '.join([f'{key} = %%({key})s' for key in row.keys() if key not in primary_keys])
        set_params = {key: row[key] for key in row.keys() if key not in primary_keys}
        params = {**where_params, **set_params}
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
        print(f'SQL: {sql} \nParams: {params}\n')
        hook.run(sql, params)
        break