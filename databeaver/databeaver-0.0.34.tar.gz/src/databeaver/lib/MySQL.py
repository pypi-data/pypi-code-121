import psycopg2
import psycopg2.extras
import configparser
import sys
import logging

from .Object import Object

class MySQL(Object):
    """
    Responsible for
    """

    DATA_TYPE_BOOLEAN = "BOOLEAN"
    DATA_TYPE_FLOAT = "FLOAT"
    DATA_TYPE_INTEGER = "INTEGER"
    DATA_TYPE_STRING = "VARCHAR(255)"
    DATA_TYPE_TEXT = "TEXT"
    DATA_TYPE_TIMESTAMP = "TIMESTAMP"

    def __init__(self):
        super().__init__()

        # Used to hold the connection to postgres
        self.connection = None

        # Connect to postgres
        self.connect()

    def connect(self):
        """
        Connect to the server. If a connection already exists do nothing.

        :return: True if a connection was created. Otherwise False.
        """

        # If we already have a connection then do nothing
        if self.connection is None:
            config = configparser.ConfigParser()
            config.read(f"{sys.path[0]}/system/config.ini")

            self.connection = psycopg2.connect(host=config['PostgreSQL']['host'],
                                               database=config['PostgreSQL']['database'],
                                               user=config['PostgreSQL']['user'],
                                               password=config['PostgreSQL']['password'])
            return True

        # We did not create a new connection during this call.
        # This does not mean we are not connected...
        return False

    def create_table(self, schema='', table_name=None, columns=None):
        """
        Description
            Creates a new table in the requested based on the column information supplied

        Responsible For
            1. Seeing if the table already exists in the given schema and raises an error as needed
            2. Creating the table as specified

        Arguments
            :param schema: Schema in which to write the data
            :param table_name: Name of the new table we want to create
            :param columns: Column Information for the table we want to create
            :return: True if a new table was created, False otherwise
        """
        logger = self.get_logger()

        # Check that the table_name was supplied
        if table_name is None:
            logger.warn("table_name must be defined")
            return

        if schema != '':
            schema = f"{schema}."

        # Format the column information in a PostgreSQL specific format
        column_list = ""
        for column in columns:
            if 'type' in column:
                data_type = column['type']
            else:
                data_type = "VARCHAR(255)"
            column_list += f"\n{column['name']} {data_type},"
        column_list = column_list[0:-1]

        try:
            cursor = self.connection.cursor()

            # create the table
            command = f"CREATE TABLE {schema}{table_name}\n(\n{column_list}\n)"
            logger.debug(command)
            cursor.execute(command)

            # close communication with the PostgreSQL database server
            cursor.close()

            # commit the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

            # Transaction has been aborted, we need to close the existing cursor and get
            cursor.close()

            # Restart the connection
            self.connection = None
            self.connect()

            # Get new cursor (not sure if I need this but for now)
            cursor = self.connection.cursor()
        finally:
            cursor.close()

    def delete_rows(self, table_name, keys_to_delete={}, schema="public", log_level=logging.DEBUG):
        """
        Delete Rows the given table

        :param table_name:
        :param keys_to_delete:
        :param schema: Schema the table resides in. Default is 'public'
        :param log_level: Logging in this method will be done at the specified level. Default debug
        :return:
        """
        logger = self.get_logger()

        # Delete all rows in the table
        where_clause = "WHERE 1=1\n"
        for key, values in keys_to_delete.items():
            new_values = []
            for val in values:
                new_values.append(f"'{val}'")

            new_values = ", ".join(new_values)
            where_clause += f"AND {str(key)} IN ({new_values})\n"

        delete_stmt = f"DELETE FROM {schema}.{table_name}\n{where_clause};\n"
        try:
            cursor = self.connection.cursor()

            # create the table
            logger.log(log_level, delete_stmt)
            cursor.execute(delete_stmt)

            rows_deleted = cursor.rowcount
            logger.log(log_level, f"{rows_deleted} rows were deleted from {table_name}")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            cursor.close()

        ###############################################
        # Close the Cursor and commit the transaction #
        ###############################################
        try:
            # Commit the changes
            self.connection.commit()

            # Close communication with the PostgreSQL database server
            cursor.close()

        except(Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            cursor.close()

    def drop_table(self, table_name=None, schema="public"):
        """
        Drops the table in the given schema
        :param table_name:
        :param schema:
        :return:
        """
        logger = self.get_logger()

        drop_stmt = f"DROP TABLE {schema}.{table_name};"

        try:
            cursor = self.connection.cursor()

            # create the table
            cursor.execute(drop_stmt)
            logger.debug(drop_stmt)

            # close communication with the PostgreSQL database server
            cursor.close()

            # commit the changes
            self.connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            cursor.close()

    def execute(self, sql, ignore_errors=False, log_level=logging.DEBUG):
        # Get a _logger
        logger = self.get_logger()

        try:
            # Get a cursor
            cursor = self.connection.cursor()

            # Execute the statement
            logger.log(log_level, sql)
            cursor.execute(sql)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(sql)
            logger.error(error)
            if ignore_errors is False:
                raise error
        finally:
            cursor.close()

        # Close the Cursor and commit the transaction
        try:
            # Commit the changes
            self.connection.commit()

            # Close communication with the PostgreSQL database server
            cursor.close()

        except(Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            if ignore_errors is False:
                raise error
        finally:
            cursor.close()

    def insert_multi_rows(self, table_name, headers=None, data=None):
        """
        Inserts all rows in a single INSERT VALUES(), VALUES() statement

        :param table_name: Name of the table the data will be inserted into
        :param headers:
        :param data:
        :return:
        """
        logger = self.get_logger()

        if headers is None or data is None or table_name is None:
            logger.warn("No data to insert")
            return

        # Create a cursor to use for our processing
        try:
            cursor = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

        # Loop over every row of data and attempt to insert it
        headers_string = ",".join(headers)
        insert_stmt = f"INSERT INTO {table_name} ({headers_string})\n VALUES\n"
        for row in data:
            row_string = []
            for value in row:
                value = str(value).replace("'", "")
                value = f"'{value}'"
                value = value.replace("'None'", "NULL")
                row_string.append(value)

            row_string = ", ".join(row_string)
            insert_stmt += f"({row_string}),\n"

        insert_stmt = f"{insert_stmt[:-2]};"
        try:
            # create the table
            logger.info(insert_stmt)
            cursor.execute(insert_stmt)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

        try:
            # close communication with the PostgreSQL database server
            cursor.close()

            # commit the changes
            self.connection.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    def insert_list_of_tuples(self, table_name=None, schema=None, headers=None, data=None):
        """
        Generates individual insert statements and executes them against the database

        :param table_name: string - Table name to be loaded
        :param schema: string - Schema to use, will default to public if no schema is provided
        :param headers: list of strings - Columns names for the matching row data
        :param data: list of tuples -  Data to be inserted.

        :return: True if a new row was created, False otherwise
        """
        logger = self.get_logger()
        # Make sure we got data to work with
        if headers is None or data is None or table_name is None:
            logger.warn("No data to insert")
            return

        # Create a cursor to use for our processing
        try:
            cursor = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

        # Determine if we have a schema or not, and build sql accordingly
        schema_clause = ''
        if schema:
            schema_clause = f"{schema}."

        # Loop over every row of data and attempt to insert it
        for row in data:
            # Create the insert statement for this row
            headers_string = ",".join(headers)

            row_string = []
            for value in row:
                value = str(value).replace("'", "")
                value = f"'{value}'"
                value = value.replace("'None'", "NULL")
                row_string.append(value)

            row_string = ", ".join(row_string)
            insert_stmt = f"INSERT INTO {schema_clause}{table_name} ({headers_string})\n VALUES({row_string});"

            try:
                # create the table
                cursor.execute(insert_stmt)
                logger.debug(insert_stmt)
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)

        try:
            # close communication with the PostgreSQL database server
            cursor.close()

            # commit the changes
            self.connection.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    def insert_list_of_dictionaries(self, table_name, rows, log_level=logging.DEBUG):
        """
        Inserts rows into a table from a list of dictionaries

        :param table_name: String - Name of the Table to Inserted Into
        :param rows: list of dictionaries - Rows to be inserted
        :param log_level: Set the log level for level configurable log messages
        :param minimize_statements:
        :return:
        """
        logger = self.get_logger()

        # Create a cursor to use for our processing
        try:
            cursor = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

        # Clean the data and group each record by the columns it would insert (so we can run them as one statement)
        data_to_insert = {}
        for row in rows:
            columns = []
            values = []
            for key, value in row.items():
                columns.append(key)
                value = str(value).replace("'", "")
                value = f"'{value}'"
                values.append(value)

            values_string = ", ".join(values)
            columns_string = ", ".join(columns)
            if columns_string not in data_to_insert:
                data_to_insert[columns_string] = ""
            data_to_insert[columns_string] += f"({values_string}),\n"

        # Insert all records grouped by the columns they will insert
        for columns, insert_values in data_to_insert.items():
            insert_stmt = f"INSERT INTO {table_name} ({columns})\n VALUES\n{insert_values}"
            insert_stmt = f"{insert_stmt[:-2]};"
            insert_stmt = insert_stmt.replace("'None'", "NULL")
            insert_stmt = insert_stmt.replace("'Null'", "NULL")
            insert_stmt = insert_stmt.replace("''", "NULL")
            try:
                logger.log(log_level, insert_stmt)
                cursor.execute(insert_stmt)
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(insert_stmt)
                logger.error(error)
                break

        # Close the cursor and commit
        try:
            # close communication with the PostgreSQL database server
            cursor.close()

            # commit the changes
            self.connection.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    def fetchall(self, query, cursor_factory=psycopg2.extras.RealDictCursor, log_level=logging.DEBUG):
        """

        :param cursor_factory: Set to None if you want list of tuples returned
        :param query: SQL statement to be executed
        :param log_level: Level to Log non error statements as. Defaults to debug
        :return result_set: Results From The Execution of <query>
        """
        logger = self.get_logger()

        with self.connection.cursor(cursor_factory=cursor_factory) as cursor:
            # Execute the SELECT EXISTS query to see if the table is already there or not
            cursor.execute(query)
            logger.log(log_level, query)

            # Return True if the table exists, false otherwise
            return cursor.fetchall()

    def table_exists(self, table_name=None, schema='public'):
        """

        :param schema:
        :param table_name:
        :return:
        """
        logger = self.get_logger()

        select_stmt = f"""SELECT EXISTS(
                              SELECT FROM information_schema.tables
                              WHERE table_schema = '{schema}'
                              AND table_name = '{table_name}');"""

        with self.connection.cursor() as cursor:
            # Execute the SELECT EXISTS query to see if the table is already there or not
            cursor.execute(select_stmt)
            logger.debug(select_stmt)

            # Return True if the table exists, false otherwise
            return cursor.fetchone()[0]
