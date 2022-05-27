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
import datetime

import argparse
import pandas as pd
import numpy as np
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# getting inventory snapshot data
cur_date = datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()
cur_year = datetime.datetime.now(tz=gettz('Asia/Kolkata')).year
prev_date = cur_date - datetime.timedelta(1)
logger.info('Inventory snapshot for date ' + str(cur_date))
stores_query = """
    select
        distinct id as "store-id"
    from
        "prod2-generico"."stores"
             """
stores = rs_db.get_df(stores_query)

# expiry_loss_zp
status1 = False
try:    
    exipry_loss_query = """
            select
                d.*,
                e."name",
                s."name" as "cost-centre",
                e."gstn",
                        r."id" as "return-item-id",
                r."taxable" as "taxable-value",
                        r."gst" as "tax-rate",
                r."gst-amount" as "tax-value",
                        r."net" as "return-net-value",
                e."id" as "distributor-id",
                "drug-id",
                        "invoice-number",
                "invoice-date",
                f."type",
                e.type as "dist-type",
                        f."drug-name",
                x.id as "invt-id",
                "batch-number",
                x."expiry"
            from
                "prod2-generico"."return-items" r
            join "prod2-generico"."debit-notes" d on
                r."debit-note-reference" = d."id"
            join "prod2-generico"."inventory" x on
                r."inventory-id" = x."id"
            join "prod2-generico"."invoices" i on
                i."id" = x."invoice-id"
            join "prod2-generico"."distributors" e on
                d."dist-id" = e."id"
            join "prod2-generico"."stores" s on
                d."store-id" = s."id"
            join "prod2-generico"."drugs" f on
                f."id" = x."drug-id"
            where
                d."dist-id" != 64
                and d."status" in ('accounted', 'settled')
                and d."category" = 'product-expired'
                and (date(d."settled-at") = date(Dateadd(d,-1,current_date)) or date(d."accounted-at") = date(Dateadd(d,-1,current_date)) ) 
                        """
    expiry_loss = rs_db.get_df(exipry_loss_query)

    logger.info('fetched expiry_loss data for returns whose debit note is settled/accounted yesterday')

    schema = 'prod2-generico'
    table_name = 'expiry-loss-accounts'
    table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

    truncate_query = '''
        delete
        from
            "prod2-generico"."expiry-loss-accounts" 
        where
            (date("settled-at") = date(Dateadd(d,-1,current_date))
                or date("accounted-at") = date(Dateadd(d,-1,current_date)) )
    '''
    rs_db_write.execute(truncate_query)

    logger.info(str(table_name) + ' table deleted for yesterday data to avoid data duplication in case of multiple runs')

    s3.write_df_to_db(df=expiry_loss[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table appended')
    
    status1 = True
except:
    logger.info('expiry_loss_ load failed')

# WC_inventory_invoices
status2 = False
try:

    # Keeping Audit loss data for current year only

    audit_loss_query = """
    SELECT
        b."id" AS "inventory-check-item-id",
        b."check-id",
        a."type" AS "audit-type",
        a."created-at" AS "audit-date",
        a."store-id",
        s."name" AS "store-name",
        b."drug-id",
        d."drug-name",
        d."type",
        d."category",
        b."inventory-id",
        b."expected",
        b."accounted",
        b."status",
        COALESCE(t."sum-changes", 0) AS "sum-changes",
        COALESCE((b."accounted" + t."sum-changes"), 0) AS "final-accounted",
        i."ptr" AS "zp-ptr",
        i."purchase-rate" AS "wc-ptr",
        COALESCE((b."expected" - (b."accounted" + t."sum-changes")),
                0) AS "qty-diff",
        COALESCE((b."expected" * i."ptr"), 0) AS "expected-value",
        COALESCE(((b."accounted" + t."sum-changes") * i."ptr"),
                0) AS "accounted-value"
    FROM
        "prod2-generico"."inventory-check-1" a
            JOIN
        "prod2-generico"."inventory-check-items-1" b ON a."id" = b."check-id"
            LEFT JOIN
        (SELECT 
            y."store-id",
                y."inventory-id",
                y."inventory-check-item-id",
                SUM(y."change") AS "sum-changes"
        FROM
            "prod2-generico"."inventory-changes-1" y
        WHERE
            y."change-reason" IN ('audit-reconciliation' , 'found-later', 'multiple-scanned', 'pack-size-error')
        GROUP BY y."store-id" , y."inventory-id" , y."inventory-check-item-id") t ON b."id" = t."inventory-check-item-id"
            LEFT JOIN
        "prod2-generico"."stores" s ON s."id" = a."store-id"
            LEFT JOIN
        "prod2-generico"."drugs" d ON d."id" = b."drug-id"
            LEFT JOIN
        "prod2-generico"."inventory-1" i ON i."id" = b."inventory-id"
    WHERE
         date(a."created-at") = date(Dateadd(d,-1,current_date))
                    """
    audit_loss = rs_db.get_df(audit_loss_query)

    logger.info('fetched audit_loss data for yesterday')

    schema = 'prod2-generico'
    table_name2 = 'audit-loss-accounts'
    table_info2 = helper.get_table_info(db=rs_db_write, table_name=table_name2, schema=schema)

    truncate_query = '''
        delete
        from
            "prod2-generico"."audit-loss-accounts"
        where
            date("audit-date") = date(Dateadd(d,-1,current_date))
    '''
    rs_db_write.execute(truncate_query)

    logger.info(str(table_name2) + ' table deleted for yesterday data to avoid duplicate data in case of multiple runs')

    truncate_query = '''
        delete
        from
            "prod2-generico"."audit-loss-accounts"
        where
            extract (y from "audit-date") != {current_year}
    '''.format(current_year= cur_year)
    rs_db_write.execute(truncate_query)

    logger.info(str(table_name2) + ' table deleted for previous years data')

    s3.write_df_to_db(df=audit_loss[table_info2['column_name']], table_name=table_name2, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name2) + ' table uploaded')

    status2 = True
except:
    logger.info('audit_loss load failed')

if (status1 & status2) is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} & {table_name2} table updated",
                      mail_body=f"{table_name} & {table_name2} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()