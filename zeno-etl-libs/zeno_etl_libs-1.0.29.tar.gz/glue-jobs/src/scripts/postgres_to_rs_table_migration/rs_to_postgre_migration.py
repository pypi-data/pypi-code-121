import argparse
import os
import sys

from pandas import DataFrame

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB, PostGreWrite
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
pg_obj = PostGreWrite()
pg_obj.open_connection()
print(f"{target_schema}.{target_table}")
tr_query = f"""delete from {target_table};"""
pg_obj.engine.execute(tr_query)
s3 = S3()

incomplete = True
last_id = None
total_pushed = 0

total_count = f"""select count(id) from "{source_schema}"."{source_table}" ;"""
df_count = pd.read_sql_query(total_count, rs_db.connection)
count = df_count.values[0]
counter = 1
while incomplete:
    logger.info("iteration no: {}".format(counter))
    limit_str = f" limit {batch_size}  " if batch_size else ""

    filter_str = f" where id > {last_id} " if last_id else ""

    query = f"""
    select
    id,
    "store-id" as store_id,
    "drug-type" as "type",
    NULL as store_name,
    NULL as dc,
    "forward-dc-id" as dc_id,
    "created-at" as uploaded_at
    from
        "{source_schema}"."{source_table}"
    {filter_str}
    order by id asc
    {limit_str} ;
    """

    df = rs_db.get_df(query=query)

    if df.empty:
        incomplete = False
    else:
        last_id = int(df['id'].values[-1])
        df.drop(columns=['id'], inplace=True)
        df.columns = [c.replace('_', '-') for c in df.columns]
        logger.info("writing batch to target table")
        df.to_sql(
            name='store_dc_mapping', con=pg_obj.engine, if_exists='append',
            chunksize=500, method='multi', index=False)
        logger.info("batch successfully written to target table")
    total_pushed += batch_size
    if total_pushed >= count:
        incomplete = False
    counter = counter + 1
rs_db.close_connection()
pg_obj.close_connection()
