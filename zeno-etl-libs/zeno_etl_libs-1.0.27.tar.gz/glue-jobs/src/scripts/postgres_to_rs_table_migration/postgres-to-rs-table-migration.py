import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3

import pandas as pd

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-st', '--source_table', default="", type=str, required=False)
parser.add_argument('-tt', '--target_table', default="", type=str, required=False)
parser.add_argument('-ss', '--source_schema', default="", type=str, required=False)
parser.add_argument('-ts', '--target_schema', default="", type=str, required=False)
parser.add_argument('-b', '--batch_size', default=1000, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

source_table = args.source_table
target_table = args.target_table
source_schema = args.source_schema
target_schema = args.target_schema
batch_size = args.batch_size

logger = get_logger()

logger.info(f"env: {env}")
rs_db = DB()
rs_db.open_connection()

tr_query = f""" truncate table "{target_schema}"."{target_table}" """
rs_db.execute(tr_query)

pg_obj = PostGre()
pg_obj.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=target_table, schema=target_schema)
columns = list(table_info['column_name'])

incomplete = True
last_id = None
total_pushed = 0

total_count = f"""select count(id) from "{source_schema}"."{source_table}" ;"""
df_count = pd.read_sql_query(total_count, pg_obj.connection)
count = df_count.values[0]
counter = 1
while incomplete:
    logger.info("iteration no: {}".format(counter))
    limit_str = f" limit {batch_size}  " if batch_size else ""

    filter_str = f" where id > {last_id} " if last_id else ""

    query = f"""
    select * 
    from
        "{source_schema}"."{source_table}"
    {filter_str} 
    order by id asc 
    {limit_str} ;
    """

    df = pd.read_sql_query(query, pg_obj.connection)

    if df.empty:
        incomplete = False
    else:
        last_id = int(df['id'].values[-1])
        df.drop(columns=['id'], inplace=True)
        df.columns = [c.replace('_', '-') for c in df.columns]
        logger.info("writing batch to target table")
        s3.write_df_to_db(df=df, table_name=target_table, db=rs_db, schema=target_schema)
        logger.info("batch successfully written to target table")
    total_pushed += batch_size
    if total_pushed >= count:
        incomplete = False
    counter = counter + 1
rs_db.close_connection()
pg_obj.close_connection()
