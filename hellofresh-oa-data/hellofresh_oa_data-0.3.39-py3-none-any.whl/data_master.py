"""
    DataMaster
    - Handles reading and writing data from/to Bodega
        DataReader:
            obj_r = DataReader('select * from staging.sasha_hf_zip_maps limit 10;')
            df = obj_r.get_result_of_sql_as_df()
            print(df)
        DataWriter:
            obj = DataWriter(data_df=df,
                             fq_table_name='staging.sasha_delete_this',
                             primary_key_list=['dest_zip_code', 'hellofresh_week'])
            obj.run_load_to_db()

    DataReader only runs "select" statements from tables us_oa_etl user has
    access to.
    DataWriter is meant to write data to tables us_oa_etl user has
    access to. The flow is as follows:
        1. Add/replace timestamp columns
        2. Create intermediary table with the same name as
           the fq_table_name in intermediate_tables schema.
        3. Load data to intermediary table in text only format with no constraints.
        4. Check if production table has primary key. Add passed one if passed
           primary_key_list arguments.
        5. Create prod table, with proper data types/primary keys
           and load from intermediary.
"""
import sys
import io
import os
import yaml
import hashlib
import pandas as pd
from loguru import logger
from datetime import datetime
from hellofresh_data import bodega_connect
from hellofresh_data.parameter_store import get_parameter_store_value
from psycopg2.errors import InvalidTextRepresentation, BadCopyFileFormat
from psycopg2.extras import RealDictCursor


class DataReader():

    def __init__(self, sql=None, staging_flag=False):

        self.sql = sql
        self.staging_flag = staging_flag
        self._logger = logger.bind(user='DataReader')

        self.instantiate_config()
        self.instantiate_bodega_creds()
        self.get_connection()
        self.validate_sql()

    def __del__(self):
        try:
            self.bodega_conn.close()
        except AttributeError:
            self.bodega_conn = None

    def instantiate_config(self):
        """
            Instantiate config to expose variables
        """
        self.__location__ = \
            os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = \
            yaml.safe_load(open(os.path.join(self.__location__, 'config.yml')))

    def instantiate_bodega_creds(self):
        """
            Retrieve bodega credentials for DDL
        """
        bodega_user_path = self.config['data_master']['bodega']['user']
        bodega_password_path = self.config['data_master']['bodega']['password']

        self.db_user = get_parameter_store_value(bodega_user_path)
        self.db_password = get_parameter_store_value(bodega_password_path)

    def get_connection(self):
        """
            Connecting to Bodega
        """

        try:
            conn_obj = bodega_connect.BodegaConnect(
                bodega_user=self.db_user,
                bodega_password=self.db_password,
                staging_flag=self.staging_flag)
            self.bodega_conn = conn_obj.bodega_connect()
        except Exception as err:
            self._logger.error('Failed to connect to DB')
            self._logger.error(err)

    def validate_sql(self):
        """
            Run basic checks on SQL.
            Assert:
                1. Only run `allowed_command` from config.
                2. Only one statement per query, meaning no
                    query delimiters present.

            This is more of a foolproof check vs. checking for an
            actual malicious behaviour. This "ensures" we only use this
            class for reading data.
        """
        sql_parts = self.sql.strip().split(' ')
        delimiter_count = self.sql.strip().count(';')

        allowed_command_ls = \
            self.config['data_master']['sql_validate_reader']['allowed_command']

        if sql_parts[0].lower() not in allowed_command_ls:
            self._logger.error(f'Can only run: {allowed_command_ls}')
            sys.exit(1)

        try:
            delimiter_count = int(delimiter_count)
        except Exception:
            delimiter_count = 0
            pass

        if int(delimiter_count) > 1:
            self._logger.error('Can only execute 1 sql command')
            sys.exit(1)

    def execute_sql(self, sql):
        """
            Execute passed in SQL statement. Rollback on error. Return data if
            available.
        """
        try:
            cur = self.bodega_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("{sql}".format(sql=sql))
            try:
                rowcount = cur.rowcount
            except Exception:
                pass
            self.bodega_conn.commit()
        except (InvalidTextRepresentation, BadCopyFileFormat):
            self.bodega_conn.rollback()
        except Exception as err:
            self.bodega_conn.rollback()
            self._logger.warning(err)

        try:
            data = cur.fetchall()
        except Exception:
            data = None
            pass

        return data, cur, rowcount

    def get_result_of_sql_as_list(self):
        """
            Return SQL result as a list
        """
        data, cur, rowcount = self.execute_sql(self.sql)
        try:
            col_names = [desc[0] for desc in cur.description]
        except Exception as err:
            self._logger.error(err)
            sys.exit(1)

        return data, col_names

    def get_result_of_sql_as_df(self):
        """
            Return SQL as a Data Frame
        """

        data, col_names = self.get_result_of_sql_as_list()

        return pd.DataFrame(data, columns=col_names)


class DataWriter(DataReader):

    def __init__(self,
                 data_df,
                 fq_table_name,
                 primary_key_list=None,
                 logging_flag=False,
                 auto_set_pkey_flag=False,
                 staging_flag=False):

        self.data_df = data_df
        self.fq_table_name = fq_table_name
        self.arg_primary_key_ls = primary_key_list
        self.logging_flag = logging_flag
        self.auto_set_pkey_flag = auto_set_pkey_flag
        self.staging_flag = staging_flag

        self._logger = logger.bind(user='DataWriter')

        super().instantiate_config()
        super().instantiate_bodega_creds()
        super().get_connection()
        self.instantiate_bodega_variables()

    def __del__(self):
        try:
            self.bodega_conn.close()
        except AttributeError:
            self.bodega_conn = None

    def instantiate_bodega_variables(self):
        """
            Initialize DB varibales from config file
        """

        self.prod_table_name = self.fq_table_name.split('.')[1]
        self.prod_schema_name = self.fq_table_name.split('.')[0]

        self.intermediate_schema = \
            self.config['data_master']['bodega']['intermediate_schema']
        self.stage_fq_table_name = '{}.{}'.format(self.intermediate_schema,
                                                  self.prod_table_name)

        try:
            if self.prod_schema_name in self.intermediate_schema:
                self._logger.error(
                    f'Cannot use {self.prod_schema_name} schema for prod')
                sys.exit(1)
        except IndexError:
            self._logger.error('Make sure you pass in schema.table format')
            self._logger.error(f'You passed: {self.fq_table_name}')
            sys.exit(1)

    def add_etl_pkey(self):
        """
            Generate a concatination of every column, except those in
            exclude_from_hash_concat_ls, for each row, casted as
            string and then create an md5 hash representation of that
            concatination. This can act as a primary key, useful for cases
            when pkey is either hard to determine or the column(s) you rely
            on as pkey is null.
        """
        self._logger.warning(f'Will append additional column, etl_pkey, '
                             f'which is a hash representation of every'
                             f' column concatinated.')

        exclude_from_hash_concat_ls = \
            self.config['data_master']['bodega']['exclude_from_hash_concat_ls']

        self.data_df['etl_pkey_raw'] = \
            (self.data_df.loc[:,
                              ~self.data_df.columns
                              .isin(exclude_from_hash_concat_ls)]
             .astype(str).values.sum(axis=1))

        self.data_df['etl_pkey'] = \
            ([hashlib.md5(str.encode(str(i))).hexdigest()
              for i in self.data_df['etl_pkey_raw']])

        del self.data_df['etl_pkey_raw']

    def set_primary_key_variables(self):
        """
            Runs a check on whether `self.fq_table_name` table has a
            primary key, if it does self.current_primary_key_str = True.

            If it does not and self.arg_primary_key_ls were passed in try to
            set primary key to self.arg_primary_key_ls in create_prod_ddl.

            If no current primary key and none were passed in log warning and
            proceed.
        """
        self.current_primary_key_str = self.current_primary_key_check()

        if self.current_primary_key_str:
            self.primary_key_exists = True
        elif self.arg_primary_key_ls:
            self.primary_key_exists = False
            self.arg_primary_key_str = ', '.join(self.arg_primary_key_ls)
            self.current_primary_key_str = self.arg_primary_key_str

        if (self.current_primary_key_str is None
           and self.arg_primary_key_ls is None):
            self.primary_key_exists = False
            self._logger.warning(f'Table {self.fq_table_name} does not have '
                                 f'a primary key nor will one be set.')

    def check_if_primary_keys_equal(self):
        """
            If primary key exists and arg_primary_key_ls were passed in
            see if they are equal. Alert in case they are not and proceed with
            current primary key.
        """
        if self.current_primary_key_str and self.arg_primary_key_ls:
            current_primary_key_ls = \
                [x.strip() for x in self.current_primary_key_str.split(',')]

            if set(current_primary_key_ls) != set(self.arg_primary_key_ls):
                self._logger.warning(f'Current primary key list: '
                                     f'{current_primary_key_ls} '
                                     f'does not match what was passed in: '
                                     f'{self.arg_primary_key_ls} '
                                     f'If you want to change primary keys use '
                                     f'you should do it manually i.e DBeaver. '
                                     f'Falling back to Current primary key '
                                     f'list')

    def get_ddl_column_ls(self):
        """
            Create DDL columns
            prod:
                column        text,
                column_number int,
                time_modified timestamp
            stage:
                column         text,
                column_number  text,
                time_modified  text
             stage_to_prod_cast:
                 column::text,
                 column_number::int,
                 time_modified::timestamp
        """
        prod_ddl = []
        stage_ddl = []
        stage_to_prod_cast = []

        df_types = self.data_df.infer_objects().dtypes
        df_column_names = list(self.data_df.columns)

        for i in range(len(df_types)):
            if '_date_' in df_column_names[i].lower():
                data_type = 'text'
            elif any(word in df_column_names[i].lower() for
                     word in ['_date', 'date_', ' date']):
                data_type = 'date'
            elif str(df_types[i]) == 'object':
                data_type = 'text'
            elif str(df_types[i]) == 'int64':
                data_type = 'int'
            elif str(df_types[i]) == 'float64':
                data_type = 'numeric'
            elif str(df_types[i]) == 'bool':
                data_type = 'boolean'
            elif str(df_types[i]) == 'json':
                data_type = 'json'
            elif str(df_types[i]) == 'datetime64' \
                    or str(df_types[i]) == 'datetime64[ns]':
                data_type = 'timestamp'
            else:
                data_type = 'text'

            if ' ' in df_column_names[i]:
                column_name = '"{}"'.format(df_column_names[i])
            else:
                column_name = df_column_names[i]

            prod_ddl.append('{} {}'.format(column_name, data_type))
            stage_ddl.append('{} text'.format(column_name))
            stage_to_prod_cast.append('{}::{}'.format(column_name,
                                                      data_type))

        self.prod_ddl_str = ', '.join(prod_ddl)
        self.stage_ddl_str = ', '.join(stage_ddl)
        self.stage_to_prod_cast_str = ', '.join(stage_to_prod_cast)

    def get_ddl_for_staging_db(self):
        """
            Create a DDL statement to create a table
            based on DF column names.
        """
        if self.logging_flag:
            self._logger.info('Create DDL for staging DB')

        self.staging_ddl_sql = """
                           create table if not exists {fq_table_name}
                          ({stage_ddl_str});
                           """.format(stage_ddl_str=self.stage_ddl_str,
                                      fq_table_name=self.stage_fq_table_name)

    def add_timestamp_columns(self):
        """
            Add created/updated at timestamps in UTC. Drop old ones if exits
        """
        try:
            self.data_df.drop('etl_created_at', 1, inplace=True)
        except Exception:
            pass
        try:
            self.data_df.drop('etl_updated_at', 1, inplace=True)
        except Exception:
            pass

        if self.logging_flag:
            self._logger.info('Adding DF timestamps')

        self.data_df['etl_created_at'] = \
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.data_df['etl_updated_at'] = \
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        self.data_df = self.data_df.astype({'etl_created_at': 'datetime64',
                                            'etl_updated_at': 'datetime64'})

    def create_intermediary_db_table(self):
        """
            Create table from a predefined DDL statement
        """
        if self.logging_flag:
            self._logger.info('Creating table %s', self.stage_fq_table_name)
        super().execute_sql(self.staging_ddl_sql)

    def load_df_to_intermediary(self):
        """
            Loads data into the DB table via COPY command.
            Data is split into chunks and is stored in memory while
            being loaded. Stage table is truncated prior to each exucution.
        """
        if self.logging_flag:
            self._logger.info('Inserting data into %s',
                              self.stage_fq_table_name)

        sio = io.StringIO()
        sio.write(self.data_df.to_csv(index=False,
                                      header=False,
                                      na_rep="[NULL]",
                                      chunksize=10000,
                                      mode='a'))
        sio.seek(0)

        if self.logging_flag:
            self._logger.info('Inserting %s into table %s',
                              len(self.data_df),
                              self.stage_fq_table_name)

        super().execute_sql("""truncate table {}
                            """.format(self.stage_fq_table_name))

        try:
            cur = self.bodega_conn.cursor()
            cur.copy_expert("""
                            COPY {}
                            FROM STDIN
                            WITH (FORMAT CSV, NULL "[NULL]")
                            """.format(self.stage_fq_table_name), sio)
            self.bodega_conn.commit()
        except (InvalidTextRepresentation, BadCopyFileFormat) as err:
            self.bodega_conn.rollback()
            self._logger.error(err)
            sys.exit(1)

        if self.logging_flag:
            self._logger.info('Inserted into bodega table: %s',
                              self.stage_fq_table_name)

    def current_primary_key_check(self):
        """
            Run query from information_schema to check
            if a primary key exists. Return as comma delimited string if one
            exits.
        """

        primary_key = super().execute_sql("""
        select array_to_string(array_agg(kcu.column_name::text), ', ')
               as primary_list
          from information_schema.table_constraints tco
          join information_schema.key_column_usage kcu
            on kcu.constraint_name = tco.constraint_name
           and kcu.constraint_schema = tco.constraint_schema
           and kcu.constraint_name = tco.constraint_name
         where tco.constraint_type = 'PRIMARY KEY'
           and kcu.table_name = '{table_name}'
           and kcu.table_schema = '{schema_name}'
                   """.format(table_name=self.prod_table_name,
                              schema_name=self.prod_schema_name))
        try:
            current_primary_key_str = primary_key[0][0]['primary_list']
        except IndexError:
            current_primary_key_str = None

        return current_primary_key_str

    def check_if_table_exist(self):
        """
            Return prod_exist_flag, used for primary key creation.
        """

        prod_exist_check = super().execute_sql("""
           SELECT table_name as table_name
             FROM information_schema.tables
            WHERE table_schema = '{schema_name}'
              AND table_name   = '{table_name}'
        """.format(table_name=self.prod_table_name,
                   schema_name=self.prod_schema_name))
        try:
            prod_exist_check[0][0]['table_name']
            prod_exist_flag = True
        except IndexError:
            prod_exist_flag = False

        return prod_exist_flag

    def create_prod_ddl(self):
        """
            DDL for prod table

            For primary key, only add one if:
                1. Currenly there is not primary key on the table
                2. Prod table does not currenly exist
                3. Primary key argument was passed in

            Above conditions have to ALL be met to set a primary key. Logic for
            #2 is that if a table was created without a primary key, one should
            not be set using DataWriter.
        """
        self.prod_ddl_ls = []

        prod_create_ddl_sql = """
             create table
             if not exists {fq_table_name}
                           ({prod_ddl_str});
           """.format(prod_ddl_str=self.prod_ddl_str,
                      fq_table_name=self.fq_table_name)

        if (self.primary_key_exists is False and
           self.check_if_table_exist() is False and
           self.arg_primary_key_ls):
            prod_create_primary_key_sql = """
                                    alter table {fq_table_name}
                                    add primary key ({constraint});
                                """.format(fq_table_name=self.fq_table_name,
                                           constraint=self.arg_primary_key_str)
        elif (self.check_if_table_exist() is True and self.arg_primary_key_ls):
            self._logger.warning(f'You passed in primary_key_list, however, '
                                 f'since {self.fq_table_name} already exists, '
                                 f'these will not be added as primary keys. '
                                 f'If needed, add manually via DBeaver.')
            prod_create_primary_key_sql = None
        else:
            prod_create_primary_key_sql = None

        prod_grant_ddl_sql = """
             grant all privileges on table {fq_table_name} to root;
             grant select on table {fq_table_name} to analyst;
             grant select on table {fq_table_name} to sashap;
                """.format(fq_table_name=self.fq_table_name)

        self.prod_ddl_ls.extend([prod_create_ddl_sql,
                                 prod_create_primary_key_sql,
                                 prod_grant_ddl_sql])

    def create_filter_for_prod_insert(self):
        """
            Generates the filter clause for the intermediary to prod insert
            based on primary key(s).
            i.e
                where stage.a = prod.a
                  and stage.b = prod.b --If composite primary key

        """

        pm_list = self.current_primary_key_str.split(', ')
        filter_str = ''
        if len(pm_list) > 1:
            filter_str += \
                f'where stage.{pm_list[0]}::text = prod.{pm_list[0]}::text'
            for key in pm_list[1:]:
                filter_str += (' and ')
                filter_str += (f'stage.{key}::text = prod.{key}::text ')
        else:
            filter_str += \
                f'where stage.{pm_list[0]}::text = prod.{pm_list[0]}::text'

        return filter_str.strip()

    def create_prod_insert_ddl(self):
        """
            Generate insert into prod table from intermediary.
        """

        if self.primary_key_exists:
            if_primary_key_exist_sql = """
                        where not exists
                              (select 1
                                 from {prod_fql} prod
                                {filter_clause}
                               )
                           on conflict ({constraint})
                           do nothing;
            """.format(prod_fql=self.fq_table_name,
                       filter_clause=self.create_filter_for_prod_insert(),
                       constraint=self.current_primary_key_str)
        else:
            if_primary_key_exist_sql = ''

        self.prod_insert_ddl_sql = """
                    insert into {prod_fql}
                    select {stage_to_prod_cast_str}
                      from {stage_fql} stage
                      {if_primary_key_exist_sql}
              """.format(prod_fql=self.fq_table_name,
                         stage_to_prod_cast_str=self.stage_to_prod_cast_str,
                         stage_fql=self.stage_fq_table_name,
                         if_primary_key_exist_sql=if_primary_key_exist_sql)

    def execute_ddl_commads(self):
        """
            Executes DDL statements generated in create_prod_ddl()
        """

        for sql in self.prod_ddl_ls:
            if sql:
                if self.logging_flag:
                    self._logger.debug(sql)
                    super().execute_sql(sql)
                else:
                    super().execute_sql(sql)

    def execute_load_to_prod_command(self):
        """
            Execute DDL statement generated in create_prod_insert_ddl()
        """

        if self.logging_flag:
            self._logger.debug(self.prod_insert_ddl_sql)
            data, cur, self.rowcount = \
                super().execute_sql(self.prod_insert_ddl_sql)
        else:
            data, cur, self.rowcount = \
                super().execute_sql(self.prod_insert_ddl_sql)

        self._logger.info(f'Inserted {self.rowcount} record(s) into Prod DB: '
                          f'{self.fq_table_name}')

    def run_load_to_db(self):
        """
            Run all functions
        """
        self.add_etl_pkey() if self.auto_set_pkey_flag else None
        self.set_primary_key_variables()
        if self.primary_key_exists:
            self.check_if_primary_keys_equal()
        self.add_timestamp_columns()
        self.get_ddl_column_ls()
        self.get_ddl_for_staging_db()
        self.create_intermediary_db_table()
        self.load_df_to_intermediary()
        self.create_prod_ddl()
        self.execute_ddl_commads()
        self.create_prod_insert_ddl()
        self.execute_load_to_prod_command()
