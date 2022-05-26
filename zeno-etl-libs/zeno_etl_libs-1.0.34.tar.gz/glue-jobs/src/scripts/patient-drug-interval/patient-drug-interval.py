#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@generico.in
# Purpose - script with database write for patient-drug-interval
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
from dateutil.tz import gettz

import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-rd', '--runtime_date_exp', default="0101-01-01", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
runtime_date_exp = args.runtime_date_exp
email_to = args.email_to

# env = 'stage'
# limit = 10
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()

# Run date
if runtime_date_exp != '0101-01-01':
    run_date = runtime_date_exp
else:
    # run_date = datetime.today().strftime('%Y-%m-%d')
    # Timezone aware
    run_date = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")

# runtime_date = '2021-09-01'
logger.info("Running for {}".format(run_date))

# Period end date
# Paramatrize it
period_end_d_ts = datetime.strptime(run_date, '%Y-%m-%d') - timedelta(days=1)
period_end_d = period_end_d_ts.strftime('%Y-%m-%d')

# data to be fetched

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

sales_q = """
        SELECT
            "patient-id",
            "drug-id",
            "created-date" as "bill-date"
        FROM
            "sales"
        WHERE "created-date" <= '{0}'
    """.format(period_end_d)
# AND "store-id" = 2

sales_q = sales_q.replace('`', '"')
logger.info(sales_q)

data_s = rs_db.get_df(query=sales_q)
data_s.columns = [c.replace('-', '_') for c in data_s.columns]
logger.info(len(data_s))

logger.info("Data length is : {}".format(len(data_s)))

data_s['bill_date'] = pd.to_datetime(data_s['bill_date'])

# Drop duplicates
data_s = data_s.drop_duplicates()
logger.info("Data length after dropping duplicates is : {}".format(len(data_s)))

# Sort data
data_s = data_s.sort_values(by=['patient_id', 'drug_id', 'bill_date'])

# Previous bill date
data_s['prev_bill_date'] = data_s.groupby(['patient_id', 'drug_id'])['bill_date'].shift(1)
data_s['purchase_interval'] = (data_s['bill_date'] - data_s['prev_bill_date']).dt.days

# Group at patient_id, drug_id
data_s_grp = data_s.groupby(['patient_id', 'drug_id']).agg({'purchase_interval': ['count', 'mean', 'std']}
                                                           ).reset_index()
data_s_grp.columns = ['patient_id', 'drug_id', 'count_interval', 'mean_interval', 'std_interval']

data_s_grp['cov'] = np.round(data_s_grp['std_interval'] / data_s_grp['mean_interval'], 2)
data_s_grp = data_s_grp.round(2)

logger.info("Length of data grp is {}".format(len(data_s_grp)))

# Remove cases where cov is NULL
data_s_grp = data_s_grp[~data_s_grp['cov'].isnull()]
logger.info("Length of data grp - after removing null cases, is {}".format(len(data_s_grp)))

# DB upload columns
final_cols = ['patient_id', 'drug_id',
              'count_interval',
              'mean_interval', 'std_interval',
              'cov']

data_export = data_s_grp[final_cols]

# For redshift specific
# Convert int columns to int
for i in ['patient_id', 'drug_id']:
    data_export[i] = data_export[i].fillna(0).astype(int)

logger.info(data_export.columns)

################################
# DB WRITE
###############################

write_schema = 'prod2-generico'
write_table_name = 'patient-drug-interval'

table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

# table_info_clean = table_info[~table_info['column_name'].isin(['id', 'created-at', 'updated-at'])]

data_export.columns = [c.replace('_', '-') for c in data_export.columns]

# Mandatory lines
data_export['created-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['created-by'] = 'etl-automation'
data_export['updated-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['updated-by'] = 'etl-automation'

# Truncate and append
rs_db_write.execute(f"set search_path to '{write_schema}'", params=None)
truncate_q = f"""
 DELETE FROM
    "{write_table_name}"
"""
rs_db_write.execute(truncate_q)

# Write to DB
s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name,
                  db=rs_db_write, schema=write_schema)
logger.info("Uploading successful with length: {}".format(len(data_export)))

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()

logger.info("File ends")
