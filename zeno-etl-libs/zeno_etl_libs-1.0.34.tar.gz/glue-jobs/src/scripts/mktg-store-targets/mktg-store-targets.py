"""
Author:neha.karekar@zeno.health, shubham.gupta@zeno.health
Purpose: Marketing Sales and Acquisition target
"""
import argparse
import os
import sys

import pandas as pd
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet

from datetime import datetime as dt

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-sd', '--start_date', default="0", type=str, required=False)
parser.add_argument('-ed', '--end_date', default="0", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env

logger = get_logger()

# Start date and end date parameters (can be changed later)
try:
    start_date = args.start_date
    start_date = str(dt.strptime(start_date, "%Y-%m-%d").date())
    end_date = args.end_date
    end_date = str(dt.strptime(end_date, "%Y-%m-%d").date())
except ValueError:
    start_date = dt.today().replace(day=1).strftime("%Y-%m-%d")
    end_date = dt.today().strftime("%Y-%m-%d")

schema = 'prod2-generico'
table_name = 'mktg-store-targets'

rs_db = DB(read_only=False)
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

read_schema = 'prod2-generico'

# Delete records of current month from table data
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f"""
       DELETE
       FROM
           "{read_schema}"."mktg-store-targets"
       WHERE
           DATE("month-ref-date") >= '{start_date}'
           AND DATE("month-ref-date") <= '{end_date}'
        """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)
    logger.info('Delete for recent month done')

gs = GoogleSheet()

mktg_store_targets = gs.download({
    "spreadsheet_id": "1AZQF5DF6bQjX3rEtgdZ2BUI7htoNUnf2DaKFFHLaiMg",
    "sheet_name": "MT",
    "listedFields": []})

mktg_store_targets = pd.DataFrame(mktg_store_targets)
mktg_store_targets['month-ref-date'] = mktg_store_targets['month-ref-date'].apply(pd.to_datetime, errors='coerce')
mktg_store_targets_today = mktg_store_targets[(mktg_store_targets['month-ref-date'] >= start_date) &
                                              (mktg_store_targets['month-ref-date'] <= end_date)]
# data type correction
mktg_store_targets_today['store-id'] = mktg_store_targets_today['store-id'].astype(int)
mktg_store_targets_today['target-sales'] = pd.to_numeric(mktg_store_targets_today['target-sales'], errors='coerce')
mktg_store_targets_today['target-acq'] = pd.to_numeric(mktg_store_targets_today['target-acq'], errors='coerce')

# etl
mktg_store_targets_today['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
mktg_store_targets_today['created-by'] = 'etl-automation'
mktg_store_targets_today['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
mktg_store_targets_today['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=mktg_store_targets_today[table_info['column_name']], file_name='marketing_store_targets.csv')
# upload to db
s3.write_df_to_db(df=mktg_store_targets_today[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)
