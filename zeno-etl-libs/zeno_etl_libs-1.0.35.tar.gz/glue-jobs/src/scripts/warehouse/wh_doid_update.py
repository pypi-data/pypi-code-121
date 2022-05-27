# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:45:59 2022

@author: vivek.sidagam@zeno.health

@Purpose: To update DOID with latest forecast
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta

sys.path.append('../../../..')

from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.utils.ipc.doid_update_ss import doid_update

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="To update DOID with latest forecast.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="vivek.sidagam@zeno.health", type=str,
                        required=False)
    parser.add_argument('-nm', '--for_next_month', default="Y", type=str,
                        required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    for_next_month = args.for_next_month

    logger = get_logger()
    logger.info("Scripts begins")

    status = False
    schema = 'prod2-generico'
    err_msg = ''
    df_uri1 = ''
    df_uri2 = ''
    drugs_not_in_doi = 0
    drugs_missed = 0
    drugs_updated = 0

    # getting run date for the script
    run_date = str(datetime.now().date())
    current_month_date = (
            datetime.now().date() -
            timedelta(days=datetime.now().day - 1))

    if for_next_month == 'Y':
        forecast_date = str(
            datetime(current_month_date.year +
                     int(current_month_date.month / 12),
                     ((current_month_date.month % 12) + 1), 1).date())
    else:
        forecast_date = str(current_month_date)

    try:
        rs_db = DB()
        rs_db.open_connection()
        wh_safety_stock_df_query = """
        select
            *
        from
            "prod2-generico"."wh-safety-stock" wss
        where
            "forecast-type" = 'forecast'
            and "forecast-date" = '{forecast_date}'
                """.format(forecast_date=forecast_date)
        wh_safety_stock_df = rs_db.get_df(wh_safety_stock_df_query)
        wh_safety_stock_df.columns = [c.replace('-', '_') for c in wh_safety_stock_df.columns]

        # CONSIDERING DRUG TYPES FOR DATA LOAD
        type_list = rs_db.get_df(
            'select distinct type from "prod2-generico".drugs')
        type_list = tuple(type_list[
                              ~type_list.type.isin(
                                  ['', 'banned', 'discontinued-products'])][
                              'type'])

        # UPLOADING SAFETY STOCK NUMBERS IN DRUG-ORDER-INFO
        ss_data_upload = wh_safety_stock_df.query('order_upto_point > 0')[
            ['wh_id', 'drug_id', 'safety_stock', 'reorder_point',
             'order_upto_point']]
        ss_data_upload.columns = [
            'store_id', 'drug_id', 'corr_min', 'corr_ss', 'corr_max']
        logger.info('updating DOID')
        new_drug_entries, missed_entries = doid_update(
            ss_data_upload, type_list, rs_db, schema, logger)
        logger.info('DOID updated')
        drugs_not_in_doi = len(new_drug_entries)
        drugs_missed = len(missed_entries)
        drugs_updated = len(ss_data_upload) - len(missed_entries) - len(new_drug_entries)
        s3 = S3()
        df_uri1 = s3.save_df_to_s3(df=new_drug_entries,
                                   file_name='DOID_new_drug_entries_{date}.csv'.format(date=str(run_date)))
        df_uri2 = s3.save_df_to_s3(df=new_drug_entries,
                                   file_name='DOID_missed_entries_{date}.csv'.format(date=str(run_date)))

        status = True

    except Exception as error:
        err_msg = str(error)
        logger.exception(str(error))

    email = Email()
    if status:
        result = 'Success'
        email.send_email_file(subject=f"wh_doid_update ({env}): {result}",
                              mail_body=f"""
                                drugs updated successfully --> {drugs_updated}
                                drugs not updated --> {drugs_missed}
                                drugs not in doid --> {drugs_not_in_doi}
                                """,
                              to_emails=email_to, file_uris=[df_uri1, df_uri2])
    else:
        result = 'Failed'
        email.send_email_file(subject=f"wh_doid_update ({env}): {result}",
                              mail_body=f"Run time: {datetime.now()} {err_msg}",
                              to_emails=email_to, file_uris=[])

    logger.info("Script ended")
