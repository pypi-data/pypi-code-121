#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
from zeno_etl_libs.helper.google.sheet.sheet import GoogleSheet
from zeno_etl_libs.logger import get_logger
from dateutil.tz import gettz

import numpy as np
import pandas as pd
import datetime as dt
import argparse

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()

logger.info(f"env: {env}")

table_name = 'goodaid-atc-sr'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

# fetching data from Gsheet
gs = GoogleSheet()
data = gs.download(data={
    "spreadsheet_id": "1JMt8oICcodWbzHqQg3DckHKFrJAR0vXmFVXOunW-38Q",
    "sheet_name": "Sheet1",
    "listedFields": []
})
data = pd.DataFrame(data)

data['drug_id'] = data['drug_id'].astype(str).astype(int)

logger.info("Data: G-sheet data fetched successfully")
logger.info(len(data))

drug_id_list = data.drug_id.unique()
drug_id_list = tuple(drug_id_list)

# providing start-date for all the drugs
query = '''
        select
            d.id as "drug_id",
            MIN(bi."created-at") as "start-date",
            d."composition-master-id"
        from
            "prod2-generico"."bill-items-1" bi
        left join "prod2-generico"."inventory-1" i on
            bi."inventory-id" = i.id
        left join "prod2-generico".drugs d on
            i."drug-id" = d.id
        where
            d."company-id" = 6984
            and d.id in {}
            and bi."created-at" is not null
        group by
            d.id,
            d."composition-master-id"  '''

min_date = rs_db.get_df(query.format(drug_id_list))

logger.info("Data: min-composition start date fetched successfully")
logger.info(len(min_date))
merged = pd.merge(left=data, right=min_date, how='inner', on='drug_id')

merged['start-date'] = pd.to_datetime(merged['start-date']).dt.date
merged['start-date'] = pd.to_datetime(merged['start-date'])
logger.info(len(merged))

# providing composition wise lot and rank
gaid_comp_min_date = f'''
        select
            MIN(bi."created-at") as "min-bill-date",
            d."composition-master-id"
        from
            "prod2-generico"."bill-items-1" bi
        left join "prod2-generico"."inventory-1" i on
            bi."inventory-id" = i.id
        left join "prod2-generico".drugs d on
            i."drug-id" = d.id
        where
            d."company-id" = 6984
        group by
            d."composition-master-id"

'''
min_date_comp = rs_db.get_df(gaid_comp_min_date)

min_date_comp['rank'] = min_date_comp['min-bill-date'].rank().astype(int)
min_date_comp['lot'] = (min_date_comp['rank'] / 25).apply(np.ceil).astype(int)
logger.info("Data: min-composition start date, lot and rank fetched successfully")
logger.info(len(min_date_comp))

goodaid_tagging = pd.merge(left=merged, right=min_date_comp, how='left', on='composition-master-id')

goodaid_tagging.columns = goodaid_tagging.columns.str.replace(" ", "-")
goodaid_tagging.columns = goodaid_tagging.columns.str.replace("_", "-")

goodaid_tagging['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_tagging['created-by'] = 'etl-automation'
goodaid_tagging['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_tagging['updated-by'] = 'etl-automation'
logger.info(len(goodaid_tagging))
# =========================================================================
# Writing table in Redshift
# =========================================================================
schema = 'prod2-generico'

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=goodaid_tagging[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)
logger.info(f"Table:{table_name} table uploaded")

# Closing the DB Connection
rs_db.close_connection()