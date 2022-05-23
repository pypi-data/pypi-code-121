"""
Author:shubham.gupta@zeno.health
Purpose: Patient_NOB_ABV_History & Campaign effectiveness
"""

import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd
from dateutil.tz import gettz

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="shubham.gupta@zeno.health", type=str, required=False)
parser.add_argument('-fr', '--full_run', default=0, type=int, required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to
full_run = args.full_run
logger = get_logger()

logger.info(f"env: {env}")
logger.info(f"print the env again: {env}")

# params
if full_run:
    start = '2017-05-13'
    end = str(dt.today().date() - timedelta(days=1))
else:
    start = str(dt.today().date() - timedelta(days=91))
    end = str(dt.today().date() - timedelta(days=1))

schema = 'prod2-generico'
table_name = "campaign-prepost"

rs_db = DB()
rs_db.open_connection()

s3 = S3()

table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

read_schema = 'prod2-generico'

if isinstance(table_info, type(None)):
    logger.info(f"table: {table_name} do not exist")
else:
    truncate_query = f"""
            DELETE
            FROM
                "{read_schema}"."{table_name}"
            WHERE
                "bill-date" BETWEEN '{start}' AND '{end}';
                """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

# fetching all store-ids
s_q = f"""
        select
            id as "store-id"
        from
            "{read_schema}"."stores" s
        where
            category = 'retail'
            and "is-active" = 1;
        """
stores = rs_db.get_df(query=s_q)
stores = stores['store-id'].unique()
patient_promo_final = pd.DataFrame()

for store in stores:
    logger.info(f"Running for Store ID : {store}")

    # Fetching all patient who used promo
    q_promo = f"""
                select
                    rm.id as "bill-id",
                    rm."patient-id", 
                    rm."total-spend" as "bill-value",
                    rm."promo-discount", 
                    pc."promo-code", 
                    pc."code-type" ,
                    rm."store-id",
                    rm."created-at" as "promo-date",
                    pc."type",
                    pc."discount-type",
                    pc."discount-level",
                    pc."flat-discount",
                    pc."percent-discount",
                    pc."max-discount",
                    pc."min-purchase",
                    pc."max-time",
                    pc."max-per-patient",
                    pc."start",
                    pc.expiry,
                    pc."campaign-id",
                    c.campaign,
                    rm.store,
                    rm.abo,
                    rm."store-manager",
                    rm."line-manager",
                    rm."store-opened-at",
                    rm."hd-flag" ,
                    rm."pr-flag",
                    rm."is-generic",
                    rm."is-chronic",
                    rm."is-repeatable"
                from
                    "{read_schema}"."retention-master" rm
                left join "{read_schema}"."promo-codes" pc on
                    rm."promo-code-id" = pc.id
                left join "{read_schema}".campaigns c on
                    pc."campaign-id" = c.id
                where
                    DATE(rm."created-at") between '{start}' and '{end}'
                    and rm."promo-code-id" is not null
                    and rm."store-id" = {store};"""

    patient_promo = rs_db.get_df(query=q_promo)
    logger.info(q_promo)
    logger.info(f'Patient promo data query size : {len(patient_promo)}')

    if patient_promo.shape[0] == 0:
        continue
    unique_patients = patient_promo['patient-id'].unique()

    if len(unique_patients) <= 1:
        unique_patients = np.append(unique_patients, [0, 0])

    # Fetching bill history of all those patient who used promo
    q_bills = f"""
            select
                rm.id,
                rm."patient-id",
                rm."total-spend" as sales,
                rm."created-at" as "bill-date",
                (case
                    when rm."promo-code-id" is null then 0
                    else 1
                end) as "promo-used"
            from
                "{read_schema}"."retention-master" rm
            where
                rm."patient-id" in {tuple(unique_patients)};
            """

    bills = rs_db.get_df(query=q_bills)

    patient_promo['start'] = pd.to_datetime(patient_promo['start'])
    patient_promo['expiry'] = pd.to_datetime(patient_promo['expiry'])

    logger.info(f'Patient bills data query size : {len(bills)}')

    patient_promo['promo-date'] = pd.to_datetime(patient_promo['promo-date'])
    bills['bill-date'] = pd.to_datetime(bills['bill-date'])

    # Created temp dataframe which will be used multiple times using filter
    temp_df = pd.merge(patient_promo, bills, how='left', on='patient-id')
    logger.info(f"temp dataframe created with size {temp_df.shape}")
    # Created time difference for filter
    temp_df['time-diff'] = temp_df['promo-date'] - temp_df['bill-date']
    temp_df['sales'] = temp_df['sales'].astype(float)
    # Copy for final database
    final_df = patient_promo.copy()

    # First filter for pre promo calculation
    for_previous_total = temp_df[temp_df['time-diff'] > timedelta(days=0)]
    resurrection = for_previous_total.copy()
    for_previous_total = for_previous_total.groupby(['bill-id'], as_index=False).agg({'id': 'nunique'})
    for_previous_total = for_previous_total.rename(columns={'id': 'previous-total-trips'})
    logger.info(f"previous total calculation done with size : {for_previous_total.shape}")
    # Merging
    final_df = pd.merge(final_df, for_previous_total, on=['bill-id'], how='left')

    # Second filter for previous 90 days calculation
    for_previous_90 = temp_df[(temp_df['time-diff'] > timedelta(days=0)) &
                              (temp_df['time-diff'] <= timedelta(days=90))]

    for_previous_90 = for_previous_90.sort_values('time-diff')

    # Sorting data to consider recent 3 trips only
    for_previous_90_3_trips = for_previous_90.groupby(['bill-id'], as_index=False).head(3)

    # Trips in previous 90 days
    for_previous_90 = for_previous_90.groupby(['bill-id'], as_index=False).agg({'id': 'nunique'})
    for_previous_90 = for_previous_90.rename(columns={'id': 'previous-90days-trips'})
    logger.info(f"previous 90D calc done with size : {for_previous_90.shape}")

    # Merging
    final_df = pd.merge(final_df, for_previous_90, on=['bill-id'], how='left')
    logger.info(final_df.info())
    logger.info(for_previous_90_3_trips.info())
    for_previous_90_3_trips = for_previous_90_3_trips.groupby(['bill-id'],
                                                              as_index=False).agg({'sales': 'mean',
                                                                                   'promo-used': 'sum'})
    for_previous_90_3_trips = for_previous_90_3_trips.rename(columns={'sales': 'previous-3trips-abv',
                                                                      'promo-used': 'pre3trips-promo'})

    # Merging
    final_df = pd.merge(final_df, for_previous_90_3_trips, on=['bill-id'], how='left')
    logger.info(f"Data for previous 3 trips in 90 days calc done with size : {final_df.shape}")

    # Third filter for next 90 days calculation (post calc)
    for_next_90 = temp_df[(temp_df['time-diff'] < timedelta(days=0)) &
                          (temp_df['time-diff'] >= timedelta(days=-90))]
    for_next_90 = for_next_90.sort_values('time-diff', ascending=False)
    for_next_90_3_trips = for_next_90.groupby(['bill-id'], as_index=False).head(3)
    for_next_90 = for_next_90.groupby(['bill-id'],
                                      as_index=False).agg({'id': 'nunique'})
    for_next_90 = for_next_90.rename(columns={'id': 'next-90days-trips', 'promo-used': 'promo-driven-trips'})
    logger.info(f"next 90D calc done with size : {for_next_90.shape}")

    # Merging
    final_df = pd.merge(final_df, for_next_90, on=['bill-id'], how='left')
    for_next_90_3_trips = for_next_90_3_trips.groupby(['bill-id'],
                                                      as_index=False).agg({'sales': 'mean',
                                                                           'promo-used': 'sum'})
    for_next_90_3_trips = for_next_90_3_trips.rename(columns={'sales': 'next-3trips-abv',
                                                              'promo-used': 'post3trips-promo'})

    # Merge
    final_df = pd.merge(final_df, for_next_90_3_trips, on=['bill-id'], how='left')
    patient_promo = final_df.rename(columns={'promo-date': 'bill-date'})

    # resurrection
    resurrection = resurrection.sort_values('time-diff')
    resurrection = resurrection.groupby('bill-id', as_index=False).head(1)
    resurrection = resurrection[['bill-id', 'time-diff']]
    resurrection['time-diff'] = resurrection['time-diff'].dt.days
    resurrection = resurrection.rename(columns={'time-diff': 'last-visit-in-days'})

    # Merging
    patient_promo = pd.merge(patient_promo, resurrection, on='bill-id', how='left')

    # Rounding & NaN value fill
    patient_promo = patient_promo.round({'previous-3trips-abv': 2, 'next-3trips-abv': 2})

    # behaviour segment
    cbsq = f"""
            select
                cbs."patient-id",
                cbs."behaviour-segment",
                cbs."segment-calculation-date"
            from
                "{read_schema}"."customer-behaviour-segment" cbs
            where
                cbs."patient-id" in {tuple(unique_patients)};"""

    cbs = rs_db.get_df(query=cbsq)

    cbs['segment-calculation-date'] = pd.to_datetime(cbs['segment-calculation-date'])

    # value segment
    cvsq = f"""
            select
                cvs."patient-id",
                cvs."value-segment",
                cvs."segment-calculation-date"
            from
                "{read_schema}"."customer-value-segment" cvs
            where
                "patient-id" in {tuple(unique_patients)};
                """

    cvs = rs_db.get_df(query=cvsq)

    cvs['segment-calculation-date'] = pd.to_datetime(cvs['segment-calculation-date'])

    # Function for normalizing date before joining

    patient_promo['month-segment'] = patient_promo['bill-date'].dt.to_period('M').dt.to_timestamp()

    patient_promo = pd.merge(patient_promo, cbs,
                             left_on=['patient-id', 'month-segment'],
                             right_on=['patient-id', 'segment-calculation-date'],
                             how='left')

    patient_promo = pd.merge(patient_promo, cvs,
                             left_on=['patient-id', 'month-segment'],
                             right_on=['patient-id', 'segment-calculation-date'],
                             how='left')

    patient_promo = patient_promo.drop(columns=['month-segment',
                                                'segment-calculation-date_x',
                                                'segment-calculation-date_y'])

    logger.info(f'Final Patient promo data size {patient_promo.shape} for store {store}')
    patient_promo_final = pd.concat([patient_promo_final, patient_promo])

logger.info(patient_promo_final.info())
# data type correction
patient_promo_final['bill-value'] = patient_promo_final['bill-value'].astype(float)
patient_promo_final['promo-discount'] = patient_promo_final['promo-discount'].astype(float)
patient_promo_final['flat-discount'] = patient_promo_final['flat-discount'].fillna(0).astype(int)
patient_promo_final['percent-discount'] = patient_promo_final['percent-discount'].fillna(0).astype(int)
patient_promo_final['max-discount'] = patient_promo_final['max-discount'].fillna(0).astype(int)
patient_promo_final['min-purchase'] = patient_promo_final['min-purchase'].fillna(0).astype(int)
patient_promo_final['max-time'] = patient_promo_final['max-time'].fillna(0).astype(int)
patient_promo_final['max-per-patient'] = patient_promo_final['max-per-patient'].fillna(0).astype(int)
patient_promo_final['campaign-id'] = patient_promo_final['campaign-id'].fillna(0).astype(int)

patient_promo_final['hd-flag'] = patient_promo_final['hd-flag'].astype(int)
patient_promo_final['pr-flag'] = patient_promo_final['pr-flag'].astype(int)
patient_promo_final['is-generic'] = patient_promo_final['is-generic'].astype(int)
patient_promo_final['is-chronic'] = patient_promo_final['is-chronic'].astype(int)
patient_promo_final['is-repeatable'] = patient_promo_final['is-repeatable'].astype(int)

patient_promo_final['previous-total-trips'] = patient_promo_final['previous-total-trips'].fillna(0).astype(int)
patient_promo_final['previous-90days-trips'] = patient_promo_final['previous-90days-trips'].fillna(0).astype(int)
patient_promo_final['pre3trips-promo'] = patient_promo_final['pre3trips-promo'].fillna(0).astype(int)
patient_promo_final['next-90days-trips'] = patient_promo_final['next-90days-trips'].fillna(0).astype(int)
patient_promo_final['post3trips-promo'] = patient_promo_final['post3trips-promo'].fillna(0).astype(int)
patient_promo_final['last-visit-in-days'] = patient_promo_final['last-visit-in-days'].fillna(-1).astype(int)
patient_promo_final['bill-date'] = pd.to_datetime(patient_promo_final['bill-date']).dt.date

# etl
patient_promo_final['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
patient_promo_final['created-by'] = 'etl-automation'
patient_promo_final['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
patient_promo_final['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=patient_promo_final[table_info['column_name']], file_name='Shubham_G/43/campaign_prepost.csv')
s3.write_df_to_db(df=patient_promo_final[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

# remove blanks
value_q = f"""update "{schema}"."{table_name}"  
            set "value-segment" = null 
            where "value-segment" = '';
            """
rs_db.execute(value_q)

# remove blanks
behaviour_q = f"""update "{schema}"."{table_name}"  
            set "behaviour-segment" = null 
            where "behaviour-segment" = '';
            """
rs_db.execute(behaviour_q)
# closing the connection
rs_db.close_connection()
