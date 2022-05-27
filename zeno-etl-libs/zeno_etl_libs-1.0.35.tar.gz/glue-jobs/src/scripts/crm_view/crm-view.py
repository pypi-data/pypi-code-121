"""
Author:shubham.gupta@zeno.health
Purpose: crm view customer stages
"""
import argparse
import os
import sys
from datetime import datetime as dt

import numpy as np
import pandas as pd
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-acd', '--alternate_calc_date', default=0, type=int, required=False)
parser.add_argument('-cd', '--calculation_date', default=0, type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to
alternate_calc_date = args.alternate_calc_date
calculation_date = args.calculation_date
logger = get_logger()

logger.info(f"env: {env}")

# params
status = 'Failed'
if alternate_calc_date:
    calculation_date = calculation_date
else:
    calculation_date = str(dt.now().date())

schema = 'prod2-generico'
table_name = 'crm-view'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

read_schema = 'prod2-generico'

if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f"""
            DELETE
            FROM
                "{read_schema}"."{table_name}"
            WHERE
                "calculation-date" = '{calculation_date}';
                """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

# Fetching all patient recency, frequency, monetary(abv)
rfm_q = f"""
        SELECT
            b."patient-id",
            SUM(bi.rate * bi.quantity) AS "total-cx-purchase",
            SUM(bi.rate * bi.quantity)/ COUNT(DISTINCT bi."bill-id") AS monetary,
            COUNT(DISTINCT bi."bill-id") AS frequency,
            DATEDIFF('days', MAX(DATE(b."created-at")), '2021-01-01') AS recency,
            SUM(i."purchase-rate" * bi.quantity) AS "total-wc-purchase",
            MIN(DATE(b."created-at")) AS "acq-date",
            MAX(DATE(b."created-at")) AS "last-bill"
        FROM
            "prod2-generico"."bills-1" b
        LEFT JOIN "prod2-generico"."bill-items-1" bi 
        ON
            b.id = bi."bill-id"
        LEFT JOIN "prod2-generico"."inventory-1" i ON
            bi."inventory-id" = i.id
        WHERE DATE(b."created-at") <= '{calculation_date}'
        GROUP BY
            b."patient-id";"""

# Fetching all patient promos
promo_q = f"""
        SELECT
            b."patient-id",
            SUM(b."promo-discount") AS "promo-discount",
            SUM(b."redeemed-points") AS "redeemed-points"
        FROM
            "{read_schema}"."bills-1" b
        WHERE
            DATE(b."created-at") <= '{calculation_date}'
        GROUP BY
            b."patient-id";"""

# Fetching all patient consumer behaviour and value segment
calc_date = calculation_date[:7] + "-01"
cbs_q = f"""
        select
            cbs."patient-id" ,
            cbs."behaviour-segment" as "current-behaviour-segment"
        from
            "{read_schema}"."customer-behaviour-segment" cbs
        where
            cbs."segment-calculation-date" = '{calc_date}';"""

cvs_q = f"""
        select
            cvs."patient-id" ,
            cvs."value-segment" as "current-value-segment"
        from 
            "{read_schema}"."customer-value-segment" cvs 
        where
            cvs."segment-calculation-date"  = '{calc_date}'; """

# Fetching all patient consumer_flag
flag_q = f"""
        select
            rm."patient-id" ,
            (case
                when max(cast (rm."is-generic" as int))= 1 then 'generic'
                else 'non-generic'
            end) as "is-generic",
            (case
                when max(cast (rm."is-repeatable" as int ))= 1 then 'repetable'
                else 'non-repeatable'
            end) as "is-repeatable",
            (case
                when max(cast (rm."is-chronic" as int))= 1 then 'chronic'
                else 'acute'
            end) as "is-chronic" ,
            (case
                when max(cast (rm."hd-flag" as int))= 1 then 'hd-customer'
                else 'non-hd-customer'
            end) as "is-hd"
        from
            "{read_schema}"."retention-master" rm
        where
            date(rm."bill-date") < '{calculation_date}'
        group by
            rm."patient-id";"""

# Fetching all patient acquisition source
acq_q = f"""
        select
            rm."patient-id",
            (case
                when rm."promo-code-id" is null then 'organic'
                else 'inorganic'
            end) as acquisition
        from
            "{read_schema}"."retention-master" rm
        where
            rm."p-first-bill-date" = rm."created-at";"""

# Fetching patient primary stores

store_q = f"""
        select
            rm."patient-id",
            rm.store,
            rm.abo,
            rm."store-manager",
            rm."store-type",
            rm."store-city" as "city",
            rm."line-manager",
            rm."store-b2b"
        from
            "{read_schema}"."retention-master" rm
        where
            rm."p-first-bill-id" = rm.id;"""

rfm = rs_db.get_df(rfm_q)
promo = rs_db.get_df(promo_q)
cbs = rs_db.get_df(cbs_q)
cvs = rs_db.get_df(cvs_q)
flags = rs_db.get_df(flag_q)
acq = rs_db.get_df(acq_q)
stores = rs_db.get_df(store_q)

# logger_info
logger.info('total number of patient, size : {}'.format(len(rfm)))

# data types
rfm['total-cx-purchase'] = rfm['total-cx-purchase'].astype(float)
rfm['total-wc-purchase'] = rfm['total-wc-purchase'].astype(float)
rfm['monetary'] = rfm['monetary'].astype(float)
rfm['acq-date'] = pd.to_datetime(rfm['acq-date'])
rfm['last-bill'] = pd.to_datetime(rfm['last-bill'])
promo['promo-discount'] = promo['promo-discount'].astype(float)
# Function for Customer stages

rfm['r-score'] = 1
rfm['f-score'] = 1
rfm['m-score'] = 1

rfm['r-score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['m-score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

try:
    rfm['f-score'] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])
except ValueError:
    rfm['f-score'] = pd.cut(rfm['frequency'], bins=[0, 1, 3, 6, 10, np.inf], labels=[1, 2, 3, 4, 5])

rfm['stage'] = np.nan
rfm['stage'] = np.where((rfm['r-score'].isin([3, 4])) & (rfm['f-score'].isin([4, 5])), 'Loyal Customers',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([4, 5])) & (rfm['f-score'].isin([2, 3])), 'Potential Loyalist',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([5])) & (rfm['f-score'].isin([4, 5])), 'Champions', rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([5])) & (rfm['f-score'].isin([1])), 'New Customer', rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([4])) & (rfm['f-score'].isin([1])), 'Promising', rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([3])) & (rfm['f-score'].isin([3])), 'Customer needing attention',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([3])) & (rfm['f-score'].isin([1, 2])), 'About to Sleep',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([1, 2])) & (rfm['f-score'].isin([3, 4])), 'At Risk',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([1, 2])) & (rfm['f-score'].isin([5])), 'Can\'t Lose them',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([1, 2])) & (rfm['f-score'].isin([1, 2])), 'Hibernating',
                        rfm['stage'])
rfm['stage'] = np.where((rfm['r-score'].isin([1])) & (rfm['f-score'].isin([1])), 'Lost', rfm['stage'])

# roi calculation at customer level
crm = pd.merge(rfm, promo, on='patient-id', how='left')
# roi = profit_gain / investment
# p = wc_purchase, s = cx_purchase, pr = promo/discount
# roi = (s-p-pr )/(p+pr)
crm['investment'] = crm['total-wc-purchase'] + crm['redeemed-points'] + crm['promo-discount']
crm['gain'] = crm['total-cx-purchase'] - crm['investment']
crm['roi'] = crm['gain'] / crm['investment']
crm = crm.drop(columns=['investment', 'gain'])

crm['abv-seg'] = pd.cut(crm['monetary'],
                        bins=[0, 200, 300, 500, 750, 1000, 1250, 1500, 2000, np.inf],
                        labels=['<=200', '201-300', '301-500',
                                '501-750', '751-1000', '1001-1250',
                                '1251-1500', '1501-2000', '>2000'])
crm['nob-seg'] = pd.cut(crm['frequency'],
                        bins=[0, 4, 10, 25, 50, 100, np.inf],
                        labels=['1-4', '5-10', '11-25',
                                '26-50', '50-100', '>100'])

# consumer behaviour and value segment
crm = pd.merge(crm, cbs, on='patient-id', how='left')
crm = pd.merge(crm, cvs, on='patient-id', how='left')

# consumer flag
crm = pd.merge(crm, flags, on='patient-id', how='left')

# consumer acquisition
crm = pd.merge(crm, acq, on='patient-id', how='left')

# consumer store data
crm = pd.merge(crm, stores, on='patient-id', how='left')

crm['calculation-date'] = calculation_date
crm['segment-calculation-date'] = calc_date

# data correction
crm['r-score'] = crm['r-score'].fillna(1)
crm['f-score'] = crm['f-score'].fillna(1)
crm['m-score'] = crm['m-score'].fillna(1)

crm['r-score'] = crm['r-score'].astype(int)
crm['f-score'] = crm['f-score'].astype(int)
crm['m-score'] = crm['m-score'].astype(int)

logger.info("info :", crm.info())

# etl
crm['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
crm['created-by'] = 'etl-automation'
crm['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
crm['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=crm[table_info['column_name']], file_name='crm_view.csv')
s3.write_df_to_db(df=crm[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# closing the connection
rs_db.close_connection()
