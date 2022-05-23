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
parser.add_argument('-yc', '--year_cutoff', default='2019', type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
year_cutoff = args.year_cutoff

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
logger.info("year_cutoff - " + year_cutoff)

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

stores_query = """
            select
                distinct id as "store-id"
            from
                "prod2-generico".stores s """
stores = rs_db.get_df(stores_query)

logger.info("Fetched distinct stores")

q_aa = """
        select
            ri."id" as "return-id",
            ri."inventory-id",
            ri."returned-quantity",
            rtd."store-id",
            str."name" as "store-name",
            drug."drug-name",
            h."name" as "dist-name",
            dn."serial",
            ri."net",
            case
                when date(iv."dispatched-at") = '0101-01-01' then 1
                else 0
            end as flag,
            iv."approved-at" as "invoice-approved-at",
            iv."dispatched-at" as "invoice-dispatched-at",
            rtd."created-at",
            ri."approved-at",
            dn."dispatched-at",
            ri."settled-at" as "ri-settled-at",
            dn."settled-at" as "dn-settled-at",
            dn."accounted-at",
            ri."status" as "return-status",
            dn."status" as "dispatch-status",
            concat(DATE_PART(mon, rtd."created-at"), concat( '-', DATE_PART(y, rtd."created-at"))) as "created-period",
            concat(DATE_PART(mon, dn."dispatched-at"), concat('-', DATE_PART(y, dn."dispatched-at"))) as "dispatch-period",
            ri."return-reason",
            date(inv."expiry") as "expiry",
            h."credit-period" ,
            concat(DATE_PART(mon, ri."settled-at"), concat('-', DATE_PART(y, ri."settled-at"))) as "settled-period",
            ri."discard-reason",
            date(ri."discarded-at") as "discarded-at",
            rtd."created-by",
            ri."approved-by",
            iv."invoice-number",
            date(iv."invoice-date") as "invoice-date",
            sdm."forward-dc-id" as "DC",
            case
                when (date(iv."dispatched-at")= '0101-01-01'
                or iv."dispatched-at" > rtd."created-at") then 'DC'
                else 'Store'
            end as "Origin",
            h."type" as "distributor-type",
            case
                when h."credit-period">0 then 'credit'
                else 'non-credit'
            end as "distributor credit",
            case
                when ri."debit-note-reference" is null
                and ri."status" = 'saved' then '1.Saved'
                when ri."debit-note-reference" is null
                and ri."status" = 'approved' then '2.Approved'
                when ri."debit-note-reference" is not null
                and dn."status" = 'Saved' then '3.DN Saved'
                when ri."debit-note-reference" is not null
                and dn."status" = 'dispatched' then '4.DN Dispatched'
                when ri."debit-note-reference" is not null
                and dn."status" = 'Settled' then '5.DN Settled'
                when ri."debit-note-reference" is not null
                and dn."status" = 'Accounted' then '6.DN Accounted'
                when ri."status" = 'discarded' then '7.discarded'
                else 'Status issue'
            end as "Comprehensive status",
            case
                when (date(iv."dispatched-at")= '0101-01-01'
                or iv."dispatched-at" > rtd."created-at")
                and extract(y from iv."dispatched-at") > {year_cutoff}
                and ri."return-reason" in (
                                'reason-product-damaged',
                                'reason-not-ordered',
                                'reason-to-be-returned',
                                'reason-wrong-product',
                                'reason-softcopy-excess',
                                'reason-near-expiry',
                                'reason-product-expired',
                                'reason-na',
                                'reason-already-returned',
                                'reason-customer-refused',
                                'reason-wrongly-ordered',
                                'reason-excess-supplied',
                                'reason-non-moving',
                                'reason-wrong-mrp',
                                'reason-wrong-expiry') then 'DC Salable returns'
                when (date(iv."dispatched-at")= '0101-01-01'
                or iv."dispatched-at" > rtd."created-at")
                and extract(y from iv."dispatched-at") > {year_cutoff}
                and ri."return-reason" in (
                                'reason-product-short',
                                'reason-short-from-dc') then 'DC Short returns'
                when ri."return-reason" in ('reason-product-damaged', 'reason-near-expiry', 'reason-product-expired', 'reason-wrong-expiry') then 'Store Expiry'
                when ri."return-reason" in ('reason-not-ordered', 'reason-to-be-returned', 'reason-wrong-product', 'reason-softcopy-excess', 'reason-na', 'reason-already-returned', 'reason-customer-refused', 'reason-wrongly-ordered', 'reason-excess-supplied', 'reason-non-moving', 'reason-wrong-mrp') then 'Store Salable'
                when ri."return-reason" in ('reason-product-short', 'reason-short-from-dc') then 'Store Short'
                else 'issue'
            end as "Comprehensive reasons"
        from
            "prod2-generico"."return-items" ri
        left join "prod2-generico"."returns-to-dc" rtd on
            ri."return-id" = rtd."id"
        left join "prod2-generico"."debit-notes" dn on
            ri."debit-note-reference" = dn."id"
        left join "prod2-generico"."stores" str on
            rtd."store-id" = str."id"
        left join "prod2-generico"."inventory" inv on
            inv."id" = ri."inventory-id"
        left join "prod2-generico"."drugs" drug on
            drug."id" = inv."drug-id"
        left join "prod2-generico"."invoices" iv on
            iv."id" = inv."invoice-id"
        left join "prod2-generico"."distributors" h on
            h."id" = iv."distributor-id"
        left join "prod2-generico"."store-dc-mapping" sdm on
            sdm."store-id" = str."id"
            and h."type" = sdm."drug-type"
        where
            ri."status" not in ('reverted',
                    'deleted')
        """.format(year_cutoff=year_cutoff)

df2 = rs_db.get_df(q_aa)

logger.info("Fetched return data")

df2['net'] = df2['net'].astype(float)
# df2[['expiry','invoice-date',]].astype(datetime.datetime.date())
status2 = False
# pd.to_datetime(df2['expiry'])

try:
    schema = 'prod2-generico'
    table_name = 'wc-returns'
    table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

    truncate_query = """
            delete from "prod2-generico"."wc-returns"
            """
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table deleted')

    s3.write_df_to_db(df=df2[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')

    status2 = True
except:
    status2 = False

if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

# logger.close()
end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} table updated",
                      mail_body=f"{table_name} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()

