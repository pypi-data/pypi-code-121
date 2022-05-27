import argparse
# this is to include zeno_etl_libs in the python search path on the run time
import sys
import os

sys.path.append('../../../..')
import pandas as pd
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3

source_pg_table = "customer_value_segment"
target_rs_table = "customer-value-segment"


def main(rs_db, pg_db, s3, limit, batch_size):
    table_info = helper.get_table_info(db=rs_db, table_name=target_rs_table, schema='prod2-generico')
    columns = list(table_info['column_name'])
    # columns.remove('id')

    rs_db.execute(query=f""" delete from "prod2-generico"."{target_rs_table}"; """)

    incomplete = True
    last_id = None
    total_pushed = 0
    while incomplete:

        limit_str = f" limit {batch_size}  " if batch_size else ""

        filter_str = f" where id > {last_id} " if last_id else ""

        query = f"""
        select
            id,
            patient_id as "patient-id", 
            segment_calculation_date as "segment-calculation-date", 
            value_segment as "value-segment"
        from
            {source_pg_table} cvs
        {filter_str} 
        order by id asc 
        {limit_str} ;
        """

        df = pd.read_sql_query(query, pg_db.connection)

        if df.empty:
            incomplete = False
        else:
            last_id = int(df['id'].values[-1])
            df = df[columns]

            s3.write_df_to_db(df=df, table_name=target_rs_table, db=rs_db, schema='prod2-generico')

        total_pushed += batch_size
        if limit and limit < total_pushed:
            incomplete = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False, help="Total patients to process")
    parser.add_argument('-b', '--batch_size', default=500000, type=int, required=False, help="batch size")
    args, unknown = parser.parse_known_args()
    env = args.env
    limit = args.limit
    batch_size = args.batch_size
    os.environ['env'] = env
    logger = get_logger()
    logger.info(f"env: {env}")

    rs_db = DB()
    rs_db.open_connection()
    _s3 = S3()
    pg_db = PostGre()
    pg_db.open_connection()

    """ calling the main function """
    main(rs_db=rs_db, pg_db=pg_db, s3=_s3, limit=limit, batch_size=batch_size)

    # Closing the DB Connection
    rs_db.close_connection()
    pg_db.close_connection()
