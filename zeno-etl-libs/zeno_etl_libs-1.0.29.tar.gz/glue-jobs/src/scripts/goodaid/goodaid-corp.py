#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz
from zeno_etl_libs.logger import get_logger

import argparse
import pandas as pd
import datetime
import numpy as np


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env


logger = get_logger()
logger.info(f"env: {env}")


rs_db = DB()
rs_db.open_connection()

s3 = S3()


# def main(rs_db, s3):
schema = 'prod2-generico'
table_name = 'inventory-ga'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

#Getting the data
#Active GoodAid drugs

query = f'''
        SELECT
            d.id as "drug_id",
            d."composition-master-id" as "composition_master_id",
            d.composition
        FROM
           "prod2-generico"."prod2-generico"."inventory-1" i
        join "prod2-generico"."prod2-generico".drugs d  on
           i."drug-id"  = d.id
        WHERE
            d."company-id"  = 6984
            and i."created-at"  <= current_date
        group by
            d."composition-master-id" ,
            d.composition,
            d.id  '''

ga_active= rs_db.get_df(query)
logger.info("Data: ga_active compositions fetched")

gaid_compositions = tuple(map(int, list(ga_active['composition_master_id'].unique())))

# Store master
query = f'''
        select
            id as "store-id",
            store as "store-name",
            "store-manager" ,
            "line-manager" ,
            abo
        from
            "prod2-generico"."prod2-generico"."stores-master" sm '''

store_master= rs_db.get_df(query)
logger.info("Data: got stores master data successfully")

# current inventory
inv = '''
        select
            a."store-id" ,
            a."drug-id" ,
            b."drug-name" ,
            b."type" ,
            b.category ,
            b.company ,
            b.composition ,
            b."composition-master-id" ,
            (c.min) as "min",
            (c."safe-stock") as "safe-stock",
            (c.max) as "max",
            SUM(a.quantity + a."locked-for-check" + a."locked-for-audit" +
                a."locked-for-return" + a."locked-for-transfer") as "current-inventory",
            SUM(a."locked-quantity") as "in-transit",
            SUM((a.quantity + a."locked-for-check" + a."locked-for-audit" +
                a."locked-for-return" + a."locked-for-transfer") * a.ptr) as "value"
        from
            "prod2-generico"."prod2-generico"."inventory-1" a
        join "prod2-generico"."prod2-generico".drugs b on
            a."drug-id" = b.id
        left join
            "prod2-generico"."prod2-generico"."drug-order-info" c on
            c."store-id" = a."store-id"
            and c."drug-id" = b.id
        where
        b."composition-master-id" in {}
        group by
            a."store-id" ,
            a."drug-id" ,
            b."drug-name" ,
            b."type" ,
            b.category ,
            b.composition ,
            b.company,
            b."composition-master-id",
            c.min ,
            c."safe-stock" ,
            c.max'''

inventory= rs_db.get_df(inv.format(gaid_compositions))
logger.info("Inventory table successfully fetched")

inventory['goodaid-flag'] = np.where(inventory['company'] == 'GOODAID',
                                         'GoodAid', 'Non-GoodAid')

inventory['ss-status'] = np.where(inventory['max'] > 0, 'ss_set', 'ss_not_set')

conditions = [
        (
                (inventory['current-inventory'] <= inventory['safe-stock']) &
                (inventory['current-inventory'] > 0)
        ),
        (
            (inventory['current-inventory'] > inventory['safe-stock'])
        ),
        (
                inventory['current-inventory'] <= 0
        )

    ]
choices = ['inv_less_than_ss', 'inv_more_than_ss', 'not_in_inventory']

inventory['inventory-flag'] = np.select(conditions, choices, default='not_in_inventory')

inventory_ga = pd.merge(left=inventory, right=store_master, on=['store-id'], how='left')
logger.info("Data: inventory_ga table fetched successfully")

inventory_ga['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
inventory_ga['created-by'] = 'etl-automation'
inventory_ga['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
inventory_ga['updated-by'] = 'etl-automation'
inventory_ga.columns = [c.replace('_', '-') for c in inventory_ga.columns]
logger.info("Data: 1st table fetched successfully")

# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=inventory_ga[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")


####
# def main(rs_db, s3):
table_name = 'order-status-ga'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# order status
o_status= f'''
        select
            a.id as "short-book-id",
            a."store-id" ,
            a."drug-id" ,
            a."drug-name" ,
            c."type" ,
            c.company ,
            c.composition ,
            a.quantity ,
            a."required-quantity" ,
            a.status ,
            a."created-at" as "short-book-created-at",
            a."dispatched-at" as "short-book-dispatched-at" ,
            a."received-at" as "short-book-received-at" ,
            a."auto-short" ,
            a."patient-id"
        from
            "prod2-generico"."prod2-generico"."short-book-1" a
        left join
                    "prod2-generico"."prod2-generico".stores b on
            a."store-id" = b.id
        left join
                    "prod2-generico"."prod2-generico".drugs c on
            c.id = a."drug-id"
        where
            DATE(a."created-at") >= '2021-02-01'
            and c."company-id" = 6984'''


order_status= rs_db.get_df(o_status)
logger.info("Data: order_status df fetched successfully")

order_status['goodaid-flag'] = np.where(order_status['company'] == 'GOODAID',
                                            'GoodAid', 'Non-GoodAid')


def get_status(order_status):
    if (order_status['auto-short'] == 1) & (order_status['patient-id'] == 4480):
        return 'auto-short'
    elif (order_status['auto-short'] == 1) & (order_status['patient-id'] != 4480):
        return 'manual-short'

order_status['order-type'] = order_status.apply(get_status, axis=1)

del order_status['auto-short']
del order_status['patient-id']

order_status['ff-hours'] = (pd.to_datetime(order_status['short-book-dispatched-at'], errors='coerce') -
                                order_status['short-book-created-at']) / np.timedelta64(1, 'h')

order_status_ga = pd.merge(left=order_status, right=store_master, on=['store-id'], how='left')


order_status_ga['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
order_status_ga['created-by'] = 'etl-automation'
order_status_ga['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
order_status_ga['updated-by'] = 'etl-automation'
order_status_ga.columns = [c.replace('_', '-') for c in order_status_ga.columns]
logger.info("Data: all the operations performed and order status data fetched successfully")

# =========================================================================
# Writing table in Redshift
# =========================================================================

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=order_status_ga[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

# Closing the DB Connection
rs_db.close_connection()



