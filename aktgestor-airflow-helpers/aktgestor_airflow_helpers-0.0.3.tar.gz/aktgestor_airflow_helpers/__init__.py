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