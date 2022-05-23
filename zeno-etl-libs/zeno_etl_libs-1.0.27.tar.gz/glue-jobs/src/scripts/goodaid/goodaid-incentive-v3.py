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
table_name = 'goodaid-incentive-v3'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)


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
        group by d.composition,d."composition-master-id" '''
ga_active_compositions= rs_db.get_df(query)
ga_active_compositions.columns = [c.replace('-', '_') for c in ga_active_compositions.columns]

g_composition = tuple(map(int, list(ga_active_compositions['composition_master_id'].unique())))
compositions = tuple([str(i) for i in ga_active_compositions['composition']])
logger.info('Data: ga_active_compositions fetched successfully: ' +str(len(ga_active_compositions)))
logger.info('Data: ga_active_compositions fetched successfully: ' +str(len(ga_active_compositions)))

# =============================================================================
# Base data
# =============================================================================
query= '''
        select
            date("created-at") as "date",
            "created-at" as "date_time",
            "bill-id" ,
            "patient-id" ,
            "store-id" ,
            "drug-id" ,
            company ,
            "company-id" ,
            composition ,
            "composition-master-id" ,
            (case when "bill-flag"= 'gross' then 1 else -1 end) as "bill_flag",
            sum(rate * "net-quantity") as "sales",
            sum("net-quantity") as "quantity",
            sum("revenue-value") as "total revenue"
        from
            "prod2-generico"."prod2-generico".sales
        where
            "company-id" = 6984
            and composition is not null
        group by
            date("created-at") ,
            ("created-at") ,
            "bill-id" ,
            "patient-id" ,
            "store-id" ,
            "drug-id" ,
            company ,
            "company-id" ,
            composition ,
            "composition-master-id" ,
            "bill-flag" '''
base_data = rs_db.get_df(query)
base_data.columns = [ c.replace ('-','_') for c in base_data.columns]
logger.info("Data: base data successfully fetched: " +str(base_data.shape))
base_data = pd.merge(left=base_data, right=store_master, on=['store_id'], how='left')

logger.info('Shape of base data is' + str(base_data.shape))

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
logger.info("Data: group_molecule table fetched successfully" +str(group_molecule.shape))
group_molecule.columns= [c.replace ('-','_') for c in group_molecule.columns]
base_data = pd.merge(left=base_data, right=group_molecule, on=['composition_master_id'], how='left')
base_data_temp = base_data.copy()
logger.info('Shape of base data after joining with group molecule is :' + str(base_data.shape))

# =============================================================================
# Attributed Store, Order Mode, Attributed date
# =============================================================================
query= '''
        select
            "bill-id" ,
            "store-id" as "attributed_store",
            date("created-at") as "attributed_date",
            (case
                when "ecom-flag" = 1 then 'Ecom'
                else 'Non-Ecom'
            end ) as "order_source"
        from
            "prod2-generico"."prod2-generico".sales s
        where
            "company-id" = 6984
            and "bill-flag" = 'gross'
        group by
            1,
            2,
            3,
            4 '''
attributed_store = rs_db.get_df(query)
attributed_store.columns = [c.replace('-', '_') for c in attributed_store.columns]
logger.info('Shape of base_data for attributed_bill :' + str(attributed_store.shape))
logger.info('Number of unique bills :' + str(attributed_store['bill_id'].nunique()))

base_data = pd.merge(left=base_data, right=attributed_store, on=['bill_id'], how='left')
logger.info('Shape of base_data after joining attributed_bill :' + str(base_data.shape))

# =============================================================================
# Goodaid incentive day-wise rate card
# =============================================================================
query = '''
        select
            "drug-id" ,
            "rate-date" ,
            incentive
        from
            "prod2-generico"."prod2-generico"."goodaid-incentive-rate-day" '''
rate_card = rs_db.get_df(query)
rate_card.columns = [c.replace('-', '_') for c in rate_card.columns]
logger.info("Data: rate card data successfully fetched: " +str(rate_card.shape))

base_data = pd.merge(left=base_data, right=rate_card, left_on=['drug_id','attributed_date'],right_on=['drug_id', 'rate_date'], how='left')
logger.info('Shape of base data after joining rate card is :' + str(base_data.shape))
base_data['incentive'].fillna(0, inplace=True)


# =============================================================================
# Condition to fetch max incentive amongst the same molecule purchased in a bill
# =============================================================================

base_data_agg = base_data.groupby(['attributed_store', 'patient_id', 'group_molecule','group_molecule_text',
                                   'order_source',
                                   'date', 'date_time', 'bill_id', 'bill_flag'],
                                  as_index=False).agg({'quantity': ['sum'], 'sales': ['sum'],
                                                       'incentive': ['max']}
                                                      ).reset_index(drop=True)
base_data_agg.columns = ["_".join(x) for x in base_data_agg.columns.ravel()]

base_data_agg.columns = base_data_agg.columns.str.rstrip('_x')

base_sort = base_data_agg.sort_values(by=[ 'attributed_store','patient_id', 'group_molecule',
                                          'group_molecule_text','date', 'date_time', 'bill_id',], ascending=True)

# =============================================================================
# Condition to keep only 1st instance from patient-group_molecule-bill return history
# =============================================================================

return_bill = base_sort[base_sort['bill_flag'] == -1].drop_duplicates(
    subset=[ 'patient_id', 'group_molecule','bill_id'], keep='first')

logger.info('Shape of return_bill is :' + str(return_bill.shape))
gross_bill = base_sort[base_sort['bill_flag'] == 1]

logger.info('Shape of gross_bill  is :' + str(gross_bill.shape))

inc_metadata = gross_bill.append(return_bill)

logger.info('Shape of inc_metadata after appending gross+return is :' + str(inc_metadata.shape))

inc_metadata = inc_metadata.sort_values(by=['patient_id',
                                            'group_molecule','group_molecule_text', 'date', 'date_time', 'bill_id'], ascending=True)

inc_metadata.drop_duplicates(keep='first', inplace=True)

logger.info('Shape of inc_meadata after dropping duplicates is :' + str(inc_metadata.shape))

# =============================================================================
# logic to calculate patient-group_molecule bill rank
# =============================================================================

inc_metadata['cum_sum'] = inc_metadata.groupby(['patient_id',
                                                'group_molecule'])['bill_flag'].cumsum()

#To extract the previous cumulated sum instance
inc_metadata['prev_cum_sum'] = inc_metadata.groupby(['patient_id',
                                                     'group_molecule'])['cum_sum'].shift(1)


inc_metadata['prev_cum_sum'].fillna(0, inplace=True)

inc_metadata['cum_sum_old'] = 0  # Can be commented once the job runs for limited time period

inc_metadata['cum_sum_final'] = inc_metadata['cum_sum'] + inc_metadata['cum_sum_old']

# =============================================================================
# Applying condition for eligible incentive
# =============================================================================

conditions = [
    (
            (inc_metadata['cum_sum_final'] == 1) &
            (inc_metadata['prev_cum_sum'] == 0)

    ),
    (
        (inc_metadata['cum_sum_final'] == 0)

    )
]
choices = ['achieved', 'deduct']

inc_metadata['incentive_flag'] = np.select(conditions, choices, default='no_opportunity')

inc_metadata = pd.merge(left=inc_metadata, right=store_master, right_on=['store_id'], left_on=['attributed_store'],
                        how='left')
logger.info('Shape of inc_meadata after joining stores_master :' + str(inc_metadata.shape))

#Fetch the cases where incentive is not tagged
zero_incentive = inc_metadata[(inc_metadata['incentive_flag']=='achieved')  & (inc_metadata['incentive_ma']==0)]
logger.info('Shape of zero_incentive data :' + str(zero_incentive.shape))

# =============================================================================
#  Adding composition in goodaid_incentive_v3
# =============================================================================

base_data_comp = base_data_temp[['bill_id', 'patient_id', 'group_molecule','composition', 'composition_master_id']]

base_data_comp = base_data_comp.sort_values(by=['bill_id', 'patient_id', 'group_molecule',
                                                 'composition_master_id'], ascending=True)
logger.info('Shape of base_data_comp  :' + str(base_data_comp.shape))

# Extracting the first composition from patient-bill-group_molecule
base_data_comp = base_data_comp.groupby(['bill_id', 'patient_id', 'group_molecule']).first().reset_index()
logger.info('Shape of base_data_comp after extracting unique composition :' + str(base_data_comp.shape))

inc_metadata = pd.merge(left=inc_metadata, right=base_data_comp, on=['bill_id', 'patient_id','group_molecule'],
                                how='left')

logger.info('Shape of inc_metadata data after merging with base_data_comp :' + str(inc_metadata.shape))

#Creating a copy of inc_metadata to sync with output table name
goodaid_incentive_v3 = inc_metadata.copy()
logger.info('Shape of goodaid_incentive_v3 data :' + str(goodaid_incentive_v3.shape))

goodaid_incentive_v3['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_incentive_v3['created-by'] = 'etl-automation'
goodaid_incentive_v3['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_incentive_v3['updated-by'] = 'etl-automation'
goodaid_incentive_v3.columns = [c.replace('_','-') for c in goodaid_incentive_v3.columns]
logger.info('Shape of goodaid_incentive_v3 data :' + str(goodaid_incentive_v3.shape))


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

s3.write_df_to_db(df=goodaid_incentive_v3[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")


# def main(rs_db, s3):
schema = 'prod2-generico'
table_name = 'goodaid-opportunity'
table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

# =============================================================================
# Total opportunity store level aggregated and avg selling qty
# =============================================================================
query= f'''
        select
            b."store-id" ,
            count(distinct concat(b."patient-id", q1."group_molecule")) as "total_opportunity",
            round(avg(a.quantity)) as "avg_qty"
        from
            "prod2-generico"."prod2-generico"."bill-items-1" a
        left join "prod2-generico"."prod2-generico"."bills-1" b on
            b.id = a."bill-id"
        left join "prod2-generico"."prod2-generico"."inventory-1" c on
            c.id = a."inventory-id"
        left join "prod2-generico"."prod2-generico".drugs d on
            d.id = c."drug-id"
        left join "prod2-generico"."prod2-generico"."patients-metadata" pm on
            pm."patient-id" = b."patient-id"
        inner join ({g_query}) q1 on
            q1."composition-master-id" = d."composition-master-id"
        where
            (d."composition-master-id" in {g_composition}
            or d."company-id" = 6984)
            and DATE(pm."last-bill-date") >= date(date_trunc('month', current_date) - interval '3 month') 
            group by 
            1 '''
opportunity = rs_db.get_df(query)
opportunity.columns = [c.replace('-', '_') for c in opportunity.columns]

logger.info('Shape of opportunity data :' + str(opportunity.shape))

# =============================================================================
# opportunity achieved
# =============================================================================
query= f'''
        select
            b."store-id" ,
            count(distinct concat(b."patient-id", q1."group_molecule")) as "total_opportunity_achieved"
        from
            "prod2-generico"."prod2-generico"."bill-items-1" a
        left join "prod2-generico"."prod2-generico"."bills-1" b on
            b.id = a."bill-id"
        left join "prod2-generico"."prod2-generico"."inventory-1" c on
            c.id = a."inventory-id"
        left join "prod2-generico"."prod2-generico".drugs d on
            d.id = c."drug-id"
        left join "prod2-generico"."prod2-generico"."patients-metadata" pm on
            pm."patient-id" = b."patient-id"
        inner join ({g_query}) q1 on
            q1."composition-master-id" = d."composition-master-id"
        where
            d."composition-master-id" in {g_composition}
            and d."company-id" = 6984
            and DATE(pm."last-bill-date") >= date(date_trunc('month', current_date) - interval '3 month') 
            group by 
            1 '''
opportunity_ach = rs_db.get_df(query)
opportunity_ach.columns = [c.replace('-', '_') for c in opportunity_ach.columns]

logger.info('Shape of opportunity_ach data :' + str(opportunity_ach.shape))

goodaid_opportunity = pd.merge(left=opportunity, right=opportunity_ach, on=['store_id'], how='left')
logger.info('Shape of goodaid_opportunity data after merging opp and opp_achieved :' + str(goodaid_opportunity.shape))

goodaid_opportunity = pd.merge(left=goodaid_opportunity, right=store_master, on=['store_id'], how='left')

logger.info('Shape of goodaid_opportunity data after joining stores_master :' + str(goodaid_opportunity.shape))

goodaid_opportunity['created-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_opportunity['created-by'] = 'etl-automation'
goodaid_opportunity['updated-at'] = dt.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
goodaid_opportunity['updated-by'] = 'etl-automation'
goodaid_opportunity.columns = [c.replace('_','-') for c in goodaid_opportunity.columns]
logger.info('Shape of goodaid_oppurtunity data :' + str(goodaid_opportunity.shape))

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

s3.write_df_to_db(df=goodaid_opportunity[table_info['column_name']], table_name=table_name, db=rs_db,
                      schema=schema)

logger.info(f"Table:{table_name} table uploaded")

# Closing the DB Connection
rs_db.close_connection()
