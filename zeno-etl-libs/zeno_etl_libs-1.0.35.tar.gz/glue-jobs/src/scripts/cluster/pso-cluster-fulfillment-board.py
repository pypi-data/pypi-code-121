#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.config.common import Config
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper import helper
from dateutil.tz import gettz

import json
from datetime import datetime, timedelta

import argparse
import pandas as pd
import numpy as np
import traceback

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str, required=False)
parser.add_argument('-rn', '--refresh_for_n_days', default="10", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
email_to = args.email_to
refresh_for_n_days = args.refresh_for_n_days

os.environ['env'] = env

logger = get_logger(level = 'INFO')

logger.info(f"env: {env}")

#secrets = config.secrets

rs_db = DB()

rs_db.open_connection()

rs_db_write = DB(read_only=False)
rs_db_write.open_connection()

s3 = S3()
start_time = datetime.now()
logger.info('Script Manager Initialized')
logger.info(f"env: {env}")
logger.info("email_to - " + email_to)
logger.info("refresh_for_n_days - " + str(refresh_for_n_days))

logger.info("")

# date parameter
logger.info("code started at {}".format(datetime.now().strftime(
    '%Y-%m-%d %H:%M:%S')))
logger.info("")

# =============================================================================
# set parameters
# =============================================================================

#pso_date1 = "2022-01-07 00:00:00"  # launch date of 3 hour delivery # Use this when you want to refresh whole table
pso_date1 = (datetime.now(tz=gettz('Asia/Kolkata')) - timedelta(days=int(refresh_for_n_days))).strftime('%Y-%m-%d %H:%M:%S') # Use this when only to update for only 7 days
pso_date2 = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# =============================================================================
# store clusters
# =============================================================================

qc = """
    select
            sf."feature-id",
            f.feature,
            sf."store-id",
            sf."is-active",
            sc."cluster-id",
        c.name as "cluster-name",
        sc."is-active" as "sc-is-active"
    from
            "prod2-generico".features f
    join "prod2-generico"."store-features" sf on
            f.id = sf."feature-id"
    join "prod2-generico"."store-clusters" sc on
            sc."store-id" = sf."store-id"
    join "prod2-generico".clusters c on
            c.id = sc."cluster-id"
    where
            sf."feature-id" = 69
        and sf."is-active" = 1
        and sc."is-active" = 1
        """

store_clusters = rs_db.get_df(qc)

orders_transfers_all = pd.DataFrame()

for cluster in store_clusters['cluster-id'].unique():
    logger.info("")
    logger.info("cluster {}".format(cluster))

    temp = store_clusters[store_clusters['cluster-id'] == cluster]

    cluster_stores = tuple(map(int, list(temp['store-id'].unique())))

    # =============================================================================
    # GET PRs
    # =============================================================================

    q1 = """
        select
            pso."order-number",
            pso.id as "patient-store-order-id",
            pso."patient-request-id",
            pso."zeno-order-id" ,
            pso."patient-id" ,
            pso."order-source" ,
            pso."order-type" ,
            pso."status" as "pso-status",
            pso."created-at" as "pso-created-at", 
            pso."store-id" ,
            s."name" as "store-name",
            pso."drug-id" ,
            pso."drug-name" ,
            pso."requested-quantity", 
            pso."inventory-quantity" as "inventory-at-creation", 
            pr."required-quantity", 
            pr."quantity-to-order", 
            pso."bill-id",
            b."created-at" as "bill-date", 
            dt."delivered-at",
            ss."type" as "slot-type",
            pso."slot-date" ,
            ss."start-time" as "slot-start-time",
            ss."end-time" as "slot-end-time"
        from
            "prod2-generico"."patients-store-orders" pso
        left join "prod2-generico"."patient-requests" pr on
            pso."patient-request-id" = pr.id
        join "prod2-generico"."stores" s on
            s."id" = pso."store-id"
        left join "prod2-generico"."bills-1" b on
            b."id" = pso."bill-id"
        left join "prod2-generico"."delivery-tracking" dt on
            dt."patient-store-order-id" = pso."id"
        left join "prod2-generico"."store-slots" ss on
            pso."slot-id" = ss.id
        where
            pso."created-at" >= '{pso_date1}'
            and pso."created-at" <= '{pso_date2}'
            and pso."store-id" in {cluster_stores}
        order by
            pso."created-at" desc;
                """.format(pso_date1=pso_date1, pso_date2=pso_date2, cluster_stores=cluster_stores)

    orders = rs_db.get_df(q1)

    orders['required-quantity'].fillna(0, inplace=True)
    orders['quantity-to-order'].fillna(0, inplace=True)

    orders['availability-tag'] = np.where(
        orders['quantity-to-order'] > 0, "pr-short", np.nan)

    orders['availability-tag'] = orders.fillna('').sort_values(
        ['order-number',
         'availability-tag']).groupby('order-number')['availability-tag'].transform('last')

    orders['availability-tag'] = np.where(
        orders['availability-tag'] != 'pr-short',
        "pr-not-short", orders['availability-tag'])

    # =============================================================================
    # Get transfers
    # =============================================================================
    trnfrs = tuple(map(int, list(orders['patient-store-order-id'].unique())))

    q2 = """
        select
            pso."order-number",
            pstm."patient-store-order-id",
            pstm."from-store-id",
            pstm."to-store-id",
            pstm."item-quantity" as "to-be-transferred-qty",
            sti."quantity" as "actual-transferred-qty",
            st."total-items",
            pstm."status" as "tn-status",
            st."status" as "transfer-status",
            st."initiated-at",
            st."transferred-at",
            st."received-at",
            DATEDIFF(min,st."transferred-at",st."received-at") as "transfer-minutes",
            zo."created-at" as "zeno-created-at"
        from
            "prod2-generico"."pso-stock-transfer-mapping" pstm
        left join "prod2-generico"."patients-store-orders" pso on
            pso.id = pstm."patient-store-order-id"
        left join "prod2-generico"."stock-transfers-1" st on
            st.id = pstm."stock-transfer-id"
        left join "prod2-generico"."stock-transfer-items-1" sti on
            sti.id = pstm."stock-transfer-item-id"
        left join "prod2-generico"."zeno-order" zo on
            zo.id = pso."zeno-order-id"
        where
            pstm."patient-store-order-id" in {}
            """.format(trnfrs)

    transfers = rs_db.get_df(q2)

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
    transfers_summ.columns = ["-".join(x) for x in transfers_summ.columns.ravel()]
    transfers_summ.rename(columns={'initiated-at-amax': 'initiated-at',
                                   'transferred-at-amax': 'transferred-at',
                                   'received-at-amax': 'received-at',
                                   'to-be-transferred-qty-sum': 'to-be-transferred-qty',
                                   'actual-transferred-qty-sum': 'actual-transferred-qty',
                                   'transfer-status-': 'transfer-status',
                                   'order-number-': 'order-number',
                                   'patient-store-order-id-': 'patient-store-order-id',
                                   'zeno-created-at-amax': 'zeno-created-at'},
                          inplace=True)

    orders_transfers = pd.merge(left=orders, right=transfers_summ,
                                how='left', on=['order-number',
                                                'patient-store-order-id'])

    orders_transfers['to-be-transferred-qty'].fillna(0, inplace=True)
    orders_transfers['actual-transferred-qty'].fillna(0, inplace=True)

    orders_transfers['zeno-created-at'] = pd.to_datetime(orders_transfers['zeno-created-at'])

    # lead to pso creation
    orders_transfers['lead-to-pso-creation-hours'] = (
                (orders_transfers['pso-created-at'] - orders_transfers['zeno-created-at'])
                / np.timedelta64(1, 'h'))

    # PSO to transfer intitate
    orders_transfers['pso-to-transfer-initiate-hours'] = (
                (orders_transfers['initiated-at'] - orders_transfers['pso-created-at'])
                / np.timedelta64(1, 'h'))

    # PSO to transfer transferred
    orders_transfers['pso-to-transfer-transfer-hours'] = (
                (orders_transfers['transferred-at'] - orders_transfers['pso-created-at'])
                / np.timedelta64(1, 'h'))

    # PSO to transfer recevied
    orders_transfers['pso-to-transfer-received-hours'] = (
                (orders_transfers['received-at'] - orders_transfers['pso-created-at'])
                / np.timedelta64(1, 'h'))

    # PSO to bill
    orders_transfers['pso-to-bill-hours'] = ((orders_transfers['bill-date'] - orders_transfers['pso-created-at'])
                                             / np.timedelta64(1, 'h'))

    orders_transfers['pso-to-bill-hours'] = np.where(
        orders_transfers['pso-to-bill-hours'] < 0, 0, orders_transfers['pso-to-bill-hours'])

    # PSO to delivered
    orders_transfers['pso-to-delivered-hours'] = (
                (orders_transfers['delivered-at'] - orders_transfers['pso-created-at'])
                / np.timedelta64(1, 'h'))

    orders_transfers['cluster-id'] = cluster

    # =============================================================================
    # Cluster Name
    # =============================================================================
    qc1 = """
        select
            c.id AS "cluster-id" ,
            c.name AS "cluster-name"
        from
            "prod2-generico".clusters c
    """

    cluster_info = rs_db.get_df(qc1)

    orders_transfers = pd.merge(orders_transfers, cluster_info, on='cluster-id', how='left')

    # =============================================================================
    # OTIF calculation -- In Full Flag
    # =============================================================================
    bills = tuple(map(int, list(orders_transfers[orders_transfers['bill-id'].notna()]['bill-id'].unique())))

    qc2 = """
        select
            bi."bill-id",
            count(distinct i."drug-id") as "drug-billed-cnt",
            sum(bi.quantity) as "quantity-billed-sum"
        from
            "prod2-generico"."bills-1" b
        join "prod2-generico"."bill-items-1" bi on
            b.id = bi."bill-id"
        join "prod2-generico"."inventory-1" i on
            i.id = bi."inventory-id"
        where
            bi."bill-id" in {}
        group by
            bi."bill-id"
            """.format(bills)

    billed = rs_db.get_df(qc2)

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

    orders_transfers_q_infull1.columns = ["-".join(x) for x in orders_transfers_q_infull1.columns.ravel()]
    orders_transfers_q_infull1.rename(columns={'requested-quantity-ordered-sum-sum': 'requested-quantity-ordered-sum',
                                               'order-number-': 'order-number'},
                                      inplace=True)

    orders_transfers_infull1 = pd.merge(orders_transfers_d_infull1, orders_transfers_q_infull1,
                                        on='order-number', how='inner')

    orders_transfers2 = pd.merge(left=orders_transfers1,
                                 right=orders_transfers_infull1,
                                 how='left', on=['order-number'])

    orders_transfers2['in-full-flag'] = np.where(
        orders_transfers2['drug-billed-cnt'] >= orders_transfers2['drug-ordered-cnt'],
        "in-full", "not-in-full")

    orders_transfers2['qty-in-full-flag'] = np.where(
        orders_transfers2['quantity-billed-sum'] >= orders_transfers2['requested-quantity-ordered-sum'],
        "qty-in-full", "qty-not-in-full")

    orders_transfers2['drug-billed-cnt'].fillna(0, inplace=True)
    orders_transfers2['quantity-billed-sum'].fillna(0, inplace=True)
    orders_transfers2['drug-ordered-cnt'].fillna(0, inplace=True)
    orders_transfers2['requested-quantity-ordered-sum'].fillna(0, inplace=True)

    # del orders_transfers2['drug_ordered_cnt']
    # del orders_transfers2['drug_billed_cnt']
    # del orders_transfers2['quantity_billed_sum']
    # del orders_transfers2['requested_quantity_ordered_sum']

    # =============================================================================
    # OTIF calculation -- on_time_flag
    # =============================================================================

    def string_to_time(x):
        try:
            return datetime.strptime(x, "%I:%M %p").time()
        except:
            try:
                return datetime.strptime(x, "%I:%M%p").time()
            except:
                return "Can't convert"

    orders_transfers2['slot-end-time-format'] = orders_transfers2['slot-end-time'].apply(lambda x: string_to_time(x))

    orders_transfers2['slot-end-date-time'] = orders_transfers2.apply(lambda x:
                                                                  datetime.combine(x['slot-date'],
                                                                             x['slot-end-time-format']), 1)

    conditions = [
        (orders_transfers2['order-type']== 'delivery') & (orders_transfers2['delivered-at'] <= orders_transfers2['slot-end-date-time']),
        (orders_transfers2['order-type'] != 'delivery') & (orders_transfers2['bill-date'] <= orders_transfers2['slot-end-date-time']),
        (orders_transfers2['delivered-at'] > orders_transfers2['slot-end-date-time'])
    ]
    choices = ['on-time','on-time','not-on-time']
    orders_transfers2['on-time-slot-basis-flag'] = np.select(conditions, choices, default='not-on-time')

    orders_transfers2['otif-flag'] = np.where(
        ((orders_transfers2['in-full-flag'] == 'in-full') &
         (orders_transfers2['on-time-slot-basis-flag'] == 'on-time')),
        "otif", "not-otif")

    orders_transfers2['qty-otif-flag'] = np.where(
        ((orders_transfers2['qty-in-full-flag'] == 'qty-in-full') &
         (orders_transfers2['on-time-slot-basis-flag'] == 'on-time')),
        "qty-otif", "qty-not-otif")

    logger.info("")
    logger.info(
        "length is same {}".format(len(orders) == len(orders_transfers2)))
    logger.info("")

    orders_transfers_all = orders_transfers_all.append(orders_transfers2)

pso_cluster_fulfillment_board = orders_transfers_all

# pso_cluster_fulfillment_board.to_csv(r"D:\3 hours delivery\ClusterFulfillment\Quantity_OTIF\data1.csv")

pso_cluster_fulfillment_board['updated-at'] = datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# Converting int column with null value to int data type
pso_cluster_fulfillment_board[['patient-request-id', 'zeno-order-id', 'drug-id','required-quantity', 'quantity-to-order', 'bill-id', 'to-be-transferred-qty', 'actual-transferred-qty', 'drug-billed-cnt', 'quantity-billed-sum']] = pso_cluster_fulfillment_board[['patient-request-id', 'zeno-order-id', 'drug-id','required-quantity', 'quantity-to-order', 'bill-id', 'to-be-transferred-qty', 'actual-transferred-qty', 'drug-billed-cnt', 'quantity-billed-sum']].apply(pd.to_numeric, errors='ignore').astype('Int64')

# =============================================================================
# writing to Redshift
# =============================================================================
schema = 'prod2-generico'
table_name = 'pso-cluster-fulfillment-board-temp'
table_name2 = 'pso-cluster-fulfillment-board'
table_info = helper.get_table_info(db=rs_db_write, table_name=table_name, schema=schema)
table_info2 = helper.get_table_info(db=rs_db_write, table_name=table_name2, schema=schema)
status2 = False
status1 = False

if isinstance(table_info, type(None)):
    raise Exception(f"table: {table_name} do not exist, create the table first")
else:
    logger.info(f"Table:{table_name} exists")

    truncate_query = f''' delete
                        from "{schema}"."{table_name}" '''
    rs_db_write.execute(truncate_query)
    logger.info(str(table_name) + ' table deleted')

    s3.write_df_to_db(df=pso_cluster_fulfillment_board[table_info['column_name']], table_name=table_name, db=rs_db_write,
                      schema=schema)

    logger.info(str(table_name) + ' table uploaded')
    status2 = True

if status2:
    if isinstance(table_info2, type(None)):
        raise Exception(f"table: {table_name2} do not exist, create the table first")
    else:
        logger.info(f"Table:{table_name2} exists")

        delete_main_query = f''' 
                            delete
                            from
                                "{schema}"."{table_name2}" 
                            where
                                "{schema}"."{table_name2}"."pso-created-at" >= '{pso_date1}' '''
        rs_db_write.execute(delete_main_query)

        logger.info(str(table_name2) + ' table deleted')

        insert_main_query = f''' 
                            insert
                                into
                                "{schema}"."{table_name2}" 
                            select
                                *
                            from
                                "{schema}"."{table_name}" 
                            '''
        rs_db_write.execute(insert_main_query)
        status1 = True

        logger.info(str(table_name2) + ' table uploaded')

if status1 is True:
    status = 'Success'
else:
    status = 'Failed'

#logger.close()
end_time = datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds()/60 , 2)
email = Email()

email.send_email_file(subject=f"{env}-{status} : {table_name2} table updated",
                      mail_body=f"{table_name2} table updated, Time for job completion - {min_to_complete} mins ",
                      to_emails=email_to, file_uris=[])

rs_db.close_connection()
rs_db_write.close_connection()
