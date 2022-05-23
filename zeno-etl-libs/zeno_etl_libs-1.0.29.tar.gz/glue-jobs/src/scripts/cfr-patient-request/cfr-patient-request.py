#!/usr/bin/env python
# coding: utf-8
"""
# Author - shubham.jangir@generico.in
# Purpose - script with database write for cfr patient request
# Todo evaluate RS read-write connections later
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

# Connections
rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()

#############################################
# Main logic block
#############################################
# Run date

if runtime_date_exp == '0101-01-01':
    # Timezone aware
    run_date = datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")
else:
    run_date = runtime_date_exp
    # runtime_date = '2018-09-01'

logger.info("Running for {}".format(run_date))

# Period end date
# Paramatrize it
period_end_d_ts = datetime.strptime(run_date, '%Y-%m-%d') - timedelta(days=1)
period_end_d = period_end_d_ts.strftime('%Y-%m-%d')

logger.info("Run date minus 1 is {}".format(period_end_d))

day_minus8 = (pd.to_datetime(run_date) - timedelta(days=8)).strftime("%Y-%m-%d")

logger.info("Runtime date minus 8 is {}".format(period_end_d))

# Read last list so that only new data to be uploaded

read_schema = 'prod2-generico'
rs_db_write.execute(f"set search_path to '{read_schema}'", params=None)

query = f"""
        SELECT
            "shortbook-date"
        FROM
            "cfr-patient-request"
        GROUP BY
            "shortbook-date"
    """
logger.info(query)

rs_db_write.execute(query, params=None)
last_data_date: pd.DataFrame = rs_db_write.cursor.fetch_dataframe()
if last_data_date is None:
    last_data_date = pd.DataFrame(columns=['shortbook_date'])
last_data_date.columns = [c.replace('-', '_') for c in last_data_date.columns]
logger.info(len(last_data_date))
last_data_date.head()

try:
    last_sb_date_max = pd.to_datetime(last_data_date['shortbook_date']).max().strftime('%Y-%m-%d')
except ValueError:
    last_sb_date_max = '2000-06-01'

logger.info("Last date in last data for cfr patient request is : {}".format(last_sb_date_max))

# Remaining data to be fetched

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

pr_q = """
    SELECT
        `id` as `short-book-id`,
        `store-id`,
        `created-at`,
        `patient-id`,
        `unique-id`,
        `drug-id`,
        `drug-name`,
        `requested-quantity`,
        `inventory-at-creation`,
        `quantity`,
        `home-delivery`,
        `received-at`,
        `bill-id`
    FROM `short-book-1`
    WHERE `auto-short` = 0
        and `auto-generated` = 0
        and date(`created-at`) > '{0}'
        and date(`created-at`) <= '{1}'
""".format(last_sb_date_max, day_minus8)

pr_q = pr_q.replace('`', '"')
logger.info(pr_q)

rs_db.execute(pr_q, params=None)
data_pr: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if data_pr is None:
    data_pr = pd.DataFrame(columns=['short_book_id', 'store_id', 'created_at', 'patient_id', 'unique_id',
                                    'drug_id', 'drug_name', 'requested_quantity',
                                    'inventory_at_creation',
                                    'quantity', 'home_delivery',
                                    'received_at', 'bill_id'])
data_pr.columns = [c.replace('-', '_') for c in data_pr.columns]
logger.info(len(data_pr))

logger.info("New PR data length is : {}".format(len(data_pr)))

data_pr['shortbook_date'] = pd.to_datetime(data_pr['created_at']).dt.normalize()

for i in ['created_at', 'received_at']:
    data_pr[i] = pd.to_datetime(data_pr[i], errors='coerce')

logger.info("Min date in new data is {} and max date is {}".format(data_pr['shortbook_date'].min().strftime("%Y-%m-%d"),
                                                                   data_pr['shortbook_date'].max().strftime(
                                                                       "%Y-%m-%d")))

##################################################
# Now loss calculation starts
##################################################

# Remove invalid requested quantity
data_pr_f = data_pr[data_pr.requested_quantity > 0]
logger.info("New PR data length after removing negative and 0 requested quantity is : {}".format(len(data_pr_f)))

# Replace NULL drug-ids with -1 so that it can be identified as new drug
data_pr_f['drug_id'] = data_pr_f['drug_id'].fillna(-1).astype(int)

# MySQL drugs table

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

drugs_q = """
        SELECT
            id as drug_id,
            `drug-name`,
            `composition`,
            category as drug_category,
            type as drug_type,
            `repeatability-index`
        FROM
            drugs
"""
drugs_q = drugs_q.replace('`', '"')
logger.info(drugs_q)

rs_db.execute(drugs_q, params=None)
data_drugs: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if data_drugs is None:
    data_drugs = pd.DataFrame(columns=['drug_id', 'drug_name', 'composition', 'drug_category',
                                       'drug_type', 'repeatability_index'])
data_drugs.columns = [c.replace('-', '_') for c in data_drugs.columns]
logger.info(len(data_drugs))

logger.info("Drug master length is : {}".format(len(data_drugs)))

# Join PR data with drugs
data_pr_f = data_pr_f.merge(data_drugs, how='left', on=['drug_id'])
data_pr_f['drug_name'] = np.where(data_pr_f['drug_id'] > 0, data_pr_f['drug_name_y'], data_pr_f['drug_name_x'])

# Search for bills in bill-items-1

bills = tuple(list(data_pr_f['bill_id'].dropna().astype(int).drop_duplicates()))

logger.info("Number of bills to be searched is : {}".format(len(bills)))

#########################################
# Sales data
#########################################

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

sales_q = """
        SELECT
            `created-at`,
            `patient-id`,
            `bill-id`,
            `drug-id`,
            sum("revenue-value")/sum("quantity") as avg_rate,
            sum("quantity") as sold_quantity
        FROM
            sales
        WHERE
            `bill-id` in {}
            and `bill-flag` = 'gross'
        GROUP BY
            `created-at`,
            `patient-id`,
            `bill-id`,
            `drug-id`
""".format(bills)

sales_q = sales_q.replace('`', '"')
# logger.info(sales_q)

rs_db.execute(sales_q, params=None)
data_b: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if data_b is None:
    data_b = pd.DataFrame(columns=['created_at', 'patient_id', 'bill_id',
                                   'drug_id', 'avg_rate', 'sold_quantity'])
data_b.columns = [c.replace('-', '_') for c in data_b.columns]
logger.info(len(data_b))

data_b['bill_date'] = pd.to_datetime(data_b['created_at']).dt.normalize()

logger.info("Bill date length is : {}".format(len(data_b)))

# Join with main data
data_b = data_b.rename(columns={'patient_id': 'bill_patient_id', 'created_at': 'bill_created_at'})

data_final_join = data_pr_f.merge(data_b, how='left', on=['bill_id', 'drug_id'])

logger.info("PR data length after joining with bills data is : {}".format(len(data_final_join)))

data_final_join['day_diff'] = (data_final_join['bill_date'] - data_final_join['shortbook_date']).dt.days

# Loss calculation
data_final_join['within_tat_flag'] = np.where(data_final_join['day_diff'].between(0, 7), 1, 0)
data_final_join['within_tat_sold_quantity'] = np.where(data_final_join['within_tat_flag'] == 1,
                                                       data_final_join['sold_quantity'], 0)

data_final_join['diff_quantity'] = data_final_join['requested_quantity'] - data_final_join[
    'within_tat_sold_quantity']
data_final_join['loss_quantity'] = np.where(data_final_join['diff_quantity'] > 0, data_final_join['diff_quantity'],
                                            0)

# Rate already present in bill attached
data_final_join['rate_present'] = np.where(data_final_join['avg_rate'] > 0, 1, 0)

# Filter out quantity > 30
data_final_join2 = data_final_join[data_final_join.requested_quantity <= 30]

logger.info("PR data length after filtering out outlier quantity is : {}".format(len(data_final_join2)))

# Populate rate for those not fulfilled
drugs = tuple(list(data_final_join2['drug_id'].dropna().drop_duplicates().astype(int)))

logger.info("Count of drugs to look up in historical sales is : {}".format(len(drugs)))

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

rate_q = """
        SELECT
            "drug-id",
            SUM("revenue-value")/SUM("quantity") AS avg_rate_system
        FROM
            "sales"
        WHERE
            date("created-at") <= '{0}'
            and "bill-flag" = 'gross'
        GROUP BY
            "drug-id"
""".format(period_end_d)

rate_q = rate_q.replace('`', '"')
logger.info(rate_q)

rs_db.execute(rate_q, params=None)
data_d: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if data_d is None:
    data_d = pd.DataFrame(columns=['drug_id', 'avg_rate_system'])
data_d.columns = [c.replace('-', '_') for c in data_d.columns]
logger.info(len(data_d))
data_d.head()

logger.info("Count of drugs to looked up successfully in historical sales is : "
            "{}".format(len(data_d)))

# Join with main data
data_final_join2 = data_final_join2.merge(data_d, how='left', on=['drug_id'])

# What should the final rate be, if present in PR then that, else if present in system then that.
data_final_join2['attributed_rate'] = np.where(data_final_join2['rate_present'] == 1, data_final_join2['avg_rate'],
                                               data_final_join2['avg_rate_system'])

# Still some drugs which are new, will not have a rate assigned
data_final_join2['system_present'] = np.where(data_final_join2['attributed_rate'] > 0, 1, 0)

# Missing value in rate is replaced by a value which is representative of all drugs rate
# Can be changed later
data_final_join2['attributed_rate'] = data_final_join2['attributed_rate'].fillna(100)

# Final loss sales
data_final_join2['final_lost_sales'] = data_final_join2['loss_quantity'].astype(float) * data_final_join2[
    'attributed_rate'].astype(float)

# Sold quantity and num_days_sold

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

sales_summ_q = """
    SELECT
        "store-id",
        "drug-id",
        COUNT(distinct date("created-at")) as num_days_sold,
        MAX(date("created-at")) as last_sold
    FROM
        "sales"
    WHERE
        date("created-at") <= '{0}'
        and "bill-flag" = 'gross'
    GROUP BY
        "store-id",
        "drug-id"
""".format(period_end_d)

sales_summ_q = sales_summ_q.replace('`', '"')
logger.info(sales_summ_q)

rs_db.execute(sales_summ_q, params=None)
data_d2: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if data_d2 is None:
    data_d2 = pd.DataFrame(columns=['store_id', 'drug_id', 'num_days_sold', 'last_sold'])
data_d2.columns = [c.replace('-', '_') for c in data_d2.columns]
logger.info(len(data_d2))
data_d2.head()

logger.info("Count of drugs with sold quantity and num_days_sold is : {}".format(len(data_d2)))

# Join with main data
data_final_join2 = data_final_join2.merge(data_d2, how='left', on=['store_id', 'drug_id'])

# Put 0 for those not sold in that store
data_final_join2['num_days_sold'] = data_final_join2['num_days_sold'].fillna(0)

# Round off some values
for i in ['attributed_rate', 'final_lost_sales']:
    data_final_join2[i] = np.round(data_final_join2[i].astype(float), 2)

# Attributed date
data_final_join2['attributed_loss_date'] = data_final_join2['shortbook_date'] + timedelta(days=7)

# Merge stores

read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

stores_q = """
        SELECT
            id AS store_id,
            store AS store_name
        FROM
            "stores-master"
"""
stores_q = stores_q.replace('`', '"')
logger.info(stores_q)

rs_db.execute(stores_q, params=None)
stores: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if stores is None:
    stores = pd.DataFrame(columns=['store_id', 'store_name'])
stores.columns = [c.replace('-', '_') for c in stores.columns]
logger.info(len(stores))

cfr_pr = data_final_join2.merge(stores, how='left', on=['store_id'])

# For redshift specific
# Convert int columns to int
for i in ['num_days_sold', 'repeatability_index', 'bill_id']:
    cfr_pr[i] = cfr_pr[i].fillna(0).astype(int)

for i in ['shortbook_date', 'attributed_loss_date', 'bill_date', 'last_sold']:
    cfr_pr[i] = pd.to_datetime(cfr_pr[i]).dt.date

logger.info(cfr_pr.columns)

#########################################
# Loss classification logic (stand-alone function), in dss it's cfr-seg
########################################
# DOI INFO
store_ids = tuple(list(cfr_pr['store_id'].dropna().astype(int).drop_duplicates()))
drug_ids = tuple(list(cfr_pr['drug_id'].dropna().astype(int).drop_duplicates()))

# Fetch all tables data
# tagging drug as new/old
read_schema = 'prod2-generico'
rs_db.execute(f"set search_path to '{read_schema}'", params=None)

doi_q = """
    SELECT 
        `store-id`, 
        `drug-id`, 
        `min`, 
        `safe-stock`, 
        `max`, 
        `drug-grade` 
    FROM
        `drug-order-info` 
    WHERE
        `store-id` in {0} 
        and `drug-id` in {1}
""".format(store_ids, drug_ids)

doi_q = doi_q.replace('`', '"')
# logger.info(doi_q)

rs_db.execute(doi_q, params=None)
doi_data: pd.DataFrame = rs_db.cursor.fetch_dataframe()
if doi_data is None:
    doi_data = pd.DataFrame(columns=['store_id', 'drug_id', 'min', 'safe_stock', 'max', 'drug_grade'])
doi_data.columns = [c.replace('-', '_') for c in doi_data.columns]
logger.info(len(doi_data))

cfr_pr = cfr_pr.merge(doi_data, how='left', on=['store_id', 'drug_id'])

cfr_pr['fulfilment_hours'] = (cfr_pr['received_at'] - cfr_pr['created_at']).astype('timedelta64[h]')


# Loss classification tag
def loss_classification_tag(x):
    if x['drug_grade'] in ['A1', 'A2']:
        return 'DS_loss'
    elif (x['inventory_at_creation']) >= (x['requested_quantity']):
        return 'system_loss'
    elif (x['fulfilment_hours'] >= 0) & (x['fulfilment_hours'] < 48):
        return 'store_loss'
    elif (x['fulfilment_hours'] >= 48) or pd.isnull(x['fulfilment_hours']):
        return 'supply_chain_loss'
    else:
        return 'None'


cfr_pr['loss_tag'] = cfr_pr.apply(loss_classification_tag, axis=1)

# DB upload columns
final_cols = ['store_id', 'store_name', 'shortbook_date', 'patient_id', 'unique_id', 'drug_id',
              'short_book_id',
              'drug_name_x', 'composition', 'repeatability_index', 'drug_category', 'drug_type',
              'requested_quantity', 'inventory_at_creation',
              'created_at', 'received_at',
              'home_delivery', 'drug_name_y',
              'bill_id', 'bill_date', 'within_tat_flag', 'within_tat_sold_quantity', 'loss_quantity',
              'system_present', 'attributed_rate', 'final_lost_sales', 'attributed_loss_date', 'num_days_sold',
              'last_sold',
              'min', 'safe_stock', 'max', 'drug_grade',
              'fulfilment_hours', 'loss_tag']

cfr_pr = cfr_pr[final_cols]

#####################################################
# Write to DB
#####################################################
data_export = cfr_pr.copy()

data_export.columns = [c.replace('_', '-') for c in data_export.columns]

write_schema = 'prod2-generico'
write_table_name = 'cfr-patient-request'

table_info = helper.get_table_info(db=rs_db_write, table_name=write_table_name, schema=write_schema)

# table_info_clean = table_info[~table_info['column_name'].isin(['id', 'created-at', 'updated-at'])]

# Mandatory lines
data_export['etl-created-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['etl-created-by'] = 'etl-automation'
data_export['etl-updated-at'] = datetime.now(
    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data_export['etl-updated-by'] = 'etl-automation'

s3.write_df_to_db(df=data_export[table_info['column_name']], table_name=write_table_name, db=rs_db_write,
                  schema=write_schema)
logger.info("Uploading successful with length: {}".format(len(data_export)))

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()

logger.info("File ends")
