#!/usr/bin/env python
# coding: utf-8
# =============================================================================
# author: saurav.maskar@zeno.health
# purpose: to populate store-group-compostion-master
# =============================================================================

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.logger import get_logger, send_logs_via_email
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

status2 = False
if env == 'dev':
    logger.info('')
    logger.info('development env setting schema and table accordingly')
    schema2 = '`test-generico`'
    table2 = '`store-group-composition-master-data-`'
elif env == 'stage':
    logger.info('')
    logger.info('staging env setting schema and table accordingly')
    schema2 = '`test-generico`'
    table2 = '`store-group-composition-master-data-`'
elif env == "prod":
    logger.info('')
    logger.info('prod env setting schema and table accordingly')
    schema2 = '`prod2-generico`'
    table2 = '`store-group-composition-master`'
else:
    logger.info('')
    logger.info('staging env setting schema and table accordingly')
    schema2 = '`test-generico`'
    table2 = '`store-group-composition-master-data-`'

# =============================================================================
# Fetching Compositions for cluster
# =============================================================================

s2 = """

select
    s."store-group-id",
    sc."cluster-id" as "cluster-id",
    i."drug-id" ,
    max(d."release")  as "release",
    max(d."dosage-form") as "dosage-form" ,
    max(d.composition) as "composition",
    Case
        when max(d."company-id") = 6984 then 'GOODAID'
        ELSE 'other'
    END AS "goodaid-flag",
    CASE
        when max(d."type") in ('ethical', 'high-value-ethical') THEN 'ethical'
        WHEN max(d."type") in ('generic', 'high-value-generic') THEN 'generic'
        ELSE 'others'
    END AS "drug-type"
from
    "prod2-generico"."inventory-1" i
inner join "prod2-generico"."store-clusters" sc on
    i."store-id" = sc."store-id"
    and sc."is-active" = 1
inner join "prod2-generico".stores s
    on
    i."store-id" = s.id
inner join "prod2-generico".drugs d on
    i."drug-id" = d.id
where
    i."franchisee-inventory" = 0
    and i.quantity>0
group by
    s."store-group-id",
    sc."cluster-id" ,
    i."drug-id"
   """
cluster_combination = rs_db.get_df(s2)

logger.info('')
logger.info('Fetched data for clusters')

# =============================================================================
# Fetching Compositions for non cluster
# =============================================================================

s3 = """
select
    s."store-group-id",
    NULL as "cluster-id",
    i."drug-id" ,
    max(d."release") as "release",
    max(d."dosage-form") as "dosage-form",
    max(d.composition) as "composition",
    Case
        when max(d."company-id") = 6984 then 'GOODAID'
        ELSE 'other'
    END AS "goodaid-flag",
    CASE
        when max(d."type") in ('ethical', 'high-value-ethical') THEN 'ethical'
        WHEN max(d."type") in ('generic', 'high-value-generic') THEN 'generic'
        ELSE 'others'
    END AS "drug-type"
from
    "prod2-generico"."inventory-1" i
inner join "prod2-generico".stores s
    on
    i."store-id" = s.id
inner join "prod2-generico".drugs d on
    i."drug-id" = d.id
where
    i."franchisee-inventory" = 0
    and i.quantity>0
group by
    s."store-group-id",
    i."drug-id"
   """
non_cluster_combination = rs_db.get_df(s3)

logger.info('')
logger.info('Fetched data for non clusters')

union = pd.concat([cluster_combination, non_cluster_combination])
union = union[union['composition'].notna()]

# =============================================================================
# Calculating current composition master
# =============================================================================

def conversion_to_str_for_join(x):
    if type(x)!= type(None) and x is not None and x != 'nan' and pd.notna(x):
        return str(int(x))
    else:
        return str(x)

union['drug-id'] = union['drug-id'].apply(conversion_to_str_for_join)

union['cluster-id'] = union['cluster-id'].fillna('-123')

# ethical

mask = (((union['drug-type'] == 'ethical') | (union['drug-type'] == 'high-value-ethical') )& (union['composition'] != '') & (union['composition'].notna()))

ethical = union[mask]

ethical.reset_index(drop=True, inplace=True)

ethical = ethical.groupby(['store-group-id', 'cluster-id', 'composition', 'dosage-form', 'release']).agg(
    {'drug-id': ','.join}).reset_index()

ethical.rename(columns={'drug-id': 'ethical-drug-id-list'}, inplace=True)

# generic
mask2 = ((union['drug-type'] == 'generic') & (union['composition'] != '') & (union['composition'].notna()))

generic = union[mask2]

generic.reset_index(drop=True, inplace=True)

generic = generic.groupby(['store-group-id', 'cluster-id', 'composition', 'dosage-form', 'release']).agg(
    {'drug-id': ','.join}).reset_index()

generic.rename(columns={'drug-id': 'generic-drug-id-list-dummy'}, inplace=True)

# goodaid

mask3 = ((union['goodaid-flag'] == 'GOODAID') & (union['composition'] != '') & (union['composition'].notna()))

goodaid = union[mask3]

goodaid.reset_index(drop=True, inplace=True)

goodaid = goodaid.groupby(['store-group-id', 'cluster-id', 'composition', 'dosage-form', 'release']).agg(
    {'drug-id': ','.join}).reset_index()

goodaid.rename(columns={'drug-id': 'goodaid-drug-id-list'}, inplace=True)

union = pd.merge(ethical, generic ,how = 'outer',on =['store-group-id', 'cluster-id', 'composition', 'dosage-form', 'release'])

union = pd.merge(union, goodaid, how='outer',
                 on=['store-group-id', 'cluster-id', 'composition', 'dosage-form', 'release'])

# If goodaid is present then in generic only show goodaid

conditions = [
    union['goodaid-drug-id-list'].notna(),
    union['goodaid-drug-id-list'].isna()
]
choices = [ union['goodaid-drug-id-list'], union['generic-drug-id-list-dummy']]
union['generic-drug-id-list'] = np.select(conditions, choices)

# If generic is present then we won't show ethical

conditions = [
    union['generic-drug-id-list'].notna(),
    union['generic-drug-id-list'].isna()
]
choices = [ None, union['ethical-drug-id-list']]
union['ethical-drug-id-list'] = np.select(conditions, choices)

union = union[['store-group-id', 'cluster-id', 'release', 'dosage-form',
               'composition', 'ethical-drug-id-list', 'generic-drug-id-list']]

union['cluster-id'] = union['cluster-id'].replace(['-123'],np.nan)

# Sorting drug-list for join with prod table and updating value where there is change

def drug_list_sorter(x):
    if type(x) == type(None) or x == 'nan' or pd.isna(x):
        return x
    else:
        lst = x.split(',')
        lst.sort(reverse=True)
        lst = lst[:5]
        sorted_csv = ",".join(lst)
        return sorted_csv

union['ethical-drug-id-list'] = union['ethical-drug-id-list'].apply(drug_list_sorter)

union['generic-drug-id-list'] = union['generic-drug-id-list'].apply(drug_list_sorter)

logger.info('')
logger.info('Calculated composition master, ready to make changes on prod table')

# =============================================================================
# writing to Prod
# =============================================================================
mysql_write = MySQL(read_only=False)
mysql_write.open_connection()

status2 = False

try:

    truncate_query = '''
                    DELETE
            FROM
                {}.{} sgcm
            WHERE
                sgcm.`store-group-id` != 2
             '''.format(schema2, table2)

    mysql_write.engine.execute(truncate_query)

    logger.info('')
    logger.info(str(table2) + ' Existing table truncated, except where store-group-id is 2')

    if env == 'dev':
        table2 = 'store-group-composition-master-data-'
    elif env == 'stage':
        table2 = 'store-group-composition-master-data-'
    elif env=='prod':
        table2 = 'store-group-composition-master'
    else:
        table2 = 'store-group-composition-master-data-'

    union.to_sql(
        name=table2, con=mysql_write.engine,
        if_exists='append',
        chunksize=500, method='multi', index=False)
    logger.info(' ')
    logger.info(str(table2) + ' table appended to MySQL')

    status2 = True

except :
    logger.info('')
    logger.info(str(table2) + 'table load failed')

if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table2} table updated",
                      mail_body=f"{table2} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

# Closing the DB Connection
rs_db.close_connection()
mysql_write.close()
