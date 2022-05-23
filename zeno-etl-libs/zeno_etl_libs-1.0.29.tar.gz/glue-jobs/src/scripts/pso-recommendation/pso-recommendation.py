"""
Author:shubham.gupta@zeno.health
Purpose: PSO Metrics
"""

import argparse
import numpy as np
import os
import pandas as pd
import sys
from dateutil.tz import gettz

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper

from datetime import datetime as dt
from datetime import timedelta

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

# =============================================================================
# set parameters
# =============================================================================

if full_run:
    pso_date1 = '2022-02-01'
    pso_date2 = str(dt.today().date() - timedelta(days=1))
else:
    pso_date1 = str(dt.today().date() - timedelta(days=10))
    pso_date2 = str(dt.today().date() - timedelta(days=1))

schema = 'prod2-generico'
table_name = "pso-recommendation-visibility"

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
                "created-at" BETWEEN '{pso_date1}' AND '{pso_date2}';
                """
    logger.info(truncate_query)
    rs_db.execute(truncate_query)

# =============================================================================
# store clusters
# =============================================================================


qc = f"""
        select
            sf."feature-id",
            f.feature,
            sf."store-id",
            sf."is-active" as "pso-recomm-active",
            coalesce(sc."cluster-id", 0) as "cluster-id",
            coalesce(c.name, '0') as "cluster-name"
        from
            "{read_schema}".features f
        left join "{read_schema}"."store-features" sf on
            f.id = sf."feature-id"
        left join "{read_schema}"."store-clusters" sc on
            sc."store-id" = sf."store-id"
        left join "{read_schema}".clusters c on
            c.id = sc."cluster-id"
        where
            sf."feature-id" = 68
            and sf."is-active" = 1; 
        """

store_clusters = rs_db.get_df(query=qc)
orders_transfers_all = pd.DataFrame()

for cluster in store_clusters['cluster-id'].unique():
    logger.info("")
    logger.info("cluster {}".format(cluster))

    temp = store_clusters[store_clusters['cluster-id'] == cluster]

    cluster_stores = tuple(map(int, list(temp['store-id'].unique())))

    # =============================================================================
    # GET PRs
    # =============================================================================

    q1 = f"""
        select
            pso."order-number",
            pso.id as "patient-store-order-id",
            pso."patient-request-id",
            pso."zeno-order-id" ,
            pso."patient-id" ,
            pso."order-source" ,
            pso."order-type" ,
            pso."slot-recommendation-status" AS "fulfillment-actions",
            pso."status" as "pso-status",
            pso."created-at" AS "pso-created-at",
            pso."store-id" ,
            s."name" as "store-name",
            pso."drug-id" ,
            pso."drug-name" ,
            pso."requested-quantity", 
            pso."inventory-quantity" as "inventory-at-creation", 
            pr."required-quantity", 
            pr."quantity-to-order", 
            pso."bill-id",
            b."created-at" AS "bill-date", 
            dt."delivered-at"
        from
            "{read_schema}"."patients-store-orders" pso
        left join "{read_schema}"."patient-requests" pr 
            on pso."order-number" = pr."patient-request-number" 
            and pso."patient-request-id" = pr.id
        join "{read_schema}"."stores" s on s."id" = pso."store-id"
        left join "{read_schema}"."bills-1" b on b."id" = pso."bill-id"
        left join "{read_schema}"."delivery-tracking" dt 
                on dt."patient-store-order-id" = pso."id"
        where
            DATE(pso."created-at") >= '{pso_date1}' 
            and DATE(pso."created-at") <= '{pso_date2}'
            and pso."store-id" in {cluster_stores}
            and b."created-at" is not null;
            """

    q2 = f"""
            select
                distinct 
                pso."order-number",
                pso."slot-date",
                psr."recommended-slot-date",
                pso."slot-id",
                psr."recommended-slot-id",
                ss_1."end-time" as "selected-end-time",
                ss_2."end-time" as "recommended-end-time",
                (case
                    when pso."slot-date" = psr."recommended-slot-date"
                    and pso."slot-id" = psr."recommended-slot-id" then 'recommended_slot'
                    else
                    'not_recommended_slot'
                end) "selected-slot"
            from
                "{read_schema}"."patients-store-orders" pso
            left join "{read_schema}"."pso-slot-recommendation" psr on
                pso."order-number" = psr."order-number"
            left join "{read_schema}"."store-slots" ss_1 on
                pso."slot-id" = ss_1.id
            left join "{read_schema}"."store-slots" ss_2 on
                pso."slot-id" = ss_2.id
            where
                DATE(pso."created-at") >= '{pso_date1}'
                and DATE(pso."created-at") <= '{pso_date2}';"""

    orders = rs_db.get_df(query=q1)
    recommendation = rs_db.get_df(query=q2)

    orders['required-quantity'].fillna(0, inplace=True)
    orders['quantity-to-order'].fillna(0, inplace=True)

    orders['delivered-at'] = pd.to_datetime(orders['delivered-at'], errors='coerce')
    orders['delivered-at'] = np.where(orders['delivered-at'].isnull(), orders['bill-date'], orders['delivered-at'])


    def string_to_time(x):
        try:
            return dt.strptime(x, "%I:%M %p").time()
        except:
            try:
                return dt.strptime(x, "%I:%M%p").time()
            except:
                return "Can't convert"


    recommendation['selected-end-time'] = recommendation['selected-end-time'].apply(
        lambda x: string_to_time(x))
    recommendation['recommended-end-time'] = recommendation['recommended-end-time'].apply(
        lambda x: string_to_time(x))

    recommendation['recommended-slot-date'] = recommendation['recommended-slot-date'].fillna(dt(2100, 1, 1))
    recommendation['slot-date'] = pd.to_datetime(recommendation['slot-date']).dt.date
    recommendation['recommended-slot-date'] = pd.to_datetime(recommendation['recommended-slot-date']).dt.date


    def early_later(x):
        if x['slot-date'] < x['recommended-slot-date']:
            return 'early_slot'
        elif (x['slot-date'] == x['recommended-slot-date']) & (x['selected-end-time'] < x['recommended-end-time']):
            return 'early_slot'
        elif x['selected-slot'] == 'recommended_slot':
            return 'recommended-slot'
        else:
            return 'later_slot'


    recommendation['early-later-slot'] = recommendation.apply(lambda x: early_later(x), 1)

    orders = pd.merge(orders, recommendation, on='order-number', how='left')

    orders['availability-tag'] = np.where(
        orders['quantity-to-order'] > 0, "pr-short", np.nan)

    orders['availability-tag'] = orders.fillna('').sort_values(
        ['order-number',
         'availability-tag']).groupby('order-number')['availability-tag'].transform('last')

    orders['availability-tag'] = np.where(
        orders['availability-tag'] != 'pr_short',
        "pr_not_short", orders['availability-tag'])
    # =============================================================================
    # Get transfers
    # =============================================================================
    trnfrs = tuple(map(int, list(orders['patient-store-order-id'].unique())))

    q2 = f"""
            select
                pso."order-number",
                pstm."patient-store-order-id",
                pstm."from-store-id",
                pstm."to-store-id",
                pstm."item-quantity" as "to-be-transferred-qty",
                sti."quantity" as "actual-transferred-qty",
                st."total-items",
                pstm."slot-date",
                pstm."status" as "tn-status",
                st."status" as "transfer-status",
                st."initiated-at",
                st."transferred-at",
                st."received-at",
                DATEDIFF(minute, st."transferred-at", st."received-at") as "transfer-minutes", 
                zo."created-at" as "zeno-created-at"
            from
                "{read_schema}"."pso-stock-transfer-mapping" pstm
            left join "{read_schema}"."patients-store-orders" pso on
                pso.id = pstm."patient-store-order-id"
            left join "{read_schema}"."stock-transfers-1" st 
                on
                st.id = pstm."stock-transfer-id"
            left join "{read_schema}"."stock-transfer-items-1" sti 
                on
                sti.id = pstm."stock-transfer-item-id"
            left join "{read_schema}"."zeno-order" zo 
                on
                zo.id = pso."zeno-order-id"
            where
                pstm."patient-store-order-id" in {trnfrs}
                """
    transfers = rs_db.get_df(query=q2)

    transfers['received-at'] = pd.to_datetime(transfers['received-at'],
                                              format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

    transfers_summ = transfers.groupby(['order-number',
                                        'patient-store-order-id']).agg(
        {'initiated-at': [np.max],
         'transferred-at': [np.max],
         'received-at': [np.max],
         'zeno-created-at': [np.max],
         'to-be-transferred-qty': [np.sum],
         'actual-transferred-qty': [np.sum]}).reset_index()
    transfers_summ.columns = ["_".join(x) for x in transfers_summ.columns.ravel()]
    transfers_summ.rename(columns={'initiated-at_amax': 'initiated-at',
                                   'transferred-at_amax': 'transferred-at',
                                   'received-at_amax': 'received-at',
                                   'to-be-transferred-qty_sum': 'to-be-transferred-qty',
                                   'actual-transferred-qty_sum': 'actual-transferred-qty',
                                   'transfer-status_': 'transfer-status',
                                   'order-number_': 'order-number',
                                   'patient-store-order-id_': 'patient-store-order-id',
                                   'zeno-created-at_amax': 'zeno-created-at'},
                          inplace=True)
    if cluster == 0:
        transfers_summ['order-number'] = np.nan
        transfers_summ['patient-store-order-id'] = np.nan
        # transfers_summ = transfers_summ.drop(columns=['index_'])
    orders_transfers = pd.merge(left=orders, right=transfers_summ,
                                how='left', on=['order-number',
                                                'patient-store-order-id'])

    orders_transfers['to-be-transferred-qty'].fillna(0, inplace=True)
    orders_transfers['actual-transferred-qty'].fillna(0, inplace=True)

    orders_transfers['zeno-created-at'] = pd.to_datetime(orders_transfers['zeno-created-at'])
    orders_transfers['initiated-at'] = pd.to_datetime(orders_transfers['initiated-at'])
    orders_transfers['transferred-at'] = pd.to_datetime(orders_transfers['transferred-at'])
    # lead to pso creation
    orders_transfers['lead-to-pso-creation-hours'] = \
        ((orders_transfers['pso-created-at'] - orders_transfers['zeno-created-at'])
         / np.timedelta64(1, 'h'))

    # PSO to transfer inititate
    orders_transfers['pso-to-transfer-initiate-hours'] = \
        ((orders_transfers['initiated-at'] - orders_transfers['pso-created-at'])
         / np.timedelta64(1, 'h'))

    # PSO to transfer transferred
    orders_transfers['pso-to-transfer-transfer-hours'] = \
        ((orders_transfers['transferred-at'] - orders_transfers['pso-created-at'])
         / np.timedelta64(1, 'h'))

    # PSO to transfer received
    orders_transfers['pso-to-transfer-received-hours'] = \
        ((orders_transfers['received-at'] - orders_transfers['pso-created-at'])
         / np.timedelta64(1, 'h'))

    # PSO to bill
    orders_transfers['pso-to-bill-hours'] = \
        ((orders_transfers['bill-date'] - orders_transfers['pso-created-at'])
         / np.timedelta64(1, 'h'))

    orders_transfers['pso-to-bill-hours'] = np.where(
        orders_transfers['pso-to-bill-hours'] < 0, 0, orders_transfers['pso-to-bill-hours'])

    # PSO to delivered
    orders_transfers['pso-to-delivered-hours'] = \
        ((orders_transfers['delivered-at'] - orders_transfers['pso-created-at'])
         / np.timedelta64(1, 'h'))

    orders_transfers['cluster-id'] = cluster

    # =============================================================================
    # Cluster Name
    # =============================================================================

    qc1 = f"""	
            select
                c.id AS "cluster-id" ,
                c.name AS "cluster-name"
            from
                "{read_schema}".clusters c
            """
    cluster_info = rs_db.get_df(query=qc1)

    orders_transfers = pd.merge(orders_transfers, cluster_info, on='cluster-id', how='left')

    # =============================================================================
    # OTIF calculation
    # =============================================================================
    bills = tuple(map(int,
                      list(orders_transfers[orders_transfers['bill-id'].notna()]['bill-id'].unique())))

    qc = f"""
        select
            bi."bill-id",
            count(distinct i."drug-id") as "drug-billed-cnt",
            sum(bi.quantity) as "quantity-billed-sum"
        from
            "{read_schema}"."bills-1" b
        join "{read_schema}"."bill-items-1" bi on
            b.id = bi."bill-id"
        join "{read_schema}"."inventory-1" i on
            i.id = bi."inventory-id"
        where
            bi."bill-id" in {bills}
        group by
            bi."bill-id"
            """
    billed = rs_db.get_df(query=qc)

    orders_transfers1 = pd.merge(left=orders_transfers,
                                 right=billed,
                                 how='left', on=['bill-id'])

    orders_transfers_d_infull1 = orders_transfers.groupby(
        ['order-number'])['drug-id'].nunique().reset_index().rename(
        columns={'drug-id': 'drug-ordered-cnt'})

    orders_transfers_q_infull1 = orders_transfers.groupby(
        ['order-number']).agg(
        {'requested-quantity': [np.sum]}).reset_index().rename(
        columns={'requested-quantity': 'requested-quantity-ordered-sum'})

    orders_transfers_q_infull1.columns = ["_".join(x) for x in orders_transfers_q_infull1.columns.ravel()]
    orders_transfers_q_infull1.rename(
        columns={'requested-quantity-ordered-sum_sum': 'requested-quantity-ordered-sum',
                 'order-number_': 'order-number'},
        inplace=True)

    orders_transfers_infull1 = pd.merge(orders_transfers_d_infull1, orders_transfers_q_infull1,
                                        on='order-number', how='inner')

    orders_transfers2 = pd.merge(left=orders_transfers1,
                                 right=orders_transfers_infull1,
                                 how='left', on=['order-number'])

    orders_transfers2['in-full-flag'] = np.where(
        orders_transfers2['drug-billed-cnt'] >= orders_transfers2['drug-ordered-cnt'],
        "in_full", "not_in_full")

    orders_transfers2['qty-in-full-flag'] = np.where(
        orders_transfers2['quantity-billed-sum'] >= orders_transfers2['requested-quantity-ordered-sum'],
        "qty_in_full", "qty_not_in_full")

    orders_transfers2['drug-billed-cnt'].fillna(0, inplace=True)
    orders_transfers2['quantity-billed-sum'].fillna(0, inplace=True)
    orders_transfers2['drug-ordered-cnt'].fillna(0, inplace=True)
    orders_transfers2['requested-quantity-ordered-sum'].fillna(0, inplace=True)

    # del orders_transfers2['drug_ordered_cnt']
    # del orders_transfers2['drug_billed_cnt']
    # del orders_transfers2['quantity_billed_sum']
    # del orders_transfers2['requested_quantity_ordered_sum']

    orders_transfers2['slot-date-time'] = orders_transfers2.apply(lambda x:
                                                                  dt.combine(x['slot-date'],
                                                                             x['selected-end-time']), 1)
    breakpoint()
    # Different definition for PSO recommendation
    orders_transfers2['otif-flag'] = np.where(
        ((orders_transfers2['in-full-flag'] == 'in-full') &
         (orders_transfers2['delivered-at'] <= orders_transfers2['slot-date-time'])),
        "otif", "not_otif")

    orders_transfers2['qty-otif-flag'] = np.where(
        ((orders_transfers2['qty-in-full-flag'] == 'qty-in-full') &
         (orders_transfers2['delivered-at'] <= orders_transfers2['slot-date-time'])),
        "qty_otif", "qty_not_otif")

    del orders_transfers2['slot-date-time']

    logger.info("")
    logger.info(
        "length is same {}".format(len(orders) == len(orders_transfers2)))
    logger.info("")
    orders_transfers_all = orders_transfers_all.append(orders_transfers2)
    pso_recommendation = orders_transfers_all
    actions = pso_recommendation.groupby('order-number', as_index=False).agg({'fulfillment-actions': 'unique'})


    def order_action_fulfillment(x):
        if 'LP' in x:
            return 'LP'
        elif 'S2S' in x:
            return 'S2S'
        elif 'DC' in x:
            return 'DC'
        elif 'SF' in x:
            return 'SF'
        else:
            return None


    actions['final-fulfillment'] = actions['fulfillment-actions'].apply(lambda x: order_action_fulfillment(x))
    actions = actions.drop(columns=['fulfillment-actions'])
    pso_recommendation = pd.merge(pso_recommendation, actions, on='order-number', how='left')

# data type correction
pso_recommendation['recommended-slot-id'] = pso_recommendation['recommended-slot-id'].fillna(0)
pso_recommendation['recommended-slot-id'] = pso_recommendation['recommended-slot-id'].astype(int)

# etl
pso_recommendation['created-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
pso_recommendation['created-by'] = 'etl-automation'
pso_recommendation['updated-at'] = dt.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
pso_recommendation['updated-by'] = 'etl-automation'

# Write to csv
s3.save_df_to_s3(df=pso_recommendation[table_info['column_name']], file_name='Shubham_G/PSO_Recomm/Pso_Recomm.csv')
s3.write_df_to_db(df=pso_recommendation[table_info['column_name']], table_name=table_name, db=rs_db, schema=schema)

logger.info('PSO Recommendation Table Uploaded Successfully')

# closing the connection
rs_db.close_connection()
