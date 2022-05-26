#!/usr/bin/env python
# coding: utf-8

# !/usr/bin/env python
# coding: utf-8
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
import datetime
from dateutil.tz import gettz

schema = 'prod2-generico'
table_name = 'buying-manager'

parser = argparse.ArgumentParser(description="Buying manager data")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="jnanansu.bisoi@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env
logger = get_logger()
rs_db = DB()
rs_db.open_connection()
s3 = S3()
gs = GoogleSheet()
gs_data = gs.download(data={
    "spreadsheet_id": "1csZwlQIic9UZU6tuS9KBIGUNN_NSMJBOAKWPr1FyX08",
    "sheet_name": "Sheet1",
    "listedFields": []
})
data = pd.DataFrame(gs_data)
data.columns = [c.replace(' ', '-') for c in data.columns]
cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    logger.info(truncate_query)
    rs_db.execute(truncate_query)
data['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['created-by'] = 'etl-automation'
data['updated-by'] = 'etl-automation'
s3.write_df_to_db(df=data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)
