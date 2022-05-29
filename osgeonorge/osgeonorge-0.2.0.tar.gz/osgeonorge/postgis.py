#!/usr/bin/env python3

"""
The postgis module contains functions for using PostgreSQL/PostGIS
as data warehouse for data from geonorge.no

Use the module like this:

.. code-block:: python

   import os
   # Import downloader class from module
   from osgeonorge.postgis import PostGISAdapter
   # Initialize class
   ognp = PostGISAdapter(host="my.pghost.no", db_name=my_gis_db",
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
   ognp.import_pg_backup("./Plan_0000_Norge_25833_Reguleringsplaner_PostGIS.backup", indices)
"""


import os
import psycopg2
import re
import subprocess
import warnings
from functools import partial
from multiprocessing import Pool

# Non-builtin imports
from osgeonorge.utils import (
    norwegian_to_ascii,
    compile_ogr_cmd,
    ogr_casts,
    consolidate_attributes,
)


class PostGISAdapter:
    """
    Basic class for importing data from geonorge.no into PostGIS
    Stores, connection parameters, connection and provides methods
    for data import and maintenance

    :todo: a) generalize import of pg_backup
           b) parallelize more
    """

    def __init__(
        self,
        host="localhost",
        port=5432,
        db_name="postgres",
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
        self.reader = reader
        #: PostgreSQL connection string used for connections
        self.connection_string = f"host={host} dbname={db_name} user={user}"
        #: Open psycopg2 connection to the specified data base
        self.connection = psycopg2.connect(self.connection_string)
        self.connection.set_session(autocommit=True)
        #: Schema to use for data import
        self.active_schema = active_schema
        #: Attribute containing the number
        self.cores = cores

    def __exit__(self):
        self.connection.close()

    def pg_table_exists(self, table, schema=None):
        """
        Check if a PG table exists

        :param connection_string: Open connection to the PostgreSQL database
        :type connection_string: str
        :param schema: Name of the PostgreSQL schema to look in
        :type schema: str
        :param table: Name of the PostgreSQL table to look for
        :type table: str

        :returns: Verification of table existence
        :rtype: bool
        """

        if not schema:
            schema = self.active_schema

        with self.connection.cursor() as cur:
            cur.execute(
                f"""SELECT EXISTS (SELECT FROM information_schema.tables
                            WHERE table_schema = '{schema}' AND table_name = '{table}');"""
            )
            res = cur.fetchone()[0]
        return res

    def list_pg_backup_content(self, pgbackup_file):
        """
        List content of a PostgreSQL dump from Geonorge
        For parallel import the number of cores to use can be specified

        :param pgbackup_file: Path to a PostgreSQL dump file to list content of
        :type pgbackup_file: str

        :returns: tuple containing content and a list of tables
        :rtype: tuple
        """

        p = subprocess.Popen(
            ["pg_restore", "-l", pgbackup_file], stdout=subprocess.PIPE
        )
        content = p.communicate()[0].decode("UTF8").split("\n")
        table_list = [
            c.split(" ")[4:6] for c in content if " TABLE " in c and " DATA " not in c
        ]
        return content, table_list

    def import_pg_backup(self, pg_backup_file, indices, table_prefix=None, target_schema=None):
        """
        Import a PostgreSQL dump from Geonorge into a target schema
        and index a user defined set of columns
        For parallel import the number of cores to use can be specified

        Assumes credentias stored in a .pgpass file

        :param pg_backup_file: Path to a PostgreSQL dump file to import
        :type pg_backup_file: str or GeonorgeAdapter
        :param indices: Dictionary with indices where keys are column names and
                    values index definitions indices for unmatched columns are ignored
        :type indices: dict
        :param target_schema: Name of the schema to import the backup to
        :type target_schema: str

        :returns: 0 in case of success
        :rtype: int
        """
        if type(pg_backup_file).__name__ == "GeonorgeAdapter":
            pg_backup_files = [
                os.path.join(pg_backup_file.work_dir, list(val[1])[0])
                for val in pg_backup_file.current_zip_content
            ]
        else:
            pg_backup_files = [pg_backup_file]

        if not target_schema:
            target_schema = self.active_schema

        for pg_backup_file in pg_backup_files:
            # Get content of the backup file
            content, table_list = self.list_pg_backup_content(pg_backup_file)

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
                    pg_backup_file,
                ]
            )

            for table in table_list:
                source_schema = table[0]
                source_table_name = table[1]
                level = table[0].split("_")[1]
                target_table_name = f"{table_prefix}_{source_table_name}_{level}" if table_prefix else f"{source_table_name}_{level}"
                columns = self.get_column_names(source_table_name)
                table_indices = [
                    indices.get(column) for column in columns if indices.get(column)
                ]
                # Drop target table if it exists
                self.pg_drop_table(target_table_name)
                self.pg_drop_table(source_table_name)
                with self.connection.cursor() as cur:
                    # Move table to different schema
                    cur.execute(
                        f"""ALTER TABLE "{source_schema}"."{source_table_name}" SET SCHEMA "{target_schema}";"""
                    )
                    cur.execute(
                        f"""ALTER TABLE "{target_schema}"."{source_table_name}" RENAME TO "{target_table_name}";"""
                    )
                if table_indices:
                    self.run_maintenance(
                        target_schema,
                        target_table_name,
                        table_indices,
                    )

            for old_schema in {table[0] for table in table_list}:
                with self.connection.cursor() as cur:
                    cur.execute(f"""DROP SCHEMA "{old_schema}";""")
        return 0

    def import_files(
        self,
        table_prefix,
        geonorge_adapter,
        schema=None,
        where_clause=None,
        target_crs=25833,
        remove_prefix=None,
        overwrite=False,
    ):
        """
        Import ogr data from GeonoreAdapter to PostgreSQL/PostGIS in a unified way

        :param table_prefix: Prefix for the name of table to import to
        :type table_prefix: str
        :param where_clause: SQL WHERE-clause without the 'WHERE' keyword to limit import
        :type where_clause: str
        :param target_crs: EPSG code of the target Coordinate Reference System
        :type target_crs: int
        :param schema: Name of the PostgreSQL schema to import into
        :type schema: str
        :param remove_prefix: Prefix to remove from object types (if dataset is to be splitted by objecttype)
        :type remove_prefix: str

        :returns: 0 in case of success
        :rtype: int
        """

        import_dict = geonorge_adapter.current_ogr_files_metadata

        if len(import_dict) < 1:
            warnings.warn("Nothing to import, please check the input")
            return None

        reference_columns = None
        if all(
            [
                layer["object_types"]
                for ogr_file in import_dict.values()
                if ogr_file
                for layer in ogr_file.values()
            ]
        ):
            reference_columns = consolidate_attributes(import_dict)

        include_layer = (
            len({layer for val in import_dict.values() for layer in val}) > 1
        )

        import_tuples = []
        for ogr_file, file_metadata in import_dict.items():
            if self.cores <= 1 or (
                len(import_dict) == 1 and len(import_dict[next(iter(import_dict))]) == 1
            ):
                [
                    import_file(
                        self.connection_string,
                        table_prefix,
                        ogr_file,
                        ogr_layer,
                        layer_content,
                        where_clause=where_clause,
                        reference_columns=reference_columns,
                        target_crs=target_crs,
                        schema=self.active_schema,
                        remove_prefix=remove_prefix,
                        include_layer=include_layer,
                        overwrite=overwrite,
                    )
                    for ogr_layer, layer_content in file_metadata.items()
                ]
            else:
                import_tuples.extend(
                    [
                        (table_prefix, ogr_file, ogr_layer, layer_content)
                        for ogr_layer, layer_content in file_metadata.items()
                    ]
                )
        if import_tuples:
            import_with_kwargs = partial(
                import_file,
                self.connection_string,
                where_clause=where_clause,
                reference_columns=reference_columns,
                target_crs=target_crs,
                schema=self.active_schema,
                remove_prefix=remove_prefix,
                include_layer=include_layer,
                overwrite=overwrite,
            )
            with Pool(self.cores) as p:
                p.starmap(import_with_kwargs, import_tuples)

    def schema_check(
        self,
        comment,
        schema=None,
        owner="postgres",
        users=None,
        reader=None,
        update=True,
    ):
        """
        Create a schema (if needed), adds comments and grants (default) access rights

        :param comment: A descriptive comment for schema content
        :type comment: str
        :param schema: Name of the PostgreSQL schema to create or update
        :type schema: str
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
        if not schema:
            schema = self.active_schema

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

        with self.connection.cursor() as cur:
            cur.execute(schema_check_sql)
            res = cur.fetchone()
            if not res[0] or update:
                cur.execute(create_schema_sql)

        return 0

    def get_column_names(self, table, schema=None):
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

        if not schema:
            schema = self.active_schema

        with self.connection.cursor() as cur:
            cur.execute(
                f"""SELECT column_name FROM information_schema.columns
                        WHERE table_schema='{schema}' AND table_name='{table}';"""
            )
            col_names = [row[0] for row in cur.fetchall()]
        return col_names

    def run_maintenance(self, table, indices, schema=None):
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

        if not schema:
            schema = self.active_schema

        table_columns = self.get_column_names(table, schema=schema)

        with self.connection.cursor() as cur:
            # Create indices on the most often used (queried) fields
            for index in indices:
                if not index[0] in table_columns:
                    warnings.warn(f"Column {index[0]} not found in table {table}, skipping...")
                    continue
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

    def pg_drop_table(self, table, schema=None):
        """
        Create indices and vacuum table

        :param schema: Name of the PostgreSQL schema to look in
        :type schema: str
        :param table: Name of the PostgreSQL table to drop
        :type table: str

        :returns: 0 in case of success
        :rtype: int

        """

        if not schema:
            schema = self.active_schema

        with self.connection.cursor() as cur:
            cur.execute(f"""DROP TABLE IF EXISTS "{schema}"."{table}";""")
        return 0


def import_file(
    connection_string,
    table_prefix,
    ogr_file,
    layer,
    content,
    reference_columns=None,
    where_clause=None,
    target_crs=25833,
    schema=None,
    include_layer=True,
    remove_prefix=None,
    overwrite=False,
    unify_attributes=True,
):
    """
    Import ogr data to PostgreSQL/PostGIS in a unified way

    :param table_prefix: Prefix for the name of table to import to
    :type table_prefix: str
    :param ogr_file: Path to an ogr readable file with GIS data to import
    :type ogr_file: str
    :param layer: Name of the layer(s) for the file to import
    :type layer: str
    :param content: A dictionary describing the content of the layer of a given OGR file
    :type content: dict
    :param file_fields: A dictionary describing the attribute columns of the layer of the input file
    :type file_fields: dict
    :param where_clause: SQL WHERE-clause without the 'WHERE' keyword to limit import
    :type where_clause: str
    :param target_crs: EPSG code of the target Coordinate Reference System
    :type target_crs: int
    :param schema: Name of the PostgreSQL schema to import into
    :type schema: str
    :param remove_prefix: Prefix to remove from object types (if dataset is to be splitted by objecttype)
    :type remove_prefix: str

    :returns: 0 in case of success
    :rtype: int
    """
    print(f"Processing {ogr_file}")

    if not schema:
        schema = "public"

    if include_layer and table_prefix:
        table_prefix = f"{table_prefix}_{layer}"

    if not table_prefix and not layer:
        raise ValueError("Either table prefix or layer must be given")

    # Define how projection should be handled
    if content and content["projection_match"]:
        projection_handling = ["-a_srs", f"EPSG:{target_crs}"]
    else:
        projection_handling = ["-t_srs", f"EPSG:{target_crs}"]

    compile_cmd = partial(
        compile_ogr_cmd,
        connection_string,
        schema,
        projection_handling,
        ogr_file,
        overwrite=overwrite,
    )
    kwargs_list = []
    if content and content["fields"] and content["object_types"]:
        for object_type in content["object_types"]:
            table_suffix = re.sub(
                r"^{}".format(remove_prefix),
                "",
                norwegian_to_ascii(object_type).lower(),
            )
            table_name = f"{table_prefix}_{table_suffix}"
            select_sql = []
            if reference_columns:
                layer_reference_columns = reference_columns[layer][object_type]
            for col_name in layer_reference_columns:
                org_col_name = [
                    col
                    for idx, col in enumerate(content["object_types"][object_type])
                    if col.lower() == col_name
                ]
                if not org_col_name:
                    select_sql.append(
                        f"CAST(NULL AS {ogr_casts[layer_reference_columns[col_name]]}) AS {col_name}"
                    )
                else:
                    select_sql.append(
                        f"CAST({org_col_name[0]} AS {ogr_casts[layer_reference_columns[col_name]]}) AS {col_name}"
                    )
            select_where = f"objekttypenavn = '{object_type}'"
            if where_clause:
                select_where = f"({select_where}) AND ({where_clause})"
            sql_string = (
                f'SELECT {", ".join(select_sql)} from polygons WHERE {select_where}'
            )
            kwargs_list.append(
                (
                    table_name,
                    {
                        "where": None,
                        "layer": None,
                        "sql_string": sql_string,
                    },
                )
            )
    else:
        table_name = table_prefix or layer
        kwargs_list.append(
            (
                table_name,
                {
                    "where": where_clause,
                    "layer": layer,
                    "sql_string": None,
                },
            )
        )

    for kwargs in kwargs_list:
        success = False
        count = 1
        while not success and count < 5:
            cmd = compile_cmd(kwargs[0], **kwargs[1])
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
                f"Command {' '.join(compile_ogr_cmd(connection_string, schema, projection_handling, ogr_file, kwargs[0], **kwargs[1]))} failed!"
            )
    return 0
