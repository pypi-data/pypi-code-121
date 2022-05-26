#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
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

table_name = 'ethical-generic-rank'

rs_db = DB()
rs_db.open_connection()

s3 = S3()

#removing old goodaid drugs from base data
ga_query = f'''
        select
            distinct ("drug-id") as "drug_id"
        from
            "prod2-generico"."prod2-generico"."goodaid-atc-sr" gas
        where
            "old-new-drug" = 'old' '''
goodaid_old_drugs = rs_db.get_df(ga_query)
drug_id_list = goodaid_old_drugs.drug_id.unique()
drug_id_list = tuple(drug_id_list)

# fetching sales data.
query = '''
        select
            "created-at",
            "drug-id" ,
            composition ,
            "composition-master-id" ,
            company,
            "company-id" ,
            "drug-name" ,
            "revenue-value",
            quantity ,
            "type" ,
            category ,
            "goodaid-availablity-flag"
        from
            "prod2-generico".sales s
        where
            "type" in ('ethical', 'generic')
            and date("created-at") >= date_trunc('day', current_date + -365 * interval '1 DAY')
            and "drug-id" not in {} '''

base_data = rs_db.get_df(query.format(drug_id_list))

logger.info("Data: base fetched successfully")
logger.info(len(base_data))

# Getting new goodaid compositions from goodaid-atc-sr table
ga_query = f''' 
        select
            distinct ("drug-id")
        from
            "prod2-generico"."prod2-generico"."goodaid-atc-sr" gas
        where
            "old-new-drug" = 'new' '''
goodaid_drugs = rs_db.get_df(ga_query)
logger.info("Data: goodaid_drugs fetched successfully")

# identifying goodaid drugs in base data
base_data['is-goodaid'] = np.where(base_data['drug-id'].isin(goodaid_drugs['drug-id'].unique().tolist()), 1, 0)
logger.info("Data: base_data with goodaid flag fetched successfully")

# rank 1
ethical_generic = base_data.groupby(
        ['composition', 'drug-id', 'drug-name', 'type', 'company', 'is-goodaid', 'goodaid-availablity-flag']).agg(
        {'quantity': 'sum', 'revenue-value': 'sum'}).reset_index()
logger.info("Data: ethical_generic fetched successfully")

ethical_generic['rank'] = ethical_generic.sort_values(['is-goodaid','type','quantity'],
                                                          ascending=[False, False, False])\
                              .groupby(['composition', 'type']).cumcount() + 1
logger.info("Data: ethical_generic with rank fetched successfully")

# compositions with >1 good aid drug
ethical_generic_ex = ethical_generic[(ethical_generic['is-goodaid'] == '1')
                                         & (ethical_generic['rank'] > 1)]
ethical_generic['exclusion'] = np.where(ethical_generic['drug-id']
                                            .isin(ethical_generic_ex['drug-id'].unique()
                                                  .tolist()), 1, 0)
logger.info("Data: ethical_generic exclusion fetched successfully")

# excluding compositions with >1 good aid drug
ethical_generic_final = ethical_generic[(ethical_generic['exclusion'] == 0)]
logger.info("Data: ethical_generic exclusion fetched successfully")

# rank data set after exclusion
ethical_generic_final = ethical_generic_final[['composition', 'drug-id', 'drug-name', 'type', 'company',
                                               'is-goodaid', 'goodaid-availablity-flag', 'quantity', 'revenue-value']]
ethical_generic_final['rank'] = ethical_generic_final.sort_values(['is-goodaid', 'type', 'quantity'],
                                                                      ascending=[False, False, False]) \
                                                         .groupby(['composition', 'type']) \
                                                         .cumcount() + 1

ethical_generic = ethical_generic_final.copy()
ethical_generic_rank = ethical_generic[ethical_generic['composition'] != '']
logger.info("Data: ethical_generic_rank  fetched successfully")

ethical_generic_rank['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
ethical_generic_rank['created-by'] = 'etl-automation'
ethical_generic_rank['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
ethical_generic_rank['updated-by'] = 'etl-automation'


# =========================================================================
# Writing table in Redshift
# =========================================================================
schema = 'prod2-generico'

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=ethical_generic_rank[table_info['column_name']], table_name=table_name, db=rs_db,
                  schema=schema)
logger.info(f"Table:{table_name} table uploaded")

# Closing the DB Connection
rs_db.close_connection()