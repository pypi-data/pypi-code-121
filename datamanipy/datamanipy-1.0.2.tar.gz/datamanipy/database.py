"""Interact with a database"""

import getpass
import keyring
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import pandas
import datetime as dt
from datamanipy.database_info import DbConnInfoStore


class Database():

    """
    A class used to represent a database.

    Attributes
    ----------
    db_key : str, optional
        Key identifying a database stored in your database connection information storage (see class DbConnInfoStorage)
    scheme : {'postgresql', 'sqlite', 'mysql', 'oracle' or 'mssql'}, optional
        Dialect used to connect to the database
    host : str, optional
        Address of the database server
    port : str, optional
        TCP port number of the database server
    name : str, optional
        Database name
    user : str, optional
        Database username
    uri : str, optional
        Database URI
    application_name : str, default 'MyPythonApp'
        Name of your application. It will allows you to retrieve your connection in the database
    """

    def __init__(self, db_key=None, scheme=None, host=None, port=None, name=None, user=None, application_name='MyPythonApp'):
        self.db_key = db_key
        self.application_name = application_name
        if self.db_key is None:
            self.db_key = db_key
            self.scheme = scheme
            self.host = host
            self.port = port
            self.name = name
            self.user = user
            self.uri = scheme + '://' + user + ':********@' + host + ':' + port + '/' + name
        else:  # get database information from storage if db_key is given
            db_storage = DbConnInfoStore()
            db = db_storage.get_db(db_key)
            self.scheme = db['scheme']
            self.host = db['host']
            self.port = db['port']
            self.name = db['name']
            self.user = db['user']
            self.uri = db['uri']
        with self.connect() as con:
            pass

    def show_info(self):
        """Show database connection information"""
        print(f'db_key: {self.db_key}')
        print(f'scheme: {self.scheme}')
        print(f'host: {self.host}')
        print(f'port: {self.port}')
        print(f'name: {self.name}')
        print(f'user: {self.user}')
        print(f'uri: {self.uri}')

    def _get_password(self):
        """Get user password in credential manager"""
        password = keyring.get_password(
            self.uri, self.user)  # try to get password from credential manager
        if password is None:
            raise ValueError
        return password

    def _ask_password(self):
        """Ask for user password"""
        return getpass.getpass(
            prompt=f'Password for {self.uri}: ')  # ask for password password

    def _password(self):
        try:
            return self._get_password()
        except:
            return self._ask_password()

    def _save_password(self, password):
        """Save password in credential manager if not already saved"""
        try:  # check if password is already saved
            pwd_already_saved = (password == self._get_password())
        except:
            pwd_already_saved = False
        if pwd_already_saved == False:  # if password is not already saved
            # ask to the user if he wants to save password
            save_pwd = input('Save password? (y/n): ')
            if save_pwd == 'y':
                keyring.set_password(
                    service_name=self.uri, username=self.user, password=password)  # save password in credential manager

    def reset_password(self):
        """Reset password"""
        password = self._ask_password()
        keyring.set_password(
            service_name=self.uri, username=self.user, password=password)  # save password in credential manager

    def engine(self):
        """Create engine"""
        password = self._password()
        engine = create_engine(
            self.uri.replace("********", password),
            executemany_mode='values_only',
            connect_args={"application_name": self.application_name})
        try:
            with engine.connect() as con:
                self._save_password(password)
        except:
            raise
        return engine

    def session(self):
        """Create a database session.
        Why use a session ? https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference
        """
        engine = self.engine()
        return sessionmaker(bind=engine, autocommit=True)

    def connect(self):
        """Connect to database"""
        engine = self.engine()
        return engine.begin()

    def import_data(self, sql):
        """Import data from database
        
        Parameters
        ----------
        sql : str
            SQL query
        
        Returns
        -------
        pandas.DataFrame
        """
        with self.connect() as con:
            data = pandas.read_sql(sql=sql, con=con)
        return data

    def import_meta(self, table_name, table_schema='public'):
        """Import table metadata from database
        
        Parameters
        ----------
        table_schema : str, default 'public'
            Database schema that contains the table
        table_name : str
            Name of the table

        Returns
        -------
        pandas.DataFrame
        """
        sql = f"SELECT column_name, data_type, is_nullable, pg_catalog.col_description(format('{table_schema}.{table_name}',isc.table_schema,isc.table_name)::regclass::oid,isc.ordinal_position) FROM information_schema.columns isc WHERE table_schema = '{table_schema}' AND table_name = '{table_name}'"
        with self.connect() as con:
            data = pandas.read_sql(sql=sql, con=con)
        return data

    def insert_data(self, df, table_name, table_schema='public', if_exists='fail', index=False):
        """Insert a dataframe into the database
        
        Parameters
        ----------
        table_name : str
            Name of the table
        table_schema : str,  default 'public'
            Database schema that contains the table
        if_exists : {'fail', 'replace', 'append'}, default 'append'
            How to behave if the table already exists.
            - fail: raise a ValueError
            - replace: drop the table before inserting new values
            - append: insert new values to the existing table
        index : bool, default True
            Write DataFrame index as a column. Uses index_label as the column name in the table.





        Returns
        -------
        pandas.DataFrame
        """
        with self.connect() as con:
            df.to_sql(name=table_name, schema=table_schema,
                      con=con, if_exists=if_exists, index=False)

    def execute(self, sql):
        """Execute a SQL query
        
        Parameters
        ----------
        sql : str
            SQL query

        Returns
        -------
        sqlalchemy.engine.cursor.LegacyCursorResult
        """
        with self.connect() as con:
            start_time = dt.datetime.now()
            print("Executing SQL query...")
            print(f"\t\t>> Start time: {start_time}")
            result = con.execute(text(sql))
            print(f"\t\t>> Done in {dt.datetime.now() - start_time}")
        return result

    def execute_file(self, sql_file):
        """Execute a SQL query stored in a file
        
        Parameters
        ----------
        sql : str
            SQL file

        Returns
        -------
        sqlalchemy.engine.cursor.LegacyCursorResult
        """
        with open(sql_file, 'r') as sql_wrapper:
            sql_query = sql_wrapper.read()
            result = self.execute(sql_query)
        return result


if __name__ == "__main__":

    # db = Database(scheme='postgresql', host='arf-rdb1-7500-0.tech.araf.local.com',
    #               port='5444', name='deom', user='a-le-potier')
    db = Database(db_key='deom')

    # print('Testing import_data:')
    # assert db.import_data(
    #     'SELECT 1 AS first_column').iloc[0]['first_column'] == 1, "import_data_from_pgsql('SELECT 1 AS first_column') should be equal to 1"

    # print('Testing import_meta:')
    # assert [col for col in db.import_meta('informatin_schema', 'columns').columns] == [
    #     'column_name', 'data_type', 'is_nullable', 'col_description'], "import_meta_from_pgsql('informatin_schema', 'columns') sould have 4 columns"

    # print('Testing insert_data:')
    # data = {'name': ['Tom', 'dick', 'harry'],
    #         'age': [22, 21, 24]}
    # df = pandas.DataFrame(data)
    # db.insert_data(df, 'z_alex', 'test_insert_package_art',
    #                if_exists='replace')
    # assert df.shape[0] == db.import_data(
    #     'SELECT * FROM z_alex.test_insert_package_art').shape[0], "insert_data(df, 'z_alex', 'test_insert_package_art', if_exists='replace') should be a dataframe"

    # print('Testing execute:')
    # result = db.execute("""
    #     SET ROLE deom; 
    #     DROP TABLE IF EXISTS table_creation_test; 
    #     CREATE TABLE table_creation_test (
    #           first_name text 
    #         , last_name text
    #         , age float8
    #     );
    #     """)
