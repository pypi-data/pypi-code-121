import argparse
import datetime
import os
import sys
from functools import reduce

import pandas as pd
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
from zeno_etl_libs.logger import get_logger

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stag, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

rs_db = DB()
rs_db.open_connection()

s3 = S3()

# def main(rs_db, s3):
schema = 'prod2-generico'
table_name = 'lnd-ma-stl'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# Read from gsheet
gs = GoogleSheet()
ma_stl_data = gs.download(data={
    "spreadsheet_id": "1CD_sae-3w4S9gOqUhxVYxcGTmS8bUR2rPHDK5T_yFTk",
    "sheet_name": "Step Up MA STL",
    "listedFields": []
})
df = pd.DataFrame(ma_stl_data)
# Correct data types
df[['timestamp', 'start date', 'date of verification checklist']] = df[
    ['timestamp', 'start date', 'date of verification checklist']] \
    .apply(pd.to_datetime, errors='coerce')
df['enter score '] = df['enter score '].apply(pd.to_numeric, errors='coerce')
df['select result'] = df['select result'].str.lower()

# separate out training calender
training_calender = df[(df['type of form'] == 'Training Calendar')]

# combine multiple course columns into one column
training_calender['course0_1_2_3_4'] = training_calender[['courses','courses.1','courses.2','courses.3','courses.4']].apply(
    lambda x: ''.join(x.dropna().astype(str)), axis=1)
training_calender = training_calender[
    ['timestamp', 'type of form', 'store name', 'employee code',
     'designation', 'start date', 'course0_1_2_3_4']]
training_calender = training_calender.rename(columns={'course0_1_2_3_4': 'course'})
training_calender = training_calender.groupby(['type of form', 'store name',
                                               'employee code', 'course']) \
    .agg({'timestamp': 'max', 'start date': 'max'}).reset_index()

# announced verification attempt 1
verif_check_announced1 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type'] == 'Announced - Attempt 1 (By STL)')]
verif_check_announced1 = verif_check_announced1[
    ['date of verification checklist', 'employee code.1', 'date of joining', 'select role',
     'select verification checklist',
     'enter score ', 'select result']]
verif_check_announced1 = verif_check_announced1.groupby(['employee code.1',
                                                         'select verification checklist']) \
    .agg({'date of verification checklist': 'max',
          'enter score ': 'max', 'select result': 'max'}) \
    .reset_index()
verif_check_announced1 = verif_check_announced1.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'an1_score', 'select result': 'an1_result',
             'date of verification checklist': 'an1_date_of_verification'})

# announced verification attempt 2
verif_check_announced2 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type'] == 'Announced - Attempt 2 (By STL)')]
verif_check_announced2 = verif_check_announced2[
    ['date of verification checklist', 'employee code.1', 'date of joining', 'select role',
     'select verification checklist',
     'enter score ', 'select result']]
verif_check_announced2 = verif_check_announced2.groupby(['employee code.1',
                                                         'select verification checklist']).agg(
    {'date of verification checklist': 'max', 'enter score ':
        'max', 'select result': 'max'}).reset_index()
verif_check_announced2 = verif_check_announced2.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'an2_score', 'select result': 'an2_result',
             'date of verification checklist': 'an2_date_of_verification'})

# announced verification attempt 3
verif_check_announced3 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type'] == 'Announced - Attempt 3 (By STL)')]
verif_check_announced3 = verif_check_announced3[
    ['date of verification checklist', 'employee code.1',
     'date of joining', 'select role',
     'select verification checklist',
     'enter score ', 'select result']]
verif_check_announced3 = verif_check_announced3.groupby(['employee code.1',
                                                         'select verification checklist']).agg(
    {'date of verification checklist': 'max', 'enter score ': 'max', 'select result': 'max'}).reset_index()
verif_check_announced3 = verif_check_announced3.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'an3_score', 'select result': 'an3_result',
             'date of verification checklist': 'an3_date_of_verification'})

# Unannounced verification attempt 1
verif_check_unannounced1 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type'] == 'Unannounced - Attempt 1 (By SBO)')]
verif_check_unannounced1 = verif_check_unannounced1[
    ['date of verification checklist', 'employee code.1',
     'date of joining', 'select role',
     'select verification checklist',
     'enter score ', 'select result']]
verif_check_unannounced1 = verif_check_unannounced1.groupby(
    ['employee code.1', 'select verification checklist']).agg(
    {'date of verification checklist': 'max', 'enter score ': 'max', 'select result': 'max'}).reset_index()
verif_check_unannounced1 = verif_check_unannounced1.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'un1_score', 'select result': 'un1_result',
             'date of verification checklist': 'un1_date_of_verification'})

# Unannounced verification attempt 2
verif_check_unannounced2 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type']
        == 'Unannounced - Attempt 2 (By SBO)')]
verif_check_unannounced2 = verif_check_unannounced2[
    ['date of verification checklist', 'employee code.1', 'date of joining', 'select role',
     'select verification checklist', 'enter score ', 'select result']]
verif_check_unannounced2 = verif_check_unannounced2.groupby(
    ['employee code.1', 'select verification checklist']).agg(
    {'date of verification checklist': 'max', 'enter score ': 'max', 'select result': 'max'}).reset_index()
verif_check_unannounced2 = verif_check_unannounced2.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'un2_score', 'select result': 'un2_result',
             'date of verification checklist': 'un2_date_of_verification'})

# Unannounced verification attempt 3
verif_check_unannounced3 = df[(df['type of form'] == 'Verification Checklist') & (
        df['verification checklist type'] == 'Unannounced - Attempt 3 (By SBO)')]
verif_check_unannounced3 = verif_check_unannounced3[
    ['date of verification checklist', 'employee code.1', 'date of joining', 'select role',
     'select verification checklist', 'enter score ', 'select result']]
verif_check_unannounced3 = verif_check_unannounced3.groupby(
    ['employee code.1', 'select verification checklist']).agg(
    {'date of verification checklist': 'max', 'enter score ':
        'max', 'select result': 'max'}).reset_index()
verif_check_unannounced3 = verif_check_unannounced3.rename(
    columns={'employee code.1': 'employee code', 'select verification checklist': 'course',
             'enter score ': 'un3_score', 'select result': 'un3_result',
             'date of verification checklist': 'un3_date_of_verification'})
# Joining all data frames to training calender
dfs = [training_calender, verif_check_announced1,
       verif_check_announced2, verif_check_announced3,
       verif_check_unannounced1, verif_check_unannounced2,
       verif_check_unannounced3]
df_final = reduce(lambda left, right: pd.merge(left, right,
                                               on=["employee code", "course"], how='left'), dfs)
df_final.columns = [c.replace(' ', '_') for c in df_final.columns]
df_final.columns = [c.lower() for c in df_final.columns]
lnd_ma_stl = df_final.copy()
# etl
lnd_ma_stl['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
lnd_ma_stl['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
lnd_ma_stl['created-by'] = 'etl-automation'
lnd_ma_stl['updated-by'] = 'etl-automation'
lnd_ma_stl.columns = [c.replace('_', '-') for c in lnd_ma_stl.columns]
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
    rs_db.execute(truncate_query)

    s3.write_df_to_db(df=lnd_ma_stl[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)
# Closing the DB Connection
rs_db.close_connection()
