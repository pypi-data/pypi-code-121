import sqlite3
import os
from cryptography.fernet import Fernet


class QuickSqlite():
    """Class to use SQLite3.

    Args:
        db_path (str): The path to the database.
        protect (bool): If True, the database will be encrypted.
        key (str): The Fernet key to use for encryption.
    """

    def __init__(self, db_path: str, protect: bool, key: str = ""):
        """Initializes the QuickSqlite Class.

        Args:
            db_path (str): The path to the database.
            protect (bool): If True, the database will be encrypted.
            key (str): The Fernet key to use for encryption.
        """
        self.__db_path = db_path
        self.__protect = protect
        self.__database_encrypted = True
        self.__key = key
        if protect is None and key == '':
            raise ValueError(
                "If Protect is True, you must provide a valid Fernet key.")

    def __connect(self):
        global conn, cursor
        if self.__protect == False:
            conn = sqlite3.connect(self.__db_path)
            cursor = conn.cursor()
        elif self.__protect == True:
            if os.path.exists(self.__db_path) == False:
                self.__database_encrypted = False
            if self.__database_encrypted == False:
                conn = sqlite3.connect(self.__db_path)
                cursor = conn.cursor()
                self._encrypt_database(self.__db_path, self.__key)
                self.__database_encrypted = True
            if self.__database_encrypted:

                self._decrypt_database(self.__db_path, self.__key)
                conn = sqlite3.connect(self.__db_path)
                cursor = conn.cursor()
                self.__database_encrypted = False

    def __close(self):
        if self.__protect == False:
            cursor.close()
            conn.close()
        elif self.__protect == True:
            if self.__database_encrypted == False:
                self._encrypt_database(self.__db_path, self.__key)
                self.__database_encrypted = True

    def _encrypt_database(self, filename, key):
        """
        Given a filename (str) and key (bytes), it encrypts the file and write it
        """
        f = Fernet(key)
        with open(filename, "rb") as file:
            # read all file data
            file_data = file.read()
            # encrypt data
        encrypted_data = f.encrypt(file_data)
        # write the encrypted file
        with open(filename, "wb") as file:
            file.write(encrypted_data)

    def _decrypt_database(self, filename, key):
        """
        Given a filename (str) and key (bytes), it decrypts the file and write it
        """
        f = Fernet(key)
        with open(filename, "rb") as file:
            # read the encrypted data
            encrypted_data = file.read()
        # decrypt data
        decrypted_data = f.decrypt(encrypted_data)
        # write the original file
        with open(filename, "wb") as file:
            file.write(decrypted_data)

    def create_table(self, table_name: str, column_name: str):
        """Creates the table with specified name and column name(s).

        Args:
            table_name (str): The name of the table to create.
            column_name (str): The column name(s) of the table.
        """
        self.__connect()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({column_name})")
        self.__close()

    def check_table_exists(self, table_name: str, column_name: str) -> bool:
        """Checks if specified table exists in the database.

        Args:
            table_name (str): Name of the table to check.
            column_name (str): The name of any column of the table.

        Returns:
            bool: True if table exists, False otherwise.
        """
        self.__connect()
        cursor.execute(
            f"SELECT {column_name} from sqlite_master WHERE type = 'table' AND name = '{table_name}'")
        table = cursor.fetchone()
        self.__close()
        if table:
            return True
        elif table is None:
            return False

    def delete_table(self, table_name: str):
        """Deletes the specified table.

        Args:
            table_name (str): The name of the table to delete.
        """
        self.__connect()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.__close()

    def alter_table(self, table_name: str, column_function: str, data: str):
        """Alters the specified thing of the specified table.

        Args:
            table_name (str): The name of the table to alter.
            column_function (str): The function you want to perform on the column.
            data (str): The data of the thing you want to alter.
        """
        self.__connect()

        p = data.split(' ')

        query = cursor.execute(
            f"SELECT COUNT(*) AS CNTREC FROM pragma_table_info('{table_name}') WHERE name='{p[0]}'")
        col_exist = query.fetchone()
        col_exist = col_exist[0] > 0
        if not col_exist:
            cursor.execute(
                f"ALTER TABLE {table_name} {column_function} COLUMN {data}")
        else:
            pass
        self.__close()

    def insert_table(self, table_name: str, column_name: str, data: list[str]):
        """Inserts the data in the specified column of the specified table.

        Args:
            table_name (str): The name of the table in which data is to be inserted.
            column_name (str): The name of the column in which data is to be inserted.
            data (list[str]): The data to be inserted.
        """
        data_count = len(data)
        loop_count = 0
        question_marks = ''
        data_tuple = tuple(data)
        for i in data:
            loop_count += 1
            question_marks += '?'
            question_marks += ' '
            if not loop_count == data_count:
                question_marks += ','

        self.__connect()
        cursor.execute(
            f"INSERT INTO {table_name} ({column_name}) VALUES ({question_marks})", (data_tuple))
        conn.commit()
        self.__close()

    def update_table(self, table_name: str, column_name: str, new_data: str, filter_column_name: str, filter_column_data: str):
        """Updates the data in the specified column of specified table.

        Args:
            table_name (str): The name of the table in which data is to be updated.
            column_name (str): The name of the column in which data is to be updated.
            new_data (str): The data to be updated.
            filter_column_name (str): The name of a column to filter the row.
            filter_column_data (str): The data of a column to filter the row.
        """
        self.__connect()
        cursor.execute(
            f"UPDATE {table_name} SET {column_name} = ? WHERE {filter_column_name} = ?", (new_data, filter_column_data))
        conn.commit()
        self.__close()

    def select_table(self, table_name: str) -> list[tuple]:
        """Returns all data of the specified table.

        Args:
            table_name (str): The name of the table of which you want the data.

        Returns:
            list[tuple]: Returns the list containing data of each row in tuples.
        """
        self.__connect()
        cursor.execute(f"SELECT * FROM {table_name}")
        result = cursor.fetchall()
        self.__close()
        return result

    def select_column(self, table_name: str, column_name: str) -> list[tuple]:
        """Returns a specified column of the specified table.

        Args:
            table_name (str): The name of the table of which you want column.
            column_name (str): The name of the column of which you want data.

        Returns:
            list[tuple]: Returns the list containing data of each row in tuples.
        """
        self.__connect()
        cursor.execute(f"SELECT {column_name} FROM {table_name}")
        result = cursor.fetchall()
        self.__close()
        return result

    def check_column_exists(self, table_name, column_name) -> bool:
        """Checks if specified column exists in the specified table.

        Args:
            table_name (str): Name of the table to check.
            column_name (str): The name of the column to check.

        Returns:
            bool: True if column exists, False otherwise.
        """
        self.__connect()

        cursor.execute(
            f"SELECT COUNT(*) AS CNTREC FROM pragma_table_info('{table_name}') WHERE name='{column_name}'")
        column = cursor.fetchone()
        column_exist = column[0] > 0

        if column_exist:
            return True
        elif not column_exist:
            return False

        self.__close()

    def select_data(self, table_name: str, column_name: str, filter_column_name: str, filter_column_data: list[str]) -> tuple[str]:
        """Returns a specified data from a specified column.

        Args:
            table_name (str): The name of the table of which you want the data.
            column_name (str): The name of the column of which you want the data.
            filter_column_name (str): The name of the column you want to be filtered through.
            filter_column_data (list[str]): The data of the column you want to be filtered through.

        Returns:
            tuple[str]: Returns a tuple consisting of the data of the specified column as string.
        """
        self.__connect()
        filter_column_name_array = filter_column_name.split()
        edited_array = []
        for filter_column_name_value in filter_column_name_array:
            edited_array.append(filter_column_name_value + '=?')

        edited_string = ' and '.join(edited_array).replace(',', '')
        filter_data_tuple = tuple(filter_column_data)

        cursor.execute(
            f"SELECT {column_name} FROM {table_name} WHERE {edited_string}", (filter_data_tuple))
        result = cursor.fetchone()
        self.__close()
        return result

    def delete_data(self, table_name: str, column_name: str, data: list[str]):
        """Deletes the specified row from the table.

        Args:
            table_name (str): The name of the table of which you want to delete the data.
            column_name (str): The name of the column of which you want to delete the data.
            data (list[str]): The data of the row to be deleted.
        """
        self.__connect()
        cursor.execute(
            f"DELETE FROM {table_name} WHERE {column_name} = ?", (data))
        conn.commit()
        self.__close()
