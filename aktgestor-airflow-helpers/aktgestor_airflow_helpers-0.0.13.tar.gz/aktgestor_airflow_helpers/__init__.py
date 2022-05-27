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

def get_update_table_sql(arn, bucket, conn_id, datamart, file, columns, primary_keys, target_table):
    """
    Retorna a query para atualizar a tabela
    arn: arn do s3
    bucket: nome do bucket
    conn_id: nome da conexão do airflow
    datamart: nome do datamart
    file: nome do arquivo
    columns: colunas da tabela
    primary_keys: chaves primárias da tabela
    """

    sql_insert = """
    -- CRIA TABELA TEMPORARIA
    CREATE temp TABLE stage_{target_table} (LIKE {target_table});

    -- INSERE DADOS DA TABELA TEMPORARIA
    COPY stage_{target_table} ({columns}) --Column Mapping Parameter
        FROM 's3://{bucket}/{conn_id}/{datamart}/{target_table}/{file}.csv' -- file url
        iam_role '{arn}'
        csv;

    -- INSERT INTO FINAL TABLE
    BEGIN TRANSACTION;

        -- delete existing rows
        DELETE FROM {target_table}
        USING stage_{target_table}
        WHERE {where_clause};

        -- insert rows
        INSERT INTO {target_table} 
        SELECT * FROM stage_{target_table};

    END TRANSACTION;

    -- DROP TEMPORARY TABLE
    DROP TABLE stage_{target_table}; 

    """
    where_clause = ' AND '.join([f'{target_table}.{key} = stage_{target_table}.{key}' for key in primary_keys])

    sql = sql_insert.format(target_table=target_table, columns=columns, bucket=bucket, conn_id=conn_id, datamart=datamart, file=file, primary_keys=primary_keys, where_clause=where_clause)
    return [item for item in sql.split(';')][:-1]