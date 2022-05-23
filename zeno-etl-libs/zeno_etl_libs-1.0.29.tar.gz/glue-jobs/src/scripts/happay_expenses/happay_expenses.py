import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
import pandas as pd
import dateutil
import datetime
from dateutil.tz import gettz
import numpy as np

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-d', '--full_run', default=0, type=int, required=False)

args, unknown = parser.parse_known_args()

env = args.env
full_run = args.full_run
os.environ['env'] = env
logger = get_logger()
logger.info(f"full_run: {full_run}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name = 'happay-expenses'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# max of data
happay_q = """
select
            date(max("expense-created-at")) max_exp
        from
            "prod2-generico"."happay-expenses" 
        """
rs_db.execute(happay_q, params=None)
max_exp_date: pd.DataFrame = rs_db.cursor.fetch_dataframe()
max_exp_date['max_exp'].fillna(np.nan ,inplace=True)
print(max_exp_date.info())
max_exp_date = max_exp_date['max_exp'].to_string(index=False)
print(max_exp_date)
# Read from gsheet
gs = GoogleSheet()
happay_data = gs.download(data={
    "spreadsheet_id": "1XTTsiGEJgX7lpgnVLgkEs0SQojz-F06dICAuqWZKLtg",
    "sheet_name": "Happay Data",
    "listedFields": []
})
df = pd.DataFrame(happay_data)
df[['expense_created_at', 'report_created_at']] = df[
    ['expense_created_at', 'report_created_at']] \
    .apply(pd.to_datetime, errors='coerce')
happay_expenses = df.copy()

# params
if full_run or max_exp_date == 'NaN':
    start = '2017-05-13'
else:
    start = max_exp_date
start = dateutil.parser.parse(start)
happay_expenses = happay_expenses[(happay_expenses['expense_created_at'] >= start)]
# etl
happay_expenses['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
happay_expenses['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
happay_expenses['created-by'] = 'etl-automation'
happay_expenses['updated-by'] = 'etl-automation'
happay_expenses.columns = [c.replace('_', '-') for c in happay_expenses.columns]
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=happay_expenses[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)
# Closing the DB Connection
rs_db.close_connection()