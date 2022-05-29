from rr.my_sql import MySqlConnection
from rr_batch import constants, sql
from rr_batch import process

__all__ = [
    'constants',
    'sql',
    'process'
]


class TruncateData(MySqlConnection):
    def __init__(self, database: str, table_list: list):
        super().__init__(database=database)
        for t in table_list:
            self.__truncate(table=t)
        self.close_connection()

    def __truncate(self, table: str):
        command = f"truncate {table};"
        self.manipulate_data(query=command, is_list=False, delete_data=True)
        print(f"{command} with success")



