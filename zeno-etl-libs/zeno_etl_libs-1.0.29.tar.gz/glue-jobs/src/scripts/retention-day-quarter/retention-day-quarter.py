"""
Author:neha.karekar@zeno.health
Purpose: retention ressurection QonQ
# Dependencies - this is used to make CAR R
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
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

# connections
parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")


rs_db = DB()
rs_db.open_connection()

s3 = S3()

# table info
schema = 'prod2-generico'
table_name = 'retention-day-quarter'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

########################################################
# BILLING data (lengthy data-set)
########################################################

# order id to patient id
q1 = """
SELECT
            "patient-id",
            "store-id",
            "id" AS bill_id,
            "created-at" AS bill_created_at
         FROM "prod2-generico"."bills-1" 
"""
rs_db.execute(q1, params=None)
data_bill: pd.DataFrame = rs_db.cursor.fetch_dataframe()
data_bill.columns = [c.replace('-', '_') for c in data_bill.columns]

data_bill['bill_created_at'] = pd.to_datetime(data_bill['bill_created_at'])
# data_bill['last_bill_created_at'] = pd.to_datetime(data_bill['bill_created_at'])
data_bill['bill_date'] = pd.to_datetime(data_bill['bill_created_at'].dt.date)
data_bill['year_bill'] = data_bill['bill_date'].dt.year
data_bill['month_bill'] = data_bill['bill_date'].dt.month
logger.info("Data for bills fetched, with length {}".format(len(data_bill)))
# First take only first bill in a month, others don't matter for retention
data_a = data_bill.groupby(['patient_id', 'year_bill', 'month_bill', 'store_id'])['bill_date'].min().reset_index()
# data_a = data_bill.groupby(['patient_id', 'year_bill', 'month_bill', 'store_id']).agg(
#   last_bill_created_at=('last_bill_created_at', 'max'), bill_date=('bill_date', 'min')).reset_index()

logger.info("Data for bills - after taking first in month, with length {}".format(len(data_a)))

# Calculate quarters
data_a['cohort_quarter'] = data_a['bill_date'].dt.to_period("Q")
data_a['cohort_quarter_number'] = data_a['cohort_quarter'].dt.strftime('%q').astype(int)

# Min bill date in quarter
data_a = data_a.sort_values(by=['patient_id', 'year_bill', 'month_bill', 'bill_date'])
data_a['rank'] = data_a.groupby(['patient_id', 'cohort_quarter']).cumcount() + 1
data_a = data_a[data_a['rank'] == 1].copy()

# Self join is needed, to find any retention
# drop duplicates should not be needed ideally
data_a_left = data_a[
    ['patient_id', 'cohort_quarter', 'cohort_quarter_number', 'year_bill', 'month_bill', 'store_id']]
data_a_left = data_a_left.rename(columns={'year_bill': 'year_cohort'})
data_a_left = data_a_left.rename(columns={'month_bill': 'month_cohort'})
# drop duplicates should not be needed ideally
data_a_right = data_a[
    ['patient_id', 'cohort_quarter', 'cohort_quarter_number', 'year_bill', 'bill_date']]
data_a_right = data_a_right.rename(columns={'cohort_quarter': 'bill_quarter'})
data_a_right = data_a_right.rename(columns={'cohort_quarter_number': 'bill_quarter_number'})
# Self join
data = data_a_left.merge(data_a_right, how='left', on=['patient_id'])

# First day in quarter
data['day_zero_in_cohort_quarter'] = data['cohort_quarter'].dt.to_timestamp()
data['day_zero_in_bill_quarter'] = data['bill_quarter'].dt.to_timestamp()

# Convert cohort quarter to string
data['cohort_quarter'] = data['cohort_quarter'].astype(str)
data['bill_quarter'] = data['bill_quarter'].astype(str)

# Day number in quarter
data['day_index'] = (data['bill_date'] - data['day_zero_in_bill_quarter']).dt.days + 1

# Remove negative date mappings
data = data[data['bill_date'] >= data['day_zero_in_cohort_quarter']].copy()

# Official quarter diff
data['quarter_diff'] = (data['year_bill'] - data['year_cohort']) * 4 + (
        data['bill_quarter_number'] - data['cohort_quarter_number'])

# We don't need history of 3+ quarters retention
data = data[data['quarter_diff'] <= 2].copy()

###############################
# Resurrection
###############################

# Now for resurrection specific
# Those who came in next quarter, are not resurrection candidates
# drop duplicates should not be needed
data_r1 = data[data['quarter_diff'] == 1][['patient_id', 'cohort_quarter']]
data_r1['resurrection_candidate'] = 0

data = data.merge(data_r1, how='left', on=['patient_id', 'cohort_quarter'])
# Rest are resurrection candidates, i.e they didnt come in next quarter,
# so we will see their resurrection, later on
data['resurrection_candidate'] = data['resurrection_candidate'].fillna(1)

logger.info("Data length is {}".format(len(data)))


# Summary numbers
data_grp = data.groupby(['cohort_quarter'])['patient_id'].apply(pd.Series.nunique).reset_index()
data_grp = data_grp.rename(columns={'patient_id': 'cohort_quarter_patients'})

# Merge with main data
data = data.merge(data_grp, how='left', on=['cohort_quarter'])

logger.info("Data length after merging with cohort base {}".format(len(data)))

# Resurrection base too
data_grp_res = data[data['resurrection_candidate'] == 1].groupby(
    ['cohort_quarter'])['patient_id'].apply(pd.Series.nunique).reset_index()
data_grp_res = data_grp_res.rename(columns={'patient_id': 'cohort_resurrection_candidates'})

# Merge with main data
data = data.merge(data_grp_res, how='left', on=['cohort_quarter'])

logger.info("Data length after merging with cohort base {}".format(len(data)))

# Final columns
final_cols = ['patient_id', 'cohort_quarter', 'cohort_quarter_number', 'year_cohort',
              'store_id', 'bill_quarter', 'bill_quarter_number', 'year_bill',
              'bill_date', 'day_zero_in_cohort_quarter',
              'day_zero_in_bill_quarter', 'day_index', 'quarter_diff',
              'resurrection_candidate', 'cohort_quarter_patients',
              'cohort_resurrection_candidates']
data.drop_duplicates(keep="first", inplace=True)
data = data[final_cols]
data['resurrection_candidate'] = data['resurrection_candidate'].astype('Int64')
data.columns = [c.replace('_', '-') for c in data.columns]
data['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['created-by'] = 'etl-automation'
data['updated-by'] = 'etl-automation'
data['bill-date'] = data['bill-date'].dt.date


#logger.info("Existing data fetched with length {}".format(len(data_dss)))
print(data.head(1))
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    logger.info(truncate_query)
    rs_db.execute(truncate_query)
    """ seek the data """
print(data.head(1))
print(table_info)
file_s3_uri_save = s3.save_df_to_s3(df=data[table_info['column_name']],
                                    file_name="retention-day-quarter.csv")
s3.write_to_db_from_s3_csv(table_name=table_name,
                           file_s3_uri=file_s3_uri_save,
                           db=rs_db, schema=schema)
s3.write_df_to_db(df=data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# Closing the DB Connection
rs_db.close_connection()


