import sqlite3 as lite
import mysql.connector as mysql
from mysql.connector.errors import Error as MySQLError
from mysql.connector import errorcode as MySQLErrorCode
import textwrap

import urllib.parse as parse
import pathlib
import os
from typing import NamedTuple
import keyring
import re
import sys

"""
General-purpose Database() object.

The database is ready to use (i.e. `connected`) upon creation.
To begin using the `Database`, making queries or inserting into it,
use the exposed API (e.g., `select(table, columns, condition) -> lite.Row:`)
or execute an explicit SQL command (e.g., `    execute(statement)`).
To create a new database, a `Database` object has to be created with
`writePermission=True`. If it does not exist yet, the database will
be created at the `Database.path` location (in **URI**).

If you want to create new tables, a dictionary(*of dictionaries*) 
containing the tables' name and their associated keys/types has 
to be passed to `Database.createTable()`. It should be in the form:

```
{table_1: {key_1: type, key_2: type, key_3: type}, 
table_2: {key_1: type, key_2: type, key_3: type}, ...}
```

The `keys` property of the `Metadata` object, and its underlying
objects, already handle the creation of the above dictionary.
Knowing that, you can quickly create a table with
`Database.createTable(Metadata.keys)`. To drop a table, use the
`Database.dropTable()` function, passing it only the table's name.
To insert data into the database, use `Database.insert()`, passing
it the table into which you want to insert and a dictionary of keys
with their associated values.

`Database` objects are created with `isolation_level = None` by default.
This is because `PEP` requires `python` to handle autocommits and
transactions as a default stance. By setting `isolation_level` to `None`,
we revert from `PEP` autocommit to `SQLite` autocommits. From there, it
is possible, using `Database.begin()`, `Database.end()`, `Database.commit()`
and `Database.rollBack()`, to manually control the transactions and commits.
This allows us to greatly increase insert speed into the database.
Similarly, `Database.asynchronous()` also changes properties of the
database to allow for faster insert. **HOWEVER**, this is a dangerous
function to use because it increases the chances of corrupt data in the
database should the server crash or should there be a power failure.

The `mtpDatabase` script in dcclab is meant to create the mtp.db
database on the cafeine2 server, under dcclab/database. It contains
the metadata of the ** Molecular Tools Platform ** `.csv` files under
dcclab/database as well as the metadata from their `.czi` files in the
cafeine2 server.

"""

class AccessDeniedError(Exception):
    def __init__(self, err):
        self.mysqlError:MySQLError = err
        super().__init__("MySQL access error: the user cannot perform the requested action: {0}".format(err))


from enum import Enum

class Type(Enum):
    Null = "NULL"
    Integer = "INTEGER"
    Real = "REAL"
    Float = "REAL"
    Text = "TEXT"
    String = "TEXT"
    Blob = "BLOB"

class Constraint(Enum):
    Primary = "PRIMARY KEY"
    Default = ""

class Column(NamedTuple):
    name: str
    type: Type
    constraint: Constraint = Constraint.Default

class Engine(Enum):
    mysql = "mysql"
    sqlite3 = "sqlite3"

class Database:
    def __init__(self, databaseURL, usePassword=True, writePermission=False):
        self.writePermission = writePermission
        self.databaseURL = databaseURL
        self.connection = None
        self.cursor = None
        self.databaseEngine = None

        self.database = None
        self.port = None
        self.usePassword = usePassword
        self.server = None

        self.databaseEngine, self.sshUser, self.sshHost, self.mysqlHost, self.mysqlUser, self.database = self.parseURL(databaseURL)

        self.connect()

    def showDatabaseInfo(self):
        class color:
            PURPLE = '\033[95m'
            CYAN = '\033[96m'
            DARKCYAN = '\033[36m'
            BLUE = '\033[94m'
            GREEN = '\033[92m'
            YELLOW = '\033[93m'
            RED = '\033[91m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'
            END = '\033[0m'

        printWidth = 70

        self.execute("select TABLE_NAME, TABLE_COMMENT from INFORMATION_SCHEMA.tables where table_schema = %s", (self.database,))
        rows = self.fetchAll()

        for row in rows:
            header = "Table: " + color.BOLD + row["TABLE_NAME"] + color.END
            print("="*printWidth)
            print(header)
            print("="*printWidth)
            print("\n".join(textwrap.wrap(row["TABLE_COMMENT"])))

            self.execute("SHOW FULL COLUMNS FROM {0}".format(row["TABLE_NAME"]))
            tableRows = self.fetchAll()
            maxFieldLength = max([ len(tableRow["Field"]) for tableRow in tableRows])

            colWidth = max(maxFieldLength+1, 20)

            formatString = "{0:" + f"{colWidth}" + "s}{1}"
            print("-"*printWidth)
            print(formatString.format("Field","Comment"))
            print("-"*printWidth)
            for tableRow in tableRows:
                description = ("\n"+" "*colWidth).join(textwrap.wrap(tableRow["Comment"],width=printWidth-colWidth))
                if len(description) <1:
                    description = "No description"
                print(formatString.format(tableRow["Field"], description))
            print("\n\n")

    def parseURL(self, url):
        #mysql://sshusername@cafeine2.crulrg.ulaval.ca/mysqlusername:mysqlpassword@questions
        match = re.search("mysql://([^@]+?)/(.*?)@(.+)", url)
        if match is not None:
            engine = Engine.mysql
            sshUser = None
            sshHost = None
            mysqlHost = match.group(1)
            mysqluser = match.group(2)
            database = match.group(3)
            return (engine, sshUser, sshHost, mysqlHost, mysqluser, database)

        match = re.search("mysql.ssh://(.+?)@([^@]+?):([^@]+?)/(.*?)@(.+)", url)
        if match is not None:
            engine = Engine.mysql
            sshUser = match.group(1)
            sshHost = match.group(2)
            mysqlHost = match.group(3)
            mysqlUser = match.group(4)
            database = match.group(5)
            return (engine, sshUser, sshHost, mysqlHost, mysqlUser, database)

        match = re.search("(sqlite|file)://(.*?)", url)
        if match is not None:
            engine = Engine.sqlite3
            sshUser = None
            sshHost = None
            mysqlHost = "127.0.0.1"
            mysqlUser = None
            database = match.group(2)
            return (engine, sshUser, sshHost, mysqlHost, mysqlUser, database)

        raise ValueError("Unrecognized or incomplete URL: {0}. Use mysql://host/mysqlusername@questions or mysql://sshusername@sshhost/mysqlusername@questions".format(url))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @property
    def path(self):
        path = pathlib.Path(self.__databasePath)
        return 'file:{}?mode={}'.format(parse.quote(path.as_posix(), safe=':/'), self.mode)

    @property
    def mode(self):
        return self.__mode

    def connect(self):
        try:
            if not self.isConnected:
                if self.databaseEngine == Engine.sqlite3:
                    self.connection = lite.connect(
                        self.database, uri=True, isolation_level=None, detect_types=lite.PARSE_DECLTYPES)
                    self.connection.row_factory = lite.Row
                    self.cursor = self.connection.cursor()
                else:
                    if self.usePassword is True:
                        if self.sshHost is not None:
                            serviceName = "mysql-{0}-ssh-{1}".format(self.mysqlHost, self.sshHost)
                        else:
                            serviceName = "mysql-{0}".format(self.mysqlHost)

                        pwd = keyring.get_password(serviceName, self.mysqlUser)
                        if pwd is None:
                            raise Exception(""" Set the password in the system password manager on the command line with:
                            python -m keyring set {0} {1}""".format(serviceName, self.mysqlUser))
                    else:
                        pwd = None

                    actualMysqlHost = self.mysqlHost
                    if self.sshHost == "cafeine2.crulrg.ulaval.ca":
                        from dcclab import Cafeine
                        self.server = Cafeine()
                        self.port = self.server.startMySQLTunnel(remote_bind_address=self.mysqlHost)
                        actualMysqlHost = "127.0.0.1"
                    else:
                        self.port = 3306

                    self.connection = mysql.connect(host=actualMysqlHost,
                                                    port=self.port,
                                                     database=self.database,
                                                     user=self.mysqlUser,
                                                     password=pwd,
                                                     use_pure=True)

                    self.cursor = self.connection.cursor(dictionary=True)

                self.enforceForeignKeys()
        except Exception as err:
            if self.connection is not None:
                self.connection.close()
                self.cursor = None
                if self.server is not None:
                    self.server.stopMySQLTunnel()
            raise(err)


    def disconnect(self):
        if self.isConnected:
            self.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def enforceForeignKeys(self):
        if self.databaseEngine == Engine.sqlite3:
            self.execute("PRAGMA foreign_keys = ON")
        else:
            self.execute("set foreign_key_checks = 1")

    def disableForeignKeys(self):
        if self.databaseEngine == Engine.sqlite3:
            self.execute("PRAGMA foreign_keys = OFF")
        else:
            self.execute("set foreign_key_checks = 0")

    def asynchronous(self):
        # Asynchronous mode means the database doesn't wait for
        # something to be entirely written before it begins
        # to write something else. It has the potential of corrupting entries
        # if the database crashed or there is a power failure.
        # However, asynchronus mode is much faster.
        if self.isConnected:
            self.execute('PRAGMA synchronous = OFF')

    def beginTransaction(self):
        if self.databaseEngine == Engine.mysql:
            if self.isConnected:
                self.execute('BEGIN')
        else:
            self.execute('BEGIN TRANSACTION')

    def endTransaction(self):
        if self.databaseEngine == Engine.mysql:
            if self.isConnected:
                self.execute('COMMIT')
        else:
            self.execute('END TRANSACTION')

    def rollbackTransaction(self):
        if self.databaseEngine == Engine.mysql:
            if self.isConnected:
                self.execute('ROLLBACK')
        else:
            self.execute('ROLLBACK')

    @property
    def isConnected(self):
        return self.connection is not None

    def commit(self):
        if self.isConnected:
            self.connection.commit()

    def rollback(self):
        if self.isConnected:
            self.connection.rollback()

    def execute(self, statement, bindings=None):
        """
        This function with "bindings" is necessary to handle binary data: it
        cannot be inserted with a string statement. The bindings are
        explained here: https://zetcode.com/db/sqlitepythontutorial/ and are
        similar to .format() but are handled properly by the sqlite3 module
        instead of a python string. Without it, binary data is inserted as a
        string, which is not good.
        """
        if self.isConnected:
            try:
                self.cursor.execute(statement, bindings)
            except MySQLError as err:
                accessDeniedErrors = [MySQLErrorCode.ER_DB_ACCESS_DENIED,
                                      MySQLErrorCode.ER_DBACCESS_DENIED_ERROR,
                                      MySQLErrorCode.ER_ACCESS_DENIED_ERROR,
                                      MySQLErrorCode.ER_TABLEACCESS_DENIED_ERROR,
                                      MySQLErrorCode.ER_COLUMNACCESS_DENIED_ERROR]
                if err.errno in accessDeniedErrors:
                    raise AccessDeniedError(err)
                else:
                    raise(err) # Nothing specific to say at this point

    def executeSelectOne(self, statement, bindings=None):
        """
        A select statement that selects a single field from a single row, fetches it and returns
        the result immediately.
        """
        self.execute(statement, bindings)
        singleRecord = self.fetchOne()
        keys = list(singleRecord.keys())
        if len(keys) == 1:
            return singleRecord[keys[0]]
        else:
            return None

    def executeSelectFetchInt(self, statement, bindings=None):
        """
        A select statement that selects a single field, fetches it, casts it
        to an int and returns the result immediately.

        If it is not an int, an exception will be raised.
        """
        return int(self.executeSelectOne(statement, bindings))

    def executeSelectFetchOneRow(self, statement, bindings = None):
        """
        A select statement that selects a single row, fetches it, and returns the result immediately
        as a dictionary.
        """
        self.execute(statement, bindings)
        return dict(self.fetchOne())

    def executeSelectFetchOneField(self, statement, bindings = None):
        """
        A select statement that selects a single field but from many rows,
        fetches it, and returns the result immediately as a dictionary.
        """
        self.execute(statement, bindings)
        rows = self.fetchAll()
        values = []

        for row in rows:
            value = list(row.values())[0]
            values.append(value)

        return values


    def fetchAll(self):
        if self.isConnected:
            return self.cursor.fetchall()

    def fetchOne(self):
        if self.isConnected:
            return self.cursor.fetchone()

    @property
    def tables(self) -> list:
        if self.databaseEngine == Engine.mysql:
            self.execute("show tables")
            rows = self.fetchAll()
            results = [ list(row.values())[0] for row in rows ]
            return results
        else:
            self.execute(".tables")
            rows = self.fetchAll()
            results = [ list(row.values())[0] for row in rows ]
            return results

    def columns(self, table) -> list:  # FixMe Find a better name?
        self.execute('SELECT * FROM "{}"'.format(table))
        columns = [description[0] for description in self.cursor.description]
        return columns

    def select(self, table, columns='*', condition=None):
        if condition is None:
            self.execute("SELECT {0} FROM {1}".format(columns, table))
        else:
            self.execute("SELECT {0} FROM {1} WHERE {2}".format(
                columns, table, condition))
        return self.fetchAll()

    def createTable(self, metadata: dict):
        if self.isConnected:
            for table, keys in metadata.items():
                statement = 'CREATE TABLE IF NOT EXISTS "{}" ('.format(table)
                attributes = []
                for key, keyType in keys.items():
                    attributes.append('{} {}'.format(key, keyType))
                statement += ",".join(attributes) + ")"
                self.execute(statement)

    def createSimpleTable(self, name, columns):
        if self.isConnected:
            statement = f'CREATE TABLE IF NOT EXISTS "{name}" '

            colStatements = []
            for c in columns:
                colStatements.append(f"{c.name} {c.type.value} {c.constraint.value}")

            statement += '(' + ','.join(colStatements) + ')'
            self.execute(statement)

    def dropTable(self, table: str):
        if self.isConnected:
            statement = 'DROP TABLE IF EXISTS "{}"'.format(table)
            self.execute(statement)

    def insert(self, table: str, entry: dict):
        if self.isConnected:
            lstKeys = []
            lstValues = []
            for key in entry.keys():
                lstKeys.append('"{}"'.format(str(key)))
                lstValues.append('"{}"'.format(str(entry[key])))
            keys = ','.join(lstKeys)
            values = ','.join(lstValues)
            statement = 'INSERT OR REPLACE INTO "{}" ({}) VALUES ({})'.format(
                table, keys, values)
            self.execute(statement)

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    db = Database("mysql://dcclab@cafeine3.crulrg.ulaval.ca/dcclab@labdata")
    db.execute('select * from files')
    print(db.fetchAll())
    # db = Database("/Users/dccote/GitHub/PyVino/raman.db")
    # db.execute('select * from files')
    # print(db.fetchAll())

