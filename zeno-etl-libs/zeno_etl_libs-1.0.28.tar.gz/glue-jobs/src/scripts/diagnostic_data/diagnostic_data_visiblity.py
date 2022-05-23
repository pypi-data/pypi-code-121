"""
Author:shubham.gupta@zeno.health
Purpose: Diagnostic Data Visibility
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

from datetime import datetime as dt
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to
logger = get_logger()

logger.info(f"env: {env}")
logger.info(f"print the env again: {env}")

schema = 'prod2-generico'
table_name = 'diagnostic-visibility'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

read_schema = 'prod2-generico'

redemption_pay_q = f"""
                SELECT
                "redemption-id",
                SUM(CASE
                    WHEN "payment-type" IN ('CASH', 'LINK') THEN amount
                    ELSE 0
                END) "cash-payment"
                FROM
                    "{read_schema}"."redemption-payments" rp
                GROUP BY
                "redemption-id",
                "store-id"; 
                """

source_q = f"""
            SELECT
                id as "redemption-id",
                "patient-id",
                source,
                status,
                "store-id",
                "total-amount" AS "total-sales",
                r."redeemed-value" AS "reward-payment",
                date("created-at") as date, 
                "call-status",
                "created-by" as pharmacist
            FROM
                "{read_schema}".redemption r;
            """

tests_q = f"""
        SELECT
            rs."redemption-id",
            rs."sku-id",
            rp.name AS "test-name",
            rs."slot-date" AS "booking-at"
        FROM
            "{read_schema}"."redemption-skus" rs
        LEFT JOIN "{read_schema}"."reward-product" rp ON
            rs."sku-id" = rp.id;"""

patient_store_info_q = f"""
                    select
                        id as "patient-id",
                        "primary-store-id" as "store-id"
                    from
                        "{read_schema}"."patients-metadata-2" pm;"""
store_master_q = f""" 
                select 
                    sm."id" as "store-id",
                    sm.store,
                    sm.city,
                    sm.line,
                    sm.abo,
                    sm."store-manager"
                from
                    "{read_schema}"."stores-master" sm;"""

acquisition_medium_q = f"""
                        SELECT
                            r."patient-id",
                            (CASE
                                WHEN (MIN(DATE(r."redemption-date")) - MIN(DATE(b."created-at"))) > 0 
                                THEN 'drug_store'
                                WHEN (MIN(DATE(r."redemption-date")) - MIN(DATE(b."created-at"))) < 0 
                                THEN 'diagnostic'
                                ELSE 'diagnostic_no_visit_store'
                            END ) "acq-medium"
                        FROM
                            "{read_schema}".redemption r
                        LEFT JOIN "{read_schema}"."bills-1" b ON
                            r."patient-id" = b."patient-id"
                        WHERE
                            r.status IN ('REDEMPTION', 'COMPLETED')
                        GROUP BY
                            r."patient-id";"""

cancel_q = f"""
            SELECT
                rcrm."redemption-id",
                rcrm.comments,
                zer."reason-name",
                zer."type" AS "reason-type"
            FROM
                "{read_schema}"."redemption-cancellation-reason-mapping" rcrm
            LEFT JOIN "{read_schema}"."zeno-escalation-reason" zer ON
                rcrm."redemption-cancellation-reason-id" = zer.id ;"""

red_pay = rs_db.get_df(redemption_pay_q)
sources = rs_db.get_df(source_q)
tests = rs_db.get_df(tests_q)
patient_store_info = rs_db.get_df(patient_store_info_q)
store_master = rs_db.get_df(store_master_q)
acquisition_medium = rs_db.get_df(acquisition_medium_q)
cancel_reason = rs_db.get_df(cancel_q)

# writing in same file different sheets
data = pd.merge(red_pay, sources, on='redemption-id', how='outer')

data = pd.merge(data, cancel_reason, on='redemption-id', how='outer')

# saving test names in array format so that it will be easy to filter out in query
tests = tests.groupby('redemption-id', as_index=True).agg({'sku-id': 'nunique', 'booking-at': 'max'}).reset_index()

tests = tests.rename(columns={'sku-id': 'number-of-tests'})

data = pd.merge(data, tests, on='redemption-id', how='left')

# If Store ID exist then Store ID Else patient primary store
data['store-id'] = data['store-id'].fillna(0)

data = pd.merge(data, store_master, on='store-id', how='left')
data['store-id'] = data['store-id'].astype(int)
data = pd.merge(data, acquisition_medium, on='patient-id', how='left')

# NODO = Number of diagnostic orders
# Only valid orders, is when status is 'REDEMPTION' or 'COMPLETED' else Canceled
data['nodo'] = np.where(data['status'].isin(['REDEMPTION', 'COMPLETED']), 1, 0)
data = data.sort_values(['date', 'redemption-id'])
data['nodo'] = data.groupby(['patient-id'], as_index=False)['nodo'].cumsum()
data['nodo'] = np.where(data['status'].isin(['REDEMPTION', 'COMPLETED']), data['nodo'], 0)

# rename of source
data['source'] = data['source'].map({'OPS_DASHBOARD': 'OPS Oracle',
                                     'LOYALTY_UI': 'App',
                                     'STORE': 'Store'})

# etl
data['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['created-by'] = 'etl-automation'
data['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
data['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=data[table_info['column_name']], file_name='data.csv')
s3.write_df_to_db(df=data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# closing the connection
rs_db.close_connection()
