import pandas as pd
import requests
import numpy as np
import sqlalchemy
import psycopg2.extras
import psycopg2.errors
from tqdm import tqdm


##################################################### PYTHOLINO ######################################################

def pytholino_alert(url, alert):
    payload = "{'Alerta': {}}".format(alert)
    a = requests.request("POST", url, data=payload)


def pytholino_error(url, scr, err):
    text = f"Eai brabos! Deu erro no script {scr}, mas ja separei aqui para vcs: {err}"
    payload = "{'Alerta': '" + text + "'}"
    a = requests.request("POST", url, data=payload)


####################################################### ADJUSTS #######################################################

def adjust_cnpj(cnpj):
    result = ''
    if cnpj is not None:
        cnpj = str(cnpj)
        for letter in cnpj:
            if letter in '0123456789':
                result += letter
        while len(result) < 14:
            result = '0' + result
    else:
        return None
    return result


def adjust_cpf(cpf):
    try:
        cpf = str(cpf)
    except TypeError:
        cpf = None
    if cpf is not None:
        result = ''
        for l in cpf:
            if l in '1234567890':
                result = result + l
        while len(result) < 11:
            result = '0' + result
    else:
        result = None
    if result == '00000000000':
        result = None
    return result


def adjust_phone(phone):
    result = ''
    try:
        phone = str(int(phone)).strip()
    except ValueError:
        phone = str(phone).strip()
    except TypeError:
        result = None
        status = 'Invalid Format Number'
        return result, status
    for char in phone:
        if char in '0123456789':
            result += char
    try:
        while result[0] == '0':
            result = result[1:]
        if result[0:2] == '55':
            result = result[2:]
        if result[2] in '6789' and len(result) == 10:
            result = result[0:2] + '9' + result[2:]
    except IndexError:
        status = 'Invalid Format Number'
        result = phone
        return result, status
    if len(result) not in (10, 11):
        status = 'Invalid Format Number'
        result = phone
    elif result[2] in '01':
        status = 'Invalid Format Number'
    else:
        status = None
    return result, status


###################################################### POSTGRES #######################################################

def postgres_insert_batch(df_batch, url, database, table):
    print(f'Inserting on {table}, {database}...')
    if df_batch.shape[0] > 0:
        engine = sqlalchemy.create_engine(url + database)
        con = engine.raw_connection()
        tuples = [tuple(x) for x in df_batch.to_numpy()]
        cols = ','.join(list(df_batch.columns))
        aux = '(' + '%s,' * (len(tuples[0]) - 1) + '%s)'
        query = "INSERT INTO " + table + "(" + cols + ") VALUES " + aux
        cur = con.cursor()
        psycopg2.extras.execute_batch(cur, query, tuples)
        con.commit()
        con.close()
        print('Done!')
    else:
        print('Empty Dataframe on insert_batch!')


def postgres_insert_batch_without_conflict(df_batch, url, database, table):
    print(f'Inserting on {table}, {database} without conflict...')
    if df_batch.shape[0] > 0:
        engine = sqlalchemy.create_engine(url + database)
        con = engine.raw_connection()
        tuples = [tuple(x) for x in df_batch.to_numpy()]
        cols = ','.join(list(df_batch.columns))
        aux = '(' + '%s,' * (len(tuples[0]) - 1) + '%s)'
        query = "INSERT INTO " + table + "(" + cols + ") VALUES " + aux + "ON CONFLICT DO NOTHING"
        cur = con.cursor()
        psycopg2.extras.execute_batch(cur, query, tuples)
        con.commit()
        con.close()
        print('Done!')
    else:
        print('Empty dataframe on insert_batch!')


def postgres_upsert(df, url, db, table, conflict_column):
    print(f'Upserting {table} from {db} on conflict {conflict_column}...')
    if df.shape[0] > 0:
        engine = sqlalchemy.create_engine(url + db)
        con = engine.raw_connection()
        cur = con.cursor()
        cols = ','.join(list(df))
        v = ','.join(['%s'] * len(list(df)))
        updates = ','.join([x + '=%s' for x in list(df)[1:]])
        rows = [list(x) for x in df.to_numpy()]
        qry = f"insert into {table} ({cols}) values ({v}) on conflict ({conflict_column}) do update set {updates}"
        for i in tqdm(rows):
            i.extend(i[1:])
            j = [None if pd.isna(x) else x for x in i]
            try:
                cur.execute(qry, tuple(j))
            except psycopg2.errors.FeatureNotSupported:
                print(i)
            except psycopg2.ProgrammingError:
                pass
        con.commit()
        con.close()
        print('Done!')
    else:
        print('Empty dataframe on upsert!')


def postgres_update_with_df(df, url, db, table, update_columns, parameter_column):
    print(f"Updating {', '.join(update_columns)} on {table}, {db} using {parameter_column} as parameter")
    engine = sqlalchemy.create_engine(url + db)
    con = engine.raw_connection()
    cur = con.cursor()
    if df.shape[0] > 0:
        for update_column in update_columns:
            for i in tqdm(df.index):
                qry = f"""update {table} set {update_column} = %s where {parameter_column} = %s"""
                if isinstance(df.at[i, update_column], np.int64):
                    a = int(df.at[i, update_column])
                elif isinstance(df.at[i, update_column], np.int32):
                    a = int(df.at[i, update_column])
                else:
                    a = df.at[i, update_column]
                if isinstance(df.at[i, parameter_column], np.int64):
                    b = int(df.at[i, parameter_column])
                elif isinstance(df.at[i, parameter_column], np.int32):
                    b = int(df.at[i, parameter_column])
                else:
                    b = df.at[i, parameter_column]
                tup = (a, b)
                cur.execute(qry, tup)
                con.commit()
        print('Done!')
    else:
        print('Empty dataframe on update_with_df!')
    con.close()
