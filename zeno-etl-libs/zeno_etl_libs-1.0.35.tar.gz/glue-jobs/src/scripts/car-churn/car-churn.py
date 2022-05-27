#!/usr/bin/env python
# coding: utf-8

"""
# Author - shubham.jangir@zeno.health
# Purpose - script with database write for car-churn
# Todo evaluate RS read-write connections later
"""

# !/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

sys.path.append('../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

from datetime import datetime
from datetime import timedelta
from dateutil.tz import gettz

import pandas as pd
import numpy as np

# Custom library imports
from zeno_etl_libs.utils.general_funcs import month_diff

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

# Connections
rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()

# Run date
if runtime_date_exp != '0101-01-01':
    run_date = runtime_date_exp
else:
    run_date = datetime.today().strftime('%Y-%m-%d')

# runtime_date = '2021-09-01'
logger.info("Running for {}".format(run_date))

# Period end date
# Paramatrize it
period_end_d = (pd.to_datetime(run_date) - timedelta(days=1)).strftime('%Y-%m-%d')

logger.info("Run date minus 1 is {}".format(period_end_d))

period_end_d_minus180 = (pd.to_datetime(period_end_d) - timedelta(days=180)).strftime('%Y-%m-%d')

logger.info("Period end date minus 180 is {}".format(period_end_d_minus180))

# Data to be fetched
#########################################################
# Bill data
########################################################
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

bills_q = """
     SELECT
        a."patient-id",
        a."store-id",
        a."id" as bill_id,
        a."created-at" AS bill_created_at,
        a."bill-date",
        a."total-spend",
        a."bill-year" as year_bill,
        a."bill-month" as month_bill,
        a."cum-nob" as nob_till_bill,
        a."cum-spend" as spend_till_bill,
        a."cum-abv" as average_bill_value,
        a."normalized-date",
        a."value-segment",
        a."value-segment-calculation-date" as value_segment_calc_date,
        a."behaviour-segment",
        b."behaviour-segment-calculation-date" as behaviour_segment_calc_date,
        b."first-bill-date" as overall_min_bill_date,
        b."primary-disease",
        (case when b."is-repeatable" is True then 1 else 0 end) as latest_is_repeatable,
        (case when b."is-generic" is True then 1 else 0 end) as latest_is_generic,
        (case when b."hd-flag" is True then 1 else 0 end) as latest_hd_flag,
        s."store" as store_name,
        s."opened-at" as store_opened_at,
        s."abo"
     FROM
        "retention-master" a
     LEFT JOIN
        "patients-metadata-2" b
        on a."patient-id" = b."id"
     LEFT JOIN
        "stores-master" s
        on a."store-id" = s."id"
     WHERE
        a."bill-date" > '{0}'
        AND a."bill-date" <= '{1}'
""".format(period_end_d_minus180, period_end_d)
# AND a."store-id" = 2

bills_q = bills_q.replace('`', '"')
logger.info(bills_q)

data_bill = rs_db.get_df(query=bills_q)
data_bill.columns = [c.replace('-', '_') for c in data_bill.columns]
logger.info(len(data_bill))

for i in ['bill_created_at', 'bill_date', 'overall_min_bill_date', 'normalized_date',
          'value_segment_calc_date', 'behaviour_segment_calc_date']:
    data_bill[i] = pd.to_datetime(data_bill[i])

logger.info("Data for bills fetched with length {}".format(len(data_bill)))

# Sort on patient_id, bill_date
data_bill = data_bill.sort_values(by=['patient_id', 'bill_created_at'])

################################
# Calculated columns
################################
# Find next bill date
data_bill['next_bill_date'] = data_bill.groupby(['patient_id'])['bill_date'].shift(-1)

# Difference between next bill date and current bill date
data_bill['day_diff_next_bill'] = (data_bill['next_bill_date'] - data_bill['bill_date']).dt.days

# But what's the difference between run_date and bill date
data_bill['day_diff_today'] = (pd.to_datetime(run_date) - data_bill['bill_date']).dt.days

# Define lost event
# Next bill diff >90 days OR next bill date NULL
# AND
# Date diff with run_date, should also be >90
data_bill['lost_event_flag'] = np.where(((data_bill['day_diff_next_bill'] > 90) |
                                         (data_bill['day_diff_next_bill'].isnull()))
                                        & (data_bill['day_diff_today'] > 90), 1, 0)

# But what's the lost attribution date
data_bill['bill_date_plus90'] = pd.to_datetime(data_bill['bill_date'] + timedelta(days=90))
data_bill['lost_attribution_date'] = np.where(data_bill['lost_event_flag'] == 1,
                                              data_bill['bill_date_plus90'].dt.strftime('%Y-%m-%d'),
                                              "")

data_bill['lost_attribution_date'] = pd.to_datetime(data_bill['lost_attribution_date'], errors='coerce')

# Month diff
data_bill['month_diff_acq'] = month_diff(data_bill['bill_date'], data_bill['overall_min_bill_date'])

################################
# Calculated columns
################################
# Round to 2 decimals
for i in ['spend_till_bill', 'average_bill_value']:
    data_bill[i] = data_bill[i].astype(float).round(2)

#################################
# Data lost
#################################
data_lost = data_bill[data_bill['lost_event_flag'] == 1].copy()

logger.info("Lost data length {}".format(len(data_lost)))

########################################################
# Churn reasons
#######################################################

############################
# PR Lost or Delayed
############################
# Todo change order-number to patient-request-number or the aligned source of truth
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

pr_q = """
    SELECT
        `patient-id`,
        `order-number`,
        `bill-id`,
        MIN(`pr-created-at`) AS min_created_at,
        MAX(`completed-at`) AS max_completed_at
    FROM
        `patient-requests-metadata`
    WHERE
        `pso-requested-quantity` > 0
        AND date(`pr-created-at`) > '{0}'
        AND date(`pr-created-at`) <= '{1}'
    GROUP BY
        `patient-id`, 
        `order-number`, 
        `bill-id`
""".format(period_end_d_minus180, period_end_d)

pr_q = pr_q.replace('`', '"')
logger.info(pr_q)

data_pr = rs_db.get_df(query=pr_q)
data_pr.columns = [c.replace('-', '_') for c in data_pr.columns]
logger.info(len(data_pr))

logger.info("PR data fetched with length {}".format(len(data_pr)))

# PR Delay
# Delay can only happen for those who billed
data_pr_b = data_pr[data_pr['bill_id'] >= 0].copy()

for i in ['min_created_at', 'max_completed_at']:
    data_pr_b[i] = pd.to_datetime(data_pr_b[i], errors='coerce')

data_pr_b['hour_diff'] = (data_pr_b['max_completed_at'] - data_pr_b['min_created_at']) / np.timedelta64(1, 'h')

data_pr_b['pr_72hrs_delay'] = np.where(data_pr_b['hour_diff'] > 72, 1, 0)

# Take unique on bills
data_pr_b_unique = data_pr_b.drop_duplicates(subset=['patient_id', 'bill_id']).copy()
data_pr_b_unique['bill_id'] = data_pr_b_unique['bill_id'].astype(int)

# Merge with main data
data_lost = data_lost.merge(data_pr_b_unique[['patient_id', 'bill_id', 'pr_72hrs_delay']],
                            how='left', on=['patient_id', 'bill_id'])
data_lost['pr_72hrs_delay'] = data_lost['pr_72hrs_delay'].fillna(0)

logger.info("Lost data length after joining with PR delay status {}".format(len(data_lost)))

# PR Loss
data_pr_lost = data_pr_b[(data_pr_b['max_completed_at'] == '0000-00-00 00:00:00') |
                         (data_pr_b['max_completed_at'].isnull())].copy()

for i in ['min_created_at', 'max_completed_at']:
    data_pr_lost[i] = pd.to_datetime(data_pr_lost[i], errors='coerce')

run_date_minus_7 = pd.to_datetime(run_date) - timedelta(days=7)
data_pr_lost = data_pr_lost[data_pr_lost['min_created_at'] <= run_date_minus_7]

logger.info("PR Loss data length {}".format(len(data_pr_lost)))

# Merge with main data
data_lost_tmp = data_lost.merge(
    data_pr_lost[['patient_id', 'order_number', 'min_created_at', 'max_completed_at']],
    how='left', on=['patient_id'])
# Because merged on patient id only, so date diff with bill date to be taken
data_lost_tmp['lost_pr_date_diff'] = (data_lost_tmp['min_created_at'] - data_lost_tmp['bill_date']).dt.days

# For a customer to be lost due to PR, the PR event should happen after that bill date
data_lost_tmp = data_lost_tmp[data_lost_tmp['lost_pr_date_diff'] > 0]

# But should be less than or equal to loss attributed day
data_lost_tmp = data_lost_tmp[data_lost_tmp['min_created_at'] <= data_lost_tmp['lost_attribution_date']]

# Drop any duplicate mappings
data_lost_tmp = data_lost_tmp.drop_duplicates(subset=['patient_id', 'bill_id'])

data_lost_tmp = data_lost_tmp[
    ['patient_id', 'bill_id', 'min_created_at', 'max_completed_at', 'lost_pr_date_diff']].copy()
data_lost_tmp['pr_lost'] = 1

logger.info("PR loss final data length is {}".format(len(data_lost_tmp)))

# Merge with main data
data_lost = data_lost.merge(data_lost_tmp, how='left', on=['patient_id', 'bill_id'])
data_lost['pr_lost'] = data_lost['pr_lost'].fillna(0)

logger.info("Lost data length after joining with PR Lost status {}".format(len(data_lost)))

############################
# HD delayed
############################
# Todo change clarify if bill-id>0 is compulsory, to get HD
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

hd_q = """
    SELECT
        `patient-id`,
        `bill-id`,
        MIN(`pso-created-at`) AS min_created_at,
        MAX(`delivered-at`) AS max_delivered_at
    FROM
        `home-delivery-metadata`
    WHERE
        `bill-id` > 0
        AND date(`pso-created-at`) > '{0}'
        AND date(`pso-created-at`) <= '{1}'
    GROUP BY
        `patient-id`, 
        `bill-id`
""".format(period_end_d_minus180, period_end_d)

hd_q = hd_q.replace('`', '"')
logger.info(hd_q)

data_hd = rs_db.get_df(query=hd_q)
data_hd.columns = [c.replace('-', '_') for c in data_hd.columns]
logger.info(len(data_hd))

logger.info("HD data fetched with length {}".format(len(data_hd)))

for i in ['min_created_at', 'max_delivered_at']:
    data_hd[i] = pd.to_datetime(data_hd[i], errors='coerce')

data_hd['hour_diff'] = (data_hd['max_delivered_at'] - data_hd['min_created_at']) / np.timedelta64(1, 'h')

data_hd['hd_24hrs_delay'] = np.where(data_hd['hour_diff'] > 24, 1, 0)

# Take unique on bills
data_hd_unique = data_hd.drop_duplicates(subset=['patient_id', 'bill_id']).copy()
data_hd_unique['bill_id'] = data_hd_unique['bill_id'].astype(int)

data_lost = data_lost.merge(data_hd_unique[['patient_id', 'bill_id', 'hd_24hrs_delay']],
                            how='left', on=['patient_id', 'bill_id'])
data_lost['hd_24hrs_delay'] = data_lost['hd_24hrs_delay'].fillna(0)

logger.info("Lost data length after joining with HD delay status {}".format(len(data_lost)))

############################
# NPS
############################
# Todo change with nps-bill-mapping later
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

nps_q = """
    SELECT
        b.`id` AS patient_id,
        a.`rating`,
        DATE(a.`created-at`) AS feedback_date
    FROM
        feedback a
    INNER JOIN patients b on
        a.phone = b.phone
    WHERE date(a.`created-at`) > '{0}'
        AND date(a.`created-at`) <= '{1}'
    GROUP BY
        b.`id`,
        a.`rating`,
        DATE(a.`created-at`)
""".format(period_end_d_minus180, period_end_d)

nps_q = nps_q.replace('`', '"')
logger.info(nps_q)

data_nps = rs_db.get_df(query=nps_q)
data_nps.columns = [c.replace('-', '_') for c in data_nps.columns]
logger.info(len(data_nps))

logger.info("NPS data fetched with length {}".format(len(data_nps)))

data_nps['feedback_date'] = pd.to_datetime(data_nps['feedback_date'])

data_nps['detractor_flag'] = np.where(((data_nps['feedback_date'] <= '2019-10-23') & (data_nps['rating'] <= 6))
                                      | (data_nps['rating'] <= 3), 1, 0)

# NPS detractors only
data_nps_d = data_nps[data_nps['detractor_flag'] == 1]

data_lost_nps_tmp = data_lost.merge(data_nps_d[['patient_id', 'rating', 'feedback_date', 'detractor_flag']],
                                    how='left', on=['patient_id'])
data_lost_nps_tmp['nps_date_diff'] = (data_lost_nps_tmp['feedback_date'] - data_lost_nps_tmp['bill_date']).dt.days

# To be lost, NPS should be on or after churn event bill date
data_lost_nps_tmp = data_lost_nps_tmp[data_lost_nps_tmp['nps_date_diff'] >= 0]

# But should be less than or equal to loss attributed day
data_lost_nps_tmp = data_lost_nps_tmp[data_lost_nps_tmp['feedback_date']
                                      <= data_lost_nps_tmp['lost_attribution_date']]

data_lost_nps = data_lost_nps_tmp.drop_duplicates(subset=['patient_id', 'bill_id'])

data_lost_nps = data_lost_nps[['patient_id', 'bill_id', 'rating', 'feedback_date', 'nps_date_diff']].copy()
data_lost_nps['nps_detractor_lost'] = 1

# Merge with main data
data_lost = data_lost.merge(data_lost_nps, how='left', on=['patient_id', 'bill_id'])
data_lost['nps_detractor_lost'] = data_lost['nps_detractor_lost'].fillna(0)

logger.info("Lost data length after joining with NPS Lost status {}".format(len(data_lost)))

##################################
# Customer returns
##################################
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

return_q = """
    SELECT
        a.`bill-id`
    FROM
        `customer-return-items-1` a
    INNER JOIN `bills-1` b
    ON a.`bill-id` = b.`id`
    WHERE
        date(b.`created-at`) > '{0}'
        AND date(b.`created-at`) <= '{1}'
    GROUP BY
        a.`bill-id`
""".format(period_end_d_minus180, period_end_d)
return_q = return_q.replace('`', '"')
logger.info(return_q)

data_return = rs_db.get_df(query=return_q)
data_return.columns = [c.replace('-', '_') for c in data_return.columns]
logger.info(len(data_return))

data_return['return_flag'] = 1

# Merge with main data
data_lost = data_lost.merge(data_return, how='left', on=['bill_id'])
data_lost['return_flag'] = data_lost['return_flag'].fillna(0)

logger.info("Lost data length after joining with Customer returns data {}".format(len(data_lost)))

#############################
# Expiry items
############################
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

expiry_q = """
    SELECT
        a.`bill-id`,
        a.`inventory-id`,
        b.`expiry`
    FROM
        `bill-items-1` a
    LEFT JOIN
        `inventory-1` b
        on a.`inventory-id` = b.`id`
    WHERE
        date(a.`created-at`) > '{0}'
        AND date(a.`created-at`) <= '{1}'
""".format(period_end_d_minus180, period_end_d)

expiry_q = expiry_q.replace('`', '"')
# logger.info(expiry_q)

data_expiry = rs_db.get_df(query=expiry_q)
data_expiry.columns = [c.replace('-', '_') for c in data_expiry.columns]
logger.info(len(data_expiry))

logger.info("Bill item data with inventory id - fetched with length {}".format(len(data_expiry)))
data_expiry['expiry'] = pd.to_datetime(data_expiry['expiry'], errors='coerce')

# Merge and calculate
data_lost_inv = data_lost[['bill_id', 'bill_date']].merge(data_expiry, how='left', on=['bill_id'])

data_lost_inv['expiry_days'] = (data_lost_inv['expiry'] - data_lost_inv['bill_date']).dt.days

data_lost_inv['expiry_less_6m'] = np.where(data_lost_inv['expiry_days'] < 180, 1, 0)

data_lost_inv_grp = data_lost_inv.groupby(['bill_id']).agg(
    {'inventory_id': 'count', 'expiry_less_6m': 'sum'}).reset_index()
data_lost_inv_grp = data_lost_inv_grp.rename(columns={'inventory_id': 'items'})

data_lost_inv_grp['expiry_less_6m_pc'] = data_lost_inv_grp['expiry_less_6m'] / data_lost_inv_grp['items']

data_lost_inv_grp['near_expiry_flag'] = np.where(data_lost_inv_grp['expiry_less_6m_pc'] >= 0.5, 1, 0)

##############################
# Merge with main data
##############################
data_lost = data_lost.merge(data_lost_inv_grp, how='left', on=['bill_id'])
data_lost['near_expiry_flag'] = data_lost['near_expiry_flag'].fillna(0)

logger.info("Lost data length after joining with Expiry items data {}".format(len(data_lost)))


# Churn event exact
def churn_event(row):
    if row['nps_detractor_lost'] == 1:
        return 'NPS Lost'
    elif row['pr_lost'] == 1:
        return 'PR Lost'
    elif row['pr_72hrs_delay'] == 1:
        return 'PR Delayed'
    elif row['hd_24hrs_delay'] == 1:
        return 'HD Delayed'
    elif row['return_flag'] == 1:
        return 'Items returned'
    elif row['near_expiry_flag'] == 1:
        return 'Near expiry items'
    else:
        return 'Not known'


data_lost['churn_event'] = data_lost.apply(lambda row: churn_event(row), axis=1)

# DB upload columns
final_cols = ['patient_id', 'store_id', 'bill_id', 'bill_created_at', 'bill_date',
              'year_bill', 'month_bill', 'nob_till_bill', 'next_bill_date', 'day_diff_next_bill',
              'day_diff_today', 'lost_event_flag',
              'bill_date_plus90', 'lost_attribution_date', 'overall_min_bill_date', 'normalized_date',
              'month_diff_acq', 'total_spend', 'spend_till_bill', 'average_bill_value',
              'pr_72hrs_delay', 'min_created_at', 'max_completed_at', 'lost_pr_date_diff', 'pr_lost',
              'hd_24hrs_delay', 'rating', 'feedback_date', 'nps_date_diff', 'nps_detractor_lost',
              'return_flag', 'items', 'expiry_less_6m', 'expiry_less_6m_pc', 'near_expiry_flag',
              'churn_event', 'latest_is_repeatable', 'latest_is_generic', 'latest_hd_flag',
              'primary_disease', 'value_segment_calc_date', 'value_segment', 'behaviour_segment_calc_date',
              'behaviour_segment', 'store_name', 'store_opened_at', 'abo']

data_export = data_lost[final_cols]

# For redshift specific
# Convert int columns to int

for i in ['bill_id', 'lost_event_flag', 'pr_72hrs_delay', 'pr_lost',
          'hd_24hrs_delay', 'nps_detractor_lost', 'return_flag',
          'expiry_less_6m', 'near_expiry_flag']:
    data_export[i] = data_export[i].fillna(0).astype(int)

# Impute for Nulls
# Impute 99999 instead of null, for now
# Todo change dtype to float in DDL
# month_diff_acq was added because of float vs integer mismatch in database writing
for i in ['day_diff_next_bill', 'lost_pr_date_diff', 'nps_date_diff', 'month_diff_acq',
          'rating']:
    data_export[i] = data_export[i].fillna(99999).astype(int)

for i in ['bill_date', 'overall_min_bill_date', 'normalized_date',
          'next_bill_date', 'bill_date_plus90', 'lost_attribution_date',
          'value_segment_calc_date', 'behaviour_segment_calc_date',
          'feedback_date']:
    data_export[i] = pd.to_datetime(data_export[i]).dt.date

logger.info(data_export.columns)

################################
# DB WRITE
###############################

write_schema = 'prod2-generico'
write_table_name = 'car-churn'

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
    WHERE
        "bill-date" > '{period_end_d_minus180}'
        AND "bill-date" <= '{period_end_d}'
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
