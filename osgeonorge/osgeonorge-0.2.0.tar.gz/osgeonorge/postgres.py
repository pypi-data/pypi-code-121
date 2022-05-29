#!/usr/bin/env python3

"""
The postgis module contains functions for using PostgreSQL/PostGIS
as data warehouse for data from geonorge.no

Use the module like this:

.. code-block:: python

   import os
   # Import downloader class from module
   from osgeonorge.postgis import PostGISImporter
   # Initialize class
   pg_importer = PostGISImporter(host="my.pghost.no", db_name=my_gis_db",
                                 user=os.getuser, active_schema="reguleringsplaner", cores=5)
   # Import a PostGIS dump from geonorge
   # Define indices to create
   indices = {"omrade": ("omrade", "gist", True),
              "grense": ("grense", "gist", True),
              "posisjon": ("posisjon", "gist", True),
              "arealformal": ("arealformal", "btree", False),
              "kommunenummer": ("kommunenummer", "btree", False),
              "lokalid": ("lokalid", "btree", False),
              "plantype": ("plantype", "btree", False),
              "planstatus": ("planstatus", "btree", False),
              "planidentifiksjon": ("planidentifiksjon", "btree", False),
              "utnyttingstype": ("utnyttingstype", "btree", False),
              "eierform": ("eierform", "btree", False),
              "ikrafttredelsesdato": ("ikrafttredelsesdato", "btree", False),
              "vertikalniva": ("vertikalniva", "btree", False),
              "utnyttingstall": ("utnyttingstall", "btree", False),
              }
   # Import backup file into the active schema
   pg_importer.import_pg_backup("./Plan_0000_Norge_25833_Reguleringsplaner_PostGIS.backup", indices)
"""


import psycopg2
import subprocess
from osgeonorge.utils import norwegian_to_ascii, compile_ogr_cmd, ogr_casts
import re


class PostGISImporter:
    """
    Basic class for importing data from geonorge.no into PostGIS

    """

    def __init__(
        self,
        host=None,
        port=5432,
        db_name="./",
        user=None,
        active_schema="public",
        owner=None,
        reader=None,
        cores=1,
        verbose=True,
    ):
        #: Attribute containg the PostGIS host to connect to
        self.host = host
        #: Attribute defining the port of the PostGIS host to connect to
        self.port = port
        #: Attribute defining the name of the PostGIS database to connect to
        self.db_name = db_name
        #: Attribute defining the name of the user used for connecting to the database
        self.user = user
        #: Attribute containing the name of the existing PostgreSQL user to own the schema and data
        self.owner = owner
        #: Attribute containing the name of the existing PostgreSQL user to have read only priveleges
        self.owner = owner
        #: PostgreSQL connection string used for connections
        self.connection_string = f"host={host} dbname={db_name} user={user}"
        #: Schema to use for data import
        self.active_schema = active_schema

    def pg_table_exists(self, schema, table):
        """
        Check if a PG table exists

        :param connection_string: Open connectipn to the PostgreSQL database
        :type connection_string: str
        :param schema: Name of the PostgreSQL schema to look in
        :type schema: str
        :param table: Name of the PostgreSQL table to look for
        :type table: str

        :returns: Verification of table existence
        :rtype: bool
        """

        with psycopg2.connect(self.connection_string) as con:
            con.set_session(autocommit=True)
            with con.cursor() as cur:
                cur.execute(
                    f"""SELECT EXISTS (SELECT FROM information_schema.tables
                            WHERE table_schema = '{schema}' AND table_name = '{table}');"""
                )
                res = cur.fetchone()[0]
        return res

    def import_pg_backup(self, pgbackup_file, indices, target_schema):
        """
        Import a PostgreSQL dump from Geonorge into a target schema
        and index a user defined set of columns
        For parallel import the number of cores to use can be specified

        Assumes credentias stored in a .pgpass file

        :param pgbackup_file: Path to a PostgreSQL dump file to import
        :type pgbackup_file: str
        :param indices: Dictionary with indices where keys are column names and
                    values index definitions indices for unmatched columns are ignored
        :type indices: dict
        :param target_schema: Name of the schema to import the backup to
        :type target_schema: str
        :param indices: Number of cores to use for parallel import
        :type indices: int

        :returns: 0 in case of success
        :rtype: int
        """
        p = subprocess.Popen(
            ["pg_restore", "-l", pgbackup_file], stdout=subprocess.PIPE
        )
        content = p.communicate()[0].decode("UTF8").split("\n")
        table_list = [
            c.split(" ")[4:6] for c in content if " TABLE " in c and " DATA " not in c
        ]

        subprocess.run(
            [
                "pg_restore",
                "-O",
                "-x",
                "-c",
                "-h",
                self.host,
                "-p",
                f"{self.port}",
                "-U",
                self.user,
                "-d",
                self.db_name,
                "-j",
                f"{self.cores}",
                pgbackup_file,
            ]
        )

        for table in table_list:
            source_schema = table[0]
            source_table_name = table[1]
            level = table[0].split("_")[1]
            target_table_name = f"{source_table_name}_{level}"
            with psycopg2.connect(self.connection_string) as con:
                con.set_session(autocommit=True)
                columns = get_column_names(con, table[0], table[1])
                table_indices = [
                    indices.get(column) for column in columns if indices.get(column)
                ]
                # Drop target table if it exists
                self.pg_drop_table(con, target_schema, target_table_name)
                with con.cursor() as cur:
                    # Move table to different schema
                    cur.execute(
                        f"""ALTER TABLE "{source_schema}"."{source_table_name}" SET SCHEMA "{target_schema}";"""
                    )
                    cur.execute(
                        f"""ALTER TABLE "{target_schema}"."{source_table_name}" RENAME TO "{target_table_name}";"""
                    )
                if table_indices:
                    run_maintenance(
                        con,
                        target_schema,
                        target_table_name,
                        table_indices,
                    )

        with psycopg2.connect(self.connection_string) as con:
            con.set_session(autocommit=True)
            for old_schema in {table[0] for table in table_list}:
                with con.cursor() as cur:
                    cur.execute(f"""DROP SCHEMA "{old_schema}";""")
        return 0

    def import_file(
        self, schema, table_prefix, ogr_file, content, file_fields, overwrite=False
    ):
        """
        Import ogr data to PostgreSQL/PostGIS in a unified way

        :param ogr_file: Path to an ogr readable file with GIS data to import
        :type ogr_file: str
        :param content: A dictionary describing the file content
        :type content: dict
        :param table_prefix: Prefix for the name of table to import to
        :type table_prefix: str

        :returns: 0 in case of success
        :rtype: int
        """
        print(f"Processing {ogr_file}")

        # Define how projection should be handled
        if content["projection_match"]:
            projection_handling = ["-a_srs", "EPSG:25833"]
        else:
            projection_handling = ["-t_srs", "EPSG:25833"]

        for object_type in content["object_types"]:
            table_suffix = re.sub(r"^kp", "", norwegian_to_ascii(object_type).lower())
            table_name = f"{table_prefix}_{table_suffix}"
            select_sql = []
            reference_columns = file_fields[object_type]
            for col_name in reference_columns:
                org_col_name = [
                    col
                    for idx, col in enumerate(content["object_types"][object_type])
                    if col.lower() == col_name
                ]
                if not org_col_name:
                    select_sql.append(
                        f"CAST(NULL AS {ogr_casts[reference_columns[col_name]]}) AS {col_name}"
                    )
                else:
                    select_sql.append(
                        f"CAST({org_col_name[0]} AS {ogr_casts[reference_columns[col_name]]}) AS {col_name}"
                    )
            select_where = f"objekttypenavn = '{object_type}'"

            sql_string = (
                f'SELECT {", ".join(select_sql)} from polygons WHERE {select_where}'
            )
            success = False
            count = 1
            while not success and count < 5:
                cmd = compile_ogr_cmd(
                    self.connection_string,
                    schema,
                    projection_handling,
                    table_name,
                    ogr_file,
                    sql_string=sql_string,
                    overwrite=overwrite,
                )

                if count >= 2:
                    cmd.remove("--config")
                    cmd.remove("PG_USE_COPY")
                    cmd.remove("YES")
                with subprocess.Popen(
                    cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
                ) as proc:
                    stdout, stderr = proc.communicate()
                    success = proc.returncode == 0
                count += 1
            if not success:
                raise ChildProcessError(
                    f"Command {' '.join(compile_ogr_cmd(self.connection_string, schema, projection_handling, sql_string, ogr_file, table_name))} failed!"
                )
        return 0


def schema_check(
    connection_string,
    schema,
    comment,
    owner="postgres",
    users=None,
    reader=None,
    update=True,
):
    """
    Create a schema (if needed), adds comments and grants (default) access rights

    :param connection_string: Open connection to the PostgreSQL database
    :type connection_string: str
    :param schema: Name of the PostgreSQL schema to create or update
    :type schema: str
    :param comment: A descriptive comment for schema content
    :type comment: str
    :param owner: Name of the PostgreSQL user to own the schema
    :type owner: str
    :param users: A list of names of existing postgres users that should get access
    :type users: list
    :param users: Name of the PostgreSQL (group-) user with read only access to the schema
    :type users: str
    :param update: A boolean value if access rights and comments of an existing schema should be updated
    :type update: bool

    :returns: Verification of table existence
    :rtype: bool
    """
    schema_check_sql = f"""SELECT exists(SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema}');"""
    create_schema_sql = f"""CREATE SCHEMA IF NOT EXISTS "{schema}" AUTHORIZATION "{owner}";
COMMENT ON SCHEMA "{schema}" IS '{comment}';
"""
    if reader:
        create_schema_sql += f"""
-- Make SCHEMA usable for user {reader}
GRANT USAGE ON SCHEMA "{schema}" TO {reader};
GRANT SELECT ON ALL TABLES IN SCHEMA "{schema}" TO {reader};
ALTER DEFAULT PRIVILEGES IN SCHEMA "{schema}" GRANT SELECT ON TABLES TO {reader};"""

    if users:
        for pg_user in users:
            create_schema_sql += f"""GRANT ALL ON SCHEMA "{schema}" TO "{pg_user}" WITH GRANT OPTION;
GRANT ALL ON ALL TABLES IN SCHEMA "{schema}" TO "{pg_user}" WITH GRANT OPTION;
ALTER DEFAULT PRIVILEGES IN SCHEMA "{schema}" GRANT ALL ON TABLES TO "{pg_user}" WITH GRANT OPTION;
"""
    print(create_schema_sql)
    with psycopg2.connect(connection_string) as con:
        con.set_session(autocommit=True)
        with con.cursor() as cur:
            cur.execute(schema_check_sql)
            res = cur.fetchone()
            if not res[0] or update:
                cur.execute(create_schema_sql)
    return 0


def get_column_names(connection, schema, table):
    """
    List column names of a given table

    :param connection: An open connection to the PostgreSQL database
    :type connection: An open psycopg2 connection object
    :param schema: Name of the PostgreSQL schema to look in
    :type schema: str
    :param table: Name of the PostgreSQL table to get columns from
    :type table: str

    :returns: A list of column names, an empty list is returned if the bale is not found
    :rtype: list
    """
    connection.set_session(autocommit=True)
    with connection.cursor() as cur:
        cur.execute(
            f"""SELECT column_name FROM information_schema.columns
                        WHERE table_schema='{schema}' AND table_name='{table}';"""
        )
        col_names = [row[0] for row in cur.fetchall()]
    return col_names


def run_maintenance(connection, schema, table, indices):
    """
    Create indices and vacuum table

    :param connection: An open connection to the PostgreSQL database
    :type connection: An open psycopg2 connection object
    :param schema: Name of the PostgreSQL schema to look in
    :type schema: str
    :param table: Name of the PostgreSQL table to run maintenance on
    :type table: str
    :param indices: A list of tuples with three elements: (column name (str), index type (str), cluster (bool))
    :type indices: list of tuples

    :returns: 0 in case of success
    :rtype: int

    """
    connection.set_session(autocommit=True)
    with connection.cursor() as cur:
        # Create indices on the most often used (queried) fields
        for index in indices:
            print(f"Creating indices on {index[0]} for table {table} ...")
            cur.execute(
                f'CREATE INDEX IF NOT EXISTS "{table}_{index[0]}" ON "{schema}"."{table}" USING {index[1]} ("{index[0]}")'
            )
            if index[2]:
                # Cluster indices because no further input is expected
                print("Clustering index...")
                cur.execute(
                    f'ALTER TABLE "{schema}"."{table}" CLUSTER ON "{table}_{index[0]}"'
                )
        # Vacuum Analyse table for making use of indices
        print(f"Analysing indices of table {table} ...")
        cur.execute(f'VACUUM ANALYZE "{schema}"."{table}";')
    return 0


def pg_drop_table(connection, schema, table):
    """
    Create indices and vacuum table

    :param connection: An open connection to the PostgreSQL database
    :type connection: An open psycopg2 connection object
    :param schema: Name of the PostgreSQL schema to look in
    :type schema: str
    :param table: Name of the PostgreSQL table to drop
    :type table: str

    :returns: 0 in case of success
    :rtype: int

    """
    connection.set_session(autocommit=True)
    with connection.cursor() as cur:
        cur.execute(f"""DROP TABLE IF EXISTS "{schema}"."{table}";""")
    return 0
