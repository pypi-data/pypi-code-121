"""
Author:neha.karekar@zeno.health
Purpose: Ecommerce confirmation call attempts
# Dependencies - This requires MongoDB connection
"""
import argparse
import datetime
import json
import os
import sys
from datetime import datetime as dt
from datetime import timedelta

import dateutil
import pandas as pd
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MongoDB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

# connections
parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-d', '--data', default=None, type=str, required=False)
# data = {"end": "2021-12-31", "start": "2021-12-01", "full_run": 1, "alternate_range": 0}
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()

data = args.data
logger.info(f"data: {data}")
data = json.loads(data) if data else {}
logger.info(f"env: {env}")
logger.info(f"data: {data}")

rs_db = DB()
rs_db.open_connection()
mg_db = MongoDB()
mg_client = mg_db.open_connection("generico-crm")

s3 = S3()

# table info
schema = 'prod2-generico'
table_name = 'ecomm-outbound-connected-log'
date_field = 'call-created-at'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
# params
job_data_params = data
if job_data_params['full_run']:
    start = '2017-05-13'
elif job_data_params['alternate_range']:
    start = job_data_params['start']
else:
    start = str(dt.today().date() - timedelta(days=1))
# convert date to pymongo format
start = dateutil.parser.parse(start)

# Read Generico crm table
db = mg_client['generico-crm']
collection = db["exotelOutgoingCallLogs"].find(
    {"CallType": {"$in": ["zeno-order-list", "zeno-order-details"]}, "status": "connected",
     "createdAt": {"$gte": start}})
callog_outbound = pd.DataFrame(list(collection))
callog_outbound['call_attempt'] = callog_outbound.sort_values(['createdAt'], ascending=[True]) \
                                      .groupby(['order_id']) \
                                      .cumcount() + 1
callog_outbound = callog_outbound[(callog_outbound['call_attempt'] <= 3)]
callog_outbound['order_id'] = callog_outbound['order_id'].astype(str).astype(int)
callog_outbound = callog_outbound[['order_id', 'order_number', 'createdAt', 'updatedAt',
                                   'CallFrom', 'call_attempt']]
dict = {'createdAt': 'call-created-at',
        'updatedAt': 'call-updated-at',
        'CallFrom': 'call-from'}
callog_outbound.rename(columns=dict, inplace=True)

# order id to patient id
zo_q = """
select
            id as "order_id",
            "patient-id"
        from
           "prod2-generico"."zeno-order" zo
        where
            date("created-at")>= '2020-12-25'
"""
rs_db.execute(zo_q, params=None)
zo: pd.DataFrame = rs_db.cursor.fetch_dataframe()
data_merge = pd.merge(callog_outbound, zo, how='left',
                      on=["order_id"])
call_outbound_log = data_merge.copy()
call_outbound_log = call_outbound_log.drop_duplicates()
call_outbound_log.columns = call_outbound_log.columns.str.lower()
call_outbound_log['patient-id'] = call_outbound_log['patient-id'].astype('Int64')
call_outbound_log['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
call_outbound_log['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
call_outbound_log['created-by'] = 'etl-automation'
call_outbound_log['updated-by'] = 'etl-automation'
call_outbound_log.columns = [c.replace('_', '-') for c in call_outbound_log.columns]
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" where "{date_field}">'{start}' '''
    logger.info(truncate_query)
    rs_db.execute(truncate_query)
    """ seek the data """
print(call_outbound_log.head(1))
print(table_info)
file_s3_uri_save = s3.save_df_to_s3(df=call_outbound_log[table_info['column_name']], file_name="call_outbound_log.csv")
s3.write_to_db_from_s3_csv(table_name=table_name,
                           file_s3_uri=file_s3_uri_save,
                           db=rs_db, schema=schema)
s3.write_df_to_db(df=call_outbound_log[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# Closing the DB Connection
rs_db.close_connection()
