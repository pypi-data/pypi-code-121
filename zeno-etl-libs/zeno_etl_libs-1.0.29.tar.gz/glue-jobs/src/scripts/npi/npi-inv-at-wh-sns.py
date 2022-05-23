#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.config.common import Config
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

logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.datetime.now()
logger.info('Script Manager Initialized')
logger.info("")
logger.info("parameters reading")
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# NPI at WH Snapshot
# =============================================================================

npi_wh_query = """
        SELECT
            f.Itemc as "itemc",
            i.name ,
            i."Location" as "aisle",
            i.Barcode as "drug-id",
            sum(f.BQty) as "bqty"
        FROM
            "prod2-generico"."prod2-generico".fifo f 
        left join "prod2-generico"."prod2-generico".item i 
        on
            f.Itemc = i.code
        WHERE
            f.Acno = 59353
            and i.barcode  !~'[^0-9]'
        GROUP by
            f.Itemc ,
            i.name ,
            i.Barcode,
            i."location" 
        HAVING sum(f.BQty)> 0
        order by f.itemc asc
"""
npi_wh = rs_db.get_df(npi_wh_query)

logger.info("Fetched NPI in WH - balance quantity -{}".format(int(sum(npi_wh['bqty']))))

npi_wh['bqty'] = npi_wh['bqty'].apply(pd.to_numeric, errors='ignore').astype('Int64')
npi_wh['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# =============================================================================
# Writing table to RS
# =============================================================================

schema = 'prod2-generico'
table_name = 'npi-inv-at-wh-sns'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

status1 = False
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' delete
                        from "{schema}"."{table_name}" 
                         where date("updated-at")<date(dateadd(d,-30,current_date))
                        '''
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table 30 days + old data deleted')

    truncate_query = f''' delete
                        from "{schema}"."{table_name}" 
                        where date("updated-at")=date(current_date)
                        '''
    rs_db_write.execute(truncate_query)
    logger.info(
        str(table_name) + 'table data deleted for current date to avoid duplicate entries in case of multiple entries')

    s3.write_df_to_db(df=npi_wh[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')
    status1 = True

if status1 is True:
    status = 'Success'
else:
    status = 'Failed'

# =============================================================================
# Sending Email
# =============================================================================

# logger.close()
end_time = datetime.datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
logger.info('min_to_complete_job - ' + str(min_to_complete))
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name} table updated",
                      mail_body=f"{table_name} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

# Closing the DB Connection
rs_db.close_connection()
rs_db_write.close_connection()