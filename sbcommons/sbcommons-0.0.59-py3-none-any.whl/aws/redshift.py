from typing import List

import psycopg2 as pg2
from sbcommons.logging.lambda_logger import get_logger

logger = get_logger(__name__)


class RedshiftClient:
    """
    Class to interact with redshift DB.
    """

    def __init__(self, host: str, port: int, db_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

    def __enter__(self):
        self.connection = pg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db_name,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, *_):
        self.cursor.close()
        self.connection.close()

    def kill_locks(self, table_name: str, exlude_users: List[str] = None):
        """
        Method to call to kill all acquired locks on a given DB table.

        :param table_name: name of the table to kill all locks for
        :param exlude_users: list of usernames for whom processes should not be terminated
        """
        exclude_users_cond = f"""    AND s.usename NOT IN ('{"', '".join(exlude_users)}');""" \
            if exlude_users else ';'

        locks_query = f'SELECT DISTINCT l.pid, s.usename ' \
            f'FROM pg_locks l ' \
            f'INNER JOIN pg_stat_all_tables t ON l.relation=t.relid ' \
            f'INNER JOIN pg_stat_activity s ON l.pid = s.procpid ' \
            f'WHERE t.schemaname || \'.\' || t.relname = \'{table_name}\' ' \
            f'    AND l."granted"' \
            f'{exclude_users_cond}'
        self.cursor.execute(locks_query)
        rows = self.cursor.fetchall()

        if rows:
            kill_lock_queries = [f'SELECT pg_terminate_backend({row[0]});' for row in rows]
            kill_lock_query = '\n'.join(kill_lock_queries)
            try:
                self.cursor.execute(kill_lock_query)
            except Exception as e:
                logger.warning(f'Exception caught when killing query! One of the PIDs in: '
                               f'{rows} (first column) was probably already terminated.')
                raise e

    def load_data(self, table, s3_bucket, s3_manifest_key):
        """
        Load data into event schema.

        :param table: table name to load data to
        :param s3_bucket: bucket where data exists
        :param s3_manifest_key: key to manifest file holding entries to load
        """

        staging_table = self._create_staging_table(table)
        self.copy_to_redshift(table_name=staging_table,
                              bucket=s3_bucket,
                              s3_key=s3_manifest_key,
                              options=['CSV', 'DELIMITER AS \'|\'', 'EMPTYASNULL', 'GZIP',
                                       'MANIFEST'],
                              should_commit=False)
        nr_events = self._count_rows(staging_table)
        rows_before = self._count_rows(table)
        self._deduplicate_and_insert(table, staging_table)
        rows_after = self._count_rows(table)
        rows_inserted = rows_after - rows_before
        self.drop_table(table=staging_table)
        logger.info(f'Inserted [{rows_inserted}] new rows into: [{table}] from {nr_events} events.')
        self.connection.commit()

    def unload_query_to_s3(self, bucket: str, path: str, unload_query: str,
                           options: List[str] = None):
        """
        This function takes a redshift query and outputs it to a specified s3 path.
        The options List is an additional unload arguments.
        You can see all arguments here https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html
        """
        if not options:
            options = ["FORMAT AS CSV", "DELIMITER AS '|'", "NULL AS ''"]
        execute_query = f'''UNLOAD ('{unload_query}') 
                            TO 's3://{bucket}/{path}' 
                            iam_role 'arn:aws:iam::485206745971:role/RedshiftRole'
                            {' '.join(options)};
                            '''
        self.cursor.execute(execute_query)
        self.connection.commit()

    def vacuum_analyze(self, table: str):
        """
        Run vacuum & analyze on all tables in the provided schemas.

        :param table: str containing table to operate on
        """
        # VACUUM cannot run inside a transaction block
        self.connection.autocommit = True
        self.cursor.execute(f'VACUUM REINDEX {table};')

    def get_state(self, state_table: str, key: str):
        query = f'SELECT s.last_updated ' \
            f'FROM {state_table} s ' \
            f'WHERE s.key = \'{key}\';'
        self.cursor.execute(query)
        state = self.cursor.fetchone()
        return state[0] if state else None

    def upsert_state(self, state_table: str, key: str, value: str):
        self.kill_locks(state_table)

        if self.get_state(state_table, key):
            query = f'UPDATE {state_table} ' \
                f'SET last_updated = \'{value}\' ' \
                f'WHERE key = \'{key}\';'
        else:
            query = f'INSERT INTO {state_table} VALUES (\'{key}\', TIMESTAMP \'{value}\');'

        self.cursor.execute(query)
        self.connection.commit()

    def _create_staging_table(self, table):
        staging_table = f'{table.split(".")[1]}_staging'
        self.cursor.execute(f'CREATE TABLE {staging_table} (LIKE {table});')
        return staging_table

    def copy_to_redshift(self, table_name: str, bucket: str, s3_key: str,
                         options: List[str] = None,
                         columns: List[str] = None,
                         should_commit: bool = False):
        """
            This us a simple copy command native to redshift.
            Please note that the table_name must include the schema dot table name.
            for example view.funnel
            OBS! Set should_commit = True when this function is called to commit after run.
        """
        col_opts = f'''({', '.join(columns)})''' if columns else ''
        if not options:
            options = ['CSV', 'DELIMITER AS \'|\'', 'EMPTYASNULL', 'GZIP', 'MANIFEST']
        query = f'''
        COPY {table_name}{col_opts}
        FROM 's3://{bucket}/{s3_key}'
        CREDENTIALS 'aws_iam_role=arn:aws:iam::485206745971:role/RedshiftRole'
        {' '.join(options)};
        '''
        self.cursor.execute(query)
        if should_commit:
            self.connection.commit()

    def truncate_table(self, table_name: str):
        """
            OBS The TRUNCATE command commits the transaction in which it is run; therefore,
            you can't roll back a TRUNCATE operation, and a TRUNCATE command may commit other
            operations when it commits itself.
        """
        query = f'TRUNCATE {table_name};'
        self.cursor.execute(query)

    def _deduplicate_and_insert(self, table, staging_table):
        self.cursor.execute(f'CREATE TEMP TABLE {staging_table}_tmp (LIKE {staging_table});')
        self.cursor.execute(f'ALTER TABLE {staging_table}_tmp ADD COLUMN rank INT;')
        query = f'''
        INSERT INTO {staging_table}_tmp
        WITH deduplicated_keys AS (
            SELECT DISTINCT stg.key
            FROM {staging_table} stg
            EXCEPT
            SELECT t.key
            FROM {table} t
        ),
        one_row_per_key AS (
            SELECT
                stg.*,
                ROW_NUMBER() OVER (PARTITION BY stg.key ORDER BY stg.sent_at DESC) AS rank
            FROM deduplicated_keys dk
            INNER JOIN {staging_table} stg ON stg.key = dk.key
        )
        SELECT orpk.*
        FROM one_row_per_key orpk
        WHERE orpk.rank = 1;
        '''
        self.cursor.execute(query)
        self.cursor.execute(f'ALTER TABLE {staging_table}_tmp DROP COLUMN rank;')
        self.cursor.execute(f'INSERT INTO {table} SELECT * FROM {staging_table}_tmp;')
        self.drop_table(table=f'{staging_table}_tmp')

    def drop_table(self, table, should_commit: bool = False):
        self.cursor.execute(f'DROP TABLE {table};')
        if should_commit:
            self.connection.commit()

    def _count_rows(self, table: str) -> int:
        self.cursor.execute(f'SELECT COUNT(*) FROM {table};')
        nr_rows = self.cursor.fetchone()
        return nr_rows[0]

    def tables_in_schemas(self, schemas: List[str]) -> List[str]:
        query = f'''
        SELECT DISTINCT t.table_schema || '.' || t.table_name::TEXT AS table
        FROM information_schema.tables t
        WHERE t.table_schema IN ('{"', '".join(schemas)}')
        ORDER BY "table";
        '''
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
