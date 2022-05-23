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

status1 = False
try:
    current_date = datetime.datetime.now(tz=gettz('Asia/Kolkata')).date() -datetime.timedelta(days=1)

    customer_return_query = f"""
        select
            a."billed-at",
            a."returned-at",
            b."patient-id",
            b."store-id",
            f."name" as "store-name",
            c."drug-id",
            d."drug-name",
            d.type,
            d.category,
            e."drug-grade",
            a."return-id",
            a."inventory-id",
            a."bill-id",
            a."returned-quantity",
            a."return-reason",
            (a."rate" * a."returned-quantity") as "return-value"
        from
            "prod2-generico"."customer-return-items-1" a
        left join
             "prod2-generico"."customer-returns-1" b on
            a."return-id" = b."id"
        left join
             "prod2-generico"."inventory-1" c on
            c."id" = a."inventory-id"
        left join
             "prod2-generico"."drugs" d on
            d."id" = c."drug-id"
        left join
             "prod2-generico"."drug-order-info" e on
            e."store-id" = b."store-id"
            and e."drug-id" = c."drug-id"
        left join
             "prod2-generico"."stores" f on
            f."id" = b."store-id"
        where a."returned-at" = {current_date} 
    """.format(current_date= current_date)

    customer_return = rs_db.get_df(customer_return_query)

    logger.info('Customer return data loaded')

    if len(customer_return)!= 0:
        customer_return['billed-date'] = customer_return['billed-at'].dt.date
        customer_return['returned-date'] = customer_return['returned-at'].dt.date
        customer_return['return-time-hrs'] = (customer_return['returned-at'] - customer_return['billed-at'])/pd.Timedelta('1s')/60/60
    else:
        customer_return['billed-date'] = current_date
        customer_return['returned-date'] = current_date
        customer_return['return-time-hrs'] = 0

    customer_return = customer_return[[
                'billed-date', 'returned-date', 'patient-id', 'store-id',
                'store-name', 'drug-id', 'drug-name', 'type', 'category',
                'drug-grade', 'return-id', 'inventory-id', 'bill-id',
                'returned-quantity', 'return-reason',
                'return-value', 'return-time-hrs'
            ]]

    truncate_query = '''
    delete from "prod2-generico"."glue-customer-return"
    where date("returned-date") = {current_date}
    '''.format(current_date= current_date )
    rs_db_write.execute(truncate_query)

    logger.info('glue-customer-return data deleted for yesterday to avoid duplication in case of multiple runs')

    customer_return['uploaded-at']=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    schema = 'prod2-generico'
    table_name = 'glue-customer-return'
    table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

    s3.write_df_to_db(df=customer_return[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info('Customer return data written to redshift')
    status1 = True
except:
    status1 = False

if status1:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f'{env} - {status} - {table_name} updated',
    mail_body=f" {table_name} table updated, Time for job completion - {min_to_complete} mins ",
    to_emails=email_to, file_uris=[])

rs_db.close_connection()
rs_db_write.close_connection()