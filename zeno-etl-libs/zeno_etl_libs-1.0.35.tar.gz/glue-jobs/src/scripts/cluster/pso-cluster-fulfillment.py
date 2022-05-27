#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB, MySQL
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

import json
from datetime import datetime, timedelta

import argparse
import pandas as pd
import numpy as np
import time
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-st', '--start1', default="NULL", type=str, required=False)
parser.add_argument('-ed', '--start2', default="NULL", type=str, required=False)
parser.add_argument('-ct', '--cluster_to_exclude_if_blank_none', default="NULL", type=str, required=False)
parser.add_argument('-wt', '--write_to_mysql', default="1", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
start1 = args.start1
start2 = args.start2
cluster_to_exclude_if_blank_none = args.cluster_to_exclude_if_blank_none
write_to_mysql = args.write_to_mysql

os.environ['env'] = env

logger = get_logger(level='INFO')

rs_db = DB()

rs_db.open_connection()

mysql_write = MySQL(read_only=False)
mysql_write.open_connection()

s3 = S3()
start_time = datetime.now(tz=gettz('Asia/Kolkata'))
today_date = start_time.strftime('%Y-%m-%d')
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("write_to_mysql- " + write_to_mysql)

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.now(tz=gettz('Asia/Kolkata')).strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# set parameters
# =============================================================================

if start1=="NULL" and start2=="NULL":
    # pick orders from to last night 2030 to today morning 0800
    logger.info("Read automated dates")
    if datetime.now(tz=gettz('Asia/Kolkata')).strftime('%H:%M:%S') < '09:30:00':
        start1 = (datetime.now(tz=gettz('Asia/Kolkata')) -
                  timedelta(days=1)).strftime('%Y-%m-%d 19:00:00')
        start2 = (datetime.now(tz=gettz('Asia/Kolkata'))).strftime('%Y-%m-%d 09:00:00')
        logger.info("start1 {}".format(start1))
        logger.info("start2 {}".format(start2))
        logger.info("")

    else:
        if env=='dev':
            def ceil_dt(dt, delta):
                return dt + (datetime(1, 1, 1, 0, 0, tzinfo=gettz('Asia/Calcutta')) - dt) % delta
        else:
            def ceil_dt(dt, delta):
                return dt + (datetime(1, 1, 1, 0, 0, 0 ,tzinfo=gettz('Asia/Calcutta'))  - dt) % delta + timedelta(minutes=23,seconds=20)


        start2 = (ceil_dt(datetime.now(tz=gettz('Asia/Kolkata')), timedelta(minutes=-30)))
        start1 = (start2 - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        start2 = ceil_dt(datetime.now(tz=gettz('Asia/Kolkata')), timedelta(minutes=-30)).strftime('%Y-%m-%d %H:%M:%S')

        logger.info("start1 {}".format(start1))
        logger.info("start2 {}".format(start2))
        logger.info("")

else:
    start1 = start1
    start2 = start2
    logger.info("Read manual dates")
    logger.info("start1 {}".format(start1))
    logger.info("start2 {}".format(start2))

# Writng this function so that we can get list of stores irrespective of input format in parameter
def fetch_number(list):
    list2 = []
    for i in list:
        try:
            int(i)
            list2.append(int(i))
        except:
            pass
    return list2


if cluster_to_exclude_if_blank_none=="NULL":
    logger.info('Missing parameter for cluster exclusion, Taking all cluster')
    cluster_to_exclude_if_blank_none = []
else:
    cluster_to_exclude_if_blank_none = cluster_to_exclude_if_blank_none
    cluster_to_exclude_if_blank_none = fetch_number(cluster_to_exclude_if_blank_none[1:-1].split(','))
    logger.info('read parameters for cluster exclusion, cluster id to exclude are - {}'.format(
        cluster_to_exclude_if_blank_none))

# =============================================================================
# store clusters
# =============================================================================

qc = """
    select
        sf."feature-id",
        f.feature,
        sf."store-id",
        sf."is-active", 
        sc."cluster-id"
    from
        "prod2-generico".features f
    join "prod2-generico"."store-features" sf on
        f.id = sf."feature-id"
    join "prod2-generico"."store-clusters" sc on 
        sc."store-id" = sf."store-id"
    where
        sf."feature-id" = 69
        and sf."is-active" = 1
        and sc."is-active" = 1
"""

store_clusters = rs_db.get_df(qc)

cluster_fullfilment_final = pd.DataFrame()
orders_raw = pd.DataFrame()
cluster_list = list(set(store_clusters['cluster-id'].unique()) - set(cluster_to_exclude_if_blank_none))

for cluster in cluster_list:
    logger.info("")
    logger.info("cluster {}".format(cluster))
    temp = store_clusters[store_clusters['cluster-id'] == cluster]

    cluster_stores = tuple(map(int, list(temp['store-id'].unique())))

    # cluster_stores = tuple(map(int, list([2, 4, 7, 8, 230, 244, 264])))
    logger.info("cluster stores {}".format(cluster_stores))
    logger.info("")

    summ_data = pd.DataFrame()

    for i in cluster_stores:
        logger.info("running for store {}".format(i))
        logger.info("")
        # analysis_store = tuple(map(int, list([i])))
        analysis_store = i
        # analysis_cluster = tuple(map(int, [x for x in cluster_stores if x != i]))
        analysis_cluster = cluster_stores

        # for manual run
        # i = 8
        # analysis_store = tuple(map(int, list([i])))
        # analysis_cluster = tuple(map(int, [x for x in cluster_stores if x != i]))

        # =============================================================================
        # Fetch open PSOs for selected time period
        # =============================================================================
        orde = """
                select
                    pso."order-number",
                    pso."patient-request-id",
                    pso."zeno-order-id" ,
                    pso."patient-id" ,
                    pso.id as "pso-id",
                    pso."order-source" ,
                    pso."order-type" ,
                    pso."status",
                    pso."created-at", 
                    pso."store-id" ,
                    s."name" as "store-name",
                    pso."drug-id" ,
                    pso."drug-name" ,
                    pso."requested-quantity", 
                    pso."inventory-quantity" as "inventory-at-creation", 
                    pr."required-quantity", 
                    pr."quantity-to-order" 
                from
                    "prod2-generico"."patients-store-orders" pso
                left join "prod2-generico"."patient-requests" pr on
                        pso."patient-request-id" = pr.id
                join "prod2-generico"."stores" s on s."id" = pso."store-id"
                where
                    pr."created-at" > '{start1}'
                    and pr."created-at" <= '{start2}'
                    and pso."store-id" = {analysis_store}
                    and pso.status not in ('billed', 'completed')
                order by pso."created-at" DESC;
        """.format(start1=start1, start2=start2, analysis_store=analysis_store)

        orders = rs_db.get_df(orde)

        orders = orders[~orders['drug-id'].isnull()]

        # =============================================================================
        # cluster inventory
        # =============================================================================

        drugs = tuple(map(int, list(orders['drug-id'].unique())))

        if len(drugs)<2:
            drugs = drugs + (0,0)

        q_inv = """
         select
             i."store-id",
             s."name" as "store-name",
             i."drug-id",
             sum(i."quantity") as "ci"
         from
             "prod2-generico"."inventory-1" i
         join "prod2-generico".stores s on
             i."store-id" = s."id"
         where
             i."store-id" in {cluster_stores}
             and i."drug-id" in {drugs}
             and i."quantity" > 0
             and i."expiry" > dateadd(day,90,getdate())
         group by
             i."store-id",
             s."name",
             i."drug-id";
         """.format(cluster_stores=cluster_stores,drugs=drugs)

        df_inv = rs_db.get_df(q_inv)

        clus_inv = df_inv[df_inv['store-id'].isin(analysis_cluster)]

        # cluster store inventory sum
        clus_inv_st_sum = clus_inv.groupby(['drug-id', 'store-id', 'store-name'],
                                           as_index=False).agg({
            'ci': ['sum']
        }).reset_index(drop=True)
        clus_inv_st_sum.columns = ["-".join(x) for x in clus_inv_st_sum.columns.ravel()]
        clus_inv_st_sum.rename(columns={'store-name-': 'clus-store-name',
                                        'store-id-': 'store-id',
                                        'drug-id-': 'drug-id',
                                        'ci-sum': 'clus-store-inv'}, inplace=True)
        # cluster inventory sum
        clus_inv_all_sum = clus_inv.groupby(['drug-id'],
                                            as_index=False).agg({
            'ci': ['sum']
        }).reset_index(drop=True)
        clus_inv_all_sum.columns = ["-".join(x) for x in clus_inv_all_sum.columns.ravel()]
        clus_inv_all_sum.rename(columns={'drug-id-': 'drug-id',
                                         'ci-sum': 'clus-inv'}, inplace=True)

        orders_clus_inv = pd.merge(left=orders,
                                   right=clus_inv_st_sum,
                                   how='left', on=['drug-id'], suffixes=('-x', '-y')).rename(
            columns={'store-id-y': 'clus-store-id'})

        orders_clus_inv = pd.merge(left=orders_clus_inv,
                                   right=clus_inv_all_sum,
                                   how='left', on=['drug-id'], suffixes=('-x', '-y')).rename(
            columns={'store-id-y': 'clus-store-id'})

        summ_data = summ_data.append(orders_clus_inv)

    summ_data['clus-inv'].fillna(0, inplace=True)
    summ_data['clus-store-inv'].fillna(0, inplace=True)
    summ_data['required-quantity'].fillna(0, inplace=True)
    summ_data['quantity-to-order'].fillna(0, inplace=True)

    summ_data['clus-inv-diff'] = (summ_data['clus-store-inv'] -
                                  summ_data['quantity-to-order'])

    # remove same store transfer due to partial inventory
    summ_data = summ_data[~(summ_data['store-id-x'] ==
                            summ_data['clus-store-id'])]

    # for QC later
    orders_raw = orders_raw.append([summ_data])

    # =============================================================================
    # MOST CRITICAL: tagging where to fulfill from
    # the logic can be cleaner
    # =============================================================================
    conditions = [
        (summ_data['quantity-to-order'] > 0) & (summ_data['clus-inv-diff'] >= 0),
        (summ_data['quantity-to-order'] == 0)
    ]
    choices = ['ff-using-single-store', 'ff-using-self-store']
    summ_data['color'] = np.select(conditions, choices)

    summ_data1 = summ_data[summ_data['color'].isin(['ff-using-single-store',
                                                    'ff-using-self-store'])]
    summ_data1 = summ_data1[['order-number', 'patient-id',
                             'pso-id', 'drug-id',
                             'color']].drop_duplicates().rename(
        columns={'color': 'tag'})
    summ_data = pd.merge(left=summ_data, right=summ_data1,
                         how='left', on=['order-number', 'patient-id',
                                         'pso-id', 'drug-id'])
    conditions = [
        (
                (summ_data['quantity-to-order'] > 0) &
                (summ_data['clus-inv'] >= summ_data['quantity-to-order']) &
                (summ_data['tag'].isnull())
        )
    ]
    choices = ['ff-using-multi-store']
    summ_data['tag'] = np.select(conditions, choices,
                                 default=summ_data['tag'])
    summ_data['tag'].fillna('ff-using-DC-WH', inplace=True)

    # to consider partial ff cases
    summ_data_temp = summ_data.groupby(['order-number',
                                        'pso-id']).size().reset_index().rename(
        columns={0: 'cumsum'})

    summ_data['order-number'] = summ_data['order-number'].astype(object)
    summ_data_temp['order-number'] = summ_data_temp['order-number'].astype(object)

    summ_data['pso-id'] = summ_data['pso-id'].astype(int)
    summ_data_temp['pso-id'] = summ_data_temp['pso-id'].astype(int)

    summ_data = pd.merge(left=summ_data, right=summ_data_temp,
                         how='left', on=['order-number', 'pso-id'])
    conditions = [
        (
                (summ_data['quantity-to-order'] > 0) &
                (summ_data['tag'] == 'ff-using-DC-WH') &
                (summ_data['cumsum'] == 1)
        ),
        (
                (summ_data['quantity-to-order'] > 0) &
                (summ_data['tag'] == 'ff-using-DC-WH') &
                (summ_data['cumsum'] > 1)
        )
    ]
    choices = ['ff-using-single-store', 'ff-using-multi-store']
    summ_data['tag'] = np.select(conditions, choices,
                                 default=summ_data['tag'])

    # =============================================================================
    # distance calculation
    # =============================================================================
    strs = """
        select
            *
        from
            (
            select
                sd."store-id-x" as "store-id-x",
                sd."store-id-y" as "clus-store-id",
                sd."distance-on-road" as "distance"
            from
                "prod2-generico"."store-distance" sd
            where
                sd."store-id-x" in {})x
        where
            x."clus-store-id" in {}
    """.format(cluster_stores, cluster_stores)

    str_info_cross = rs_db.get_df(strs)

    summ_data = pd.merge(summ_data,
                         str_info_cross[['store-id-x', 'clus-store-id', 'distance']],
                         how='left',
                         left_on=['store-id-x', 'clus-store-id'],
                         right_on=['store-id-x', 'clus-store-id'])

    summ_data_clean = summ_data.drop(summ_data[
                                         # ((summ_data['tag'] == 'ff_using_single_store') &
                                         # (summ_data.clus_inv_diff < 0)) |
                                         (summ_data['tag'] == 'ff-using-self-store') |
                                         (summ_data['tag'] == 'ff-using-DC-WH')].index)

    # this is likely redundant
    str_avail_cnt = summ_data_clean.groupby(['clus-store-id'])['pso-id'].count().reset_index().rename(
        columns={'pso-id': 'drug-availability-cnt'})

    summ_data_clean = pd.merge(summ_data_clean,
                               str_avail_cnt,
                               how='left',
                               left_on=['clus-store-id'],
                               right_on=['clus-store-id'])

    # =============================================================================
    # ff_using_single_store
    # =============================================================================
    ff_using_single_store = summ_data_clean[
        summ_data_clean['tag'] == 'ff-using-single-store']

    ff_using_single_store_best = ff_using_single_store.sort_values(
        ['clus-store-inv', 'distance'],
        ascending=[False, True]).groupby(['order-number',
                                          'pso-id']).head(1)
    ff_using_single_store_best = ff_using_single_store_best[['order-number',
                                                             'pso-id',
                                                             'clus-store-id',
                                                             'clus-store-name']]. \
        rename(columns={'clus-store-id': 'best-store-id',
                        'clus-store-name': 'best-store-name'})

    ff_using_single_store_best_all = pd.merge(ff_using_single_store,
                                              ff_using_single_store_best,
                                              how='left',
                                              left_on=['order-number', 'pso-id'],
                                              right_on=['order-number', 'pso-id'])

    ff_using_single_store_final = ff_using_single_store_best_all[
        ff_using_single_store_best_all['clus-store-id'] ==
        ff_using_single_store_best_all['best-store-id']]

    # =============================================================================
    # ff_using_multi_store
    # =============================================================================
    ff_using_multi_store = summ_data_clean[
        summ_data_clean['tag'] == 'ff-using-multi-store']

    ff_using_multi_store.sort_values(['order-number',
                                      'pso-id',
                                      'clus-store-inv'],
                                     ascending=[True, True, False], inplace=True)

    ff_using_multi_store['cumsum'] = ff_using_multi_store.groupby(['order-number',
                                                                   'pso-id'])['clus-store-inv'].cumsum()

    ff_using_multi_store['cond'] = np.where(
        ff_using_multi_store['cumsum'] >= ff_using_multi_store['quantity-to-order'],
        'red', 'green')

    ff_using_multi_store['temp'] = ff_using_multi_store['cumsum'].mask(ff_using_multi_store['cond'] != 'red').groupby(
        ff_using_multi_store['pso-id']).transform('first').astype(int, errors='ignore')

    ff_using_multi_store['cond'] = np.where(((ff_using_multi_store['cumsum'] ==
                                              ff_using_multi_store['temp']) &
                                             (ff_using_multi_store['cond'] == 'red')),
                                            'green',
                                            ff_using_multi_store['cond'])
    del ff_using_multi_store['temp']

    ff_using_multi_store_final = ff_using_multi_store[
        ff_using_multi_store['cond'] == 'green']

    ff_using_multi_store_final['best-store-id'] = ff_using_multi_store_final['clus-store-id']
    ff_using_multi_store_final['best-store-name'] = ff_using_multi_store_final['clus-store-name']

    ff_using_single_multi_store = ff_using_single_store_final.append(
        [ff_using_multi_store_final])

    # =============================================================================
    # final dataset
    # =============================================================================
    ff_using_single_multi_store['to-pick'] = np.where((
        (ff_using_single_multi_store['clus-store-inv'] >=
         ff_using_single_multi_store['quantity-to-order'])),
        ff_using_single_multi_store['quantity-to-order'],
        ff_using_single_multi_store['clus-store-inv'])

    ff_using_single_multi_store['cluster-id'] = cluster

    cluster_fullfilment_final = (cluster_fullfilment_final.append([ff_using_single_multi_store]))

# =============================================================================
# check whether algorithm missed any PSOs
# =============================================================================
check_final = cluster_fullfilment_final.groupby(['pso-id'])['to-pick'].sum().reset_index()

check_first = orders_raw[
    orders_raw['quantity-to-order'] > 0][[
    'pso-id', 'drug-name',
    'quantity-to-order',
    'clus-inv']].drop_duplicates().reset_index(drop=True)

check_first = check_first.groupby(['pso-id']).agg(
    {'quantity-to-order': [np.sum],
     'drug-name': [max],
     'clus-inv': [np.max]}).reset_index()
check_first.columns = ["-".join(x) for x in check_first.columns.ravel()]

check_first.rename(columns={'pso-id-': 'pso-id',
                            'drug-name-max': 'drug-name',
                            'quantity-to-order-sum': 'quantity-to-order',
                            'clus-inv-amax': 'clus-inv'},
                   inplace=True)

check_first1 = check_first
check_first = check_first[check_first['clus-inv'] > 0]

check_first_final = pd.merge(check_first1,
                             check_final,
                             how='left',
                             left_on=['pso-id'],
                             right_on=['pso-id'])

logger.info("")
logger.info("missed {}".format((len(check_first) - len(check_final))))
logger.info("missed PSOs {}".
            format(list(sorted(set(check_first['pso-id']) -
                               set(check_final['pso-id'])))))
logger.info("")

# =============================================================================
# for pushing to DSS/PROD
# =============================================================================
output_df = cluster_fullfilment_final[['pso-id',
                                       'best-store-id',
                                       'best-store-name',
                                       'store-id-x',
                                       'store-name',
                                       'drug-id',
                                       'drug-name',
                                       'to-pick',
                                       'created-at',
                                       'cluster-id']].rename(columns={
    'best-store-name': 'from-store',
    'store-name': 'to-store',
    'to-pick': 'item-quantity',
    'created-at': 'pso-created_at'
})
output_df['slot-date'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d')
output_df['is-active'] = 1
output_df['created-by'] = 'data@generico.in'
output_df['updated-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
output_df.sort_values(by=['from-store'], ascending=False,
                      inplace=True)

# for DSS
output_df.rename(columns={'pso-id': 'patient-store-order-id',
                          'best-store-id': 'from-store-id',
                          'best-store-name': 'from-store-name',
                          'store-id-x': 'to-store-id',
                          'store-name': 'to-store-name'}, inplace=True)

# for MySQL
output_df_mysql = output_df[['patient-store-order-id',
                             'item-quantity',
                             'from-store-id',
                             'to-store-id',
                             'slot-date',
                             'is-active',
                             'created-by',
                             'updated-at']]

output_df_mysql.rename(columns={
    'patient-store-order-id': 'patient-store-order-id',
    'item-quantity': 'item-quantity',
    'from-store-id': 'from-store-id',
    'to-store-id': 'to-store-id',
    'slot-date': 'slot-date',
    'is-active': 'is-active',
    'created-by': 'created-by',
    'updated-at': 'updated-at'}, inplace=True)

logger.info("")
logger.info("completed for cluster {}".format(cluster_stores))
logger.info("")
logger.info("{} PSOs created from {} to {}".format(len(output_df),
                                                   start1, start2))
logger.info("")

pso_cluster_fulfillment = output_df
pso_cluster_fulfillment['pso-created-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
# output_df_json = json.loads(output_df.to_json(orient='records'))
pso_cluster_fulfillment[['from-store-id', 'to-store-id', 'drug-id', 'item-quantity']] = pso_cluster_fulfillment[['from-store-id', 'to-store-id', 'drug-id', 'item-quantity']].apply(pd.to_numeric, errors='ignore').astype('Int64')
#
# =============================================================================
# writing to PG
# =============================================================================

# pushing pso_cluster_fulfillment table to redshift table
status2 = False
number_of_writing_attempts = 0

if int(write_to_mysql) == 1:

    try:
        number_of_writing_attempts = number_of_writing_attempts+1
        schema = 'prod2-generico'
        table_name = 'pso-cluster-fulfillment'
        table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

        s3.write_df_to_db(df=pso_cluster_fulfillment[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)

        logger.info(' ')
        logger.info('table appended to Redshift')

        # pushing to mysql prod
        output_df_mysql.to_sql(
            name='pso-stock-transfer-mapping', con=mysql_write.engine,
            if_exists='append',
            chunksize=500, method='multi', index=False)
        logger.info(' ')
        logger.info('table appended to MySQL')

        status2 = True

    except Exception as error:
        logger.exception(error)
        logger.info(f'writing to mysql failed - attempt - {number_of_writing_attempts}')
        status2 = False

    if status2 == False:
        logger.info('Writing to mysql table failed, Mostly it is due to deadlock issue, sleep for 3 mins')
        time.sleep(180)
        logger.info('slept for 3 mins')

        try:
            number_of_writing_attempts = number_of_writing_attempts + 1
            logger.info(f'attempt number - {number_of_writing_attempts}')
            # pushing to mysql prod
            output_df_mysql.to_sql(
                name='pso-stock-transfer-mapping', con=mysql_write.engine,
                if_exists='append',
                chunksize=500, method='multi', index=False)
            logger.info(' ')
            logger.info('table appended to MySQL')
            status2 = True
        except Exception as error:
            logger.exception(error)
            logger.info(f'writing to mysql failed - attempt - {number_of_writing_attempts}')
            status2 = False

    if status2 is True:
        status = 'Success'
    else:
        status = 'Failed'
else:
    status = 'test'

pso_added_uri = s3.save_df_to_s3(df=check_first_final, file_name='pso_transfer_details_{}_{}.csv'.format(start1, start2))

end_time = datetime.now(tz=gettz('Asia/Kolkata'))
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)
email = Email()

email.send_email_file(subject='{} - {} - {} PSOs, {} clus_missed, {} algo_missed from {} to {}'.format(
    env, status,
    len(check_first1),
    (len(check_first1) - len(check_final)),
    (len(check_first) - len(check_final)),
    start1, start2),
    mail_body=f" pso-stock-transfer-mapping table update - {status}\n"
              f"Time for job completion - {min_to_complete} mins\n"
              f" Number of writing attempts - {number_of_writing_attempts}",
    to_emails=email_to, file_uris=[pso_added_uri])

rs_db.close_connection()
mysql_write.close()