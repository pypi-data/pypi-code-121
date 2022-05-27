"""Store database connection information"""

import json
import pathlib
import os


class DbConnInfoStore():

    """
    A class used to represent a store that contains databases connection information.
    You can add a new database in your store thanks to the add_db method.
    Each database is referenced using a user-defined key (db_key).
    You can retrieve your database connexion information thanks to the get_db(db_key) method.

    Attributes
    ----------
    dir_path : os.path, default [home directory]/datamanipy
        Directoy path that contains the databases connection information storage named db_info.json


    Examples
    --------

    Add a new database in the store.

    >>> store = DbConnInfoStore()
    >>> store.add_db(db_key='mydb1', scheme='postgresql', host='localhost', port='5432', name='db1', user='myname')

    List all databases in the store.

    >>> store = DbConnInfoStore()
    >>> store.add_db(db_key='mydb2', scheme='postgresql', host='localhost', port='5432', name='db2', user='myname')
    >>> store.add_db(db_key='mydb3', scheme='postgresql', host='localhost', port='5432', name='db3', user='myname')
    >>> store.list_db()
    {'mydb2': {'scheme': 'postgresql', 'host': 'localhost', 'port': '5432', 'name': 'db1', 'user': 'myname', 'uri': 'postgresql://myname:********@localhost:5432/db2'},
     'mydb3': {'scheme': 'postgresql', 'host': 'localhost', 'port': '5432', 'name': 'db1', 'user': 'myname', 'uri': 'postgresql://myname:********@localhost:5432/db3'}}

    Print database information.

    >>> store = DbConnInfoStore()
    >>> store.add_db(db_key='mydb4', scheme='postgresql', host='localhost', port='5432', name='db4', user='myname')
    >>> store.show_db('mydb4')
    mydb4:
        scheme: postgresql
        host: localhost
        port: 5432
        name: db4
        user: myname
        uri: postgresql://myname:********@localhost:5432/db4

    Delete a database from the store.

    >>> store = DbConnInfoStore()
    >>> store.add_db(db_key='mydb5', scheme='postgresql', host='localhost', port='5432', name='db5', user='myname')
    >>> store.drop_db('mydb5')
    """

    def __init__(self, dir_path=os.path.join(pathlib.Path.home(), 'datamanipy')):
        self.dir_path = dir_path
        self.file_path = os.path.join(dir_path, 'db_info.json')
        self._create_json()

    def _create_json(self):
        """Create a folder named 'datamanipy' in the user directory"""
        if os.path.exists(self.dir_path) == False:
           os.mkdir(self.dir_path)
        if os.path.exists(self.file_path) == False:
            with open(self.file_path, 'w') as file:
                json.dump({}, file)

    def db_exists(self, db_key):
        """Check if the database key already exists in the store
        
        Parameters
        ----------
        db_key : str
            Key identifying a database potentially stored in your database connection information store
        
        Returns
        -------
        bool
        """
        with open(self.file_path, 'r') as file:
            return db_key in json.load(file).keys()

    def list_db(self):
        """List all database info"""
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def add_db(self, db_key, scheme, host, port, name, user):
        """Add a new database in your database connection information store
        
        Parameters
        ----------
        db_key : str
            User-defined key identifying the database you want to store in your database connection information store
        scheme : {'postgresql', 'sqlite', 'mysql', 'oracle' or 'mssql'}
            Dialect used to connect to the database
        host : str
            Address of the database server
        port : str
            TCP port number of the database server
        name : str
            Database name
        user : str
            Database username
        """

        if self.db_exists(db_key):
            raise KeyError('The database key {db_key} already exists.')

        else:
            db_list = self.list_db()
            db_list[db_key] = {
                'scheme': scheme,
                'host': host,
                'port': port,
                'name': name,
                'user': user,
                'uri': scheme + '://' + user + ':********@' + host + ':' + port + '/' + name}
            with open(self.file_path, 'w') as file:
                json.dump(db_list, file)

    def drop_db(self, db_key):
        """Drop a database
        
        Parameters
        ----------
        db_key : str
            Key identifying the database you want to delete from your database connection information store
        """

        if self.db_exists(db_key):
            db_list = self.list_db()
            del db_list[db_key]
            with open(self.file_path, 'w') as file:
                json.dump(db_list, file)
        else:
            raise KeyError(f'The database key {db_key} does not exist.')

    def clean(self):
        """Clean all database information store"""
        with open(self.file_path, 'w') as file:
            json.dump({}, file)

    def get_db(self, db_key):
        """Get database information

        Parameters
        ----------
        db_key : str
            Key identifying a database stored in your database connection information store
        
        Returns
        -------
        dict :
            {'scheme': database dialect, 
            'host': server address, 
            'port': TCP port number, 
            'name': database name, 
            'user': username, 
            'uri': database URI}
        """

        if self.db_exists(db_key):
            return self.list_db()[db_key]
        else:
            raise KeyError(f'The database key {db_key} does not exist.')

    def show_db(self):
        """Show database information"""
        if len(self.list_db().keys()) == 0:
            print('No database stored.')
        for db_key in self.list_db().keys():
            print(f'{db_key}:')
            for key in self.get_db(db_key):
                print(f'     {key}: {self.get_db(db_key)[key]}')


if __name__ == "__main__":

    store = DbConnInfoStore()

    store.clean()
    store.show_db()
    print(store.list_db())
    print(store.db_exists('deom'))

    store.add_db(db_key='deom', scheme='postgresql',
                    host='arf-rdb1-7500-0.tech.araf.local.com', port='5444', name='deom', user='a-le-potier')

    store.show_db()
    print(store.list_db())
    print(store.db_exists('deom'))

