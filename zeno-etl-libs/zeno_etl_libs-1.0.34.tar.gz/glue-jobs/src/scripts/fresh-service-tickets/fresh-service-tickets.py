import argparse
import os
import sys

import pandas as pd
from pandas.io.json import json_normalize

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.fresh_service.fresh_service import FreshService

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-l', '--limit', default=None, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
limit = args.limit

logger = get_logger()

logger.info(f"env: {env}")

rs_db = DB(read_only=False)
rs_db.open_connection()

s3 = S3()

all_tickets_data = pd.DataFrame()
page = 1
check = 1

# get the last updated at
query = f"""
    select
        max("updated-at") as "max-updated-at"
    from
        "prod2-generico"."freshservice-tickets"
"""
max_update_date_df: pd.DataFrame = rs_db.get_df(query=query)
max_update_date = None
if not max_update_date_df.empty:
    max_update_date = max_update_date_df.values[0][0]

fs = FreshService()
while True:
    tickets = fs.get_tickets(page=page, updated_since=None)
    df = json_normalize(tickets)

    if limit and limit < page:
        logger.info(f"fetched given pages: {limit}")
        # this break is for testing purpose
        break

    if len(df) > 0:
        logger.info(f"page no: {page}, length len(df): {len(df)}")
        page += 1
        df['created-by'] = 'etl-automation'
        df['updated-by'] = 'etl-automation'
        all_tickets_data = all_tickets_data.append(df)
    else:
        logger.info("Fetched all tickets successfully")
        break

all_tickets_data.columns = [c.replace("_", "-") for c in all_tickets_data.columns]

# Fixing the data types
for col in ['created-at', 'updated-at', 'due-by']:
    all_tickets_data[col] = pd.to_datetime(all_tickets_data[col], errors='coerce')

for col in ['requester-id', 'responder-id']:
    # all_tickets_data[col] = all_tickets_data[col].astype('str', errors='ignore')
    all_tickets_data[col] = all_tickets_data[col].astype('Int64', errors='ignore')

col_length = {"to-emails": 240, 'description': 49000, 'description-html': 49000}
for col in col_length.keys():
    all_tickets_data[col] = all_tickets_data[col].apply(lambda x: str(x)[0:col_length[col]])

# all_tickets_data.info()
schema = 'prod2-generico'
table_name = 'freshservice-tickets'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")

logger.info(f"Table:{table_name} exists and input data has all columns")

# FIXME: Why download all tickets every time, every API call has $ attached to it. use filter in the API call
# link: https://api.freshservice.com/#filter_tickets

truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)

s3.write_df_to_db(df=all_tickets_data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)
logger.info("Pushed tickets successfully")
rs_db.close_connection()
