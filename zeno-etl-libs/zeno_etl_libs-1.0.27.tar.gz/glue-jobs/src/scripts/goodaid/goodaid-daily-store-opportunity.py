#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz
from zeno_etl_libs.logger import get_logger

import argparse
import pandas as pd
import datetime as dt
import numpy as np


parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
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
table_name = 'goodaid-daily-store-opportunity'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)


# =============================================================================
# Existing Good-Aid composition
# =============================================================================
query = f'''
        select
           distinct(d.composition),d."composition-master-id" 
        from
            "prod2-generico"."prod2-generico"."wh-sku-subs-master" a
        inner join 
        "prod2-generico"."prod2-generico".drugs d on
            d.id = a."drug-id"
        where
            d."company-id" = 6984
            and a."add-wh" = 'Yes'
        group by d.composition,d."composition-master-id"  '''
ga_active_compositions= rs_db.get_df(query)
ga_active_compositions.columns = [c.replace('-', '_') for c in ga_active_compositions.columns]

g_composition = tuple(map(int, list(ga_active_compositions['composition_master_id'].unique())))
compositions = tuple([str(i) for i in ga_active_compositions['composition']])
logger.info('Data: ga_active_compositions fetched successfully: ' +str(len(ga_active_compositions)))
logger.info('Data: ga_active_compositions fetched successfully: ' +str(len(ga_active_compositions)))


# =============================================================================
# Stores Master
# =============================================================================
query= '''
        select
            id as "store_id",
            "store-type" ,
            city ,
            store as "store_name",
            "line-manager" ,
            abo
        from
            "prod2-generico"."prod2-generico"."stores-master" sm '''
store_master= rs_db.get_df(query)
store_master.columns = [c.replace('-', '_') for c in store_master.columns]
logger.info('Data: store_master data fetched successfully: ' +str(len(store_master)))


# =============================================================================
# Group Molecule
# =============================================================================
g_query= '''
        select
            cm."composition-master-id"  as "composition-master-id", 
            LISTAGG( distinct cm."molecule-master-id" , '-' ) 
             WITHIN GROUP (ORDER by cm."molecule-master-id" ) as "group_molecule",
            listagg(distinct mm."name" ,'-' ) as "group_molecule_text"
        from
            "prod2-generico"."prod2-generico"."composition-master-molecules-master-mapping" cm
        inner join "prod2-generico"."prod2-generico"."molecule-master" mm 
        on
            cm."molecule-master-id" = mm.id
        where
            cm."composition-master-id" is not null
        group by
            cm."composition-master-id"
            '''
group_molecule = rs_db.get_df(g_query)
group_molecule.columns= [c.replace ('-','_') for c in group_molecule.columns]
group_molecule.sort_values(by='group_molecule', ascending=True, inplace= True)
group_molecule.reset_index(inplace= True, drop = True)
logger.info("Data: group_molecule table fetched successfully" +str(group_molecule.shape))


# =============================================================================
# Extract store-wise day wise actual opportunity based on billing
# =============================================================================
query = f'''
        select
            date(s."created-at") as "date",
            s."store-id" ,
            q1."group_molecule",
            q1."group_molecule_text",
            count(distinct concat(s."patient-id", q1."group_molecule")) as "total_opportunity"
        from
            "prod2-generico"."prod2-generico".sales s
        inner join ({g_query}) q1 
        on
            q1."composition-master-id" = s."composition-master-id"
        where
            (s."composition-master-id" in {g_composition}
                or s."company-id" = 6984)
            and date(s."created-at") >= '2021-01-01'
            and "bill-flag" = 'gross'
        group by
            1,2,3,4 '''
goodaid_daily_store_opportunity = rs_db.get_df(query)
goodaid_daily_store_opportunity.columns = [c.replace('-', '_') for c in goodaid_daily_store_opportunity.columns]

logger.info('Shape of goodaid_daily_store_opportunity data  :' + str(goodaid_daily_store_opportunity.shape))


# =============================================================================
#  Extracting composition wise opportunity
# =============================================================================
query = f'''
        select
            date(s."created-at") as "date",
            s."store-id" ,
            q1."group_molecule",
            s.composition ,
            s."composition-master-id" ,
            count(distinct concat(concat(s."patient-id", q1."group_molecule"), s."composition-master-id")) as "total_opportunity"
        from
            "prod2-generico"."prod2-generico".sales s
        inner join ({g_query}) q1 
        on
            q1."composition-master-id" = s."composition-master-id"
        where
            (s."composition-master-id" in {g_composition}
                or s."company-id" = 6984)
            and date(s."created-at") >= '2021-01-01'
            and "bill-flag" = 'gross'
        group by
            1,2,3,4,5 '''
goodaid_daily_opp_comp = rs_db.get_df(query)
goodaid_daily_opp_comp.columns = [c.replace('-', '_') for c in goodaid_daily_opp_comp.columns]
logger.info('Shape of goodaid_daily_opp_comp data  :' + str(goodaid_daily_opp_comp.shape))


# =============================================================================
#  Extrating total_opportunity at date-store_group_molecule
# =============================================================================
goodaid_composition = goodaid_daily_opp_comp.groupby(['date', 'store_id', 'group_molecule'],
                                                     as_index=False).agg({"total_opportunity": "sum"}).reset_index(drop=True)

goodaid_composition.rename({'total_opportunity': 'aggregate_total_opportunity'}, axis=1, inplace=True)

goodaid_daily_opp_comp = pd.merge(left=goodaid_daily_opp_comp,
                                                       right=goodaid_composition,
                                                       on=['date', 'store_id', 'group_molecule'], how='left')

logger.info('Shape of goodaid_daily_opp_comp data after joining goodaid_composition :' + str(goodaid_daily_opp_comp.shape))

#Creating an multiplier field

goodaid_daily_opp_comp['multiplier'] = goodaid_daily_opp_comp['total_opportunity'] / \
                                                                  goodaid_daily_opp_comp['aggregate_total_opportunity']
goodaid_daily_opp_comp=goodaid_daily_opp_comp[['date', 'store_id', 'group_molecule',
                                            'composition','composition_master_id','multiplier']]

goodaid_daily_store_opportunity = pd.merge(right=goodaid_daily_opp_comp,
                                                       left=goodaid_daily_store_opportunity,
                                                       on=['date', 'store_id', 'group_molecule'], how='left')

goodaid_daily_store_opportunity['actaul_total_opp'] = \
    goodaid_daily_store_opportunity['total_opportunity'] * goodaid_daily_store_opportunity[
        'multiplier']

goodaid_daily_store_opportunity['actaul_total_opp']=np.ceil(goodaid_daily_store_opportunity['actaul_total_opp'])

logger.info('Shape of goodaid_daily_store_opportunity data after joining comp_opp :' + str(goodaid_daily_store_opportunity.shape))

goodaid_daily_store_opportunity = pd.merge(left=goodaid_daily_store_opportunity, right=store_master,
                                           on=['store_id'], how='left')

logger.info('Shape of goodaid_daily_store_opportunity data after joining stores_master :' + str(goodaid_daily_store_opportunity.shape))

goodaid_daily_store_opportunity['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_daily_store_opportunity['created-by'] = 'etl-automation'
goodaid_daily_store_opportunity['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_daily_store_opportunity['updated-by'] = 'etl-automation'
goodaid_daily_store_opportunity.columns = [c.replace('_','-') for c in goodaid_daily_store_opportunity.columns]
logger.info('Shape of goodaid_opportunity data :' + str(goodaid_daily_store_opportunity.shape))


# =========================================================================
# Writing table in Redshift
# =========================================================================
if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    print(f"Table:{table_name} exists")
truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
rs_db.execute(truncate_query)
logger.info(f"Table:{table_name} table truncated")

s3.write_df_to_db(df=goodaid_daily_store_opportunity[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")


# Closing the DB Connection
rs_db.close_connection()
