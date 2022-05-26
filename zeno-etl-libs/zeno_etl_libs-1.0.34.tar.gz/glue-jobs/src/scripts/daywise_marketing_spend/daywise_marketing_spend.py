"""
Author:shubham.gupta@zeno.health
Purpose: marketing_spend & campaign effectiveness
"""

import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-fr', '--full_run', default=0, type=int, required=False)
parser.add_argument('-ar', '--alternate_range', default=0, type=int, required=False)
parser.add_argument('-st', '--start', default="2017-01-01", type=str, required=False)
parser.add_argument('-ed', '--end', default=str(dt.now().date()), type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to
full_run = args.full_run
alternate_range = args.alternate_range
start = args.start
end = args.end
logger = get_logger()

logger.info(f"env: {env}")
logger.info(f"print the env again: {env}")

# params
if full_run:
    start = '2017-05-13'
    end = str(dt.today().date() - timedelta(days=1))
elif alternate_range:
    start = start
    end = end
else:
    start = str(dt.today().date() - timedelta(days=2))
    end = str(dt.today().date() - timedelta(days=1))

schema = 'prod2-generico'
table_name = 'daywise-marketing-spend'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

read_schema = 'prod2-generico'
s = start
e = end

if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f"""
            DELETE
            FROM
                "{read_schema}"."{table_name}"
            WHERE
                "date" BETWEEN '{s}' AND '{e}';
                """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)
# Date_wise_spend_and_sale_calculation
market_spend_q = f"""
    SELECT
        T1.date_ as date ,
        T1.store_id,
        T1.`promo-code`,
        T1.`code-type`,
        T1.new_patient,
        T1.unique_patients_count,
        T1.total_bills_count,
        T1.sales,
        T1.profit,
        T2.marketing_spend
    FROM
        (
        SELECT
            date(b.`created-at`) AS date_,
            b.`store-id` AS store_id,
            coalesce(pc."promo-code", '0') AS "promo-code",
            coalesce(pc."code-type", '0') AS "code-type",
            (CASE
                WHEN date(b.`created-at`)= date(pm.`first-bill-date`) THEN 1
                ELSE 0
            END) AS new_patient,
            COUNT(DISTINCT b.`patient-id`) AS unique_patients_count,
            COUNT(DISTINCT b.id) AS total_bills_count,
            SUM(bi.quantity * bi.rate) AS sales,
            (SUM(bi.quantity * bi.rate)-SUM(i.`purchase-rate` * bi.quantity)) AS profit
        FROM
            "{read_schema}".`bills-1` b
        LEFT JOIN "{read_schema}".`promo-codes` pc ON
            b.`promo-code-id` = pc.id
        LEFT JOIN "{read_schema}".`bill-items-1` bi ON
            b.id = bi.`bill-id`
        LEFT JOIN "{read_schema}".`patients-metadata` pm ON
            b.`patient-id` = pm.`patient-id`
        LEFT JOIN "{read_schema}".`inventory-1` i ON
            bi.`inventory-id` = i.id
        WHERE
            date(b.`created-at`) BETWEEN '{s}' AND '{e}'
        GROUP BY
            date(b.`created-at`),
            b.`store-id`,
            new_patient,
            pc.`promo-code`,
            pc.`code-type` ) T1
    LEFT JOIN 
    (
        SELECT
            date(b.`created-at`) AS date_,
            b.`store-id` AS store_id,
            coalesce(pc."promo-code", '0') AS "promo-code",
            coalesce(pc."code-type", '0') AS "code-type",
            (CASE
                WHEN date(b.`created-at`)= date(pm.`first-bill-date`) THEN 1
                ELSE 0
            END) AS new_patient,
            COUNT(DISTINCT b.`patient-id`) AS unique_patients_count,
            COUNT(DISTINCT b.id) AS total_bills_count,
            SUM(b.`promo-discount`) AS marketing_spend
        FROM
            "{read_schema}".`bills-1` b
        LEFT JOIN "{read_schema}".`promo-codes` pc ON
            b.`promo-code-id` = pc.id
        LEFT JOIN "{read_schema}".`patients-metadata` pm ON
            b.`patient-id` = pm.`patient-id`
        WHERE
            date(b.`created-at`) BETWEEN '{s}' AND '{e}'
        GROUP BY
            date(b.`created-at`),
            b.`store-id`,
            new_patient,
            pc.`promo-code`,
            pc.`code-type` ) T2 ON
        T1.date_ = T2.date_
        AND T1.store_id = T2.store_id
        AND T1.new_patient = T2.new_patient
        AND T1.`promo-code` = T2.`promo-code`
        AND T1.`code-type` = T2.`code-type`;"""

market_spend_q = market_spend_q.replace('`', '"')
logger.info(market_spend_q)

marketing_spend_sales = rs_db.get_df(market_spend_q)
marketing_spend_sales.columns = [c.replace('-', '_') for c in marketing_spend_sales.columns]
logger.info(len(marketing_spend_sales))

# If customer is not using any promo so tagging him as 'Organic'

# Temporary : will resolve query
marketing_spend_sales['pr_tag'] = 0
marketing_spend_sales['hd_tag'] = 0
# Filling null value as '0'
fill_value = {'promo_code': 'Organic',
              'code_type': 'Organic'}

marketing_spend_sales = marketing_spend_sales.fillna(value=fill_value)

# store attributes
store_q = f"""
        select
            id as store_id ,
            store,
            abo,
            "store-manager",
            "line-manager",
            "opened-at" as store_open_at
        from
            "{read_schema}"."stores-master" sm;
        """

store_q = store_q.replace('`', '"')
logger.info(store_q)

rs_db.execute(store_q, params=None)
store_attr: pd.DataFrame = rs_db.cursor.fetch_dataframe()
store_attr.columns = [c.replace('-', '_') for c in store_attr.columns]
logger.info(len(store_attr))
store_attr.head()

marketing_spend_sales = pd.merge(marketing_spend_sales,
                                 store_attr,
                                 left_on='store_id',
                                 right_on='store_id',
                                 how='left')

marketing_spend_sales['redeemed_point'] = None
marketing_spend_sales.columns = [c.replace('_', '-') for c in marketing_spend_sales.columns]

# etl
marketing_spend_sales['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
marketing_spend_sales['created-by'] = 'etl-automation'
marketing_spend_sales['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
marketing_spend_sales['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=marketing_spend_sales[table_info['column_name']], file_name='marketing_spend_sales.csv')
s3.write_df_to_db(df=marketing_spend_sales[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# closing the connection
rs_db.close_connection()
