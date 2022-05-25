from numpy import result_type
import psycopg2

def connect(user,pw,host,Port,database):
    heroku_db_url = "postgres://{}:{}@{}:{}/{}".format(user,pw,host,Port,database)
    connection =  psycopg2.connect(heroku_db_url, sslmode='require')
    return connection

def fetchDataInDatabase(sql:str, params:list, connection):
    cursor = connection.cursor()
    cursor.execute(sql,params)
    result = cursor.fetchall()
    return result

def insertDataIntoDatabase(sql:str, params:list, connection):    
    
    cursor = connection.cursor()
    try:
        cursor.execute(sql,params)
        connection.commit()
        cursor.close()
        return None
    except Exception as e:
        connection.commit()
        cursor.close()
        return e