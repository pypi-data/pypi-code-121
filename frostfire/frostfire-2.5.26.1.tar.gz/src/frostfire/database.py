import mysql.connector
from src.frostfire import functions

def princess_quick_connect():
    config_dict = functions.get_config_dict()
    host_ip = config_dict['princess']['ip_address']
    username = config_dict['princess']['username']
    password = config_dict['princess']['password']
    port = config_dict['princess']['port']
    return connect_to_mysql_database(host_ip=host_ip,username=username,password=password,port=port)

def create_dict_insert_query(database_name, table_name, insert_dict):
    top_query = 'INSERT INTO `'+database_name+'`.`'+table_name+'`('
    bottom_query = ')VALUES('
    for key in insert_dict.keys():
        value = insert_dict[key]
        top_query = top_query + '`' + key + '`,'
        if type(value) is int or type(value) is float:
            bottom_query = bottom_query + str(value) + ','
        else:
            bottom_query = bottom_query + "'"+str(value) + "',"
    # Remove trailing commas
    top_query = top_query[:-1]

    bottom_query = bottom_query[:-1]+');'
    insert_query = top_query+bottom_query
    return insert_query


def insert_into_database(database_connection, insert_statement):
    cursor = database_connection.cursor()
    cursor.execute(insert_statement)
    database_connection.commit()
    cursor.close()

def connect_to_mysql_database(host_ip, username, password,port):
    try:
        database_connection = mysql.connector.connect(
            host=host_ip,
            user=username,
            passwd=password,
            port=port
        )
        if database_connection:
            return database_connection
        else:
            print("Failed connection to "+host_ip)
            exit(0)
    except:
        print("Failed connection to "+host_ip)
        exit(0)


def query_dict(database_connection, query):
    cursor = database_connection.cursor(dictionary="True")
    cursor.execute(query)
    cursor_result = cursor.fetchall()
    cursor.close()
    return cursor_result

def get_table_list_from_database(database_connection, database_name):

    cursor = database_connection.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables where table_schema='"+database_name+"'")
    cursor_result = cursor.fetchall()
    tables = []
    for row in cursor_result:
        tables.append(str(row[0]))
    cursor.close()
    return tables


def insert_list_into_database(database_connection, query_list):
    cursor = database_connection.cursor()
    temp_execute_count = 0
    for insert_statement in query_list:
        cursor.execute(insert_statement)
        temp_execute_count += 1
        if temp_execute_count >= 100:
            database_connection.commit()
            temp_execute_count = 0
    if temp_execute_count > 0:
        database_connection.commit()
    cursor.close()


