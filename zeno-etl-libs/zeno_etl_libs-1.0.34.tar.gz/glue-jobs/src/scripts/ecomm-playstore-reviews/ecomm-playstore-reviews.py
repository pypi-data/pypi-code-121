import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import pandas as pd
import dateutil
import datetime
from dateutil.tz import gettz
import numpy as np
from zeno_etl_libs.helper.google.playstore.playstore import Reviews

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
parser.add_argument('-d', '--full_run', default=0, type=int, required=False)

args, unknown = parser.parse_known_args()

env = args.env
full_run = args.full_run
os.environ['env'] = env
logger = get_logger()
logger.info(f"full_run: {full_run}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name = 'ecomm-playstore-reviews'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# max of data
playstore_q = """
select
            date(max("review-created-at")) max_exp
        from
            "prod2-generico"."ecomm-playstore-reviews" 
        """
rs_db.execute(playstore_q, params=None)
max_exp_date: pd.DataFrame = rs_db.cursor.fetch_dataframe()
max_exp_date['max_exp'].fillna(np.nan, inplace=True)
print(max_exp_date.info())
max_exp_date = max_exp_date['max_exp'].to_string(index=False)
print(max_exp_date)
# Read from gsheet
reviews = Reviews()
reviews_list = reviews.get()
# reviews_list
reviews_list_new = []
for r in reviews_list:
    for c in r['comments']:
        rc = {}
        rc.update({"reviewId": r['reviewId'], "authorName": r['authorName']})
        rc.update(c)
        reviews_list_new.append(rc)
df = pd.json_normalize(reviews_list_new)
df = df[['reviewId', 'authorName', 'userComment.text', 'userComment.starRating', 'userComment.reviewerLanguage',
          'userComment.lastModified.seconds']]
dict = {'reviewId': 'review-id',
        'userComment.text': 'review',
        'authorName': 'author-name',
        'userComment.starRating': 'star-rating',
        'userComment.reviewerLanguage': 'reviewer-lang'}
df.rename(columns=dict, inplace=True)
df['review-created-at'] = df['userComment.lastModified.seconds'].apply(
    lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
df=df.drop(['userComment.lastModified.seconds'],axis=1)

# params
if full_run or max_exp_date == 'NaN':
    start = '2017-05-13'
else:
    start = max_exp_date
start = dateutil.parser.parse(start)
print(df)
df['review-created-at'] = df['review-created-at'] .apply(pd.to_datetime, errors='coerce')
df = df[(df['review-created-at'] >= start)]
# etl
df['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
df['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
df['created-by'] = 'etl-automation'
df['updated-by'] = 'etl-automation'
df.columns = [c.replace('_', '-') for c in df.columns]
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")
print(start)
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" where "review-created-at" >='{start}' '''
print(truncate_query)
rs_db.execute(truncate_query)
s3.write_df_to_db(df=df[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)
# Closing the DB Connection
rs_db.close_connection()