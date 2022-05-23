# -*- coding: utf-8 -*-
"""
Created on Wed May 4 11:52:28 2022

@author: vivek.sidagam@zeno.health

Purpose: To generate distributor level forecast at warehouse for the next month
"""

import os
import sys
import argparse

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from calendar import monthrange

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger, send_logs_via_email
from zeno_etl_libs.helper.email.email import Email

from zeno_etl_libs.utils.warehouse.data_prep.wh_data_prep \
    import get_launch_stock_per_store

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="To generate distributor level forecast at warehouse for the next month.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to', default="vivek.sidagam@zeno.health",
                        type=str, required=False)
    parser.add_argument('-nso', '--nso_history_days', default=90, type=int,
                        required=False)

    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    nso_history_days = args.nso_history_days

    logger = get_logger()
    logger.info("Script begins")

    status = False
    err_msg = ''
    df_uri = ''
    run_date = str(datetime.now().date())
    current_month_date = (
            datetime.now().date() -
            timedelta(days=datetime.now().day - 1))
    next_month_date = datetime(current_month_date.year + \
                               int(current_month_date.month / 12), \
                               ((current_month_date.month % 12) + 1), 1).date()
    num_days = monthrange(next_month_date.year, next_month_date.month)[1]

    try:
        df = pd.DataFrame()
        rs_db = DB()
        rs_db.open_connection()
        q1 = """
            select
                b.Barcode as drug_id,
                sum(case when Vno < 0 then 0 else coalesce(a.bqty, 0) end) as balance_quantity,
                sum(case when Vno > 0 then 0 else coalesce(a.Tqty, 0) end) as locked_quantity
            from
                "prod2-generico".fifo a
            right join "prod2-generico".item b on
                a.itemc = b.code
            where
                b.code > 0
                and b.Barcode !~ '[^0-9]'
                and a.Psrlno in (
                select
                    Psrlno
                from
                    "prod2-generico".SalePurchase2 sp
                where
                    Vtype = 'PB')
                and a.TQty > 0
            group by
                b.Barcode,
                b.name
            """
        wh_inventory = rs_db.get_df(q1)
        logger.info("data pulled from RS")
        wh_inventory['drug_id'] = pd.to_numeric(wh_inventory['drug_id'])
        wh_inventory = wh_inventory.astype(int, errors='ignore')
        wh_inventory['total_quantity'] = wh_inventory['balance_quantity'] + wh_inventory['locked_quantity']

        # get wh portfolio
        drugs_list = rs_db.get_df(
            '''
            select
                wssm."drug-id" as drug_id,
                d."drug-name" as drug_name,
                f.fcst,
                f.ss,
                f.rop,
                f.oup
            from
                "prod2-generico"."wh-sku-subs-master" wssm
            left join (
                select
                    "drug-id",
                    fcst,
                    "safety-stock" as ss,
                    "reorder-point" as rop,
                    "order-upto-point" as oup
                from
                    "prod2-generico"."wh-safety-stock" wss
                where
                    "forecast-date" = (
                    select
                        max("forecast-date")
                    from
                        "prod2-generico"."wh-safety-stock")) f on
                f."drug-id" = wssm."drug-id"
            left join "prod2-generico".drugs d on
                d.id = wssm."drug-id"
            where
                wssm."add-wh" = 'Yes'
                and d."type" <> 'discontinued-products'
                and d.company <> 'GOODAID'
            ''')
        drugs_list.fillna(0, inplace=True)
        drugs_list = drugs_list.astype(int, errors='ignore')
        # getting params
        logger.info('reading input file to get expected_nso')
        params_table_raw = """
            select
                "month-begin-dt" as month_begin_Dt,
                value as expected_nso
            from
                "prod2-generico"."wh-forecast-repln-input"
            where
                "param-name" = 'expected_nso'
        """
        params_table = rs_db.get_df(params_table_raw)
        params_table = params_table.apply(pd.to_numeric, errors='ignore')
        try:
            expected_nso = int(params_table[
                                   params_table['month_begin_date'] == str(next_month_date)]['expected_nso'])
        except Exception as error:
            expected_nso = 0

        logger.info('expected_nso parameter read --> ' + str(expected_nso))
        logger.info('nso_history_days --> ' + str(nso_history_days))

        # getting launch stock per store
        launch_stock_per_store = get_launch_stock_per_store(rs_db, nso_history_days)
        logger.info('launch stock per store pulled')
        drugs_list = drugs_list.merge(launch_stock_per_store, on='drug_id', how='left')
        drugs_list['launch_stock_per_store'].fillna(0, inplace=True)
        drugs_list['fcst'] += drugs_list['launch_stock_per_store'] * expected_nso
        drugs_list['fcst'] = drugs_list['fcst'].round().astype(int)
        del drugs_list['launch_stock_per_store']

        df = drugs_list.copy()
        df = df.merge(wh_inventory, on='drug_id', how='left')
        df['below_rop'] = np.where(df['total_quantity'] <= df['rop'], True, False)
        df.loc[df['below_rop'] == False, 'purchase_quantity'] = np.ceil(
            (df['fcst'] - (df['total_quantity'] - df['rop'])) / (
                    df['oup'] - df['rop']) + 1) * (df['oup'] - df['rop'])
        df.loc[df['below_rop'] == True, 'purchase_quantity'] = np.ceil(
            df['oup'] - (df['total_quantity'] - 4 * df['fcst'] / num_days)) + (
                                                                       df['oup'] - df['rop']) * np.ceil(
            (df['fcst'] - np.ceil(df['oup'] - (
                    df['total_quantity'] - 4 * df['fcst'] / num_days))) / (
                    df['oup'] - df['rop']) + 1)
        df['purchase_quantity'].fillna(0, inplace=True)
        df.loc[df['purchase_quantity'] <= 0, 'purchase_quantity'] = 0
        del df['below_rop']

        s3 = S3()
        df_uri = s3.save_df_to_s3(df=df, file_name='wh_dist_pur_fcst_{date}.csv'.format(date=str(next_month_date)))

        status = True

    except Exception as error:
        err_msg = str(error)
        logger.exception(str(error))

    # Sending email
    email = Email()
    if status:
        result = 'Success'
        email.send_email_file(subject='''Warehouse distributor M+1 purchase forecast for {date} ({env}): {result} 
        '''.format(date=str(next_month_date), env=env, result=result),
                              mail_body=f"Run time: {datetime.now()} {err_msg}",
                              to_emails=email_to, file_uris=[df_uri])
    else:
        result = 'Failed'
        email.send_email_file(subject='''Warehouse distributor M+1 purchase forecast for {date} ({env}): {result} 
        '''.format(date=str(next_month_date), env=env, result=result),
                              mail_body=f"Run time: {datetime.now()} {err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")
