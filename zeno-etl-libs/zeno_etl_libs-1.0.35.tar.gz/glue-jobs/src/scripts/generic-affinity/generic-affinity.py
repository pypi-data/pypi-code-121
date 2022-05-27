import argparse
import sys
import os

sys.path.append('../../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from dateutil.relativedelta import relativedelta
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
import pandas as pd
import numpy as np
import dateutil
import datetime
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")

args, unknown = parser.parse_known_args()

env = args.env
os.environ['env'] = env
logger = get_logger()

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name1 = 'generic-affinity'
table_name2 = 'patient-generic-affinity'
table_info1 = helper.get_table_info(db=rs_db, table_name=table_name1, schema=schema)
table_info2 = helper.get_table_info(db=rs_db, table_name=table_name2, schema=schema)

# =============================================================================
# patient level bill count
# =============================================================================


gb = """
    select
    	"patient-id" ,
    	count(distinct case when "type" = 'generic' and "bill-flag" = 'gross' then "bill-id" end ) as "generic_bill_count",
    	count(distinct case when "bill-flag" = 'gross' then "bill-id" end) as gross_bill_count
    from
    	"prod2-generico".sales
    where
    	date("created-at")< CURRENT_DATE
    group by
    	"patient-id"
    """
p_bills=rs_db.get_df(gb)

logger.info("Data: patient level bill count fetched successfully")

p_bills.columns = [c.replace('-', '_') for c in p_bills.columns]
p_bills[['generic_bill_count', 'gross_bill_count']].fillna(0, inplace=True)

p_bills['generic_bill_pct'] = (p_bills['generic_bill_count'] / (p_bills['gross_bill_count'])) * 100

# =============================================================================
# patient level substitution
# =============================================================================


subs = """
    select
    	"patient-id" ,
    	"substitution-status" ,
    	sum(quantity) as quantity
    from
    	"prod2-generico".sales
    where
    	"bill-flag" = 'gross'
    	and "type" = 'generic'
    	and date("created-at")<CURRENT_DATE 
    group by
    	"patient-id", "substitution-status" 
    """
p_subs=rs_db.get_df(subs)

p_subs.columns = [c.replace('-', '_') for c in p_subs.columns]

p_subs['quantity'].fillna(0, inplace=True)
p_subs1 = pd.pivot_table(p_subs,
                         values='quantity',
                         index=['patient_id'],
                         columns=['substitution_status']).reset_index()
p_subs1.columns = [c.replace('-', '_') for c in p_subs1.columns]

p_subs1.fillna(0, inplace=True)
p_subs1['subs_pct'] = (p_subs1['substituted'] / (p_subs1['substituted'] + p_subs1['not_substituted'])) * 100

metadata = pd.merge(right=p_subs1, left=p_bills, on=['patient_id'], how='left')

# =============================================================================
# patient level return %
# =============================================================================


ret = """
    select
    	"patient-id" ,
    	count(distinct case when "type" = 'generic' and "bill-flag" = 'return' then "bill-id" end ) as "generic_return_bill_count",
    	count(distinct case when "bill-flag" = 'return' then "bill-id" end) as "gross_return_bill"
    from
    	"prod2-generico".sales
    where
    	date("created-at")< CURRENT_DATE
    group by
    	"patient-id"
    """
p_return=rs_db.get_df(ret)

p_return.columns = [c.replace('-', '_') for c in p_return.columns]

p_return[['generic_return_bill_count', 'gross_return_bill']].fillna(0, inplace=True)
p_return['return_pct'] = ((p_return['generic_return_bill_count']) / (p_return['gross_return_bill'])) * 100

p_return['not_return_pct'] = 100 - p_return['return_pct']

metadata = pd.merge(left=metadata, right=p_return, on=['patient_id'], how='left')

metadata['not_return_pct'].fillna(100, inplace=True)

# =============================================================================
# patient level recency
# =============================================================================

rec = """
    select
    	"patient-id" ,
    	max("created-at") as "last_visit"
    from
    	"prod2-generico".sales
    where
    	"bill-flag" = 'gross'
    	and date("created-at")<CURRENT_DATE
    group by
    	"patient-id"

    """
p_recency=rs_db.get_df(rec)

p_recency.columns = [c.replace('-', '_') for c in p_recency.columns]

prev_date = (datetime.datetime.today() + relativedelta(days=-1))
p_recency['last_visit'] = pd.to_datetime(p_recency['last_visit'], format="%y-%m-%d")
p_recency['prev_date'] = prev_date
p_recency['prev_date'] = pd.to_datetime(p_recency['prev_date'], format="%y-%m-%d")

p_recency['num_months'] = (p_recency['prev_date'] - p_recency['last_visit']) / np.timedelta64(1, 'M')

conditions = [
    (

        (p_recency['num_months'] <= 3)
    ),

    (
            (p_recency['num_months'] > 3) &
            (p_recency['num_months'] <= 6)
    ),

    (
            (p_recency['num_months'] > 6) &
            (p_recency['num_months'] <= 12)
    ),

    (

        (p_recency['num_months'] > 12)
    )
]
choices = [100,
           75, 50, 25]
p_recency['recency_pct'] = np.select(conditions, choices,
                                     default=0)
p_recency['recency_pct'].fillna(0, inplace=True)

metadata = pd.merge(left=metadata, right=p_recency, on=['patient_id'], how='left')

# =============================================================================
# patient level generic recency
# =============================================================================

gen_rec = """
    select
    	"patient-id" ,
    	max("created-at") as "last_generic_visit"
    from
    	"prod2-generico".sales
    where
    	"bill-flag" = 'gross'
    	and "type" ='generic'
    	and date("created-at")<CURRENT_DATE
    group by
    	"patient-id"
    """
p_grecency=rs_db.get_df(gen_rec)

p_grecency.columns = [c.replace('-', '_') for c in p_grecency.columns]

p_grecency['last_generic_visit'] = pd.to_datetime(p_grecency['last_generic_visit'], format="%y-%m-%d")
p_grecency['g_prev_date'] = prev_date
p_grecency['g_prev_date'] = pd.to_datetime(p_grecency['g_prev_date'], format="%y-%m-%d")

p_grecency['g_num_months'] = ((p_grecency['g_prev_date'] - p_grecency['last_generic_visit'])
                              / np.timedelta64(1, 'M'))

conditions = [
    (

        (p_grecency['g_num_months'] <= 3)
    ),

    (
            (p_grecency['g_num_months'] > 3) &
            (p_grecency['g_num_months'] <= 6)
    ),

    (
            (p_grecency['g_num_months'] > 6) &
            (p_grecency['g_num_months'] <= 12)
    ),

    (

        (p_grecency['g_num_months'] > 12)
    )
]
choices = [100,
           75, 50, 25]
p_grecency['gen_recency_pct'] = np.select(conditions, choices,
                                          default=0)
p_grecency.drop('g_prev_date', axis='columns', inplace=True)
p_grecency['gen_recency_pct'].fillna(0, inplace=True)

metadata = pd.merge(left=metadata, right=p_grecency, on=['patient_id'], how='left')

metadata.fillna(0, inplace=True)

metadata['generic_likelihood'] = ((metadata['generic_bill_pct'] + metadata['gen_recency_pct']
                                   + metadata['subs_pct'] + metadata['not_return_pct'] +
                                   metadata['recency_pct']) / (5))

conditions = [
    (

        (metadata['generic_likelihood'] >= 80)
    ),

    (
            (metadata['generic_likelihood'] < 80) &
            (metadata['generic_likelihood'] >= 60)
    ),

    (
            (metadata['generic_likelihood'] < 60) &
            (metadata['generic_likelihood'] >= 50)
    ),

    (

            (metadata['generic_likelihood'] < 50) &
            (metadata['generic_likelihood'] >= 25)
    ),

    (

        (metadata['generic_likelihood'] < 25)
    )
]

choices = [5,
           4, 3, 2, 1]
metadata['generic_affinity_score'] = np.select(conditions, choices,
                                               default=3)

generic_affinity = metadata
logger.info('length of generic_affinity is :' + str(len(generic_affinity)))

patient_generic_affinity = metadata[['patient_id', 'generic_affinity_score']]

logger.info('length of patient_generic_affinity is :', str(len(patient_generic_affinity)))

#Pushing data for generic_affinity

generic_affinity.columns = [c.replace('_', '-') for c in generic_affinity.columns]

generic_affinity['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

generic_affinity['created-by'] = 'etl-automation'

logger.info('Columns name of generic_affinity table for ordering purpose :', str((generic_affinity.columns)))

generic_affinity = generic_affinity[generic_affinity['gross-bill-count']>0]

generic_affinity = generic_affinity[['created-at','created-by','patient-id'
	,'gross-bill-count'	,'generic-bill-count','generic-bill-pct'
	,'generic-unavailable','not-in-inventory','not-substituted'
	,'substituted' ,'subs-pct','gross-return-bill','generic-return-bill-count'
	,'return-pct','not-return-pct','last-visit','prev-date'
	,'num-months','recency-pct','last-generic-visit','g-num-months'
	,'gen-recency-pct','generic-likelihood','generic-affinity-score']]

if isinstance(table_info1, type(None)):
    raise Exception(f"table: {table_name1} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name1} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name1}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=generic_affinity[table_info1['column_name']], table_name=table_name1, db=rs_db,
                      schema=schema)


#Pushing data for patient_generic_affinity

patient_generic_affinity.columns = [c.replace('_', '-') for c in patient_generic_affinity.columns]

patient_generic_affinity['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

patient_generic_affinity['created-by'] = 'etl-automation'

patient_generic_affinity = patient_generic_affinity[["created-at" ,"created-by" , "patient-id" , "generic-affinity-score"]]

if isinstance(table_info2, type(None)):
    raise Exception(f"table: {table_name2} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name2} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name2}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=patient_generic_affinity[table_info2['column_name']], table_name=table_name2, db=rs_db,
                      schema=schema)

# Closing the DB Connection
rs_db.close_connection()