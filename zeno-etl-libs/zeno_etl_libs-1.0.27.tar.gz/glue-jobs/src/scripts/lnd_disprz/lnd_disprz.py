import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.disprz.disprz import Dizprz
import pandas as pd
import datetime
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env
logger = get_logger()
rs_db = DB()
rs_db.open_connection()

s3 = S3()

schema = 'prod2-generico'
table_name = 'lnd-disperz-data'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

disprz = Dizprz()

df = disprz.get_disprz_dataframe()

df.columns = [c.replace(' ', '_') for c in df.columns]
df.columns = [c.lower() for c in df.columns]
df = df.drop(['totalcount'], axis=1)
df = df[
    ['userid', 'username', 'userdisplayname', 'email', 'userstatus', 'journeyname', 'moduleid',
     'modulename', 'moduletype', 'moduletypeid', 'partnerid', 'enrollmenttype',
     'primarytag', 'secondarytag', 'estimatedduration', 'timespent',
     'enrollmenttypedescription', 'modulestatus', 'completionpercentage',
     'modulelessonid', 'publishedon', 'completedon', 'lastaccessedon',
     'iscomplete', 'programid', 'programname', 'skillid',
     'skillname', 'department', 'location', 'designation', 'startedon',
     'moduleduedate']]

df[['publishedon', 'completedon', 'lastaccessedon','startedon',
     'moduleduedate']] = df[
    ['publishedon', 'completedon', 'lastaccessedon','startedon',
     'moduleduedate']] \
    .apply(pd.to_datetime, errors='coerce')

# etl
df['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
df['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
df['created-by'] = 'etl-automation'
df['updated-by'] = 'etl-automation'

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=df[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)
# Closing the DB Connection
rs_db.close_connection()
