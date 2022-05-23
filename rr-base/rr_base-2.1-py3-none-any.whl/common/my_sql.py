import mysql.connector


class MySqlConnection:

    def __init__(self, user='root', password='password', host='127.0.0.1', database='sys'):
        self.connection = mysql.connector.connect(user=user, password=password,
                                                  host=host,
                                                  database=database)
        self.__cursor_connection = self.connection.cursor()
        self.data_result = None

    def get_data(self, query, close_connection=False):
        try:
            self.__cursor_connection.execute(query)
            self.data_result = list(self.__cursor_connection.fetchall())
            if close_connection:
                self.close_connection()
            return self.data_result, self.__cursor_connection.column_names
        except Exception as e:
            print(e)

    def manipulate_data(self, query, data=None, is_list=True, delete_data=False, close_connection=False):
        try:
            if is_list and not delete_data:
                self.__cursor_connection.executemany(query, data)
            elif not delete_data:
                self.__cursor_connection.execute(query, data)
            else:
                self.__cursor_connection.execute(query)

            self.connection.commit()
            if close_connection:
                self.close_connection()
        except Exception as e:
            self.close_connection()
            raise print(e)

    def close_connection(self):
        try:
            self.connection.close()
        except Exception as e:
            raise print(e)
