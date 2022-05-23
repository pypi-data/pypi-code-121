"""
# Author - shubham.jangir@zeno.health shubham.gupta@zeno.health
# Purpose - script with DSS write action for customer value segments
"""

import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger

import numpy as np
from datetime import datetime as dt
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-pe', '--period_end_d_plus1', default=0, type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
os.environ['env'] = env

logger = get_logger()

# params
try:
    period_end_d_plus1 = args.period_end_d_plus1
    period_end_d_plus1 = str(dt.strptime(period_end_d_plus1, "%Y-%m-%d").date())
except KeyError:
    period_end_d_plus1 = dt.today().strftime('%Y-%m-%d')

logger.info(period_end_d_plus1)

schema = 'prod2-generico'
table_name = 'customer-value-segment'

rs_db = DB()
rs_db.open_connection()

s3 = S3()


def seek():
    """ get the data """
    pass


def run_fun(rs_db, s3):
    # write logic here
    pass


table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)
logger.info(table_info)
if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")

read_schema = 'prod2-generico'

s = f"""
    SELECT
        "patient-id",
        COUNT(DISTINCT "id") AS "total-bills",
        SUM("net-payable") AS "total-spend"
    FROM "{read_schema}"."bills-1"
    WHERE DATEDIFF('days', date("created-at"),'{period_end_d_plus1}') between -90 and -1
    GROUP BY "patient-id"
    """

data = rs_db.get_df(query=s)

data['total-spend'] = data['total-spend'].astype(float)
data['abv'] = np.round(data['total-spend'] / data['total-bills'], 2)
data = data.sort_values(['total-spend'], ascending=False)
data['rank'] = data['total-spend'].rank(method='dense', ascending=False)
data['rank'] = data['rank'].astype(int)
data['cumm-sales'] = data.sort_values(['total-spend'], ascending=False)['total-spend'].cumsum()

len_data = len(data)

def assign_value_segment(row):
    if row['rank'] <= 0.05 * len_data:
        return 'platinum'
    elif (row['rank'] > 0.05 * len_data) & (row['rank'] <= 0.1 * len_data):
        return 'gold'
    elif (row['rank'] > 0.1 * len_data) & (row['rank'] <= 0.2 * len_data):
        return 'silver'
    else:
        return 'others'


data['value-segment'] = data.apply(lambda row: assign_value_segment(row), axis=1)

platinum_length = len(data[data['value-segment'] == 'platinum'])
gold_length = len(data[data['value-segment'] == 'gold'])
silver_length = len(data[data['value-segment'] == 'silver'])
others_length = len(data[data['value-segment'] == 'others'])

platinum_data = data[data['value-segment'] == 'platinum']

# Write to csv
s3.save_df_to_s3(df=platinum_data, file_name='value_segment_data_platinum.csv')

logger.info('Length of Platinum segment is {}'.format(platinum_length))
logger.info('Length of Gold segment is {}'.format(gold_length))
logger.info('Length of Silver segment is {}'.format(silver_length))
logger.info('Length of Others segment is {}'.format(others_length))

q2 = f"""
    SELECT
        "patient-id",
        "store-id",
        COUNT(DISTINCT "id") AS "store-bills",
        SUM("net-payable") AS "store-spend"
    FROM "{read_schema}"."bills-1"
    WHERE DATEDIFF('days', date("created-at"),'{period_end_d_plus1}') between -90 and -1
    GROUP BY "patient-id","store-id" 
    """

data_store = rs_db.get_df(query=q2)

data_store['rank'] = data_store.sort_values(['store-bills', 'store-spend'], ascending=[False, False]) \
                         .groupby(['patient-id']) \
                         .cumcount() + 1

patient_store = data_store[data_store['rank'] == 1][['patient-id', 'store-id']]

q3 = f"""
    SELECT
        "id" AS "store-id",
        "name" AS "store-name"
    FROM "{read_schema}"."stores"
    """

stores = rs_db.get_df(q3)

patient_store = patient_store.merge(stores, how='inner', on=['store-id', 'store-id'])
data = data.merge(patient_store, how='inner', left_on=['patient-id'], right_on=['patient-id'])

# Export data
keep_cols = ['patient-id', 'total-bills', 'total-spend', 'abv', 'rank',
             'value-segment', 'store-id', 'store-name']

write_data = data[keep_cols]

runtime_month = dt.today().strftime('%Y-%m')

runtime_date = dt.today().strftime('%Y-%m-%d')

write_data['segment-calculation-date'] = period_end_d_plus1
write_data['base-list-identifier'] = runtime_month
write_data['upload-date'] = runtime_date

# etl
write_data['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
write_data['created-by'] = 'etl-automation'
write_data['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
write_data['updated-by'] = 'etl-automation'

logger.info(write_data.head())

# Write to csv
s3.save_df_to_s3(df=write_data[table_info['column_name']], file_name='value_segment_data.csv')
s3.write_df_to_db(df=write_data[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)
