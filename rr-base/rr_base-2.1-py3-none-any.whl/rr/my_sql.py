import mysql.connector
import pandas as pd
from typing import List


class MySqlConnection:

    def __init__(self, user: str = 'root', password: str = 'password', host: str = '127.0.0.1', database: str = 'sys'):
        self.__connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self.__cursor_connection = self.__connection.cursor()
        self.__user = user
        self.__password = password
        self.__host = host
        self.__database = database

    def __cursor_connection_test(self):
        try:
            if self.__connection.is_connected():
                print('db connected')
                return
            else:
                self.__connection = mysql.connector.connect(user=self.__user, password=self.__password,
                                                            host=self.__host, database=self.__database)
                self.__cursor_connection = self.__connection.cursor()
                print('connection to db')

        except Exception as e:
            print(e)

    def get_data(self, query, return_data_frame: bool = False, close_connection=False):
        try:
            self.__cursor_connection_test()
            self.__cursor_connection.execute(query)
            data_result = list(self.__cursor_connection.fetchall())
            if close_connection:
                self.close_connection()
            if not return_data_frame:
                return data_result, self.__cursor_connection.column_names
            else:
                return pd.DataFrame(data=data_result, columns=self.__cursor_connection.column_names)
        except Exception as e:
            raise print(e, query)

    def manipulate_data(self, query: str, data: List[tuple] = None, is_list: bool = True,
                        delete_data: bool = False, close_connection: bool = False):
        try:
            self.__cursor_connection_test()
            if is_list and not delete_data:
                self.__cursor_connection.executemany(query, data)
            elif not delete_data:
                self.__cursor_connection.execute(query, data)
            else:
                self.__cursor_connection.execute(query)

            self.__connection.commit()
            if close_connection:
                self.close_connection()
        except Exception as e:
            self.close_connection()
            raise print(e)

    def close_connection(self):
        try:
            self.__connection.close()
        except Exception as e:
            raise print(e)
