#!/usr/bin/env python
# coding: utf-8

#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

import json
from datetime import datetime, timedelta

import argparse
import pandas as pd
import numpy as np
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-dd', '--doh_days', default=60, type=int, required=False)
parser.add_argument('-sd', '--sold_days', default=90, type=int, required=False)
parser.add_argument('-ed', '--expiry_days', default=210, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
doh_days = args.doh_days
sold_days = args.sold_days
expiry_days = args.expiry_days

os.environ['env'] = env

logger = get_logger(level = 'INFO')

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.now()
logger.info('Script Manager Initialized')
logger.info("")
logger.info("parameters reading")
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("doh_days - " + str(doh_days))
logger.info("sold_days - " + str(sold_days))
logger.info("expiry_days -" + str(expiry_days))

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# NPI at store
# =============================================================================

npi_store_query = """
select
    *
from
    "prod2-generico"."dead-stock-inventory" dsi
where
    "inventory-type" = 'Rotate'
"""
npi_store = rs_db.get_df(npi_store_query)

logger.info("Fetched NPI from dead-stock-inventory - lines -{}".format(len(npi_store)))

# =============================================================================
# Fetching Store-Clusters List
# =============================================================================

s0 = """
SELECT
    s."store-id",
    sc."cluster-id"
FROM
    (
    SELECT
        s.id as "store-id"
    FROM
        "prod2-generico".stores s
    WHERE
        s.category = 'retail' )s
left join (
    SELECT
        sc."store-id" ,
        sc."cluster-id" 
    FROM
        "prod2-generico"."store-clusters" sc
    WHERE
        sc."is-active" = 1)sc
    ON
    s."store-id" = sc."store-id"

"""

clust_store = rs_db.get_df(s0)

logger.info("Fetched store-cluster combo")

npi_store = pd.merge(npi_store, clust_store[['store-id', 'cluster-id']], on='store-id', how='left')

# =============================================================================
# Adding Cluster Sold Quantity
# =============================================================================

cluster_sold_total = pd.DataFrame()

for cluster_id in tuple(map(int, (list(clust_store[clust_store['cluster-id'].notna()]['cluster-id'].astype(int).unique())))):

    s00 = """
        select
            sc."store-id"
        from
            "prod2-generico"."store-clusters" sc
        where
            sc."is-active" = 1
            and sc."cluster-id" in ({cluster_id})
        """.format(cluster_id=cluster_id)
    dist_stores = rs_db.get_df(s00)

    stores_in_cluster = tuple(map(int, dist_stores['store-id'].values.tolist()))
    logger.info('stores in cluster {}-{}'.format(cluster_id, stores_in_cluster))

    drgs = tuple(map(int, (list(npi_store[npi_store['cluster-id'] == cluster_id]['drug-id'].unique()))))

    s1 = """
        select
            '{cluster_id}' as "cluster-id",
            "drug-id",
            sum("net-quantity") as "clus-sales-qty"
        from
            "prod2-generico"."sales" sh
        where
            "store-id" in {stores_in_cluster}
            -- and "created-date" >= '2022-04-14'
            and date("created-at") >=dateadd(d,-{sold_days},current_date)
            and "drug-id" in {drgs}
        group by
            "drug-id"
    """.format(cluster_id=cluster_id, stores_in_cluster=stores_in_cluster, sold_days=sold_days, drgs=drgs)

    cluster_sold = rs_db.get_df(s1)
    cluster_sold_total = cluster_sold_total.append(cluster_sold, ignore_index='True')

    logger.info('cluster-{},Cluster_sold_added'.format(cluster_id))

npi_store[['cluster-id', 'drug-id']]=npi_store[['cluster-id', 'drug-id']].apply(pd.to_numeric, errors='ignore').astype('Int64')
cluster_sold_total[['cluster-id', 'drug-id']]=cluster_sold_total[['cluster-id', 'drug-id']].apply(pd.to_numeric, errors='ignore').astype('Int64')

# =============================================================================
# Adding Flags - Cluster sold, Shelf life more than 6 months
# =============================================================================

npi_store = pd.merge(npi_store, cluster_sold_total, on=['cluster-id', 'drug-id'], how='left')

npi_store['days-to-expire'] = (pd.to_datetime(npi_store['expiry'])-datetime.today()).dt.days

def timecheck(a):
    if a > expiry_days:
        return 1
    else:
        return 0

npi_store['shelf-life-more-than-6-months-flag'] = npi_store['days-to-expire'].apply(timecheck)

npi_store['clus-sales-qty'].fillna(0, inplace=True)

npi_store['clus-sales-qty'] = npi_store['clus-sales-qty'].astype(int)

def clustsoldcheck(a):
    if a == 0:
        return 0
    else:
        return 1

npi_store['clust-sold-flag'] = npi_store['clus-sales-qty'].apply(clustsoldcheck)

logger.info("Added Flags in dead_stock_inventory - Current lines -{}".format(len(npi_store)))

npi_store_summary = npi_store[npi_store['shelf-life-more-than-6-months-flag']==1]
npi_store_summary = npi_store_summary[npi_store_summary['clust-sold-flag']==0]

npi_store_summary = npi_store_summary.groupby('store-id').agg({'store-name':'first',
                                          'quantity':'sum',
                                          'locked-quantity':'sum',
                                          'value':'sum',
                                          'locked-value':'sum'}).reset_index()

npi_store_summary['sns-time'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
npi_store['created-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
npi_store['created-by']= 'data.science@zeno.health'
npi_store['updated-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
npi_store['updated-by'] = 'data.science@zeno.health'

npi_store_summary =npi_store_summary[['store-id','store-name','quantity','locked-quantity','value','locked-value','sns-time']]
npi_store_summary['created-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
npi_store_summary['created-by']= 'data.science@zeno.health'
npi_store_summary['updated-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
npi_store_summary['updated-by'] = 'data.science@zeno.health'

npi_store[['invoice-id','invoice-item-id','distributor-id','short-book-id']] = npi_store[['invoice-id','invoice-item-id','distributor-id','short-book-id']].apply(pd.to_numeric, errors='ignore').astype('Int64')

# =============================================================================
# writing to Redshift
# =============================================================================
schema = 'prod2-generico'
table_name = 'npi-inventory-at-store'
table_name2 = 'npi-inventory-at-store-sns-last-3-month'
table_name3 = 'npi-inventory-at-store-sns-summary'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)
table_info2 = helper.get_table_info(db=rs_db_write, table_name=table_name2, schema=schema)
table_info3 = helper.get_table_info(db=rs_db_write, table_name=table_name3, schema=schema)
status2 = False
status1 = False
status3 = False

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' delete
                        from "{schema}"."{table_name}" '''
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table deleted')

    s3.write_df_to_db(df=npi_store[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')
    status2 = True

if status2:
    if isinstance(table_info2, type(None)):
        raise Exception(f"table: {table_name2} do not exist, create the table first")
    else:
        logger.info(f"Table:{table_name2} exists")

        npi_store['sns-time']= datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

        delete_main_query = f''' 
                            delete
                            from
                                "{schema}"."{table_name2}" 
                            where
                                extract(mon from "sns-time") = extract(mon from current_date) '''
        rs_db_write.execute(delete_main_query)

        logger.info(str(table_name2) + ' table data deleted for same months entry')

        delete_main_query = f''' 
                            delete
                            from
                                "{schema}"."{table_name2}" 
                            where
                                DATE("sns-time")< DATE(dateadd(d,-125,current_date)) '''
        rs_db_write.execute(delete_main_query)

        logger.info(str(table_name2) + ' table data deleted for 4+ month old data')

        s3.write_df_to_db(df=npi_store[table_info2['column_name']], table_name=table_name2, db=rs_db_write,
                          schema=schema)

        logger.info(str(table_name2) + ' table uploaded')

        status1 = True

if status1:
    logger.info(f"Table:{table_name2} exists")

    delete_main_query = f''' 
                        delete
                        from
                            "{schema}"."{table_name3}" 
                        where
                            extract(mon from "sns-time") = extract(mon from current_date) '''
    rs_db_write.execute(delete_main_query)

    logger.info(str(table_name3) + ' table data deleted for same months entry')

    s3.write_df_to_db(df=npi_store_summary[table_info3['column_name']], table_name=table_name3, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name3) + ' table uploaded')

    status3 = True

if status3 is True:
    status = 'Success'
else:
    status = 'Failed'

# logger.close()
end_time = datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} table updated",
                      mail_body=f"{table_name2} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()
