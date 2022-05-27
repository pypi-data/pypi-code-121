#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - script with database write for missed-call-crm
# Dependencies - This requires MongoDB connection
# Todo evaluate RS/MySQL read-write connections later
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, MongoDB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
import dateutil
from dateutil.tz import gettz

import pandas as pd
import numpy as np

# Import custom functions
from zeno_etl_libs.utils.consumer.crm_campaigns import CrmCampaigns

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

# Instantiate the CRM campaigns class
cc = CrmCampaigns()

# Connections
# Don't redo the connections already instantitated from Classes
'''
rs_db = DB()
rs_db.open_connection()

# ALERT: read_only=False, if you want connection which writes
ms_connection = MySQL(read_only=False)
ms_connection.open_connection()
'''

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

# MongoDB Client
mg_db = MongoDB()
mg_client = mg_db.open_connection("generico-crm")

s3 = S3()

# Run date
if runtime_date_exp != '0101-01-01':
    run_date = runtime_date_exp
else:
    run_date = datetime.today().strftime('%Y-%m-%d')

# run_date = '2021-09-01'
logger.info("Running for {}".format(run_date))

run_date_minus1 = (pd.to_datetime(run_date) - timedelta(days=1)).strftime('%Y-%m-%d')

logger.info(f"Run date is {run_date} and previous date is {run_date_minus1}")

run_date_minus1_ts = dateutil.parser.parse(f"{run_date_minus1} 00:00:00")
run_date_ts = dateutil.parser.parse(f"{run_date} 23:59:59")

logger.info(f"Look up period is {run_date_minus1_ts} to {run_date_ts}")

#########################################################
# Read from Mongo-DB
########################################################

# Pick only for period mentioned
# date_time is the timestamp column
# But since it's string, so have to convert to date, before processing

# Read Generico crm table
db = mg_client['generico-crm']

# Query
collection = db['callLogs'].find({"type": "STORE_CALL_CONNECT",
                                  "$expr": {
                                      "$and": [
                                          {
                                              "$gte": [{"$dateFromString": {"dateString": "$date_time"}},
                                                       run_date_minus1_ts]
                                          },
                                          {
                                              "$lte": [{"$dateFromString": {"dateString": "$date_time"}},
                                                       run_date_ts]
                                          }
                                      ]
                                  }
                                  })

# Get into pandas data-frame
data_raw = pd.DataFrame(list(collection))

logger.info("Data fetched is with length {}".format(len(data_raw)))

# List data columns
logger.info("Column names in data are {}".format(data_raw.columns))

####################################################
# Filters on rows or columns
###################################################

# Doing it in later blocks, so ignore for now
# Exclude patient id 0
# data = data_raw[data_raw['patient_id'] > 0]
data = data_raw.copy()

# print("Data length after excluding patient id 0 - is {}".format(len(data)))

unique_cols = ['call_type', 'status', 'type', 'is_active', 'to_number', 'from_number',
               'store_id', 'duration', 'date_time']

# Find unique entries
data_unique = data[unique_cols].drop_duplicates()

logger.info("Unique data length is - {}".format(len(data_unique)))

# Convert to object
data_unique['is_active'] = data_unique['is_active'].astype(str)

# Convert to time-stamp
data_unique['date_time'] = pd.to_datetime(data_unique['date_time'])

############################################
# Upload to DSS unique table
############################################
read_schema = 'prod2-generico'
rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)

last_dss_q = """
    SELECT
        "call-type",
        "status",
        "type",
        "is-active",
        "to-number",
        "from-number",
        "store-id",
        "duration",
        "date-time"
    FROM
        "store-call-logs-entries"
"""

last_dss_q = last_dss_q.replace('`', '"')
logger.info(last_dss_q)

rs_db_write.execute(last_dss_q, params=None)
last_data_dss: pd.DataFrame = rs_db_write.cursor.fetch_dataframe()
if last_data_dss is None:
    last_data_dss = pd.DataFrame(columns=['call_type', 'status', 'type',
                                          'is_active', 'to_number', 'from_number',
                                          'store_id', 'duration', 'date_time'])
last_data_dss.columns = [c.replace('-', '_') for c in last_data_dss.columns]
logger.info(len(last_data_dss))

logger.info("Last data in DSS length {}".format(len(last_data_dss)))

# Convert to date-time
last_data_dss['date_time'] = pd.to_datetime(last_data_dss['date_time'])

# Join and check which to insert and which to update

# Data match with mySQL
data_export_dss = data_unique.merge(
    last_data_dss, how='outer', on=unique_cols, indicator=True)

# To upload
data_insert_dss = data_export_dss[data_export_dss['_merge'] == 'left_only']
data_insert_dss.drop(['_merge'], axis=1, inplace=True)

logger.info("Length in left dataset after outer join {}".format(data_insert_dss))

# Upload to DSS
################################
# DB WRITE
###############################
write_schema = 'prod2-generico'
write_table_name = 'store-call-logs-entries'

table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

# table_info_clean = table_info[~table_info['column_name'].isin(['id', 'created-at', 'updated-at'])]

data_export = data_insert_dss.copy()
data_export.columns = [c.replace('_', '-') for c in data_export.columns]

# Mandatory lines
data_export['created-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['created-by'] = 'etl-automation'
data_export['updated-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['updated-by'] = 'etl-automation'

logger.info("Insert DSS started")

# Write to DB
s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name,
                  db=rs_db_write, schema=write_schema)
logger.info("Uploading successful with length: {}".format(len(data_export)))

logger.info("Insert DSS Done")

###############################################################
# Processing for calling-dashboard
##############################################################
# Remove dummy stores
# Now fetch from unique table, and process for calling dashboard
read_schema = 'prod2-generico'
rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)

dss_q = """
    SELECT
        "call-type",
        "status",
        "type",
        "is-active",
        "to-number",
        "from-number",
        "store-id",
        "duration",
        "date-time"
    FROM
        "store-call-logs-entries"
    WHERE
        "store-id" not in (52, 60, 92, 111, 149)
"""
dss_q = dss_q.replace('`', '"')
logger.info(dss_q)

rs_db_write.execute(dss_q, params=None)
data_dss: pd.DataFrame = rs_db_write.cursor.fetch_dataframe()
if data_dss is None:
    data_dss = pd.DataFrame(columns=['call_type', 'status', 'type',
                                     'is_active', 'to_number', 'from_number',
                                     'store_id', 'duration', 'date_time'])
data_dss.columns = [c.replace('-', '_') for c in data_dss.columns]
logger.info(len(data_dss))

# Convert to time-stamp
data_dss['date_time'] = pd.to_datetime(data_dss['date_time'])

logger.info("Data call logs from DSS fetched with length {}".format(len(data_dss)))

# Now that we have unique, find data last 1days (so total 2-days including today)
# Can be parameterized

# Data recent
data = data_dss[data_dss['date_time'] >= run_date_minus1].copy()

logger.info("Data last 2-days length is - {}".format(len(data)))

# First make customer number final
# If Missed or incoming, then use from_number,
# If outgoing then used to_number

data['patient_number'] = np.where(data['call_type'].isin(['MISSED', 'INCOMING']), data['from_number'],
                                  np.where(data['call_type'] == 'OUTGOING', data['to_number'], np.nan))

# Now see how many of them actually have patient id's mapped
# Remove those who don't

phones = tuple(data['patient_number'].dropna().drop_duplicates().to_list())

logger.info("Phones to be searched in patients table - length is {}".format(len(phones)))

##############################
# MySQL patients table
##############################

patients_info_q = """
    SELECT
        phone as patient_number,
        id as patient_id
    FROM
        patients
    WHERE
        phone in {}
""".format(phones)

data_p = pd.read_sql_query(patients_info_q, cc.ms_connection_read.connection)
data_p.columns = [c.replace('-', '_') for c in data_p.columns]

logger.info("Patient id found for phones - length {}".format(len(data_p)))

# Merge
data = data.merge(data_p, how='inner', on=['patient_number'])

logger.info("Length for calling data for patient id present - {}".format(len(data)))

data = data.sort_values(by=['date_time'])

# Now filters come
# Divide into 3-3hrs windows. And then put year, month, day, window index
data['year_call'] = data['date_time'].dt.year
data['month_call'] = data['date_time'].dt.month
data['day_call'] = data['date_time'].dt.day
data['hour_call'] = data['date_time'].dt.hour

# For now divide into 1-day bucket, and check that same day should not be duplicates

# Now find out cases where missed call, but within 30minutes, and incoming call from same number.
# Remove those cases

# Sort data by date_time alone
data = data.sort_values(by=['date_time'])


# Change HH:MM:SS to seconds
def hms_to_seconds(t):
    split_t = [int(i) for i in t.split(':')]
    if len(split_t) == 3:
        h, m, s = split_t
        return 3600 * h + 60 * m + s
    elif len(split_t) == 2:
        m, s = split_t
        return 60 * m + s
    else:
        s = split_t[0]
        return s


data['duration_sec'] = data.apply(lambda row: hms_to_seconds(row['duration']), axis=1)

logger.info("Avg value of duration is {}".format(data['duration_sec'].mean()))

# Cases can be
# Missed call, incoming
# Missed call, missed call, incoming
# Missed call, incoming, missed call

# First remove the successive missed calls and keep only latest of them
# For that, shift lag -1 and see if successive call is missed call or not

# GROUP CALL TYPE into MISSED, 'OTHERS'
data['call_type_grp'] = np.where(data['call_type'] != 'MISSED', 'OTHERS',
                                 data['call_type'])

logger.info("Unique call type groups are {}".format(data['call_type_grp'].unique()))

logger.info("Current df head is {}".format(data.head()))

# Assign 1 to MISSED and 0 for others, and start from first instance of Missed call
data['missed_call_flag'] = np.where(data['call_type_grp'] == 'MISSED', 1, 0)

# Sort data by date_time
data = data.sort_values(by=['patient_id', 'date_time'])

logger.info("Data length before applying missed call filter is {}".format(len(data)))

# MISSED CALL CUM-FLAG
data['missed_call_cumsum'] = data.groupby(['patient_id'])['missed_call_flag'].cumsum()

logger.info("Current df head is {}".format(data.head()))

# FILTER FOR >=1 MISSED CALL CUMSUM
data = data[data['missed_call_cumsum'] >= 1].copy()

logger.info("Data length AFTER applying missed call filter is {}".format(len(data)))

logger.info("Current df head is {}".format(data.head()))

# Grouping call durations across calls
data = data.groupby(['year_call', 'month_call', 'day_call', 'store_id',
                     'patient_id', 'call_type_grp'])['duration_sec'].sum().reset_index()

data['same_day_prev_call_type'] = data.groupby(['year_call', 'month_call', 'day_call',
                                                'patient_id'])['call_type_grp'].shift(1)

data['same_day_next_call_type'] = data.groupby(['year_call', 'month_call', 'day_call',
                                                'patient_id'])['call_type_grp'].shift(-1)

data['same_day_next_call_duration_sec'] = data.groupby(['year_call', 'month_call', 'day_call',
                                                        'patient_id'])['duration_sec'].shift(-1)

# Only Missed
data_f = data[((data['call_type_grp'] == 'MISSED') & (data['same_day_next_call_type'].isnull()))
              | ((data['call_type_grp'] != 'MISSED') & (data['same_day_prev_call_type'] == 'MISSED') &
                 (data['duration_sec'] < 30))].copy()

logger.info("length of missed call data is {}".format(len(data_f)))

logger.info("Current df head is {}".format(data_f.head()))

# Unique
data_f_unique = data_f.drop_duplicates(subset=['year_call',
                                               'month_call',
                                               'day_call',
                                               'patient_id'])

logger.info("Unique (per day) length {}".format(len(data_f_unique)))

################################################
# Insert in mySQL - mandatory steps
################################################
# Remove Last 7 days billed already

data_f_unique = cc.no_bill_in_last_n_days(data_f_unique, run_date, last_n_days_param=7)

# Should not have been called in last 7-days thru calling dashboard
# Can be paramatrized, or changed later to 2days
data_f_unique = cc.no_call_in_last_n_days(data_f_unique, run_date, last_n_days_param=7)

# Read DND list
data_f_unique = cc.remove_dnd(data_f_unique)

#################################################
# MySQL insert
# Upload to mySQL DB
#################################################

# Output to calling-dashboard, ensure unique
data_c = data_f_unique[['store_id', 'patient_id']].copy()
data_c['campaign_id'] = 19
data_c['callback_reason'] = 'For callback'
data_c['list_date'] = run_date
data_c['call_date'] = data_c['list_date']

# Remove any duplicates
data_c = data_c.drop_duplicates(subset='patient_id')

logger.info("Unique list to be considered for calling dashboard - length {}".format(len(data_c)))

logger.info("mySQL - Insert starting")

data_c.columns = [c.replace('_', '-') for c in data_c.columns]

data_c.to_sql(name='calling-dashboard', con=cc.ms_connection_write.engine, if_exists='append', index=False,
              method='multi', chunksize=500)

logger.info("mySQL - Insert ended")

logger.info("Missed call - Calling list data inserted/uploaded to mySQL for run date {}"
            " with length : {}".format(run_date, len(data_c)))

# Closing the DB Connections
rs_db_write.close_connection()
cc.close_connections()

logger.info("File ends")
