import os
import sys
import math
from datetime import datetime, timedelta, time
import logging
import gzip
import psycopg2
import psycopg2.extras
from s3.client import Client as s3_client
from clickhouse_driver import Client
from pg_s3_ch.sql_queries import (
    SQL_HISTORY,
    SQL_HISTORY_RANGE,
    SQL_HISTORY_RANGE_NO_INT,
    SQL_HISTORY_NO_INT,
    SQL_CH_TABLES,
    SQL_PG_TABLES,
    SQL_CH_SCHEMA,
    SQL_SORT_PART,
    SQL_CREATE_AS,
    SQL_DROP_TABLE,
    SQL_PARTS,
    SQL_EXCHANGE_TABLE
)

PG_HISTORY_STEP_DEFAULT = 500000
FILE_PATH = "./csv/{entity_name}_{range_from}.csv.gz"
S3_FILE_FORMAT = "{endpoint_url}/{bucket}/{upload_path}/{entity_name}_*.csv.gz"
EXPORT_PATH = "./csv"


def setup_logging():
    global logger
    logger = logging.getLogger("pg_s3_ch")
    logging.basicConfig(
        stream=sys.stdout,
        level="INFO",
        format="%(asctime)s %(processName)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_files_dir():
    try:
        logging.info('Working directory is {getcwd}'.format(getcwd=os.getcwd()))
        os.makedirs(EXPORT_PATH)
    except OSError:
        logging.info('Can\'t create directory {export_path}'.format(export_path=EXPORT_PATH))
    else:
        logging.info('{export_path} was successfully created'.format(export_path=EXPORT_PATH))


def drop_files_dir():
    if os.path.isdir(EXPORT_PATH):
        for file in os.listdir(EXPORT_PATH):
            logging.info("Remove file %s", file)
            os.remove(EXPORT_PATH + "/" + file)
        os.removedirs(EXPORT_PATH)


def sql_to_file(cnx, file_path, sql):
    """
    Save result of sql to file
    :param cnx:
    :param file_path:
    :param sql:
    :return:
    """
    with gzip.open(file_path, 'wt') as fa:
        cursor = cnx.cursor()
        cursor.copy_to(fa, '({sql})'.format(sql=sql), null='')
        cursor.close()


def file_to_s3(s3_client_, file_path, s3_path):
    """
    Save result of sql to file
    :param s3_path:
    :param s3_client_:
    :param file_path:
    :return:
    """
    logging.info(os.path.basename(file_path))
    s3_client_.upload_file(file_path, s3_path)


class PGS3CH:
    """ """

    def __init__(self, config, s3_config, ch_config, pg_config):
        """
        Init class to transfer data
        :param config:
        :param s3_config:
        :param ch_config:
        :param pg_config:
        """
        setup_logging()
        self.execution_date = os.getenv("execution_date")

        self.config = config
        self.s3_config = s3_config
        self.pg_config = pg_config
        self.ch_config = ch_config

        self.temp_table_prefix = self.ch_config.get("temp_table_prefix", "_temp_")

        self.ch_client = None
        self.connect_to_ch()

        self.entity_name = self.config["name"]
        self.key_field = self.config.get("key_field", "id")
        self.pg_history_step = self.config.get(
            "pg_history_step", PG_HISTORY_STEP_DEFAULT
        )

        self.ch_name = self.config.get("ch_name", self.entity_name)

        self.incremental = self.config.get("incremental", False)
        if self.incremental:
            self.range_parts_per_day = int(self.config.get("range_parts_per_day", 24))
            self.incremental_field = str(
                self.config.get("incremental_field", "updated_at")
            )

        self.schema_ch_insert_fields = []
        self.schema_ch_insert_names = []
        self.schema_pg_select_fields = {}
        self.ch_fields = {}
        self.key_field_is_int = True
        self.ch_exclude_columns = (
            ",".join(
                [
                    "'" + item + "'"
                    for item in self.config["ch_exclude_columns"].split(",")
                ]
            )
            if "ch_exclude_columns" in self.config
            else "''"
        )

    def get_table_schema_ch(self):
        sql = SQL_CH_SCHEMA.format(
            database=self.ch_config["database"],
            table=self.ch_name,
            exclude_columns=self.ch_exclude_columns,
        )

        logger.info(sql)
        result = self.ch_client.execute(sql)
        try:
            type_key_field = [r[1] for r in result if r[0] == self.key_field][0]
        except IndexError as E:
            logging.error('Can not find key field. Even "id" is not in schema')
            raise IndexError(E)

        if "int" not in type_key_field.lower():
            self.key_field_is_int = False

        for row in result:
            if row[0].replace('_dt', '') in self.config["ch_exclude_columns"].split(","):
                continue
            if row[2].find("Exclude") == -1:
                self.schema_pg_select_fields[row[0]] = row[1]

            if row[2].find("#OnInsert:") > -1:
                start = row[2].find("#OnInsert:") + 10
                end = row[2].find(":EndOnInsert#")
                self.schema_ch_insert_fields.append(row[2][start:end])
            else:
                self.schema_ch_insert_fields.append(row[0])
            self.schema_ch_insert_names.append(row[0])

        if len(self.schema_pg_select_fields) < 1:
            logger.info("CH schema error: %s ", self.schema_pg_select_fields)
            sys.exit(1)

        if len(self.schema_ch_insert_fields) < 1:
            logger.info(
                "CH schema error: %s. Have you already created the table?", self.ch_name
            )

            sys.exit(1)

        logger.info(
            "CH schema for %s.%s - OK", self.ch_config["database"], self.ch_name
        )

    def sync_tables(self, tables_to_exclude=None):
        """
        :param tables_to_exclude: list of tables shouldn't  being considered
        :return: tuple : (list of tables need to remove, list of tables need to create or recreate)
        """
        logger.info("Get tables from pg")
        cnx = self.connect_to_pg()

        cursor = cnx.cursor()
        tables_to_exclude = (
            ",".join(["'" + item + "'" for item in tables_to_exclude.split(",")])
            if tables_to_exclude
            else "''"
        )

        sql = SQL_PG_TABLES.format(tables_to_exclude=tables_to_exclude)
        cursor.execute(sql)
        tables_pg = [r[0] for r in cursor]
        cursor.close()
        cnx.close()

        logger.info("Get tables from ch")

        sql = SQL_CH_TABLES.format(
            database=self.ch_config["database"], tables_to_exclude=tables_to_exclude
        )
        result = self.ch_client.execute(sql)
        tables_ch = [r[0] for r in result]
        return tables_ch, tables_pg

    def save_sync_tables(self, client_description, save_table_name, tables_to_exclude):
        """

        :param client_description:
        :param save_table_name:
        :param tables_to_exclude:
        :return: None
        """
        tables_ch, tables_pg = self.sync_tables(tables_to_exclude=tables_to_exclude)
        tables_to_remove = [c for c in tables_ch if c not in tables_pg]

        new_tables = []
        for row in tables_pg:
            items = {
                "client_description": client_description,
                "table_name_ch": row,
                "table_name_pg": row,
                "database_pg": self.pg_config["database"],
                "database_ch": self.ch_config["database"],
            }

            new_tables.append(items)

        table_name = f"{save_table_name}"
        if len(tables_pg) > 0:
            columns = list(items.keys())
            columns = ",".join(columns)

        for items in new_tables:

            sql_stat = "SELECT 1 FROM {table_name} WHERE database_pg = '{database_pg}' AND table_name_pg = '{table_name_pg}' AND database_ch = '{database_ch}'".format(
                table_name=table_name,
                database_pg=self.pg_config["database"],
                table_name_pg=items["table_name_pg"],
                database_ch=self.ch_config["database"],
            )

            check_statement = self.ch_client.execute(sql_stat)
            if len(check_statement) == 0:
                logger.info("Add new table %s", table_name)
                self.ch_client.execute(
                    f"INSERT INTO {table_name} ({columns}) VALUES",
                    [items],
                    types_check=True,
                )

        for items in tables_to_remove:
            drop_stat = "DROP TABLE IF EXISTS  {database_ch}.{table_name_pg}".format(
                database_ch=self.ch_config["database"], table_name_pg=items
            )
            logger.info(drop_stat)

    def connect_to_ch(self):

        settings = {"insert_quorum": 3}

        self.ch_client = Client(
            host=self.ch_config["host"],
            user=self.ch_config["user"],
            password=self.ch_config["password"],
            database=self.ch_config["database"],
            settings=settings,
        )

    def connect_to_pg(self):
        cnx = psycopg2.connect(
            user=self.pg_config["user"],
            password=self.pg_config["password"],
            host=self.pg_config["host"],
            port=self.pg_config["port"],
            database=self.pg_config["database"],
            sslmode="disable",
        )

        cnx.set_client_encoding("UTF8")
        return cnx

    def extract_to_s3(self):
        logger.info("Starting extract to s3")
        cnx = self.connect_to_pg()
        cursor = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql_history_local = SQL_HISTORY

        if self.key_field_is_int:
            sql = SQL_HISTORY_RANGE.format(
                key_field=self.key_field, name=self.entity_name
            )
            cursor.execute(sql)
        else:
            logger.info("Change logic of extracting data")
            sql = SQL_HISTORY_RANGE_NO_INT.format(
                key_field=self.key_field, name=self.entity_name
            )
            cursor.execute(sql)
            sql_history_local = SQL_HISTORY_NO_INT

        for row in cursor:
            min_id = row["min_id"]
            max_id = row["max_id"]
        cursor.close()

        logger.info("Min ID: %d", min_id)
        logger.info("Max ID: %d", max_id)

        if min_id is None or max_id is None:
            logger.info("Max_id or min_id is None. Process is stopped.")
            sys.exit(0)

        step = self.pg_history_step

        end = math.ceil(max_id / step)
        logger.info("Range from 0 to %s, multiply by %s", end, step)

        client = s3_client(
            aws_access_key_id=self.s3_config["S3_ACCESS_KEY"],
            aws_secret_access_key=self.s3_config["S3_ACCESS_SECRET"],
            endpoint_url=self.s3_config["S3_ENDPOINT_URL"],
            bucket=self.s3_config["S3_TOPMIND_CLIENT_DATA_BUCKET"],
        )
        create_files_dir()

        for _id in range(0, end):
            range_from = min_id + _id * step
            range_to = min_id + _id * step + step - 1

            sql = sql_history_local.format(
                key_field=self.key_field,
                name=self.entity_name,
                fields='"' + '","'.join(self.schema_pg_select_fields.keys()) + '"',
                range_from=range_from,
                range_to=range_to,
            )

            logger.info(sql)
            file_path = FILE_PATH.format(entity_name=self.entity_name, range_from=range_from)
            logger.info("Saving local: %s", file_path)
            sql_to_file(cnx, file_path, sql)

            path = "{upload_path}/{filename}".format(
                upload_path=self.s3_config["UPLOAD_PATH"],
                filename=os.path.basename(file_path),
            )
            logger.info("Copying to S3: %s", self.s3_config["S3_ENDPOINT_URL"] + '/' + path)
            file_to_s3(client, file_path, path)

        cnx.close()
        drop_files_dir()
        logger.info("Full extract finished")

    def get_partion_sorting_key(self):
        sql = SQL_SORT_PART.format(
            database=self.ch_config["database"], name=self.ch_name
        )

        result = self.ch_client.execute(sql)[0]

        return result

    def create_temporary_table(self):

        order_by, partition_by = self.get_partion_sorting_key()
        temp_table_partition_by = partition_by
        temp_table_order_by = order_by

        sql = SQL_CREATE_AS.format(
            staging_database=self.ch_config["staging_database"],
            temp_table_prefix=self.temp_table_prefix,
            database=self.ch_config["database"],
            table=self.ch_name,
            temp_table_order_by=temp_table_order_by
            if temp_table_order_by != ""
            else "tuple()",
            temp_table_partition_by=temp_table_partition_by,
        )
        logger.info(sql)
        self.ch_client.execute(sql)

    def drop_temporary_table(self):

        sql = SQL_DROP_TABLE.format(
            database=self.ch_config["staging_database"],
            prefix=self.temp_table_prefix,
            table=self.ch_name,
        )
        self.ch_client.execute(sql)
        logger.info(sql)

    def optimize(self):
        """
        Optimize table
        :return: None
        """
        sql = SQL_PARTS.format(
            database=self.ch_config["database"], table=self.ch_name
        )
        result = self.ch_client.execute(sql)

        for row in result:
            logger.info("Partition %s has %s parts", row[0], row[1])

            sql_optimize = """OPTIMIZE TABLE {database}.{table} ON CLUSTER '{{cluster}}' PARTITION {partition} """.format(
                database=self.ch_config["database"],
                table=self.ch_name,
                partition=row[0],
            )
            logger.info(sql_optimize)
            self.ch_client.execute(sql_optimize)
            logger.info("OK")

    def s3_to_temp(self):
        """

        :return:
        """

        schema = []
        schema_insert = []

        for k in self.schema_pg_select_fields:
            schema.append(k + " " + self.schema_pg_select_fields[k])

        for k in self.schema_ch_insert_fields:
            schema_insert.append(k)

        logger.info(
            "Copying from %s/%s to %s.%s%s",
            self.s3_config["S3_ENDPOINT_URL"],
            self.s3_config["S3_TOPMIND_CLIENT_DATA_BUCKET"],
            self.ch_config["database"],
            self.temp_table_prefix,
            self.ch_name,
        )
        s3_file_path = S3_FILE_FORMAT.format(endpoint_url=self.s3_config["S3_ENDPOINT_URL"],
                                        bucket=self.s3_config["S3_TOPMIND_CLIENT_DATA_BUCKET"],
                                        upload_path=self.s3_config["UPLOAD_PATH"],
                                        entity_name=self.entity_name)

        sql = """
            INSERT INTO {staging_database}.{temp_table_prefix}{table}  ({schema_insert_name})
            SELECT 
                {schema_insert}, NOW()
            FROM s3("{s3_file_path}", 
                    '{S3_ACCESS_KEY}',
                    '{S3_ACCESS_SECRET}',
                    'TSV', 
                    '{schema}',
                    'gzip'
                    );
            """.format(
            s3_file_path=s3_file_path,
            schema_insert_name='"' + '","'.join(self.schema_ch_insert_names + ['ts_captured']) + '"',
            staging_database=self.ch_config["staging_database"],
            table=self.ch_name,
            temp_table_prefix=self.temp_table_prefix,

            S3_ACCESS_KEY=self.s3_config["S3_ACCESS_KEY"],
            S3_ACCESS_SECRET=self.s3_config["S3_ACCESS_SECRET"],
            entity_name=self.entity_name,
            schema=", ".join(schema),
            schema_insert=", ".join(schema_insert),
        )
        logger.info(sql)

        self.ch_client.execute(sql)

        logger.info("Loading from S3 successful")

    def exchange_temp_to_prod(self):
        """

        :return:
        """
        sql = SQL_EXCHANGE_TABLE.format(
            database_staging=self.ch_config["staging_database"],
            prefix=self.temp_table_prefix,
            database=self.ch_config["database"],
            table=self.ch_name,
        )

        logger.info(sql)
        self.ch_client.execute(sql)

    def extract_updated_to_s3(self):
        """
        Extract incremental data
        :return: None
        """
        cnx = self.connect_to_pg()

        cursor = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        range_from = datetime.combine(
            datetime.strptime(self.execution_date[0:10], "%Y-%m-%d").date(), time()
        )

        parts = self.range_parts_per_day

        client = s3_client(
            aws_access_key_id=self.s3_config["S3_ACCESS_KEY"],
            aws_secret_access_key=self.s3_config["S3_ACCESS_SECRET"],
            endpoint_url=self.s3_config["S3_ENDPOINT_URL"],
            bucket=self.s3_config["S3_TOPMIND_CLIENT_DATA_BUCKET"],
        )

        create_files_dir()

        for k in range(0, parts):
            range_to = range_from + timedelta(seconds=3600 * 24 / parts - 0.000001)
            if range_from > datetime.now() + timedelta(hours=3):
                break

            sql = SQL_HISTORY.format(
                key_field=self.incremental_field,
                name=self.entity_name,
                fields='"' + '","'.join(self.schema_pg_select_fields.keys()) + '"',
                range_from=range_from,
                range_to=range_to,
            )

            logger.info(sql)
            file_path = FILE_PATH.format(entity_name=self.entity_name, range_from=range_from)
            logger.info("Saving local: %s", file_path)
            sql_to_file(cnx, file_path, sql)

            path = "{upload_path}/{filename}".format(
                upload_path=self.s3_config["UPLOAD_PATH"],
                filename=os.path.basename(file_path),
            )
            logger.info("Copying to S3: %s", self.s3_config["S3_ENDPOINT_URL"] + '/' + path)
            file_to_s3(client, file_path, path)

            range_from = range_from + timedelta(hours=24 / parts)

        drop_files_dir()
        cursor.close()
        cnx.close()

        logging.info("extract_updated finished")

    def copy_prod_to_temp(self):
        """
        Insert all data except incrememtal to temp table
        :return: None
        """
        sql = """
                INSERT INTO {staging_database}.{temp_table_prefix}{table} 
                SELECT * FROM {database}.{table}   
                WHERE {primary_key_field} 
                   NOT IN (SELECT {primary_key_field} 
                           FROM {staging_database}.{temp_table_prefix}{table})
              """.format(
            staging_database=self.ch_config["staging_database"],
            temp_table_prefix=self.temp_table_prefix,
            database=self.ch_config["database"],
            table=self.entity_name,
            primary_key_field=self.key_field,
        )

        logging.info(sql)
        self.ch_client.execute(sql)

    def transfer_data_incremental(self):
        """
        Transfer data incremental
        :return: None
        """
        if not self.incremental:
            raise ValueError("Transfer parameter should be incremental")
        self.get_table_schema_ch()
        self.drop_temporary_table()
        self.create_temporary_table()
        self.extract_updated_to_s3()
        self.s3_to_temp()
        self.copy_prod_to_temp()
        self.exchange_temp_to_prod()
        self.optimize()
        self.drop_temporary_table()

    def transfer_data_full(self):
        """
        Transfer full data
        :return: None
        """
        self.get_table_schema_ch()
        self.extract_to_s3()
        self.drop_temporary_table()
        self.create_temporary_table()
        self.s3_to_temp()
        self.exchange_temp_to_prod()
        self.optimize()
        self.drop_temporary_table()
