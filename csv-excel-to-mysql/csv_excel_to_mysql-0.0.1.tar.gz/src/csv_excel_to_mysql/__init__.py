import mysql.connector as connection
import pandas as pd


class CSVXLToMySQL:

    def __init__(self, file: str, table: str, host: str, database: str, username: str, password: str):
        self.file = file
        self.table = table
        self.host = host
        self.database = database
        self.username = username
        self.password = password
        self.__db_connection = None
        self.__cursor = None
        self.__input_df = None
        self.__input_dtypes = None
        self.__error = 0

    def __read_input_data(self):
        try:
            if (self.file.endswith('.xlsx')) | (self.file.endswith('.xls')):
                self.__input_df = pd.read_excel(self.file, parse_dates=True)
            elif self.file.endswith('.csv'):
                self.__input_df = pd.read_csv(self.file, sep=',', parse_dates=True)
            else:
                raise Exception('Invalid file format')
        except Exception as file_error:
            self.__error = 1
            print(f'UNABLE TO READ INPUT FILE\nReason: {file_error}')
        else:
            print('INPUT FILE READ SUCCESSFUL')

    def __get_input_schema(self):
        py_to_db_map = {'object': 'VARCHAR(200)',
                        'float64': 'FLOAT',
                        'int64': 'INT',
                        'datetime64[ns]': 'DATE'}

        if self.__input_df is not None:
            try:
                self.__input_dtypes = self.__input_df.dtypes.astype('str').map(py_to_db_map).reset_index()
                if any(self.__input_dtypes.iloc[:, 1].isna()):
                    raise Exception('No Mapping for 1 or more data types')
            except Exception as dtype_error:
                self.__error = 1
                print(f'UNABLE TO PARSE INPUT FILE DATA TYPES\nReason: {dtype_error}')
            else:
                print('INPUT DATA TYPES PARSE SUCCESSFUL')

    def __connect(self):
        try:
            self.__db_connection = connection.connect(host=self.host,
                                                      username=self.username,
                                                      password=self.password)
        except Exception as conn_exception:
            self.__error = 1
            print(f'UNABLE TO CONNECT TO DB SERVER\nREASON: {conn_exception}')
        else:
            print('DB SERVER CONNECTION SUCCESSFUL')

    def __database_exists(self):
        db_exists = False
        if self.__db_connection is not None:
            self.__cursor = self.__db_connection.cursor()
            self.__cursor.execute('SHOW DATABASES')
            db_list = [i[0] for i in self.__cursor.fetchall()]
            if self.database in db_list:
                db_exists = True
                print(f'DATABASE {self.database} ALREADY EXISTS. HENCE USING THE EXISTING DATABASE')
            return db_exists

    def __create_db(self):
        if self.__db_connection is not None:
            create_db_query = f'CREATE DATABASE {self.database};'
            try:
                self.__cursor = self.__db_connection.cursor()
                self.__cursor.execute(create_db_query)
                self.__db_connection.commit()
            except Exception as e:
                self.__error = 1
                print(f'UNABLE TO CREATE DATABASE {self.database}\nREASON: {e}\n{create_db_query}')
            else:
                print(f'SUCCESSFULLY CREATED DATABASE NAMED {self.database}')

    def __table_exists(self):
        table_exists = False
        if self.__db_connection is not None:
            self.__cursor = self.__db_connection.cursor()
            self.__cursor.execute(f'SHOW TABLES FROM {self.database}')
            table_list = [i[0] for i in self.__cursor.fetchall()]
            if self.table in table_list:
                table_exists = True
                print(f'TABLE {self.table} ALREADY EXISTS. HENCE USING THE EXISTING TABLE')
            return table_exists

    def __create_db_table(self):
        if self.__input_dtypes is not None:
            dtypes_str = ''
            for _, col, dtype in self.__input_dtypes.itertuples():
                dtypes_str += f"{col.replace(' ', '_')} {dtype}, "
            dtypes_str = dtypes_str[:-2]
            create_table_query = f'CREATE TABLE {self.database}.{self.table} ({dtypes_str})'
            create_table_query = create_table_query.replace('-', '_')

            if self.__db_connection is not None:
                try:
                    self.__cursor.execute(create_table_query)
                    self.__db_connection.commit()
                except Exception as e:
                    self.__error = 1
                    print(f'ERROR: UNABLE TO CREATE TABLE {self.table}\nREASON: {e}\n{create_table_query}')
                else:
                    print(f'SUCCESSFULLY CREATED TABLE NAMED {self.table}')

    def __insert_db_records(self):
        insert_row_query = ''
        n_to_insert = len(self.__input_df)
        n_inserted = 0
        try:
            for row in self.__input_df.itertuples():
                insert_row_query = f'INSERT INTO {self.database}.{self.table} VALUES ('
                insert_row_query += ", ".join(str(i) if ((type(i) == int) | (type(i) == float))
                                              else '"'+str(i).replace('"', "'")+'"' for i in list(row)[1:])
                insert_row_query += ')'
                insert_row_query = insert_row_query.replace('nan', 'NULL')
                # print(insert_row_query)
                self.__cursor.execute(insert_row_query)
                n_inserted += 1
        except Exception as insert_error:
            self.__error = 1
            print(f'ERROR: INSERTED {n_inserted} of {n_to_insert}\nINSERTION NOT COMPLETED\n'
                  f'REASON: {insert_error}\n{insert_row_query}\nROLLING BACK')
            self.__db_connection.rollback()
        else:
            print(f'INSERTED {n_inserted} OF {n_to_insert} RECORDS\nINSERTION SUCCESSFUL')
        self.__db_connection.commit()

    def __close_connection(self):
        if self.__db_connection is not None:
            self.__cursor.close()
            self.__db_connection.close()
            self.__db_connection = None
            self.__cursor = None
            print('DB CONNECTION CLOSED')

    def load_to_db(self):
        if self.__error == 0:
            self.__read_input_data()
        if self.__error == 0:
            self.__get_input_schema()
        if self.__error == 0:
            self.__connect()
        if self.__error == 0:
            if not self.__database_exists():
                self.__create_db()
        if self.__error == 0:
            if not self.__table_exists():
                self.__create_db_table()
        if self.__error == 0:
            self.__insert_db_records()
        if self.__db_connection is not None:
            self.__close_connection()
        if self.__error == 0:
            print('TASK COMPLETE')
        if self.__error == 1:
            print('TASK INCOMPLETE')
