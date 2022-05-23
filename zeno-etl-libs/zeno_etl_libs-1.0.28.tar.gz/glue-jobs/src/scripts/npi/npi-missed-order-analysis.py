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
parser.add_argument('-ad', '--analysis_date_parameter', default="NULL", type=str, required=False)
parser.add_argument('-adis', '--analysis_date_parameter_inv_sns', default="NULL", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
analysis_date_parameter = args.analysis_date_parameter
analysis_date_parameter_inv_sns = args.analysis_date_parameter_inv_sns

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
logger.info("analysis_date_parameter - " + analysis_date_parameter)
logger.info("analysis_date_parameter_inv_sns - " + analysis_date_parameter_inv_sns)
logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

analysis_date = (datetime.datetime.now(tz=gettz('Asia/Kolkata')) -datetime.timedelta(days=1)).strftime('%Y-%m-%d')
analysis_date_sns = (datetime.datetime.now(tz=gettz('Asia/Kolkata')) -datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# analysis_date = '2022-05-11'
# analysis_date_sns = '2022-05-09'

# =============================================================================
# Setting Analysis date
# =============================================================================

# analysis_date decides - For which day Shortbook orders need to be evaluated
# analysis_date_sns decides - For which day Fifo Inventory is taken
# By Default - Yesterdays Order Analysis With Yesterdays FIFO Will be done, To Give Time for orders to bounce

if analysis_date_parameter!="NULL":
    analysis_date = analysis_date_parameter
else:
    analysis_date = analysis_date

logger.info('analysis-date - '+ str(analysis_date))


if analysis_date_parameter_inv_sns!="NULL":
    analysis_date_sns = analysis_date_parameter_inv_sns
else:
    analysis_date_sns = analysis_date_sns

logger.info('analysis_date_sns Inventory of this day will be used for analysis - '+ str(analysis_date_sns))
# =============================================================================
# Fetching NPI at WH for today morning
# =============================================================================

npi_wh_query = """
    select
        *
    from
        "prod2-generico"."npi-inv-at-wh-sns"
    where date("updated-at") = '{analysis_date}'
""".format(analysis_date = analysis_date_sns)
whlivenpi= rs_db.get_df(npi_wh_query)

logger.info("Fetched NPI in WH - balance quantity -{}".format(int(sum(whlivenpi['bqty']))))

whlivenpi['aisle_number'] = (whlivenpi.loc[:,'aisle'].astype(str).str[1:3])
mask = (whlivenpi['aisle_number'] == '10') | (whlivenpi['aisle_number'] == '11')
whlivenpi = whlivenpi[mask]

whlivenpi = whlivenpi.groupby(['itemc','name','aisle_number','drug-id']).agg(sum).reset_index()


# =============================================================================
# Fetching Shortbook Orders for the day
# =============================================================================

drugs = tuple(map(int,(whlivenpi['drug-id'].unique())))
if len(drugs)==0:
    drugs = [0]
    drugs= str(list(drugs)).replace('[', '(').replace(']', ')')

sb_orders_query = """
select
	sb.id as "short-book-id",
    sb."store-id" ,
	sb."drug-name",
	sb."drug-id" ,
	case
		when sb."auto-short" = 0 then 'pr'
		when sb."auto-short" = 1
		and "patient-id" = 4480 then 'as'
	end as "order-type",
	sb.quantity AS "orderd-quantity",
    sb."distributor-id",
	d.name as "distributor-name",
	case
		when sb."distributor-id" = 8105 then 'warehouse-order'
		else 'other-distributor-order'
	end as "order-source"
from
	"prod2-generico"."short-book-1" sb
left join "prod2-generico".distributors d 
	on
	sb."distributor-id" = d.id
where
	(sb."auto-short" = 0
		or (sb."auto-short" = 1
			and "patient-id" = 4480))
	and "drug-id" in {drugs}
	and DATE(sb."created-at") = '{analysis_date}'
    """.format(drugs=drugs, analysis_date=analysis_date)
sb_orders= rs_db.get_df(sb_orders_query)

logger.info("fetched shortbook orders for analysis date")

# =============================================================================
# Checking Error with Fixed Distrubutor tag
# =============================================================================

sb_orders['store-drug'] = sb_orders['store-id'].astype(str)+'-'+ sb_orders['drug-id'].astype(str)

store_drug = tuple(map(str, (list( sb_orders['store-drug'].unique()))))


fixed_distrubutor_query = """
    select
        concat(fd."store-id" , concat('-', fd."drug-id")) as "store-drug-fixed-distributor"
    from
        "prod2-generico"."fixed-distributors" fd
    where
        active = 1
        and "distributor-id" = 8105
        and concat(fd."store-id" , concat('-', fd."drug-id")) in {store_drug}
    group by
        "drug-id",
        "store-id"
    """.format(store_drug=store_drug)
fixed_distributor_check = rs_db.get_df(fixed_distrubutor_query)

logger.info("Fetched relevant fixed distributor data")

sb_orders = sb_orders.merge(fixed_distributor_check,left_on ='store-drug', right_on = 'store-drug-fixed-distributor',how = 'left')

def fixed_check(x):
    if x is None:
        return 0
    else:
        return 1

sb_orders['fixed-distributor-tag'] = sb_orders['store-drug-fixed-distributor'].apply(fixed_check)

sb_orders['dummy'] = 1

del sb_orders['store-drug']
del sb_orders['store-drug-fixed-distributor']

sb_orders_fix_tag = sb_orders

sb_orders_fix_tag = sb_orders_fix_tag.groupby(['drug-id','drug-name','order-type']).agg({'dummy':sum,
                                                            'fixed-distributor-tag':sum}).reset_index()

sb_orders_fix_tag['fixed-distributor-issue-percentage'] = 1 - (sb_orders_fix_tag['fixed-distributor-tag']/sb_orders_fix_tag['dummy'])

del sb_orders_fix_tag['dummy']
del sb_orders_fix_tag['fixed-distributor-tag']

def fixed_flag(x):
    if x> 0:
        return 1
    else:
        return 0

sb_orders_fix_tag['fixed-distributor-flag'] = sb_orders_fix_tag['fixed-distributor-issue-percentage'].apply(fixed_flag)

# =============================================================================
# Fetching shortbook-order logs to check bounce orders
# =============================================================================

dist_short_book_ids = tuple(map(int, list( sb_orders['short-book-id'].unique())))
if len(dist_short_book_ids )==0:
    dist_short_book_ids  = [0]
    dist_short_book_ids = str(list(dist_short_book_ids )).replace('[', '(').replace(']', ')')
    
order_logs_query = """
    select
        "short-book-id" ,
        "ordered-dist-id" ,
        concat(coalesce("ordered-dist-id" ,0),concat('-',coalesce("status",'null'))) as "dist-status"
    from
        "prod2-generico"."short-book-order-logs" sbol
    where
        "short-book-id" in {dist_short_book_ids}
    order by sbol.id ASC
        """.format(dist_short_book_ids=dist_short_book_ids)
order_logs= rs_db.get_df(order_logs_query)

logger.info("Fetched order logs")

order_logs['dist-status'] = order_logs['dist-status'].astype(str)
order_logs['ordered-dist-id'] = order_logs['ordered-dist-id'].astype(str)

order_logs = order_logs.groupby(['short-book-id']).agg({'dist-status':','.join,
                                                       'ordered-dist-id':','.join}).reset_index()

order_logs['shortbookid-dist-status'] = str('(') + order_logs['short-book-id'].astype(str)+ str('  ') +order_logs['dist-status'] + str(')')

del order_logs['dist-status']

sb_orders= sb_orders.merge(order_logs, on = 'short-book-id', how = 'left')

sb_orders = pd.pivot_table(sb_orders, values='orderd-quantity', index=['drug-name','drug-id','order-type','store-id','ordered-dist-id','shortbookid-dist-status'], columns='order-source',aggfunc='sum',fill_value=0).reset_index()

sb_orders['total-orders'] = sb_orders['other-distributor-order']+sb_orders['warehouse-order']

sb_orders['store-id'] = sb_orders['store-id'].astype(str)

sb_orders = sb_orders.groupby(['drug-id','drug-name','order-type']).agg({'store-id':','.join,
                                                            'ordered-dist-id':','.join,
                                                            'shortbookid-dist-status':','.join,
                                                            'other-distributor-order':sum,
                                                            'warehouse-order':sum,
                                                            'total-orders':sum}).reset_index()


sb_orders = sb_orders.merge(sb_orders_fix_tag, on = ['drug-id','drug-name','order-type'], how = 'left')

def order_check(x):
    if '8105' in x:
        return 1
    else:
        return 0

sb_orders['ordered-flag'] = sb_orders['ordered-dist-id'].apply(order_check)

# =============================================================================
# extra-order-to-diff-distrubutor Check
# =============================================================================

whlivenpi['drug-id'] = whlivenpi['drug-id'].apply(pd.to_numeric, errors='ignore').astype('Int64')

sb_orders = sb_orders.merge(whlivenpi[['drug-id','bqty']],on='drug-id',how='left')

sb_orders.loc[sb_orders['bqty']>=sb_orders['total-orders'] , 'extra-order-to-diff-distrubutor'] = sb_orders['other-distributor-order']
sb_orders.loc[(sb_orders['total-orders'] >sb_orders['bqty']) & (sb_orders['other-distributor-order']>(sb_orders['total-orders']-sb_orders['bqty'])) , 'extra-order-to-diff-distrubutor'] = sb_orders['other-distributor-order'] - (sb_orders['total-orders']-sb_orders['bqty'])
sb_orders.loc[(sb_orders['total-orders'] >sb_orders['bqty']) & (sb_orders['other-distributor-order']<(sb_orders['total-orders']-sb_orders['bqty'])) , 'extra-order-to-diff-distrubutor'] = 0
sb_orders['extra-order-to-diff-distrubutor'] = sb_orders['extra-order-to-diff-distrubutor'].apply(pd.to_numeric, errors='ignore').astype('Int64')

conditions = [((sb_orders['extra-order-to-diff-distrubutor']>0)&(sb_orders['ordered-flag']==1))]
choices = [1]
sb_orders['bounce-flag'] = np.select(conditions, choices, default = 0)

conditions = [((sb_orders['extra-order-to-diff-distrubutor']>0)&(sb_orders['fixed-distributor-flag']==1))]
choices = [1]
sb_orders['fixed-distributor-flag'] = np.select(conditions, choices, default = 0)

conditions = [((sb_orders['extra-order-to-diff-distrubutor']>0)&(sb_orders['fixed-distributor-flag']==1))]
choices = [sb_orders['fixed-distributor-issue-percentage']]
sb_orders['fixed-distributor-issue-percentage'] = np.select(conditions, choices, default = 0)

sb_orders.rename(columns={'store-id':'store-ids'},inplace = True)

del sb_orders['ordered-dist-id']
del sb_orders['ordered-flag']
sb_orders['extra-order-to-diff-distrubutor'] = sb_orders['extra-order-to-diff-distrubutor'].fillna(0)
conditions = [sb_orders['extra-order-to-diff-distrubutor']==0,
            ((sb_orders['extra-order-to-diff-distrubutor']>0)&(sb_orders['bounce-flag']==1)),
            ((sb_orders['extra-order-to-diff-distrubutor']>0)&(sb_orders['fixed-distributor-flag']==1))]
choices = ['no-issue','bounce-issue','fixed-distributor-table-issue']
sb_orders['issue-type'] = np.select(conditions, choices, default = 'different-issue')


sb_orders['analysis-date'] = analysis_date

sb_orders = sb_orders[['drug-id','drug-name','order-type','store-ids','shortbookid-dist-status','bqty','warehouse-order','other-distributor-order','total-orders','extra-order-to-diff-distrubutor','bounce-flag','fixed-distributor-flag','fixed-distributor-issue-percentage','issue-type','analysis-date']]

logger.info("table is ready to be written in Redshift")

# =============================================================================
# Writing table to RS
# =============================================================================

schema = 'prod2-generico'
table_name = 'npi-missed-order-analysis'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)

status1 = False
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = ''' delete
                        from "{schema}"."{table_name}"
                        where date("analysis-date") = '{analysis_date}'
                        '''.format(schema=schema,table_name=table_name,analysis_date=analysis_date)
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table deleted')

    s3.write_df_to_db(df=sb_orders[table_info['column_name']], table_name=table_name, db=rs_db_write,
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

