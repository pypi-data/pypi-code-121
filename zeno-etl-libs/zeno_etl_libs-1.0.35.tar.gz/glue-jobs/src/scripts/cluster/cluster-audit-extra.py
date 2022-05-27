#!/usr/bin/env python
# coding: utf-8

#created by - saurav maskar
#Objective - push all transfer note failed everyday into store audit,
    #Transfer note are failing because inventory is at store according to system
    # but it is not locally found, so we need to put those in audit

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
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
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health,vijay.pratap@zeno.health", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()

rs_db.open_connection()

s3 = S3()
start_time = datetime.now()
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# set parameters
# =============================================================================
# Change pso_date_1 As Date required to add in audit, yesterdays,

pso_date1 = (datetime.now() - timedelta(days = 1)).date()
pso_date2 = (datetime.now() - timedelta(days = 1)).date()

# =============================================================================
# expired pso
# =============================================================================

q1 = """
    Select
            pstm."from-store-id" AS "store-id" ,
        pso."drug-id" 
    FROM
        "prod2-generico"."pso-stock-transfer-mapping" pstm
    Left JOIN "prod2-generico"."pso-stock-transfer-inventory-mapping" pstim ON 
        pstm.id = pstim."pso-stock-transfer-mapping-id"
    Left join "prod2-generico"."patients-store-orders" pso 
        ON
        pstm."patient-store-order-id" = pso.id
    WHERE
        DATE(pso."created-at") >= '{}'
        and DATE(pso."created-at") <= '{}'
        and pstm."status" = 'expired'
    order by
        pso."created-at" DESC
    """.format(pso_date1, pso_date2)

expired_pso = rs_db.get_df(q1)

expired_pso['store-drug'] = expired_pso['store-id'].astype(str) + "-" +expired_pso['drug-id'].astype(str)

logger.info("")
logger.info("fetched expired pso's data, total items - {}".format(len(expired_pso['store-drug'])) )
logger.info("")

#=============================================================================
# drugs which are already in audit extra and not scanned to be removed
#=============================================================================

q2 = """
    select
        ae."drug-id" ,
        ae."store-id"
    FROM
        "prod2-generico"."audit-extra" ae
    WHERE
        ae.status = 'active'
    """
store_drugs_in_audit = rs_db.get_df(q2)

store_drugs_in_audit['store-drug-audit'] = store_drugs_in_audit['store-id'].astype(str) + "-" +store_drugs_in_audit['drug-id'].astype(str)

logger.info("")
logger.info("fetched active store-drug combinations in audit extra - {}".format(len(store_drugs_in_audit['store-drug-audit'])))
logger.info("")

#Checking if store-drug combination is already in audit

expired_pso_audit_check = pd.merge(expired_pso ,store_drugs_in_audit['store-drug-audit'],left_on = 'store-drug',
                                   right_on = 'store-drug-audit', how ='left')

expired_pso_after_audit_check = expired_pso_audit_check[expired_pso_audit_check['store-drug-audit'].isna()]

unique_store_drug_series = pd.Series(expired_pso_after_audit_check['store-drug'].unique())

unique_store_drug_1 = unique_store_drug_series.str.split(pat= '-', expand = True)

logger.info("")
logger.info("Removed drugs which are already in audit extra and status is saved, unique store-drug-combination - {}".format(len(unique_store_drug_1)))
logger.info("")

# =============================================================================
# creating output table
# =============================================================================
unique_store_drug = pd.DataFrame()
if len(unique_store_drug_1)>0:
    unique_store_drug['drug-id'] = unique_store_drug_1[1].astype(int)
    unique_store_drug['store-id'] = unique_store_drug_1[0].astype(int)
    unique_store_drug['created-by'] = 'system@zeno.health'

    logger.info("")
    logger.info("Table to append created, items to add - {}".format(len(unique_store_drug['drug-id'])))
    logger.info("")
else:
    logger.info("")
    logger.info("Table to append created, items to add - {}".format(len(unique_store_drug)))
    logger.info("")

# =============================================================================
# writing to audit_extra
# =============================================================================
# prod mysql
mysql_write = MySQL(read_only=False)
mysql_write.open_connection()

status2 = False

try:
    unique_store_drug.to_sql(
    name='audit-extra', con=mysql_write.engine,
    if_exists='append',
    chunksize=500, method='multi', index=False)
    logger.info('')
    logger.info('audit-extra' + ' table appended')

    status2 = True

except:
    logger.info(' ')
    logger.info(str('audit-extra') + ' table not appended correctly')

    status2 = False

if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

# email.send_email_file(subject='{} {} : Cluster Audit extra table'.format(
#                env, status),
#     mail_body=f" audit-extra table updated, Time for job completion - {min_to_complete} mins ",
#     to_emails=email_to, file_uris=[pso_added_uri])

rs_db.close_connection()
mysql_write.close()