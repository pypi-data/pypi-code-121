#!/usr/bin/env python
# coding: utf-8
"""
# Author - shubham.jangir@zeno.health
# Purpose - script with database write for CRM converted customers' details
"""
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

parser = argparse.ArgumentParser(description="This is ETL custom script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.jangir@zeno.health", type=str, required=False)
parser.add_argument('-rd', '--full_run', default="no", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
full_run = args.full_run
email_to = args.email_to

# env = 'stage'
# limit = 10
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

# Connections
rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()

# Run date
run_date = datetime.today().strftime('%Y-%m-%d')
# runtime_date = '2021-09-01'
logger.info("Running for {}".format(run_date))

# Period start-date
if full_run == 'yes':
    period_start_d = '2017-01-01'
else:
    # Run only for last 30days, because for earlier, status woult not change
    # It can as well be, run only for last 15days, but 30 is a good buffer
    period_start_d = (pd.to_datetime(run_date) - timedelta(days=30)).strftime('%Y-%m-%d')

logger.info("Running from {} to {}".format(period_start_d, run_date))

# Remaining data to be fetched

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params = None)

data_q = """
        SELECT 
            c.`patient-id`,
            c.`store-id`,
            c.`call-date` call_date,
            max( (case when ((d.`call-recording-url` is not null
            and d.`call-recording-url` !='') or (d.`connected` =1)) then 1 else 0 end)) as connected
        FROM
            `calling-dashboard` c
        INNER JOIN `calling-history` d
        on c.`id` = d.`calling-dashboard-id`
        WHERE
            c.`status`='closed'
            and c.`call-date` >= '{0}'
        GROUP BY
            c.`patient-id`,
            c.`store-id`,
            c.`call-date`
""".format(period_start_d)

data_q = data_q.replace('`','"')
logger.info(data_q)

rs_db.execute(data_q, params=None)
calling_dashboard_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if calling_dashboard_data is None:
    calling_dashboard_data = pd.DataFrame(columns = ['patient_id', 'store_id', 'call_date'])
calling_dashboard_data.columns = [c.replace('-', '_') for c in calling_dashboard_data.columns]
logger.info(len(calling_dashboard_data))
calling_dashboard_data.head()

calling_dashboard_data['call_date'] = pd.to_datetime(calling_dashboard_data['call_date'])

calling_dashboard_data['call_year'] = calling_dashboard_data['call_date'].dt.year
calling_dashboard_data['call_month'] = calling_dashboard_data['call_date'].dt.month

# For maximum call date in month
# Order on connected desc, then can take drop duplicates
calling_dashboard_data = calling_dashboard_data.sort_values(by = ['patient_id', 'store_id',
                                                                 'call_year', 'call_month',
                                                                  'connected'],
                                                           ascending = [True, True,
                                                                       True, True,
                                                                       False])
logger.info(len(calling_dashboard_data))

calling_dashboard_data = calling_dashboard_data.drop_duplicates(subset = ['patient_id', 'store_id',
                                                                          'call_year', 'call_month'])
logger.info(len(calling_dashboard_data))


# Find window date that is 15 days after the calling date

calling_dashboard_data['window_date'] = calling_dashboard_data['call_date'] + timedelta(days=15)

# Make a tuple of those unique patient ids

unique_patient_ids_tuple = tuple(calling_dashboard_data['patient_id'].drop_duplicates().to_list())
logger.info("Look up for {} patients".format(len(unique_patient_ids_tuple)))


read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params = None)

data_q = """
        SELECT 
            `patient-id`,
            date(`created-at`) bill_date,
            sum("revenue-value") spend
        FROM
            sales
        WHERE
            `patient-id` in {0}
            AND "bill-flag" = 'gross'
        GROUP BY
            `patient-id`,
            date(`created-at`)
""".format(unique_patient_ids_tuple)

data_q = data_q.replace('`','"')
#logger.info(data_q)

rs_db.execute(data_q, params=None)
patient_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if patient_data is None:
    patient_data = pd.DataFrame(columns = ['patient_id', 'bill_date', 'spend'])
patient_data.columns = [c.replace('-', '_') for c in patient_data.columns]
logger.info(len(patient_data))
patient_data.head()

patient_data['bill_date'] = pd.to_datetime(patient_data['bill_date'])

# Round the spend values
patient_data['spend'] = patient_data['spend'].astype(float).round(2)

# Merge patient bill data and calling dashboard data
conversion_data = pd.merge(patient_data, calling_dashboard_data, how='left', on='patient_id')

# Keep only those records from merged dataframe
# where calling date falls within the window date (converted customners)

conversion_data = conversion_data[((conversion_data['bill_date'] >= conversion_data['call_date']) & (
        conversion_data['bill_date'] <= conversion_data['window_date']))]
conversion_data.sort_values('patient_id', inplace=True)

# Find out the minimum bill date of converted customer
min_bill_date_after_conversion = conversion_data.groupby(['patient_id', 'call_date'])['bill_date'].min().to_frame(
    name='min_bill_date_after_conversion').reset_index()

# Merge minimum bill date of converted customer with conversion data from above
conversion_data = pd.merge(conversion_data, min_bill_date_after_conversion,
                           left_on=['patient_id', 'call_date', 'bill_date'],
                           right_on=['patient_id', 'call_date', 'min_bill_date_after_conversion'])
conversion_data.drop(['call_month', 'call_year', 'window_date',
                      'min_bill_date_after_conversion'], axis=1,inplace=True)


# Take latest call-date, for any bill-date, to avoid bondary cases
conversion_data = conversion_data.sort_values(by=['patient_id', 'bill_date', 'call_date'],
                                              ascending=[True, False, False])

conversion_data = conversion_data.drop_duplicates(subset=['patient_id', 'bill_date'])

# Sort again to ascending
conversion_data = conversion_data.sort_values(by=['patient_id', 'call_date'])

conversion_data = conversion_data[['patient_id', 'store_id',
                                   'call_date', 'bill_date', 'spend', 'connected']]

#################################################
# Write to dB
################################################
# Truncate table data and reset index

write_schema = 'prod2-generico'
write_table_name = 'crm-conversion-overall'

table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

# table_info_clean = table_info[~table_info['column_name'].isin(['id','created-at','updated-at'])]

rs_db_write.execute(f"set search_path to '{write_schema}'", params = None)

truncate_q = f"""
    DELETE FROM
        "{write_table_name}"
    WHERE
        "call-date" >= '{period_start_d}'
"""

truncate_q = truncate_q.replace('`','"')
logger.info(truncate_q)

rs_db_write.execute(truncate_q, params=None)

data_export = conversion_data.copy()
data_export.columns = [c.replace('_', '-') for c in data_export.columns]

# Mandatory lines
data_export['created-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['created-by'] = 'etl-automation'
data_export['updated-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['updated-by'] = 'etl-automation'

# Upload data to dB, sensitive
s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name, db=rs_db_write,
                  schema=write_schema)
logger.info("Uploading successful with length: {}".format(len(data_export)))

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()

logger.info("File ends")
