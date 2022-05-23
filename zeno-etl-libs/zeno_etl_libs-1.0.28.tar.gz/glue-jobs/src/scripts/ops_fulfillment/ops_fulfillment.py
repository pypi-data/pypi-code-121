# -*- coding: utf-8 -*-
"""
Created on Thu May 5 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: auto short fulfilment percentages
"""

import os
import sys
import argparse
import pandas as pd
import datetime
import numpy as np

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB, PostGreWrite
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email


def short_book_data(rs_db=None, logger=None, cur_date=None, last_date=None, stores=None):
    # AR/MS/PR data load
    short_book_query = '''
        select
            case
                when "auto-short" = 1
                and "home-delivery" = 0
                and "patient-id" = 4480 then 'Auto Short'
                when "auto-short" = 1
                and "home-delivery" = 0
                and "patient-id" != 4480 then 'Manual Short'
                when "auto-short" = 0
                and "auto-generated" = 0
                and "home-delivery" = 0 then 'Patient Request'
                when "auto-short" = 0
                and "auto-generated" = 0
                and "home-delivery" = 1 then 'Patient Request with HD'
                else 'Invalid'
            end as request_type,
            a.id,
            a."store-id",
            s.name as store_name,
            a."ordered-distributor-id",
            f.name as distributor_name,
            a."drug-id",
            a."drug-name",
            b."type" as drug_type,
            b."category",
            c."drug-grade",
            "inventory-at-creation",
            "inventory-at-ordering",
            "quantity",
            "status",
            a."created-at" as "sb-created-at",
            a."invoiced-at",
            a."dispatched-at",
            a."received-at",
            a."completed-at",
            a."delivered-at",
            date(a."created-at") as "created-date",
            a."decline-reason"
        from
            "prod2-generico"."short-book-1" a
        left join "prod2-generico".drugs b on
            a."drug-id" = b.id
        left join "prod2-generico"."drug-order-info" c on
            a."drug-id" = c."drug-id"
            and a."store-id" = c."store-id"
        left join "prod2-generico"."stores" s on
            a."store-id" = s.id
        left join "prod2-generico"."distributors" f on
            f."id" = a."ordered-distributor-id"
        where
            (("auto-short" = 1
                and "home-delivery" = 0)
            or ("auto-short" = 0
                and "auto-generated" = 0))
            and quantity > 0
            and date(a."created-at") >=  '{last_date}'
            and date(a."created-at") <= '{cur_date}'
            and a."store-id" in {stores}
    '''.format(last_date=str(last_date), cur_date=str(cur_date), stores=stores)
    short_book = rs_db.get_df(short_book_query)
    short_book['invoiced-at'] = short_book['invoiced-at'].astype(str).replace('0101-01-01 00:00:00',
                                                                              '0000-00-00 00:00:00')
    short_book['dispatched-at'] = short_book['dispatched-at'].astype(str).replace('0101-01-01 00:00:00',
                                                                                  '0000-00-00 00:00:00')
    short_book['received-at'] = short_book['received-at'].astype(str).replace('0101-01-01 00:00:00',
                                                                              '0000-00-00 00:00:00')
    short_book['completed-at'] = short_book['completed-at'].astype(str).replace('0101-01-01 00:00:00',
                                                                                '0000-00-00 00:00:00')
    short_book['delivered-at'] = short_book['delivered-at'].astype(str).replace('0101-01-01 00:00:00',
                                                                                '0000-00-00 00:00:00')

    short_book.columns = list(map(
        lambda st: str.replace(st, '-', '_'), list(short_book.columns.values)))
    short_book['week_day'] = pd.to_datetime(short_book['sb_created_at']).dt.weekday
    short_book['ops_ff_date'] = str(cur_date)
    short_book['store_ff_date'] = str(cur_date)
    logger.info('# of rows ' + str(short_book.shape[0]))

    return short_book


def as_ms_fulfilment_calc(short_book=None, logger=None):
    '''Auto Short Calculations'''
    # filter auto short for fulfilment calculation
    as_ms = short_book[short_book['request_type'].isin(['Auto Short', 'Manual Short'])]
    # ops fulfilment calculation
    as_ms['ops_ff_days'] = -1
    # ops store days calculation
    as_ms['ops_ff_days'] = np.where(
        as_ms['invoiced_at'] == '0000-00-00 00:00:00',
        -1,
        (pd.to_datetime(
            as_ms.loc[as_ms['invoiced_at'] != '0000-00-00 00:00:00', 'invoiced_at'],
            format='%Y-%m-%d', errors='ignore').dt.date -
         pd.to_datetime(as_ms['sb_created_at']).dt.date) / np.timedelta64(1, 'D')
    )
    as_ms.loc[(as_ms['invoiced_at'] != '0000-00-00 00:00:00'), 'ops_ff_date'] = pd.to_datetime(
        as_ms.loc[(as_ms['invoiced_at'] != '0000-00-00 00:00:00'), 'invoiced_at'],
        format='%Y-%m-%d', errors='ignore').dt.date
    # correcting for order days when AS created on friday(4) and saturday (5)
    as_ms.loc[(as_ms['week_day'] == 5) &
              (as_ms['ops_ff_days'] > 0), 'ops_ff_days'] -= 1
    as_ms.loc[(as_ms['week_day'] == 4) &
              (as_ms['drug_type'].isin(['generic']) &
               (as_ms['ops_ff_days'] > 0)), 'ops_ff_days'] -= 1
    # setting ops status
    as_ms['ops_status'] = ''

    as_ms.loc[as_ms['status'].isin(['declined']), 'ops_status'] = 'Declined'
    as_ms.loc[as_ms['status'].isin(['lost', 'failed', 're-ordered']), 'ops_status'] = 'Lost'
    as_ms.loc[as_ms['ops_status'].isin(['Declined']), 'ops_ff_date'] = as_ms.loc[
        as_ms['ops_status'].isin(['Declined']), 'created_date']
    as_ms.loc[as_ms['ops_status'].isin(['Lost']), 'ops_ff_date'] = as_ms.loc[
        as_ms['ops_status'].isin(['Lost']), 'created_date']

    as_ms.loc[as_ms['status'].isin(['saved', 'ordered']), 'ops_status'] = 'Pending'

    as_ms.loc[(as_ms['status'].isin(['invoiced', 'dispatched', 'received'])) &
              (as_ms['ops_ff_days'] <= 1), 'ops_status'] = '24 hours'
    as_ms.loc[(as_ms['status'].isin(['invoiced', 'dispatched', 'received'])) &
              (as_ms['ops_ff_days'] == 2), 'ops_status'] = '48 hours'
    as_ms.loc[(as_ms['status'].isin(['invoiced', 'dispatched', 'received'])) &
              (as_ms['ops_ff_days'] == 3), 'ops_status'] = '72 hours'
    as_ms.loc[(as_ms['status'].isin(['invoiced', 'dispatched', 'received'])) &
              (as_ms['ops_ff_days'] > 3), 'ops_status'] = 'Delayed'
    as_ms.loc[as_ms['ops_status'] == '', 'ops_status'] = 'None'

    logger.info(
        '# of entries in Short book with no ops status' +
        str(as_ms[as_ms['ops_status'] == 'None'].shape[0]))

    # store fulfilment calculation
    as_ms['store_ff_days'] = -1
    # store store days calculation
    as_ms['store_ff_days'] = np.where(
        as_ms['received_at'] == '0000-00-00 00:00:00',
        -1,
        (pd.to_datetime(
            as_ms.loc[as_ms['received_at'] != '0000-00-00 00:00:00', 'received_at'],
            format='%Y-%m-%d', errors='ignore').dt.date -
         pd.to_datetime(as_ms['sb_created_at']).dt.date).fillna(pd.to_timedelta('NaT')) / np.timedelta64(1, 'D')
    )
    as_ms.loc[(as_ms['received_at'] != '0000-00-00 00:00:00'), 'store_ff_date'] = pd.to_datetime(
        as_ms.loc[(as_ms['received_at'] != '0000-00-00 00:00:00'), 'received_at'],
        format='%Y-%m-%d', errors='ignore').dt.date
    # correcting for order days when AS created on friday(4) and saturday (5)
    as_ms.loc[(as_ms['week_day'] == 5) &
              (as_ms['store_ff_days'] > 0), 'store_ff_days'] -= 1
    as_ms.loc[(as_ms['week_day'] == 4) &
              (as_ms['drug_type'].isin(['generic'])) &
              (as_ms['store_ff_days'] > 0), 'store_ff_days'] -= 1
    # setting store status
    as_ms['store_status'] = ''

    as_ms.loc[as_ms['status'].isin(['declined']), 'store_status'] = 'Declined'
    as_ms.loc[as_ms['status'].isin(['lost', 'failed', 're-ordered']), 'store_status'] = 'Lost'
    as_ms.loc[as_ms['store_status'].isin(['Declined']), 'store_ff_date'] = as_ms.loc[
        as_ms['store_status'].isin(['Declined']), 'created_date']
    as_ms.loc[as_ms['store_status'].isin(['Lost']), 'store_ff_date'] = as_ms.loc[
        as_ms['store_status'].isin(['Lost']), 'created_date']

    as_ms.loc[as_ms['status'].isin(['saved', 'ordered', 'invoiced', 'dispatched']), 'store_status'] = 'Pending'

    as_ms.loc[(as_ms['status'].isin(['received'])) &
              (as_ms['store_ff_days'] <= 1), 'store_status'] = '24 hours'
    as_ms.loc[(as_ms['status'].isin(['received'])) &
              (as_ms['store_ff_days'] == 2), 'store_status'] = '48 hours'
    as_ms.loc[(as_ms['status'].isin(['received'])) &
              (as_ms['store_ff_days'] == 3), 'store_status'] = '72 hours'
    as_ms.loc[(as_ms['status'].isin(['received'])) &
              (as_ms['store_ff_days'] > 3), 'store_status'] = 'Delayed'
    as_ms.loc[as_ms['store_status'] == '', 'store_status'] = 'None'

    logger.info('# of entries in Short book with no ops status' +
                str(as_ms[as_ms['store_status'] == 'None'].shape[0]))

    return as_ms


def pr_fulfilment_calc(short_book=None, logger=None):
    '''Patient Request Calculations'''
    # filter auto short for fulfilment calculation
    pr = short_book[~short_book['request_type'].isin(['Auto Short', 'Manual Short'])]

    # ops fulfilment calculation
    pr['ops_ff_days'] = -1
    # ops store days calculation
    pr.loc[(pr['invoiced_at'] != '0000-00-00 00:00:00'), 'ops_ff_days'] = (pd.to_datetime(
        pr.loc[(pr['invoiced_at'] != '0000-00-00 00:00:00'), 'invoiced_at'],
        format='%Y-%m-%d', errors='ignore').dt.date -
                                                                           pd.to_datetime(
                                                                               pr.loc[(pr[
                                                                                           'invoiced_at'] != '0000-00-00 00:00:00'), 'sb_created_at']
                                                                           ).dt.date) / np.timedelta64(1, 'D')
    pr.loc[(pr['invoiced_at'] != '0000-00-00 00:00:00'), 'ops_ff_date'] = pd.to_datetime(
        pr.loc[(pr['invoiced_at'] != '0000-00-00 00:00:00'), 'invoiced_at'],
        format='%Y-%m-%d', errors='ignore').dt.date

    pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'ops_ff_days'] = (pd.to_datetime(
        pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'completed_at'],
        format='%Y-%m-%d', errors='ignore').dt.date -
                                                                            pd.to_datetime(
                                                                                pr.loc[(pr[
                                                                                            'completed_at'] != '0000-00-00 00:00:00'), 'sb_created_at']
                                                                            ).dt.date) / np.timedelta64(1, 'D')
    pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'ops_ff_date'] = pd.to_datetime(
        pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'completed_at'],
        format='%Y-%m-%d', errors='ignore').dt.date

    # correcting for order days when AS created on friday(4) and saturday (5)
    pr.loc[(pr['week_day'] == 5) &
           (pr['ops_ff_days'] > 0), 'ops_ff_days'] -= 1
    pr.loc[(pr['week_day'] == 4) &
           (pr['drug_type'].isin(['generic']) &
            (pr['ops_ff_days'] > 0)), 'ops_ff_days'] -= 1
    # setting ops status
    pr['ops_status'] = ''

    pr.loc[pr['status'].isin(['declined']), 'ops_status'] = 'Declined'
    pr.loc[pr['status'].isin(['lost', 'failed', 're-ordered']), 'ops_status'] = 'Lost'
    pr.loc[pr['ops_status'].isin(['Declined']), 'ops_ff_date'] = pr.loc[
        pr['ops_status'].isin(['Declined']), 'created_date']
    pr.loc[pr['ops_status'].isin(['Lost']), 'ops_ff_date'] = pr.loc[pr['ops_status'].isin(['Lost']), 'created_date']

    pr.loc[pr['status'].isin(['saved', 'ordered']), 'ops_status'] = 'Pending'

    pr.loc[(pr['status'].isin(['invoiced', 'dispatched', 'received', 'completed'])) &
           (pr['ops_ff_days'] <= 1), 'ops_status'] = '24 hours'
    pr.loc[(pr['status'].isin(['invoiced', 'dispatched', 'received', 'completed'])) &
           (pr['ops_ff_days'] == 2), 'ops_status'] = '48 hours'
    pr.loc[(pr['status'].isin(['invoiced', 'dispatched', 'received', 'completed'])) &
           (pr['ops_ff_days'] == 3), 'ops_status'] = '72 hours'
    pr.loc[(pr['status'].isin(['invoiced', 'dispatched', 'received', 'completed'])) &
           (pr['ops_ff_days'] > 3), 'ops_status'] = 'Delayed'
    pr.loc[pr['ops_status'] == '', 'ops_status'] = 'None'

    logger.info(
        '# of entries in Short book with no ops status' +
        str(pr[pr['ops_status'] == 'None'].shape[0]))

    # store fulfilment calculation
    pr['store_ff_days'] = -1
    # store store days calculation
    pr.loc[(pr['received_at'] != '0000-00-00 00:00:00'), 'store_ff_days'] = (pd.to_datetime(
        pr.loc[(pr['received_at'] != '0000-00-00 00:00:00'), 'received_at'],
        format='%Y-%m-%d', errors='ignore').dt.date -
                                                                             pd.to_datetime(
                                                                                 pr.loc[(pr[
                                                                                             'received_at'] != '0000-00-00 00:00:00'), 'sb_created_at']
                                                                             ).dt.date) / np.timedelta64(1, 'D')
    pr.loc[(pr['received_at'] != '0000-00-00 00:00:00'), 'store_ff_date'] = pd.to_datetime(
        pr.loc[(pr['received_at'] != '0000-00-00 00:00:00'), 'received_at'],
        format='%Y-%m-%d', errors='ignore').dt.date

    pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'store_ff_days'] = (pd.to_datetime(
        pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'completed_at'],
        format='%Y-%m-%d', errors='ignore').dt.date -
                                                                              pd.to_datetime(
                                                                                  pr.loc[(pr[
                                                                                              'completed_at'] != '0000-00-00 00:00:00'), 'sb_created_at']
                                                                              ).dt.date) / np.timedelta64(1, 'D')
    pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'store_ff_date'] = pd.to_datetime(
        pr.loc[(pr['completed_at'] != '0000-00-00 00:00:00'), 'completed_at'],
        format='%Y-%m-%d', errors='ignore').dt.date

    # correcting for order days when AS created on friday(4) and saturday (5)
    pr.loc[(pr['week_day'] == 5) &
           (pr['store_ff_days'] > 0), 'store_ff_days'] -= 1
    pr.loc[(pr['week_day'] == 4) &
           (pr['drug_type'].isin(['generic'])) &
           (pr['store_ff_days'] > 0), 'store_ff_days'] -= 1
    # setting store status
    pr['store_status'] = ''

    pr.loc[pr['status'].isin(['declined']), 'store_status'] = 'Declined'
    pr.loc[pr['status'].isin(['lost', 'failed', 're-ordered']), 'store_status'] = 'Lost'
    pr.loc[pr['ops_status'].isin(['Declined']), 'store_ff_date'] = pr.loc[
        pr['store_status'].isin(['Declined']), 'created_date']
    pr.loc[pr['ops_status'].isin(['Lost']), 'store_ff_date'] = pr.loc[pr['store_status'].isin(['Lost']), 'created_date']

    pr.loc[pr['status'].isin(['saved', 'ordered', 'invoiced', 'dispatched']) &
           (pr['request_type'] == 'Patient Request'), 'store_status'] = 'Pending'
    pr.loc[pr['status'].isin(['saved', 'ordered', 'invoiced', 'dispatched', 'received']) &
           (pr['request_type'] == 'Patient Request with HD'), 'store_status'] = 'Pending'

    pr.loc[(pr['status'].isin(['received', 'completed'])) &
           (pr['store_ff_days'] <= 1) &
           (pr['request_type'] == 'Patient Request'), 'store_status'] = '24 hours'
    pr.loc[(pr['status'].isin(['received', 'completed'])) &
           (pr['store_ff_days'] == 2) &
           (pr['request_type'] == 'Patient Request'), 'store_status'] = '48 hours'
    pr.loc[(pr['status'].isin(['received', 'completed'])) &
           (pr['store_ff_days'] == 3) &
           (pr['request_type'] == 'Patient Request'), 'store_status'] = '72 hours'
    pr.loc[(pr['status'].isin(['received', 'completed'])) &
           (pr['store_ff_days'] > 3) &
           (pr['request_type'] == 'Patient Request'), 'store_status'] = 'Delayed'

    pr.loc[(pr['status'].isin(['completed'])) &
           (pr['store_ff_days'] <= 1) &
           (pr['request_type'] == 'Patient Request with HD'), 'store_status'] = '24 hours'
    pr.loc[(pr['status'].isin(['completed'])) &
           (pr['store_ff_days'] == 2) &
           (pr['request_type'] == 'Patient Request with HD'), 'store_status'] = '48 hours'
    pr.loc[(pr['status'].isin(['completed'])) &
           (pr['store_ff_days'] == 3) &
           (pr['request_type'] == 'Patient Request with HD'), 'store_status'] = '72 hours'
    pr.loc[(pr['status'].isin(['completed'])) &
           (pr['store_ff_days'] > 3) &
           (pr['request_type'] == 'Patient Request with HD'), 'store_status'] = 'Delayed'

    pr.loc[pr['store_status'] == '', 'store_status'] = 'None'

    logger.info('# of entries in Short book with no ops status' +
                str(pr[pr['store_status'] == 'None'].shape[0]))

    return pr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="auto short fulfilment percentages.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.sidagam@zeno.health", type=str,
                        required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to

    logger = get_logger()
    logger.info("Scripts begins")

    status = False
    err_msg = ''

    # getting dates for refreshing the fulfilment percentages
    cur_date = datetime.datetime.now().date()
    last_date = cur_date - datetime.timedelta(days=8)

    # running as fulfilment func
    logger.info('Latest date to pull' + str(cur_date))
    logger.info('Last date to pull' + str(last_date))

    try:
        rs_db = DB()
        rs_db.open_connection()
        # getting store list
        store_list_query = '''
            select
                distinct "store-id"
            from
                "prod2-generico"."short-book-1"
            where
                (("auto-short" = 1
                    and "home-delivery" = 0)
                or ("auto-short" = 0
                    and "auto-generated" = 0))
                and quantity > 0
                and date("created-at") >= '{last_date}'
                and date("created-at") <= '{cur_date}'
        '''.format(last_date=last_date, cur_date=cur_date)
        stores = rs_db.get_df(store_list_query)
        stores = str(stores['store-id'].to_list()).replace('[', '(').replace(']', ')')
        fptr_query = '''
            select
                "drug-id",
                avg("final-ptr") as fptr
            from
                "prod2-generico"."inventory-1" i2
            group by
                "drug-id"
        '''
        fptr = rs_db.get_df(fptr_query)
        fptr.columns = list(map(
            lambda st: str.replace(st, '-', '_'), list(fptr.columns)))

        rs_db.execute(""" delete from "prod2-generico"."ops-fulfillment" """)

        as_ms_fulfilment_all = pd.DataFrame()
        pr_fulfilment_all = pd.DataFrame()

        logger.info('getting data for store: ' + str(stores))
        # getting short book info for last 8 days
        short_book = short_book_data(
            rs_db=rs_db, logger=logger, cur_date=cur_date,
            last_date=last_date, stores=stores)
        '''Auto short Manual short calculation'''
        as_ms_fulfilment = as_ms_fulfilment_calc(
            short_book=short_book, logger=logger)
        as_ms_fulfilment = as_ms_fulfilment.merge(fptr, on='drug_id', how='left')
        logger.info('AS/MS size ' + str(as_ms_fulfilment.shape[0]))
        as_ms_fulfilment_all = as_ms_fulfilment_all.append(as_ms_fulfilment)

        '''Patient request calculation'''
        pr_fulfilment = pr_fulfilment_calc(
            short_book=short_book, logger=logger)
        pr_fulfilment = pr_fulfilment.merge(fptr, on='drug_id', how='left')
        logger.info('PR size ' + str(pr_fulfilment.shape[0]))
        pr_fulfilment_all = pr_fulfilment_all.append(pr_fulfilment)

        fdf = pd.concat([as_ms_fulfilment_all, pr_fulfilment_all], ignore_index=True)
        fdf['created-at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fdf['created-by'] = 'etl-automation'
        fdf['updated-at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fdf['updated-by'] = 'etl-automation'

        fdf.columns = [c.replace('_', '-') for c in fdf.columns]
        fdf = fdf[['request-type', 'id', 'store-id', 'store-name',
                   'ordered-distributor-id', 'distributor-name', 'drug-id', 'drug-name',
                   'drug-type', 'category', 'drug-grade', 'inventory-at-creation',
                   'inventory-at-ordering', 'quantity', 'fptr', 'status', 'sb-created-at',
                   'invoiced-at', 'dispatched-at', 'received-at', 'completed-at',
                   'delivered-at', 'created-date', 'decline-reason', 'ops-ff-days',
                   'store-ff-days', 'week-day', 'ops-status', 'ops-ff-date',
                   'store-status', 'store-ff-date', 'created-at', 'created-by',
                   'updated-at', 'updated-by']]
        s3 = S3()
        logger.info("writing to rs")
        s3.write_df_to_db(df=fdf, table_name='ops-fulfillment', db=rs_db,
                          schema='prod2-generico')
        logger.info("written to rs")
        rs_db.close_connection()
        pg_write = PostGreWrite()
        pg_write.open_connection()
        logger.info("writing to postgres")
        pg_write.engine.execute(""" delete from ops_fulfillment """)
        fdf = pd.concat([as_ms_fulfilment_all, pr_fulfilment_all], ignore_index=True)
        fdf.columns = [c.replace('_', '-') for c in fdf.columns]
        fdf = fdf[['request-type', 'id', 'store-id', 'store-name',
                   'ordered-distributor-id', 'distributor-name', 'drug-id', 'drug-name',
                   'drug-type', 'category', 'drug-grade', 'inventory-at-creation',
                   'inventory-at-ordering', 'quantity', 'fptr', 'status', 'sb-created-at',
                   'invoiced-at', 'dispatched-at', 'received-at', 'completed-at',
                   'delivered-at', 'created-date', 'decline-reason', 'ops-ff-days',
                   'store-ff-days', 'week-day', 'ops-status', 'ops-ff-date',
                   'store-status', 'store-ff-date']]
        fdf.columns = [c.replace('-', '_') for c in fdf.columns]
        fdf.rename(columns={'sb_created_at': 'created_at'}, inplace=True)
        fdf['fptr'] = fdf['fptr'].astype(float)
        fdf['ops_ff_date'] = pd.to_datetime(fdf['ops_ff_date'])
        fdf['store_ff_date'] = pd.to_datetime(fdf['store_ff_date'])
        fdf.to_sql(
            name='ops_fulfillment', con=pg_write.engine, if_exists='append',
            chunksize=500, method='multi', index=False)
        logger.info("written to postgres")
        status = True

    except Exception as error:
        logger.info("exception incurred")
        err_msg = str(error)
        logger.info(str(error))

    # Sending email
    logger.info("sending email")
    email = Email()
    if status:
        result = 'Success'
        email.send_email_file(subject=f"ops_fulfillment ({env}): {result}",
                              mail_body=f"Run time: {datetime.datetime.now()} {err_msg}",
                              to_emails=email_to, file_uris=[])
    else:
        result = 'Failed'
        email.send_email_file(subject=f"ops_fulfillment ({env}): {result}",
                              mail_body=f"{err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")

# DDL for table
"""
CREATE TABLE "prod2-generico"."ops-fulfillment" (
	"request-type" varchar(255) NULL,
	"short-book-id" int8 NULL,
	"store-id" int8 NULL,
	"store-name" varchar(255) NULL,
	"ordered-distributor-id" float8 NULL,
	"distributor-name" text NULL,
	"drug-id" float8 NULL,
	"drug-name" text NULL,
	"drug-type" text NULL,
	category text NULL,
	"drug-grade" text NULL,
	"inventory-at-creation" int8 NULL,
	"inventory-at-ordering" int8 NULL,
	quantity int8 NULL,
	fptr float8 NULL,
	status text NULL,
	"sb-created-at" timestamp NULL,
	"invoiced-at" text NULL,
	"dispatched-at" text NULL,
	"received-at" text NULL,
	"completed-at" text NULL,
	"delivered-at" text NULL,
	"created-date" date NULL,
	"decline-reason" text NULL,
	"ops-ff-days" float8 NULL,
	"store-ff-days" float8 NULL,
	"week-day" int8 NULL,
	"ops-status" text NULL,
	"ops-ff-date" date NULL,
	"store-status" text NULL,
	"store-ff-date" date NULL,
	"created-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"created-by" VARCHAR default 'etl-automation' ENCODE lzo,
	"updated-at" TIMESTAMP without TIME zone default getdate() ENCODE az64,
	"updated-by" VARCHAR default 'etl-automation' ENCODE lzo 
);

ALTER TABLE "prod2-generico"."ops-fulfillment" owner to "admin";
"""
